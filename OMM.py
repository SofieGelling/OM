import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# 1. Excel inlezen
FILE  = r'TAT KPI Sheet (2).xlsx'
SHEET = 'Samples Release 2025'
df = pd.read_excel(FILE, sheet_name=SHEET)

# 2. Kolommen selecteren & hernoemen
df = df[['Batch number',
         'Date received lab',
         'Planned',
         'Analyses completed',
         'Approval analyses',
         'Finish date QC',
         'Duedate']].copy()

df.columns = ['Order', 'Received', 'Planned', 'Analyses', 'Approved', 'Finished', 'DueDate']
df['Order'] = df['Order'].astype(str)

# Datum-kolommen naar datetime
for col in ['Received', 'Planned', 'Analyses', 'Approved', 'Finished', 'DueDate']:
    df[col] = pd.to_datetime(df[col], errors='coerce')

df = df[df['Finished'].isna()].copy()  # Alleen openstaande

# 3. Kleuren
COLORS = {
    'Onvoltooid': 'lightgray',
    'Planned': 'lightgreen',
    'Analyses': 'gold',
    'Approved': 'mediumorchid'
}

# 4. Segmenten bouwen
today = pd.Timestamp.today().normalize()
step_order = ['Planned', 'Analyses', 'Approved']
segments = []

for _, row in df.iterrows():
    order = row['Order']
    cur = row['Received']
    if pd.isna(cur):
        continue

    color = 'Onvoltooid'
    for step in step_order:
        step_date = row[step]
        if pd.notna(step_date) and step_date > cur:
            segments.append(dict(Order=order, Start=cur, Finish=step_date, Stap=color))
            cur = step_date
            color = step

    segments.append(dict(Order=order, Start=cur, Finish=today, Stap=color))

seg_df = pd.DataFrame(segments)

# 5. Hovertekst toevoegen via merge (en correct sorteren)
def build_hover(r):
    lines = [f"<b>{r['Order']}</b>: onvoltooid"]
    if pd.notna(r['Received']): lines.append(f"Received: {r['Received'].date()}")
    if pd.notna(r['Planned']): lines.append(f"Planned: {r['Planned'].date()}")
    if pd.notna(r['Analyses']): lines.append(f"Analyses completed: {r['Analyses'].date()}")
    if pd.notna(r['Approved']): lines.append(f"Approval analyses: {r['Approved'].date()}")
    if pd.notna(r['DueDate']): lines.append(f"Due date: {r['DueDate'].date()}")
    return "<br>".join(lines)

df['Hover'] = df.apply(build_hover, axis=1)
seg_df = seg_df.merge(df[['Order', 'Hover']], on='Order', how='left')

# 6. Volgorde y-as instellen op volgorde in DataFrame
order_cat = pd.Categorical(seg_df['Order'], categories=df['Order'].unique(), ordered=True)
seg_df['Order'] = order_cat

# 7. Timeline tekenen
fig = px.timeline(
    seg_df,
    x_start='Start',
    x_end='Finish',
    y='Order',
    color='Stap',
    color_discrete_map=COLORS,
    custom_data=['Hover']
)
fig.update_traces(hovertemplate='%{customdata[0]}<extra></extra>')
fig.update_yaxes(autorange='reversed')

# 8. Due-date markers
fig.add_trace(go.Scatter(
    x=df['DueDate'],
    y=df['Order'],
    mode='markers',
    marker=dict(symbol='diamond', size=9, color='red'),
    name='Due Date',
    hovertemplate=df['DueDate'].dt.strftime("Due date: %Y-%m-%d") + "<extra></extra>"
))

# 9. Layout
fig.update_layout(
    title='Voortgang openstaande batches (balk tot vandaag)',
    xaxis_title='Datum',
    yaxis_title='Batch nummer',
    legend_title='Processtap',
    height=900
)

fig.show()
