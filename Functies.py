import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import streamlit as st
import plotly.express as px
from OM import filter_OOS



# Vinden van dubbelen 
def find_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Retourneert alle rijen met dubbele batchnummers.
    """
    if 'Batch number' not in df.columns:
        return pd.DataFrame()

    # Zet de batchnummers allemaal om naar string
    df['Batch number'] = df['Batch number'].astype(str)

    duplicates = df[df.duplicated(subset='Batch number', keep=False)].copy()
    return duplicates.sort_values(by='Batch number')


# verwijderen van NAN rijen 
def remove_empty_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Verwijdert rijen waar alle kernvelden leeg of NaN zijn.
    """
    cols = [
        'Batch number',
        'Type of samples',
        'Duedate',
        'Finish date QC',
        'Date received lab',
        'Product code'
    ]

    # Zorg dat kolommen bestaan, anders voeg je ze tijdelijk toe voor controle
    for col in cols:
        if col not in df.columns:
            df[col] = pd.NA

    # Filter rijen waar ALLE genoemde kolommen leeg zijn
    cleaned_df = df.dropna(subset=cols, how='all')
    return cleaned_df


# Kijken per type sample hoe lang het mag duren 
def get_tat_targets(df: pd.DataFrame) -> dict:
    """
    Maakt een dictionary van alle unieke 'Type of sample' gekoppeld aan hun 'TAT target'.

    Parameters:
    df (pd.DataFrame): De dataset met de kolommen 'Type of sample' en 'TAT target'.

    Returns:
    dict: Dictionary met 'Type of sample' als key en 'TAT target' als value.
    """
    # Verwijder rijen met lege waarden in de benodigde kolommen
    filtered_df = df[['Type of samples', 'TAT Target']].dropna()

    # Groepeer per type en neem de eerste unieke waarde van TAT target
    tat_dict = filtered_df.drop_duplicates().set_index('Type of samples')['TAT Target'].to_dict()

    return tat_dict


# tijden tussen iedere stap in 
def wachttijden(df):
    df['Type of samples'] = df['Type of samples'].replace({'GMP+ des': 'GMP+ Des'})

    # Stapnamen
    steps = ['Date received lab', 'Planned', 'Analyses completed', 'Approval analyses', 'Finish date QC']
    for step in steps:
        df[step] = pd.to_datetime(df[step], errors='coerce')

    # Categorieën
    categories = ['Verpakking', 'RM', 'RM-API', 'GMP+', 'GMP', 'GMP+ Des']

    # Resultaatstructuur
    results = {cat: [] for cat in categories}

    # Loop per categorie en bereken tussenstappen
    for cat in categories:
        subset = df[df['Type of samples'] == cat]
        step_durations = []

        for _, row in subset.iterrows():
            for i in range(len(steps) - 1):
                date1 = row[steps[i]]
                date2 = row[steps[i + 1]]
                if pd.notna(date1) and pd.notna(date2) and date2 >= date1:
                    diff = (date2 - date1).days
                    step_durations.append((i, diff))

        # Gemiddelde per stap index
        step_avgs = [0] * (len(steps) - 1)
        counts = [0] * (len(steps) - 1)
        for i, diff in step_durations:
            step_avgs[i] += diff
            counts[i] += 1

        for i in range(len(step_avgs)):
            if counts[i] > 0:
                step_avgs[i] /= counts[i]

        results[cat] = step_avgs

    # 🌈 Visualisatie
    fig = go.Figure()
    step_labels = [f"{steps[i]} → {steps[i+1]}" for i in range(len(steps)-1)]
    x = categories

    kleuren = ['#d1d1d1', '#87a9fa', '#0acafa', '#07f702', '#54A24B']  # Zelfgekozen kleuren

    for i, step_label in enumerate(step_labels):
        y_values = [results[cat][i] for cat in categories]
        hover_texts = [
            f"<b>Sample type:</b> {cat}<br>"
            f"<b>Stap:</b> {step_label}<br>"
            f"<b>Gem. dagen:</b> {round(y_values[j], 2)}"
            for j, cat in enumerate(categories)
        ]

        fig.add_trace(go.Bar(
            x=x,
            y=y_values,
            name=step_label,
            hovertext=hover_texts,
            hoverinfo='text',
            marker_color=kleuren[i % len(kleuren)],
            text=None  # Verberg tekst op de balk zelf
        ))

    fig.update_layout(
        barmode='group',
        title='Gemiddelde tijd tussen stappen per sample type',
        xaxis_title='Sample type',
        yaxis_title='Gemiddelde tijd (dagen)',
        legend_title='Stappen',
        height=600
    )

    fig.show()


