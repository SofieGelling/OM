import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ---------- 1. Excel inlezen ----------
FILE = r'TAT KPI Sheet (2).xlsx'  # <-- pad evt. aanpassen
SHEET = 'Samples Release 2025'

df = pd.read_excel(FILE, sheet_name=SHEET)

# ---------- 2. Relevante kolommen ----------
df = df[['Batch number',
         'Date received lab',
         'Planned',
         'Analyses completed',
         'Approval analyses',
         'Finish date QC',
         'Duedate']].copy()

df.columns = ['Order', 'Received', 'Planned', 'Analyses', 'Approved', 'Finished', 'DueDate']

# ---------- 3. Datums casten ----------
for col in ['Received', 'Planned', 'Analyses', 'Approved', 'Finished', 'DueDate']:
    df[col] = pd.to_datetime(df[col], errors='coerce')

# alleen nog niet afgeronde batches
df = df[df['Finished'].isna()].copy()
# Zet batchnummer overal naar string zodat het altijd matcht
df['Order'] = df['Order'].astype(str)


# ---------- 4. Kleuren ----------
COLORS = {
    'Planned'    : 'lightgreen',
    'Analyses'   : 'gold',
    'Approved'   : 'mediumorchid',
    'Onvoltooid' : 'lightgray'
}

    # helper om segment toe te voegen
def add_seg(step_name, start, finish):
    segments.append({
        'Order' : order,
        'Start' : start,
        'Finish': finish,
        'Stap'  : step_name
    })
# ---------- 5. Segmenten bouwen ----------
segments = []
today = pd.Timestamp.today().normalize()

for _, r in df.iterrows():
    order = str(r['Order'])
    cur   = r['Received']                 # startpunt is altijd Received
    if pd.isna(cur):
        continue                          # zonder Received kunnen we niks tekenen



    # Planned
    if pd.notna(r['Planned']) and r['Planned'] > cur:
        add_seg('Planned', cur, r['Planned'])
        cur = r['Planned']

    # Analyses
    if pd.notna(r['Analyses']) and r['Analyses'] > cur:
        add_seg('Analyses', cur, r['Analyses'])
        cur = r['Analyses']

    # Approved
    if pd.notna(r['Approved']) and r['Approved'] > cur:
        add_seg('Approved', cur, r['Approved'])
        cur = r['Approved']

    # Onvoltooid stuk tot vandaag (altijd aanwezig)
    if cur < today:
        add_seg('Onvoltooid', cur, r['DueDate'])

segments_df = pd.DataFrame(segments)

# ---------- 6. Tijdlijn tekenen ----------
fig = px.timeline(
    segments_df,
    x_start="Start",
    x_end="Finish",
    y="Order",
    color="Stap",
    color_discrete_map=COLORS,
)

fig.update_yaxes(autorange="reversed")

# ---------- 7. Custom hovers ----------
custom_hover = []
for s in segments_df.itertuples():
    lines = [f"Received: {df.loc[df['Order']==s.Order,'Received'].iloc[0].date()}"]
    if s.Stap in ['Planned', 'Analyses', 'Approved']:
        lines.append(f"{s.Stap}: {s.Finish.date()}")
    if s.Stap == 'Onvoltooid':
        row = df.loc[df['Order']==s.Order].iloc[0]
        if pd.notna(row['Planned']):
            lines.append(f"Planned: {row['Planned'].date()}")
        if pd.notna(row['Analyses']):
            lines.append(f"Analyses completed: {row['Analyses'].date()}")
        if pd.notna(row['Approved']):
            lines.append(f"Approval analyses: {row['Approved'].date()}")
        if pd.notna(row['DueDate']):
            lines.append(f"Due date: {row['DueDate'].date()}")
    custom_hover.append("<br>".join(lines))

fig.update_traces(hovertemplate=[h + "<extra></extra>" for h in custom_hover])

# ---------- 8. Due-date markers ----------
due_df = df.dropna(subset=['DueDate'])
fig.add_trace(go.Scatter(
    x=due_df['DueDate'],
    y=due_df['Order'].astype(str),
    mode='markers',
    marker=dict(symbol='diamond', size=10, color='red'),
    name='Due Date',
    hovertemplate=due_df['DueDate'].dt.strftime("Due date: %Y-%m-%d") + "<extra></extra>"
))

# Legend items komen nu één keer voor; geen duplicates meer
fig.update_layout(
    title="Voortgang batches – eindigend op vandaag",
    xaxis_title="Datum",
    yaxis_title="Batch nummer",
    height=900,
    legend_title="Processtap"
)

fig.show()
