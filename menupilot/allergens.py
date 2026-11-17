"""
Allergen detection for MenuPilot.

Takes the text of a restaurant menu, splits it into dishes and asks Claude which
of the 14 EU allergens each dish contains. Extracted from experiments/allergen_test.py
(M2): same prompt file, same JSON schema, same user message, so the M2 results
still describe what the app does.
"""

import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROMPT_FILE = ROOT / "prompts" / "allergen_system.txt"

DEFAULT_MODEL = "claude-haiku-5-5"

ALLERGENS = ["gluten", "crustaceans", "eggs", "fish", "peanuts", "soy", "milk",
             "nuts", "celery", "mustard", "sesame", "sulphites", "lupin", "molluscs"]

# USD per million tokens. Source: https://platform.claude.com/docs/en/about-claude/pricing
# (checked 18 Oct 2026). Update if you change model.
PRICES = {
    "claude-haiku-5-5": {"input": 0.10, "output": 0.50},
    "claude-sonnet-5-5": {"input": 2.00, "output": 10.00},
}

SCHEMA = {
    "type": "object",
    "properties": {
        "contains": {"type": "array", "items": {"type": "string", "enum": ALLERGENS}},
        "may_contain": {"type": "array", "items": {"type": "string", "enum": ALLERGENS}},
    },
    "required": ["contains", "may_contain"],
}


def load_system_prompt():
    return PROMPT_FILE.read_text(encoding="utf-8")


# ---------------------------------------------------------------- menu splitting

BULLET = re.compile(r"^\s*[-*•·]\s*")
PRICE = re.compile(r"\s*[-–—.]*\s*\d+(?:[.,]\d{1,2})?\s*(?:€|eur|euros?)?\s*$", re.IGNORECASE)
SEPARATOR = re.compile(r"\s+[-–—]\s+|:\s+")

# Section headings found on menus (FR, EN, DE, IT). A line that is exactly one of
# these, with or without a trailing colon and in any case, is a heading, not a dish.
# Kept deliberately narrow: skipping a real dish would hide its allergens.
SECTION_HEADINGS = {
    # starters
    "entrées", "entrees", "entrée", "entree", "hors d'oeuvre", "hors d'œuvre", "hors-d'oeuvre",
    "starters", "appetizers", "vorspeisen", "antipasti",
    # mains
    "plats", "plats principaux", "plat principal", "mains", "main courses", "main dishes",
    "hauptgerichte", "hauptspeisen", "primi", "primi piatti", "secondi", "secondi piatti",
    # desserts
    "desserts", "nachspeisen", "nachtisch", "dolci",
    # other common sections
    "soupes", "soups", "suppen", "salades", "salads", "salate",
    "pâtes", "pates", "pasta", "pizzas", "viandes", "poissons", "fisch",
    "accompagnements", "sides", "side dishes", "beilagen",
    "fromages", "boissons", "drinks", "getränke",
    "menu", "menu du jour", "menu enfant", "kids menu", "suggestions", "suggestions du chef",
    "carte", "à la carte", "a la carte", "végétarien", "vegetarian",
    "fish", "burgers", "grillades", "from the grill", "rotisserie", "rôtisserie", "veggy", "vegan",
}

# Singular words that are only treated as headings inside a combined heading such as
# "Poisson & Viande" or "Fromages & Desserts" (alone, "Poisson" could be a dish).
COMBINED_ONLY = {"poisson", "viande", "fromage", "dessert", "entrée", "entree", "plat", "salade",
                 "soupe", "burger", "grill", "meat", "cheese", "starter", "main", "side"}

ARTICLE = re.compile(r"^(?:(?:les|le|la|des|der|die|das|the|nos|notre|unsere|our)\s+|l')", re.IGNORECASE)
COMBINE = re.compile(r"\s*(?:&|/|\+|,|\bet\b|\bund\b|\band\b)\s*", re.IGNORECASE)
EDGES = re.compile(r"^[\W_]+|[\W_]+$")


def is_section_heading(line):
    """
    True if the line is a menu section heading such as "Entrées", "DESSERTS", "Plats :",
    "Les Pâtes", "— Desserts —" or a combined one like "Poisson & Viande".
    """
    normalized = EDGES.sub("", line.strip().lower().replace("’", "'"))
    if normalized in SECTION_HEADINGS or ARTICLE.sub("", normalized) in SECTION_HEADINGS:
        return True
    parts = [ARTICLE.sub("", EDGES.sub("", p)) for p in COMBINE.split(normalized)]
    return len(parts) > 1 and all(p in SECTION_HEADINGS or p in COMBINED_ONLY for p in parts)


def split_menu(text):
    """
    Turn a pasted menu into a list of (dish_name, description) pairs.

    MVP rule: one dish per line. "Name - description" or "Name: description"
    is split in two; bullets and a trailing price are removed; empty lines
    and lines shorter than 3 characters are skipped. Lines that are a known
    section heading ("Entrées", "Desserts:", "PLATS") are skipped too, unless
    they carry a price.
    """
    dishes = []
    for line in text.splitlines():
        line = BULLET.sub("", line).strip()
        without_price = PRICE.sub("", line).strip()
        has_price = without_price != line
        line = without_price
        if len(line) < 3:
            continue
        if not has_price and is_section_heading(line):
            continue
        parts = SEPARATOR.split(line, maxsplit=1)
        name = parts[0].strip()
        description = parts[1].strip() if len(parts) > 1 else ""
        dishes.append((name, description))
    return dishes


# ---------------------------------------------------------------- detection

def user_message(dish_name, description=""):
    # Same format as in the M2 experiment.
    text = f"Dish: {dish_name}"
    if description and description.strip() != dish_name.strip():
        text += f"\nDescription: {description}"
    return text


def make_client(timeout=30.0, max_retries=2):
    import anthropic
    return anthropic.Anthropic(timeout=timeout, max_retries=max_retries)  # reads ANTHROPIC_API_KEY


def detect_allergens(dish_name, description="", client=None, system_prompt=None, model=DEFAULT_MODEL):
    """
    Ask Claude for the allergens of one dish.

    Returns a dict with: contains, may_contain (sorted lists of EU allergen names),
    tokens_in, tokens_out, cost_usd, latency_s. Raises on API errors: the caller decides
    what to show the user.
    """
    client = client or make_client()
    system_prompt = system_prompt or load_system_prompt()

    start = time.perf_counter()
    response = client.messages.create(
        model=model,
        max_tokens=300,
        system=system_prompt,
        tools=[{
            "name": "report_allergens",
            "description": "Report the allergens of the dish.",
            "input_schema": SCHEMA,
        }],
        tool_choice={"type": "tool", "name": "report_allergens"},  # forces a JSON answer
        messages=[{"role": "user", "content": user_message(dish_name, description)}],
    )
    latency = time.perf_counter() - start

    answer = next((b.input for b in response.content if b.type == "tool_use"), None)
    if answer is None:
        raise ValueError("The model did not return an allergen list.")

    # Keep only valid allergen names; "may contain" never repeats "contains".
    contains = sorted({a for a in answer.get("contains", []) if a in ALLERGENS})
    may_contain = sorted({a for a in answer.get("may_contain", []) if a in ALLERGENS} - set(contains))

    tokens_in = response.usage.input_tokens
    tokens_out = response.usage.output_tokens
    price = PRICES.get(model)
    cost = (tokens_in * price["input"] + tokens_out * price["output"]) / 1_000_000 if price else None

    return {
        "contains": contains,
        "may_contain": may_contain,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "cost_usd": cost,
        "latency_s": round(latency, 2),
    }
