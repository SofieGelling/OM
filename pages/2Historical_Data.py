import streamlit as st
from Functies import Boxplot

st.set_page_config(page_title="Historical_Data", layout="wide")
st.title("Boxplots")

if 'excel_df' in st.session_state:
    Boxplot(st.session_state['excel_df'])
    
else:
    st.warning("⚠️ Upload an Excel file on the main page first.")
