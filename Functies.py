import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go


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



df = pd.read_excel('TAT KPI Sheet (3).xlsx', sheet_name='Samples Release 2025')