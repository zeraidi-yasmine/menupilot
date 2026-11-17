# TODO: after M3

Everything for M3 (due Mon 16 Nov) is done or tracked elsewhere. This list is what comes next. The bugs and the planned fixes are in [KNOWNBUGS.md](KNOWNBUGS.md).

## Features still planned

- [ ] File upload (PDF text layer, plain text) and photo input.
- [ ] Translation FR / DE / EN (`prompts/translate_system.txt`), checked by hand on 10 dishes.
- [ ] Chef questions as a short dialogue instead of the "To confirm" column (optional).
- [ ] Deploy on Streamlit Community Cloud with the API key in its secrets and a low spend limit on the key; live URL in the README.
- [ ] Replace the API key that was shared on Discord (new key, delete the old one).

## M4 (due Mon 30 Nov): testing and iteration

- [ ] Prompt fixes from KNOWNBUGS.md: dishes without a description, wine and sulphites, mayonnaise, mustard and celery in sauces, too many questions. Each change is re-run on the 71 cases of `data/eval_cases.csv` and on the three test menus.
- [ ] Evaluation with at least 20 cases or 5 test users and a written script; results table with the metric before and after the changes.
- [ ] At least 5 issues found, each with the commit that fixed it.
- [ ] At least 3 failure cases with the real input and output.
- [ ] Updated cost figures if the prompt or the model changes.

## Final package (due Sun 13 Dec, 23:59)

- [ ] README complete against the 10 headings (business case, EU AI Act, privacy and ethics in 250 words or fewer, AI tools used, who did what).
- [ ] Setup in 5 steps or fewer, example data, `.env.example`.
- [ ] Slides as a PDF and a backup demo video of 2 to 3 minutes.
- [ ] Individual reflections, each student on Moodle.
- [ ] Tag `final-submission`. Presentation and live demo on Wed 16 Dec.
