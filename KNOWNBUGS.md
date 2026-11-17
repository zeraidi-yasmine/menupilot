# Known bugs and planned fixes (13 Nov 2026)

This file lists the bugs we found in MenuPilot and what we plan to fix, in order. The bugs come from three menu tests (a generated menu, Le Quai Steffen and Luci). Results and numbers are in PROJECT_LOG.md (M3 section); the short version for readers is in README section 7. When a bug is fixed, tick it here and log the commit.

Source: the generated test menu, Le Quai Steffen and Luci (see PROJECT_LOG.md, M3 section, and README section 7).
Rule: every fix that changes the prompt must be re-run on the 71 cases of `data/eval_cases.csv` and on the three test menus, and the before/after numbers go in the M4 results table. Each fixed issue is logged with its commit.
Menu texts and the restaurants' allergen lists are not committed: keep the raw exports on your own machine and log only the numbers.

## Before M3 (Mon 16 Nov): small fixes, no prompt change

- [x] **Headings with an article or combined headings** ("Les Entrées", "Poisson & Viande", "Fromages & Desserts", "The Essentials of Luxembourg", "Burgers", "From the Grill"). Strip a leading article (Les, Le, La, L', Die, Der, Das, The) and split combined headings on "&", "et", "und", "and" before matching the heading list; add the missing words (fish, burgers, grill, poisson, viande, fromages, pâtes).
- [x] **"Skip" option per row** in the editable table, because no heading list will catch every heading: the owner ticks "not a dish" and the row is ignored.
- [x] **Warning for empty rows.** A dish with no certain allergen and no question must not look "safe": show "No allergen found, please check" in the "To confirm" column and highlight the row.
- [x] Re-run the three test menus and note which of the bugs above are fixed (README section 7).

## After M3 (by Mon 30 Nov, M4): prompt and evaluation changes

- [ ] **Dishes without a description or with a vague name** ("Le dessert du jour", "Boule de glace", "Tarte aux quetsches"): the model must ask the chef instead of answering nothing or answering with certainty. Prompt change, then check recall on the 71 cases.
- [ ] **Wine, vinegar, stocks and sauces:** report sulphites at least as "to confirm" for any wine, vinegar, dried fruit or stock; as certain when wine is named as an ingredient ("vin blanc", "sauce au vin rouge", "Rieslingspaschtéit"). Both restaurants declare sulphites in most dishes.
- [ ] **Mayonnaise, mustard, celery:** mayonnaise means eggs and usually mustard; stocks and sauces often contain celery. Check whether a prompt hint helps without adding noise.
- [ ] **Too many questions** (8 for "Soupe de poisson", 2.7 per dish on average at Le Quai Steffen): rank the questions by likelihood and show at most a few. This can lower recall, so measure it first.
- [ ] **Nuts never reported or asked about** (Luci, 4 dishes): look at the declaration with the restaurant's numbering in mind before changing anything.
- [ ] **Restaurant coding that does not fit the standard list** (seafood, missing legend): do not tune the prompt to it. Say it in the README as a limit of the comparison.

## Evaluation and documentation

- [ ] Put the first run (before the fixes) and the re-run (after) in one results table for M4.
- [ ] Mark each fixed bug in README section 7 and in PROJECT_LOG.md with the commit that fixed it (M4 asks for at least 5 issues, each with its commit).
- [ ] Keep at least 3 failure cases with the real input and output (README section 6).
- [ ] Update the cost figures if the prompt gets longer.
