# Run 20261018-0025_keywords_keywords

- Backend: `keywords`, model: `keywords`
- Prompt: `prompts/allergen_system.txt`
- Cases run: 71, errors: 0, scored: 59 (cases with a `suspected_issue` are excluded from the scores)

| Group | Cases | Recall | Recall incl. may_contain | Precision | Exact match | Median latency (s) | Max latency (s) |
|---|---|---|---|---|---|---|---|
| all | 59 | 64% | 64% | 93% | 41% | 0.00 | 0.00 |
| menu_declared | 18 | 44% | 44% | 100% | 11% | 0.00 | 0.00 |
| menu_team_labelled | 21 | 57% | 57% | 93% | 48% | 0.00 | 0.00 |
| recipe_synthetic | 20 | 92% | 92% | 91% | 60% | 0.00 | 0.00 |


## Audit cases (declaration suspected wrong) — review by hand

| id | dish | declared | model contains | model may_contain | suspected issue |
|---|---|---|---|---|---|
| DEC-02 | Spaghetti alla Napoletana | gluten;crustaceans;eggs;fish;sulphites;molluscs | fish;gluten;molluscs |  | Crustaceans declared although no crustacean is listed (possibly a shared sauce base). |
| DEC-04 | Spaghetti al pesto | gluten;eggs | gluten |  | No milk declared although pesto usually contains parmesan or pecorino: to verify. |
| DEC-17 | Coupe Odette | peanuts;nuts | nuts;peanuts |  | No milk or eggs declared, although the same menu says all its ice creams contain milk and egg: probable omission. |
| DEC-18 | Panna cotta | milk | nuts |  | Hazelnut option without a nut declaration: probable omission. |
| DEC-20 | Poulet Gong Bao | gluten;peanuts;soy | nuts |  | Cashews are tree nuts (8) but peanuts (5) are declared: error, or the recipe actually uses peanuts. |
| DEC-21 | Noix de St. Jacques à l’ail | gluten;crustaceans;soy | molluscs;nuts |  | Scallops are molluscs (14), not crustaceans (2): probable error. |
| DEC-22 | Salade de calamar | crustaceans;sesame | molluscs |  | Squid is a mollusc (14), not a crustacean (2): probable error. |
| DEC-23 | Salade d’algues | mustard | sesame |  | Sesame oil listed but mustard (10) declared instead of sesame (11): probable typo. |
| DEC-24 | Edamame |  |  |  | Edamame are soybeans but no allergen is declared: probable omission. |
| DEC-28 | Tom Yam Gung Bao | gluten;crustaceans;fish | crustaceans;fish;molluscs;nuts |  | Scallops listed but no molluscs (14) declared: probable omission. |
| DEC-29 | Maki saumon roll | crustaceans;milk | fish;milk |  | Salmon is fish (4) but crustaceans (2) declared: probable error. |
| DEC-30 | Printemps roll avocat cheese | gluten | milk |  | Cheese without milk (7), while the maki version of the same filling declares 7: probable omission. |