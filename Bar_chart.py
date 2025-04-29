import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import plotly.graph_objects as go
import plotly.express as px

df = pd.read_excel('TAT KPI Sheet (1).xlsx', sheet_name='Samples Release 2025')
df

# Define stages in order
stage_columns = ['Planned', 'Analyses completed', 'Approval analyses', 'Finish date QC']

# Function to determine latest (current) stage — excluding 'Finish date QC'
def get_current_stage(row):
    for stage in reversed(stage_columns[:-1]):  # Exclude last stage
        if pd.notna(row[stage]):
            return stage
    return 'No stage'

# Exclude batches that are finished (have 'Finish date QC' filled)
df_in_progress = df[df['Finish date QC'].isna()].copy()

# Add current stage column for in-progress batches
df_in_progress['Current Stage'] = df_in_progress.apply(get_current_stage, axis=1)

# Count how many are in each current stage
stage_counts = df_in_progress['Current Stage'].value_counts().reindex(stage_columns[:-1], fill_value=0)

# Plot
fig = px.bar(
    stage_counts,
    x=stage_counts.values,
    y=stage_counts.index,
    orientation='h',
    labels={'y': 'Stage', 'x': 'Number of Batches'},
    title='In-Progress Batches per Stage (Finished Excluded)'
)

fig.update_layout(yaxis=dict(categoryorder='array', categoryarray=stage_columns[:-1]))
fig.show()