# Architecture (M3, 13 November 2026)

![MenuPilot architecture](architecture.png)

**Status:** this is what is built today (the M3 MVP). The M2 sketch, which also planned file upload and translation, is kept as [m2_architecture_plan.png](m2/m2_architecture_plan.png).

## How it works

The owner pastes a menu (one dish per line) into the Streamlit app (`app.py`). `menupilot/allergens.py` splits it into dishes (name and description; section headings such as "Entrées" are skipped, and any other line can be ticked "Not a dish"). For each dish, one request goes to the Anthropic Messages API with the prompt from `prompts/allergen_system.txt`. The model is `claude-haiku-5-5`, with a forced tool call so that the answer is JSON with two allergen lists: `contains` (certain) and `may_contain` (to confirm). The app shows a table with one checkbox per allergen; the `may_contain` allergens appear in the "To confirm" column, as questions for the chef. The owner corrects the table and clicks "Validate allergens". Only then can the table be downloaded as a PDF menu or a CSV (`menupilot/pdf_export.py`). The offline evaluation (`experiments/allergen_test.py`) uses the same prompt on the 71 dishes of `data/eval_cases.csv`.

## What leaves our system

- **To Anthropic (API):** for each dish, the dish name and description as typed, together with the prompt. One request per dish. No interview data, no guest data, no uploaded files (there is no upload).
- **Stays with us:** the pasted menu, the results, the table and the validated table live in the session memory of the app only. Nothing is written to disk; it is lost when the session ends. The PDF and CSV are downloaded to the owner's own computer.

## Secrets

The API key (`ANTHROPIC_API_KEY`) lives in `.env`, which is listed in `.gitignore` and never committed; `.env.example` shows the format without a key. When the app is deployed, the key goes into the hosting platform's secrets instead. The key is only sent to Anthropic, to authenticate each request.

## Where things live

| What | Where |
|---|---|
| User interface, validation step, downloads | `app.py` |
| Menu splitting, heading detection, allergen call | `menupilot/allergens.py` |
| Prompt | `prompts/allergen_system.txt` |
| Model name, `max_tokens`, JSON schema, prices | `menupilot/allergens.py` |
| PDF export | `menupilot/pdf_export.py` |
| Evaluation script and data | `experiments/allergen_test.py`, `data/eval_cases.csv` |

## Not built yet

File upload (PDF, photo), translation FR/DE/EN, persistent storage, user accounts. The chef questions are the "To confirm" column; there is no separate question dialogue.

## Switch option

The evaluation script can also run `llama3.1:8b` locally through Ollama (M2: recall 53%, against 80% for Claude on the same 59 cases). The app itself uses the Anthropic API only.

## Diagram source

The picture above is exported from this Mermaid source. Edit it here, then export it again to `architecture.png` (for example with `mmdc -i architecture.mmd -o docs/architecture.png -s 3`).

```mermaid
flowchart TB
    owner(["<b>Restaurant owner / chef</b><br/>web browser"])
    files(["<b>PDF / CSV file</b><br/>saved on the owner's computer"])

    subgraph ours ["MenuPilot: our system (Python, Streamlit)"]
        direction TB
        app["<b>1. Streamlit app</b> (app.py)<br/>paste menu, edit table, Validate allergens"]
        split["<b>2. Menu splitting</b> (menupilot/allergens.py)<br/>one dish per line, headings skipped"]
        detect["<b>3. Allergen detection</b> (menupilot/allergens.py)<br/>one call per dish, JSON answer"]
        export["<b>4. Export</b> (menupilot/pdf_export.py)<br/>validated table as PDF and CSV"]
        state[("<b>Session memory</b><br/>results, table, validated table<br/>not saved to disk")]
        subgraph repo ["In the repository"]
            direction TB
            prompt[("<b>Prompt</b><br/>prompts/allergen_system.txt")]
            config[("<b>Model config, in code</b><br/>claude-haiku-5-5, max_tokens 300,<br/>JSON schema, prices")]
        end
        env[(".env, git-ignored<br/><b>ANTHROPIC_API_KEY</b><br/>(Streamlit secrets if deployed)")]
        evalbox["<b>Offline evaluation</b><br/>experiments/allergen_test.py<br/>71 dishes in data/eval_cases.csv"]
    end

    subgraph anth ["LEAVES OUR SYSTEM: sent to Anthropic"]
        api["<b>Anthropic Messages API</b><br/>model claude-haiku-5-5"]
    end

    owner -->|"menu text"| app
    app -->|"menu text"| split
    split -->|"dishes: name + description"| detect
    detect -->|"suggested allergens"| app
    app <--> state
    app -->|"validated table"| export
    export --> files
    prompt --> detect
    config --> detect
    env -. "API key" .-> detect
    detect <==>|"OUT: dish name, description, prompt<br/>IN: contains / may_contain (JSON)"| api
    prompt --> evalbox
    evalbox -. "OUT: test dishes" .-> api

    classDef external fill:#fdebd0,stroke:#d35400,color:#000
    classDef data fill:#eaeded,stroke:#566573,color:#000
    classDef secret fill:#fadbd8,stroke:#c0392b,color:#000
    classDef person fill:#d6eaf8,stroke:#2471a3,color:#000
    class api external
    class prompt,config,state data
    class env secret
    class owner,files person
    style anth fill:#fef5e7,stroke:#d35400,stroke-width:2px,stroke-dasharray:6 4
    style ours fill:#f8f9f9,stroke:#2e4053,stroke-width:2px
    style repo fill:#f2f4f4,stroke:#99a3a4,stroke-dasharray:3 3
```
