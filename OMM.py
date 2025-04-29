import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# ------------------------------------------------------------------
# 1. Excel inlezen
FILE  = r'TAT KPI Sheet (2).xlsx'          # <-- pad aanpassen indien nodig
SHEET = 'Samples Release 2025'
df = pd.read_excel(FILE, sheet_name=SHEET)

# ------------------------------------------------------------------
# 2. Kolommen selecteren & hernoemen
df = df[['Batch number',
         'Date received lab',
         'Planned',
         'Analyses completed',
         'Approval analyses',
         'Finish date QC',
         'Duedate']].copy()

df.columns = ['Order', 'Received', 'Planned', 'Analyses', 'Approved', 'Finished', 'DueDate']
df['Order'] = df['Order'].astype(str)      # nummer → string

# Datum-kolommen naar datetime
for col in ['Received', 'Planned', 'Analyses', 'Approved', 'Finished', 'DueDate']:
    df[col] = pd.to_datetime(df[col], errors='coerce')

# Alleen batches die nog niet af zijn
df = df[df['Finished'].isna()].copy()

# ------------------------------------------------------------------
# 3. Kleuren
COLORS = {
    'Onvoltooid' : 'lightgray',   # vóór Planned of als er géén stappen zijn
    'Planned'    : 'lightgreen',
    'Analyses'   : 'gold',
    'Approved'   : 'mediumorchid'
}

# ------------------------------------------------------------------
# 4. Segmenten bouwen
segments   = []
today      = pd.Timestamp.today().normalize()
step_order = ['Planned', 'Analyses', 'Approved']

for _, row in df.iterrows():
    order      = row['Order']
    start_date = row['Received']
    due_date   = row['DueDate']
    if pd.isna(start_date):
        continue                    # kan niet tekenen zonder Received

    last_color = 'Onvoltooid'
    last_date  = start_date

    # loop over chronologische stappen
    for step in step_order:
        step_date = row[step]
        if pd.notna(step_date) and step_date > last_date:
            # segment in huidige kleur tot de datum van deze stap
            segments.append(dict(Order=order,
                                 Start=last_date,
                                 Finish=step_date,
                                 Stap=last_color))
            # nieuwe kleur wordt kleur van deze stap
            last_color = step
            last_date  = step_date

    # laatste segment (kleur = last_color) tot vandaag
    segments.append(dict(Order=order,
                         Start=last_date,
                         Finish=due_date,
                         Stap=last_color))

# DataFrame met alle blokken
seg_df = pd.DataFrame(segments)

# ------------------------------------------------------------------
# 5. Hover-tekst genereren per order
def build_hover(r):
    lines = [f"<b>{r['Order']}</b>: onvoltooid"]
    if pd.notna(r['Received']):
        lines.append(f"Received: {r['Received'].date()}")
    if pd.notna(r['Planned']):
        lines.append(f"Planned: {r['Planned'].date()}")
    if pd.notna(r['Analyses']):
        lines.append(f"Analyses completed: {r['Analyses'].date()}")
    if pd.notna(r['Approved']):
        lines.append(f"Approval analyses: {r['Approved'].date()}")
    if pd.notna(r['DueDate']):
        lines.append(f"Due date: {r['DueDate'].date()}")
    return "<br>".join(lines)

hover_map = {r['Order']: build_hover(r) for _, r in df.iterrows()}
seg_df['Hover'] = seg_df['Order'].map(hover_map)

# ------------------------------------------------------------------
# 6. Tijdlijn tekenen
fig = px.timeline(
    seg_df,
    x_start="Start",
    x_end="Finish",
    y="Order",
    color="Stap",
    color_discrete_map=COLORS
)
fig.update_traces(hovertemplate=seg_df['Hover'] + "<extra></extra>")
fig.update_yaxes(autorange="reversed")

# ------------------------------------------------------------------
# 7. Due-date markers
due_df = df.dropna(subset=['DueDate'])
fig.add_trace(go.Scatter(
    x=due_df['DueDate'],
    y=due_df['Order'],
    mode='markers',
    marker=dict(symbol='diamond', size=9, color='red'),
    name='Due Date',
    hovertemplate=due_df['DueDate'].dt.strftime("Due date: %Y-%m-%d") + "<extra></extra>"
))

# ------------------------------------------------------------------
# 8. Layout
fig.update_layout(
    title="Voortgang openstaande batches (balk loopt tot vandaag)",
    xaxis_title="Datum",
    yaxis_title="Batch nummer",
    legend_title="Processtap",
    height=900
)

fig.show()
