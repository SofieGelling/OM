import streamlit as st
import pandas as pd
from OM import planning  # Zorg dat deze functie bestaat

st.set_page_config(page_title="Batch planner", layout="wide")
st.title("📦 Open Batches Viewer")

uploaded = st.file_uploader("Upload Excel-bestand", type="xlsx")

if uploaded:
    df = pd.read_excel(uploaded, sheet_name="Samples Release 2025")

    # Toggle of expander om de grafiek zichtbaar te maken
    show_plot = st.toggle("📊 Toon/verberg planning")

    if show_plot:
        fig = planning(df)
        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("👈 Voeg het 'TAT KPI' Excel-bestand toe om de tijdlijn te zien")

## put this is command file
## python -m streamlit run StreamLit.py