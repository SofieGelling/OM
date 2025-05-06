import pandas as pd

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
