"""Streamlit screen. Run with:  python -m streamlit run app.py"""
import json
import tempfile

import pandas as pd
import streamlit as st

from checks import check
from extractor import build_prompt, extract, parse_json, read_notice, which_provider
from fields import FIELDS

st.set_page_config(page_title="Notice Reader", layout="wide")
st.title("Class Action Notice Reader")
st.caption("AI reads the notice. Code checks the AI. A person decides.")

provider = which_provider()
labels = {"gemini": "Gemini API (free key)", "claude": "Claude API",
          "manual": "Manual mode (free, no key)"}
st.info(f"Mode: {labels[provider]}")

up = st.file_uploader("Upload a settlement notice", type=["pdf", "txt"])


def show_results(result, text):
    st.subheader("Extracted terms")
    st.dataframe(pd.DataFrame([
        {"field": k,
         "value": result.get("fields", {}).get(k),
         "evidence": result.get("evidence", {}).get(k)}
        for k in FIELDS
    ]), use_container_width=True)

    st.subheader("Needs human review")
    issues = check(result, text)
    if issues:
        st.dataframe(pd.DataFrame(issues, columns=["field", "issue", "detail"]),
                     use_container_width=True)
    else:
        st.success("All checks passed")
    st.download_button("Download JSON", json.dumps(result, indent=2), "notice.json")


if up:
    suffix = "." + up.name.split(".")[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(up.read())
    text = read_notice(tmp.name)

    if provider == "manual":
        st.subheader("Step 1: Copy this prompt")
        st.caption("Click the copy icon (top right of the box), then paste it into "
                   "claude.ai or gemini.google.com (both free).")
        st.code(build_prompt(text), language=None)
        st.subheader("Step 2: Paste the AI's answer here")
        answer = st.text_area("AI answer (the JSON)", height=250)
        if st.button("Check the answer") and answer.strip():
            try:
                show_results(parse_json(answer), text)
            except Exception as e:
                st.error(f"Could not read the answer as JSON: {e}")
    else:
        with st.spinner("Reading notice..."):
            result = extract(text)
        show_results(result, text)
