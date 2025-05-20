import streamlit as st
from Functies import find_duplicates   # ← your helper

st.set_page_config(page_title="Analysis", layout="wide")
st.title("🚩 Data-quality checks")

# ─────────────────────────────────────────────────────────────
# Inleiding
st.markdown("""
<span style='font-size: 0.9em; color: grey;'>
This page helps you identify and fix common data issues that may impact analysis or timeline visualization.

Typical problems include:
- Missing or renamed required columns.
- Duplicate batch numbers, which can cause visual overlap.
- Old or finished entries that clutter current insights.

Use the filters and duplicate check below to clean and refine your dataset.
</span>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Vereiste kolommen uitleg
with st.expander("📋 Required column names", expanded=False):
    st.markdown("""
Your uploaded file **must include** the following column names **without changes**:

- `Batch number`  
- `Date received lab`  
- `Planned`  
- `Analyses completed`  
- `Approval analyses`  
- `Finish date QC`  
- `Duedate`

You may add or remove other columns as needed, but **do not rename or delete** these required ones. If any are missing or renamed, the timeline and other features may not work correctly.
""")

# ─────────────────────────────────────────────────────────────
# Check of bestand is ingeladen
if 'excel_df' not in st.session_state:
    st.info("👈 First upload a spreadsheet on the main page.")
    st.stop()

df = st.session_state['excel_df']

# ─────────────────────────────────────────────────────────────
# Duplicates-sectie met uitleg + check + unfinished toggle in één expander
with st.expander("🔍 Duplicate batch numbers", expanded=True):
    st.markdown("""
If multiple rows share the same **Batch number**, the timeline chart may show overlapping bars or misleading durations.

This tool allows you to:
- Detect batch number duplicates
- Select specific rows to remove
- Filter only unfinished batches if desired

Removing duplicates helps clean your dataset and ensures accurate visualizations.
""")

    # Filter on finished batches
    show_open = st.toggle("Show *only* unfinished batches", value=True)
    working_df = df[df['Finish date QC'].isna()] if show_open else df

    # Duplicate check
    if st.button("🔍 Run duplicate check"):
        st.session_state['duplicates'] = find_duplicates(working_df)

    duplicates = st.session_state.get('duplicates')

    if duplicates is None:
        st.info("Press the button above to scan for duplicates.")
    elif duplicates.empty:
        st.success("✅ No duplicate batch numbers found.")
    else:
        st.warning(f"⚠️ {len(duplicates)} duplicate batch rows found — select any rows you want to delete.")

        selected = [
            idx for idx, r in duplicates.iterrows()
            if st.checkbox(
                f"Batch {r['Batch number']}  |  "
                f"Sample {r.get('Type of samples','')}  |  "
                f"Due {r.get('Duedate','')}  |  "
                f"Finished {r.get('Finish date QC','')}  |  "
                f"Received {r.get('Date received lab','')}  |  "
                f"Product {r.get('Product code','')}",
                key=f"dup_{idx}"
            )
        ]

        if selected and st.button("🗑️ Delete selected rows"):
            st.session_state['excel_df'] = st.session_state['excel_df'].drop(index=selected).reset_index(drop=True)
            st.session_state['duplicates'] = duplicates.drop(index=selected).reset_index(drop=True)
            st.success(f"✅ Deleted {len(selected)} row(s) from the dataset.")
