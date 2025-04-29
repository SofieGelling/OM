import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import plotly.graph_objects as go
import plotly.express as px

df = pd.read_excel('TAT KPI Sheet (1).xlsx', sheet_name='Samples Release 2025')

stage_columns = ['Planned', 'Analyses completed', 'Approval analyses', 'Finish date QC']
colors = ['blue', 'orange', 'green', 'red']

fig = go.Figure()

for i, (_, row) in enumerate(df.iterrows()):
    batch = row['Batch number']
    planned = row['Planned']
    tat_days = row['TAT Target']

    # Skip if batch has no stages or only QC
    valid_stages = [col for col in stage_columns if pd.notna(row[col])]
    if len(valid_stages) == 0 or (len(valid_stages) == 1 and valid_stages[0] == 'Finish date QC'):
        continue

    # Plot actual stage timeline
    stage_dates = [row[col] for col in valid_stages]
    stage_colors = [colors[stage_columns.index(col)] for col in valid_stages]
    stage_labels = valid_stages

    fig.add_trace(go.Scatter(
        x=stage_dates,
        y=[str(batch)] * len(stage_dates),
        mode='lines+markers',
        line=dict(color='gray'),
        marker=dict(color=stage_colors, size=10),
        text=stage_labels,
        hovertemplate='<b>Batch %{y}</b><br>%{text}: %{x|%Y-%m-%d}<extra></extra>',
        name=str(batch),
        showlegend=False
    ))

    # Add TAT target line if 'Planned' and TAT are present
    if pd.notna(planned) and pd.notna(tat_days):
        tat_end = planned + pd.Timedelta(days=int(tat_days))
        fig.add_trace(go.Scatter(
            x=[planned, tat_end],
            y=[str(batch), str(batch)],
            mode='lines',
            line=dict(color='red', dash='dash'),
            hoverinfo='text',
            text=[f'TAT start: {planned.date()}', f'TAT deadline: {tat_end.date()}'],
            name='TAT Target',
            showlegend=False
        ))

# Final layout
fig.update_layout(
    title='Interactive Product Timeline with TAT Target',
    xaxis_title='Date',
    yaxis_title='Batch number',
    height=400 + len(df) * 3,
    xaxis=dict(type='date'),
    hovermode='closest',
    margin=dict(l=100, r=20, t=40, b=40)
)

fig.show()