import streamlit as st
import pandas as pd
from OM import planning      

# Runnen:  streamlit run /Users/sofiegellings/OM/StreamLit.py

st.set_page_config(page_title="Batch planner", layout="wide")
st.title("Open Batches Viewer")

uploaded = st.file_uploader("Upload Excel file", type="xlsx")

if uploaded:
    raw = pd.read_excel(uploaded, sheet_name="Samples Release 2025")
    fig = planning(raw)            # ⬅️ één regel, klaar
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("👈 Voeg het 'TAT KPI' Excel-bestand toe om de tijdlijn te zien")
