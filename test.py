from OM import filter_by_sample_type
import pandas as pd

FILE  = r'TAT KPI Sheet (2).xlsx'

SHEET = 'Samples Release 2025'
df = pd.read_excel(FILE, sheet_name=SHEET)
print(filter_by_sample_type(df, ['RM', 'GMP+']))