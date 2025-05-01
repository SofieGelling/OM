import streamlit as st
import pandas as pd
from OM import planning  
# pip install st-pages
# streamlit run StreamLit.py

# -------------------------    Pagina met toggle    ---------------------------------------------------

st.set_page_config(page_title="Dashboard", layout="wide")
st.title("Welkom bij je Batch Dashboard")
st.markdown("👈 Kies een pagina in het zijmenu om te beginnen.")
