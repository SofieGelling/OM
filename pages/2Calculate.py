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
             'Type of samples',
             'TAT Target']].copy()

    df.columns = ['ProductID','Order', 'Received', 'Planned', 'Analyses', 'Approved', 'Finished', 'DueDate', 'Type', 'Target']
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
                target_value = df_type['Target'].iloc[0] 
                if len(df_type) < 5:
                    with cols[j]:
                        st.warning(f"⚠️ Too few samples for type '{t}' ({len(df_type)} entries)")
                else:
                    fig = px.box(df_type, y='Time_in_lab', title=f'Time in Lab - Type: {t}')
                    fig.add_shape(
                        type="line",
                        x0=-0.5, x1=0.5,  # width of the box
                        y0=target_value, y1=target_value,
                        line=dict(color="red", width=2)
                        )
                    fig.add_annotation(
                        y=target_value,
                        x=0.5,  # box is centered on x=0
                        text=f"Target: <b>{target_value}<b>",
                        showarrow=False,
                        yshift=10,
                        font=dict(color="red")
                        )
                    cols[j].plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ Upload an Excel file on the main page first.")
    