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

