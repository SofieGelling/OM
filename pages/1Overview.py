import streamlit as st
from OM import planning, filter_by_sample_type, filter_OOS
import pandas as pd

st.set_page_config(page_title="Schedule", layout="wide")
st.title("📦 Scheduling Timeline")

if 'excel_df' in st.session_state:
    df = st.session_state['excel_df']
    df = df[df['Finish date QC'].isna()].copy()
    df['Date received lab'] = pd.to_datetime(df['Date received lab'], errors='coerce')

    # Extra sorteeroptie
    sort_column = st.selectbox(
        "📑 Sort by:",
        ['DueDate (soonest first)', 'Date received lab (earliest first)']
    )
    if sort_column == 'DueDate (soonest first)':
        df = df.sort_values(by='Duedate', ascending=True)
    elif sort_column == 'Date received lab (earliest first)':
        df = df.sort_values(by='Date received lab', ascending=True)

    # Filteren op sample type
    type_samples = df['Type of samples'].unique()
    filter_samples = []
    with st.expander("🔍 Filter: Type of samples", expanded=False):
        for sample in type_samples:
            if st.checkbox(str(sample), value=True):
                filter_samples.append(sample)

    # SOO filter
    remove_soo = st.toggle("Remove OOS cases", value=False)
    if remove_soo:
        df = filter_OOS(df)

    # Voor de eerste keer vaste standaardkleuren
    color_scheme = 'Default'
    marker_shape = 'square'
    marker_color = '#000000'

    # Check of er sample-types gekozen zijn
    if not filter_samples:
        st.warning("⚠️ Selecteer minimaal één 'Type of sample' om de tijdlijn te bekijken.")
    else:
        fig = planning(
            df=filter_by_sample_type(df, filter_samples),
            color_scheme=color_scheme,
            marker_shape=marker_shape,
            marker_color=marker_color
        )
        st.plotly_chart(fig, use_container_width=True)

        # Kleureninstellingen ONDER de grafiek
        scheme_options = ['Default', 'Blues', 'Pinks', 'Greys', 'Greens', 'Oranges']
        with st.expander("🎨 Change colours", expanded=False):
            color_scheme  = st.selectbox("🎨 Choose a colour scheme", scheme_options, key="color_scheme")
            marker_shape  = st.selectbox("🔷 Marker symbol", ['square', 'circle', 'diamond'], key="marker_shape")
            marker_color  = st.color_picker("🖌️ Marker colour", '#000000', key="marker_color")

else:
    st.warning("⚠️ Upload an Excel file on the main page first.")



