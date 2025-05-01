import streamlit as st
from OM import planning  # of waar je functie staat

st.set_page_config(page_title="Planning", layout="wide")
st.title("📦 Planningstijdlijn")

if 'excel_df' in st.session_state:
    df = st.session_state['excel_df']
    fig = planning(df)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ Upload eerst een bestand op de hoofdpagina.")

