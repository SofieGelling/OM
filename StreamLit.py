import streamlit as st
import pandas as pd
from Functies import remove_empty_rows
# pip install st-pages
# streamlit run StreamLit.py

# -------------------------    Pagina met toggle    ---------------------------------------------------

st.set_page_config(page_title="Excel Upload", layout="wide")
st.title("📥 Upload your Excel file")

uploaded = st.file_uploader("Upload Excel file", type="xlsx")

if uploaded:
    df = pd.read_excel(uploaded, sheet_name="Samples Release 2025")
    df = remove_empty_rows(df)
    st.session_state['excel_df'] = df  # ⬅️ store for use on other pages
    st.success("✅ File saved! You can now proceed to the other pages.")

    # Optional: preview
    st.subheader("Preview:")
    st.dataframe(df.head())
else:
    st.info("👈 Upload a file to get started.")

