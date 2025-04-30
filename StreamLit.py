import streamlit as st
import pandas as pd
from Planning import planning

st.title("Open Batches Viewer")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])
if uploaded_file:
    raw_df = pd.read_excel(uploaded_file, sheet_name="Samples Release 2025")
    raw_df = raw_df[['Batch number', 'Date received lab', 'Planned',
                     'Analyses completed', 'Approval analyses',
                     'Finish date QC', 'Duedate']].copy()

    fig = planning(raw_df)
    st.plotly_chart(fig, use_container_width=True)
