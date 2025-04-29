import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. Lees Excel in
df = pd.read_excel('TAT KPI Sheet (1).xlsx', sheet_name='Samples Release 2025')

# 2. Kolomnamen aanpassen aan jouw bestand
df = df[[
    'Batch number',
    'Date received lab',
    'Planned',
    'Analyses completed',
    'Approval analyses',
    'Finish date QC',
    'Duedate'
]].copy()

df.columns = ['Order', 'Start', 'Step1', 'Step2', 'Step3', 'End', 'DueDate']

# 3. Zorg dat alle datums echt datums zijn
for col in ['Start', 'Step1', 'Step2', 'Step3', 'End', 'DueDate']:
    df[col] = pd.to_datetime(df[col], errors='coerce')

# 4. Filter op openstaande (niet-afgeronde) orders
df_open = df[df['End'].isna()].copy()
df_open['DueDate'] = pd.to_datetime(df_open['DueDate'], errors='coerce')
df_open = df_open.sort_values('DueDate')

# 5. Bouw tijdlijn op
records = []
for _, row in df_open.iterrows():
    last_date = row['Start']
    for step in ['Step1', 'Step2', 'Step3', 'End']:
        if pd.notna(row[step]):
            records.append({
                'Order': str(row['Order']),  # maak string voor y-as
                'Start': last_date,
                'Finish': row[step],
                'Status': 'Voltooid'
            })
            last_date = row[step]
        else:
            eindpunt = min(datetime.now(), row['DueDate']) if pd.notna(row['DueDate']) else datetime.now()
            records.append({
                'Order': str(row['Order']),
                'Start': last_date,
                'Finish': eindpunt,
                'Status': 'Open'
            })
            break

timeline_df = pd.DataFrame(records)

# 6. Debug: check de inhoud
print(timeline_df.head(10))

# 7. Plot
fig = px.timeline(
    timeline_df,
    x_start="Start",
    x_end="Finish",
    y="Order",
    color="Status",
    color_discrete_map={'Voltooid': 'seagreen', 'Open': 'tomato'}
)
fig.update_yaxes(autorange="reversed")
fig.update_layout(title_text="Overzicht voortgang orders")

# 8. Show de figuur
fig.show()
