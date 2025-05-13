import streamlit as st
from Functies import find_duplicates

st.set_page_config(page_title="Analyse", layout="wide")
st.title("📊 Analyse")


if 'excel_df' in st.session_state:
    df = st.session_state['excel_df']

    st.subheader("Check for duplicate batch numbers")

    # Toggle: alleen niet-afgeronde batches
    filter_unfinished = st.toggle("🔘 Show only non-finished batches")
    working_df = df[df['Finish date QC'].isna()] if filter_unfinished else df

    # Check-knop om duplicaten te zoeken
    if st.button("🔍 Check for duplicate batch numbers"):
        duplicates = find_duplicates(working_df)
        st.session_state['duplicates'] = duplicates  # ⬅️ opslaan in session

    # Als er eerder gevonden duplicaten zijn:
    if 'duplicates' in st.session_state:
        duplicates = st.session_state['duplicates']

        if not duplicates.empty:
            st.warning("⚠️ Duplicate batch numbers found:")
            st.markdown("**Select rows to delete:**")

            # ⬅️ lijst om geselecteerde indexen op te slaan
            selected_rows = []
            for i, row in duplicates.iterrows():
                label = (
                    f"Batch: {row['Batch number']} | "
                    f"Sample Type: {row.get('Type of samples', '')} | "
                    f"DueDate: {row.get('Duedate', '')} | "
                    f"Finish QC: {row.get('Finish date QC', '')} | "
                    f"Received: {row.get('Date received lab', '')} | "
                    f"Product: {row.get('Product code', '')}"
                )
                if st.checkbox(label, key=f"select_{i}"):
                    selected_rows.append(i)

            # Verwijderknop onderaan
            if selected_rows and st.button("🗑️ Delete selected rows"):
                st.session_state['excel_df'] = st.session_state['excel_df'].drop(index=selected_rows).reset_index(drop=True)
                # duplicaten opnieuw opslaan zonder verwijderde
                st.session_state['duplicates'] = st.session_state['duplicates'].drop(index=selected_rows).reset_index(drop=True)
                st.success(f"✅ {len(selected_rows)} row(s) deleted from the dataset.")
        else:
            st.success("✅ No duplicate batch numbers found.")
else:
    st.info("👈 Upload a spreadsheet file from the main page first.")


