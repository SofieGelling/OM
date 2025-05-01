import streamlit as st
import pandas as pd
# pip install st-pages
# streamlit run StreamLit.py

# -------------------------    Pagina met toggle    ---------------------------------------------------

st.set_page_config(page_title="Excel Upload", layout="wide")
st.title("📥 Upload je Excelbestand")

uploaded = st.file_uploader("Upload Excel-bestand", type="xlsx")

if uploaded:
    df = pd.read_excel(uploaded, sheet_name="Samples Release 2025")
    st.session_state['excel_df'] = df  # ⬅️ opslaan voor andere pagina’s
    st.success("✅ Bestand opgeslagen! Ga naar de andere pagina’s.")

    # Optioneel: preview
    st.subheader("Voorbeeld:")
    st.dataframe(df.head())
else:
    st.info("👈 Upload een bestand om te starten.")
