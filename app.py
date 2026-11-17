"""
MenuPilot MVP: paste a menu, get the 14 EU allergens of each dish.

Run from the repository root:  streamlit run app.py
"""

import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from menupilot.allergens import (ALLERGENS, detect_allergens, is_section_heading, load_system_prompt,
                                 make_client, split_menu)
from menupilot.pdf_export import allergen_pdf

# The API key comes from .env locally, or from the app's secrets once deployed.
load_dotenv()
try:
    if "ANTHROPIC_API_KEY" in st.secrets:
        os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]
except FileNotFoundError:
    pass  # no secrets file when running locally


def allergen_table(results):
    """
    One row per dish and one True/False column per EU allergen, ticked when the
    model says the dish contains it. "May contain" stays as text: those allergens
    are suggestions the owner has to confirm, so they are not ticked by default.
    """
    rows = []
    for _, r in results.iterrows():
        contains = set(filter(None, r["Contains"].split(", ")))
        to_confirm = r["May contain"]
        if r["Error"]:
            to_confirm = "⚠ Analysis failed: tick by hand"
        elif not contains and not to_confirm:
            to_confirm = "⚠ No allergen found: please check"  # an empty row must not look "safe"
        row = {"Dish": r["Dish"], "Not a dish": False}
        row.update({a: a in contains for a in ALLERGENS})
        row["To confirm"] = to_confirm
        rows.append(row)
    return pd.DataFrame(rows, columns=["Dish", "Not a dish", *ALLERGENS, "To confirm"])


st.set_page_config(page_title="MenuPilot", page_icon="🍽️")
st.title("MenuPilot")
st.write("Paste your menu, one dish per line. MenuPilot suggests the allergens of each dish; "
         "you check them before publishing.")

menu = st.text_area(
    "Menu",
    height=220,
    placeholder="Bouneschlupp - haricots verts, pommes de terre, lardons, crème\n"
                "Gromperekichelcher\n"
                "Tarte aux quetsches - 6,50 €",
)

if st.button("Find allergens", type="primary"):
    dishes = split_menu(menu)
    skipped = [line.strip() for line in menu.splitlines() if line.strip() and is_section_heading(line)]
    if skipped:
        st.caption("Skipped as section headings: " + ", ".join(skipped))
    if not dishes:
        st.warning("No dishes found. Paste at least one dish name, one per line.")
    elif not os.getenv("ANTHROPIC_API_KEY"):
        st.error("No API key found. Add ANTHROPIC_API_KEY to your .env file (see .env.example).")
    else:
        client = make_client()
        system_prompt = load_system_prompt()
        rows = []
        progress = st.progress(0.0, text="Analysing dishes…")
        for i, (name, description) in enumerate(dishes, start=1):
            try:
                result = detect_allergens(name, description, client=client, system_prompt=system_prompt)
                error = ""
            except Exception as exc:  # one failed dish should not stop the whole menu
                result, error = {}, f"Analysis failed: {type(exc).__name__}"
            rows.append({
                "Dish": name,
                "Contains": ", ".join(result.get("contains", [])),
                "May contain": ", ".join(result.get("may_contain", [])),
                "Error": error,
                "cost_usd": result.get("cost_usd"),
                "latency_s": result.get("latency_s"),
            })
            progress.progress(i / len(dishes), text=f"Analysed {i} of {len(dishes)} dishes")
        progress.empty()
        st.session_state["results"] = pd.DataFrame(rows)
        st.session_state["table"] = allergen_table(st.session_state["results"])
        st.session_state.pop("validated", None)  # a new analysis needs a new validation

if "results" in st.session_state:
    df = st.session_state["results"]
    if "Not a dish" not in st.session_state["table"].columns:
        # The table in this browser session was made by an older version of the app: rebuild it.
        st.session_state.pop("allergen_editor", None)
        st.session_state.pop("validated", None)
        st.session_state["table"] = allergen_table(df)
    st.subheader("Check the allergens")
    st.write("Ticked = the AI found this allergen. Tick or untick to match your recipes. "
             "\"To confirm\" lists allergens a standard recipe usually has: ask the chef.")
    edited = st.data_editor(
        st.session_state["table"],
        hide_index=True,
        use_container_width=True,
        disabled=["Dish", "To confirm"],
        column_config={
            "Not a dish": st.column_config.CheckboxColumn(
                "Not a dish", help="Tick if this line is a heading or something else that is not a dish."),
            **{a: st.column_config.CheckboxColumn(a.capitalize()) for a in ALLERGENS},
        },
        key="allergen_editor",
    )
    dishes = edited[~edited["Not a dish"]].drop(columns="Not a dish")
    no_allergen = dishes[~dishes[ALLERGENS].any(axis=1)]["Dish"].tolist()
    if no_allergen:
        st.warning("No allergen ticked for: " + ", ".join(no_allergen) + ". This is right only if the dish "
                   "really contains none of the 14 allergens.")
    if st.button("Validate allergens"):
        st.session_state["validated"] = edited.copy()
    if "validated" in st.session_state:
        if st.session_state["validated"].equals(edited):
            st.success(f"Allergen table validated for {len(dishes)} dishes.")
            pdf_title = st.text_input("Title of the PDF", value="Menu")
            pdf_col, csv_col, _ = st.columns([1, 1, 3])  # narrow columns keep the buttons side by side
            pdf_col.download_button("Download as PDF", data=allergen_pdf(dishes, title=pdf_title),
                                    file_name="menupilot_allergens.pdf", mime="application/pdf")
            csv_col.download_button("Download as CSV", data=dishes.to_csv(index=False).encode("utf-8-sig"),
                                    file_name="menupilot_allergens.csv", mime="text/csv")
        else:
            st.warning("You changed the table after validating. Click \"Validate allergens\" again.")

    failed = (df["Error"] != "").sum()
    if failed:
        st.error(f"{failed} dish(es) could not be analysed. Check them by hand or try again.")
    ok = df[df["Error"] == ""]
    if len(ok):
        st.caption(f"{len(ok)} dishes · total cost ${ok['cost_usd'].sum():.4f} · "
                   f"median time per dish {ok['latency_s'].median():.1f} s")
    st.info("These are suggestions from an AI model and can be wrong. "
            "Check every dish against your recipes before publishing.")
