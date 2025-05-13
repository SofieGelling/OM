import streamlit as st
from OM import planning, filter_by_sample_type
import pandas as pd

st.set_page_config(page_title="Planning", layout="wide")
st.title("📦 Planningstijdlijn")

if 'excel_df' in st.session_state:
    df = st.session_state['excel_df']

    # ► Kleurenschema‑opties moeten overeenkomen met de dict‑sleutels in planning()
    scheme_options = ['Default', 'Blues', 'Pinks', 'Greys', 'Greens', 'Oranges']
    with st.expander("🎨 Change colours", expanded=False):
        color_scheme  = st.selectbox("🎨 Choose a colour scheme", scheme_options)
        marker_shape  = st.selectbox("🔷 Marker symbol", ['square', 'circle', 'diamond'])
        marker_color  = st.color_picker("🖌️ Marker colour", '#000000')

    df = df[df['Finish date QC'].isna()].copy()
    df['Date received lab'] = pd.to_datetime(df['Date received lab'], errors='coerce')

    type_samples = df['Type of samples'].unique()
    filter_samples = []
    with st.expander("🔍 Filter: Type of samples", expanded=False):
        for sample in type_samples:
            if st.checkbox(str(sample), value=True):
                filter_samples.append(sample)
            
    
        # 🔽 Extra sorteeroptie
    sort_column = st.selectbox(
        "📑 Sort by:",
        ['DueDate (soonest first)', 'Date received lab (earliest first)']
    )
    if sort_column == 'DueDate (soonest first)':
        df = df.sort_values(by='Duedate', ascending=True)
    elif sort_column == 'Date received lab (earliest first)':
        df = df.sort_values(by='Date received lab', ascending=True)

    #filter_sample = st.selectbox('Samples to filter', type_samples)
    # ⬇️ Gebruik de gekozen waarden i.p.v. hard‑coded tekst
    fig = planning(
        df= filter_by_sample_type(df, filter_samples),
        color_scheme=color_scheme,
        marker_shape=marker_shape,
        marker_color=marker_color
    )
    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("⚠️ Upload an Excel file on the main page first.")


