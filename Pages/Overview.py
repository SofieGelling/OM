import streamlit as st
import pandas as pd
from OM import planning  # of from Planning import planning

st.title("📦 Planningstijdlijn")

uploaded = st.file_uploader("Upload Excel-bestand", type="xlsx")
if uploaded:
    df = pd.read_excel(uploaded, sheet_name="Samples Release 2025")
    fig = planning(df)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("👈 Upload een Excelbestand om verder te gaan.")