# Boxplots 
def Boxplot(df: pd.DataFrame):
    df = df[['Product code',
             'Batch number',
             'Date received lab',
             'Planned',
             'Analyses completed',
             'Approval analyses',
             'Finish date QC',
             'Duedate',
             'Type of samples',
             'TAT Target',
             'Reason overdue']].copy()

    df.columns = ['ProductID','Order', 'Received', 'Planned', 'Analyses', 'Approved', 'Finished', 'DueDate', 'Type', 'Target', 'Reason overdue']
    df['Order'] = df['Order'].astype(str)
    df['Type'] = df['Type'].astype(str).str.upper()

    df_n = df[df['Finished'].notna()].copy()
    df_n['Finished'] = pd.to_datetime(df_n['Finished'])
    df_n['Received'] = pd.to_datetime(df_n['Received'])
    df_n['Month'] = df_n['Finished'].dt.month
    df_n = df_n[df_n['Month'] > 0]
    df_n['Time_in_lab'] = (df_n['Finished'] - df_n['Received']).dt.days

    unique_types = sorted(df_n['Type'].unique())
    selected_type = st.selectbox("Select a sample type", unique_types)

    df_type = df_n[df_n['Type'] == selected_type]

    if len(df_type) < 5:
        st.warning(f"⚠️ Too few samples for type '{selected_type}' ({len(df_type)} entries)")
        return

    # Hovervoorbereiding
    df_type['Order_fmt'] = df_type['Order']
    df_type['ProductID_fmt'] = df_type['ProductID']
    df_type['Received_fmt'] = df_type['Received'].dt.date.astype(str)
    df_type['Finished_fmt'] = df_type['Finished'].dt.date.astype(str)
    df_type['Time_in_lab_fmt'] = df_type['Time_in_lab'].astype(str)

    default_target = df_type['Target'].iloc[0]
    col1, col2 = st.columns([1, 2])
    show_target_line = col1.checkbox("Show targetline", value=True)
    remove_soo = col1.toggle("Remove OOS cases", value=False)
    if remove_soo:
        df_type = filter_OOS(df_type)
    target_value = col2.number_input("Targetvalue (days)", value=float(default_target), step=1.0)


    fig = px.box(
        df_type,
        x='Month',
        y='Time_in_lab',
        points='outliers',
        title=f"Time in Lab per Month - Type: {selected_type}",
        category_orders={'Month': list(range(1, 13))},
        custom_data=[
            'Order_fmt', 'ProductID_fmt', 'Received_fmt', 'Finished_fmt', 'Time_in_lab_fmt'
        ]
    )

    fig.update_xaxes(type='category')

    fig.update_traces(
        hovertemplate=
            "<b>Order = %{customdata[0]}</b><br>" +
            "<b>ProductID = %{customdata[1]}</b><br>" +
            "Received = %{customdata[2]}<br>" +
            "Finished = %{customdata[3]}<br>" +
            "Time in lab = %{customdata[4]}<extra></extra>"
    )

    if show_target_line:
        fig.add_shape(
            type="line",
            xref='x',
            yref='y',
            x0='-1',
            x1='12',
            y0=target_value,
            y1=target_value,
            line=dict(color="red", width=2)
        )

        fig.add_annotation(
            x=12, y=target_value,
            text=f"Target: <b>{target_value}</b>",
            showarrow=False,
            yshift=10,
            font=dict(color="red")
        )


    # Negatieve punten
    negatief = df_type[df_type['Time_in_lab'] < 0]
    if not negatief.empty:
        fig.add_trace(go.Scatter(
            x=negatief['Month'],
            y=negatief['Time_in_lab'],
            mode='markers',
            marker=dict(color='red', size=8, symbol='circle'),
            name='Negatief'
        ))

    fig.update_yaxes(title_text="Time in lab")
    fig.update_layout(height=700)
    st.plotly_chart(fig, use_container_width=True)


df = pd.read_excel('TAT KPI Sheet (3).xlsx', sheet_name='Samples Release 2025')