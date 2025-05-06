import streamlit as st
from OM import planning   # functie die je net hebt aangepast

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

    # ⬇️ Gebruik de gekozen waarden i.p.v. hard‑coded tekst
    fig = planning(
        df,
        color_scheme=color_scheme,
        marker_shape=marker_shape,
        marker_color=marker_color
    )
    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("⚠️ Upload an Excel file on the main page first.")


