"""Streamlit UI: streamlit run app.py"""
import streamlit as st

from main import run

st.set_page_config(page_title="Research Agent", page_icon="🔎")
st.title("🔎 Multi-Agent Research Assistant")
st.caption("Planner → parallel researchers → writer ⇄ critic")

topic = st.text_input("Research topic", placeholder="e.g. solid-state batteries for EVs")
if st.button("Run research", disabled=not topic):
    log = st.status("Agents working...", expanded=True)
    report, path = run(topic, on_event=lambda m: log.write(m))
    log.update(label="Done", state="complete")
    st.markdown(report)
    st.download_button("Download report", report, file_name=path.split("/")[-1])
