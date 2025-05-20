import streamlit as st
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Calculate", layout="wide")
st.title("Calculations")

if 'excel_df' in st.session_state:
    df = st.session_state['excel_df']
    df = df[['Product code',
             'Batch number',
             'Date received lab',
             'Planned',
             'Analyses completed',
             'Approval analyses',
             'Finish date QC',
             'Duedate',
             'Type of samples']].copy()

    df.columns = ['ProductID','Order', 'Received', 'Planned', 'Analyses', 'Approved', 'Finished', 'DueDate', 'Type']
    df['Order'] = df['Order'].astype(str)
    df['Type'] = df['Type'].astype(str)
    df_n = df[df['Finished'].notna()].copy()
 
    # Convert dates and calculate Time_in_lab in days
    df_n['Finished'] = pd.to_datetime(df_n['Finished'])
    df_n['Received'] = pd.to_datetime(df_n['Received'])
    df_n['Time_in_lab'] = (df_n['Finished'] - df_n['Received']).dt.days

    # Get unique types
    list_all_types = list(df_n['Type'].unique())

    # Plot boxplots, 2 per row
    for i in range(0, len(list_all_types), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(list_all_types):
                t = list_all_types[i + j]
                df_type = df_n[df_n['Type'] == t]

                fig = px.box(df_type, y='Time_in_lab', title=f'Time in Lab - Type: {t}')
                cols[j].plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ Upload an Excel file on the main page first.")
    