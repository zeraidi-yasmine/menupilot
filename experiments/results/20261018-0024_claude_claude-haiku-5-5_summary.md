# Run 20261018-0024_claude_claude-haiku-5-5

- Backend: `claude`, model: `claude-haiku-5-5`
- Prompt: `prompts/allergen_system.txt`
- Cases run: 71, errors: 0, scored: 59 (cases with a `suspected_issue` are excluded from the scores)

| Group | Cases | Recall | Recall incl. may_contain | Precision | Exact match | Median latency (s) | Max latency (s) |
|---|---|---|---|---|---|---|---|
| all | 59 | 80% | 94% | 93% | 47% | 0.97 | 1.57 |
| menu_declared | 18 | 61% | 86% | 100% | 22% | 0.97 | 1.36 |
| menu_team_labelled | 21 | 93% | 98% | 87% | 57% | 0.95 | 1.15 |
| recipe_synthetic | 20 | 90% | 100% | 93% | 60% | 0.98 | 1.57 |

- Mean tokens per dish: 1216 in, 80 out
- Mean cost per dish: $0.000162 (total for this run: $0.0115)

## Audit cases (declaration suspected wrong) — review by hand

| id | dish | declared | model contains | model may_contain | suspected issue |
|---|---|---|---|---|---|
| DEC-02 | Spaghetti alla Napoletana | gluten;crustaceans;eggs;fish;sulphites;molluscs | fish;gluten;molluscs | eggs;milk | Crustaceans declared although no crustacean is listed (possibly a shared sauce base). |
| DEC-04 | Spaghetti al pesto | gluten;eggs | eggs;gluten;milk | nuts;sulphites | No milk declared although pesto usually contains parmesan or pecorino: to verify. |
| DEC-17 | Coupe Odette | peanuts;nuts | milk;nuts;peanuts | eggs;gluten;soy | No milk or eggs declared, although the same menu says all its ice creams contain milk and egg: probable omission. |
| DEC-18 | Panna cotta | milk | milk;nuts | eggs;gluten;soy | Hazelnut option without a nut declaration: probable omission. |
| DEC-20 | Poulet Gong Bao | gluten;peanuts;soy | gluten;nuts;soy | eggs;sesame;sulphites | Cashews are tree nuts (8) but peanuts (5) are declared: error, or the recipe actually uses peanuts. |
| DEC-21 | Noix de St. Jacques à l’ail | gluten;crustaceans;soy | molluscs | eggs;fish;gluten;milk;soy | Scallops are molluscs (14), not crustaceans (2): probable error. |
| DEC-22 | Salade de calamar | crustaceans;sesame | molluscs |  | Squid is a mollusc (14), not a crustacean (2): probable error. |
| DEC-23 | Salade d’algues | mustard | sesame | gluten;soy;sulphites | Sesame oil listed but mustard (10) declared instead of sesame (11): probable typo. |
| DEC-24 | Edamame |  | soy |  | Edamame are soybeans but no allergen is declared: probable omission. |
| DEC-28 | Tom Yam Gung Bao | gluten;crustaceans;fish | crustaceans;fish;molluscs | eggs;gluten;soy;sulphites | Scallops listed but no molluscs (14) declared: probable omission. |
| DEC-29 | Maki saumon roll | crustaceans;milk | fish;milk | gluten;sesame;soy;sulphites | Salmon is fish (4) but crustaceans (2) declared: probable error. |
| DEC-30 | Printemps roll avocat cheese | gluten | gluten;milk | crustaceans;eggs;sesame;soy | Cheese without milk (7), while the maki version of the same filling declares 7: probable omission. |