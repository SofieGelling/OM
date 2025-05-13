import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import numpy as np


def planning(df, color_scheme='Default', marker_shape='square', marker_color='black'):
    # 2. Kolommen selecteren & hernoemen
    df = df[['Batch number',
             'Date received lab',
             'Planned',
             'Analyses completed',
             'Approval analyses',
             'Finish date QC',
             'Duedate',
             'Type of samples']].copy()

    df.columns = ['Order', 'Received', 'Planned', 'Analyses', 'Approved', 'Finished', 'DueDate', 'Type']
    df['Order'] = df['Order'].astype(str)
    df['Type'] = df['Type'].astype(str)

    # Datum-kolommen naar datetime
    for col in ['Received', 'Planned', 'Analyses', 'Approved', 'Finished', 'DueDate']:
        df[col] = pd.to_datetime(df[col], errors='coerce')

    df = df[df['Finished'].isna()].copy()  # Alleen openstaande

    # 3. Kleuren - met kleurenschema opties
    color_schemes = {
        'Default': {
            'Onvoltooid': '#d1d1d1',
            'Planned': '#87a9fa',
            'Analyses': '#0acafa',
            'Approved': '#07f702'
        },
        'Blues': {
            'Onvoltooid': '#8dbdf4',
            'Planned': '#4f88de',
            'Analyses': '#2567d1',
            'Approved': '#154bb5'
        },
        'Pinks': {
            'Onvoltooid': '#f59ab4',
            'Planned': '#ef5c91',
            'Analyses': '#e91e63',
            'Approved': '#ad1457'
        },
        'Greys': {
            'Onvoltooid': '#bbbbbb',
            'Planned': '#909090',
            'Analyses': '#6b6b6b',
            'Approved': '#4d4d4d'
        },
        'Greens': {
            'Onvoltooid': '#aed9b8',
            'Planned': '#6fcf97',
            'Analyses': '#43a047',
            'Approved': '#2e7d32'
        },
        'Oranges': {
            'Onvoltooid': '#ffcc80',
            'Planned': '#ffa726',
            'Analyses': '#fb8c00',
            'Approved': '#e65100'
        }
    }
    COLORS = color_schemes.get(color_scheme, color_schemes['Default'])

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
            if pd.notna(step_date) and step_date >= cur:
                segments.append(dict(Order=order, Start=cur, Finish=step_date, Stap=color))
                cur = step_date
                color = step

        segments.append(dict(Order=order, Start=cur, Finish=row['DueDate'], Stap=color))


    seg_df = pd.DataFrame(segments)


    df['Hover'] = df.apply(build_hover, axis=1)
    required_columns = ['Order', 'Hover']
    for col in required_columns:
        if col not in df.columns:
            raise KeyError(f"Column '{col}' not found in dataframe.")

    seg_df = seg_df.merge(df[required_columns], on='Order', how='left')

    #seg_df = seg_df.merge(df[['Order', 'Hover']], on='Order', how='left')

    # 6. Zorg dat y-as categorisch blijft
    df['Order'] = df['Order'].astype(str)
    seg_df['Order'] = seg_df['Order'].astype(str)

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
    fig.update_yaxes(type='category', autorange='reversed')

    # 8.1 Verticale lijn voor vandaag (volledig doorgetrokken, met legenda)
    fig.add_shape(
        type="line",
        x0=today,
        y0=-0.5,
        x1=today,
        y1=len(df)-0.5,
        line=dict(color="grey", width=2, dash="dot")
    )

    # Today toevoegen aan legenda
    fig.add_trace(go.Scatter(
        x=[today],
        y=[None],  # y=None zodat hij geen punt tekent
        mode='lines',
        line=dict(color="grey", width=2, dash="dot"),
        name=f"Today: {today.date()}"
    ))

    fig.add_trace(go.Scatter(
        x=df['DueDate'],
        y=df['Order'],
        mode='markers',
        marker=dict(symbol=marker_shape, size=9, color=marker_color),
        name='Due Date',
        hovertemplate=df['DueDate'].dt.strftime("Due date: %Y-%m-%d") + "<extra></extra>",
        showlegend=True
    ))

    # 9. Layout
    fig.update_layout(
        title='Open batches (as of today)',
        xaxis_title='Date',
        yaxis_title='Batch nummer',
        legend_title='Process step',
        height=900
    )

    return fig

    # 5. Hovertekst toevoegen via merge (en correct sorteren)
def build_hover(r):
    lines = [f"<b>{r['Order']}</b>: onvoltooid"]
    if pd.notna(r['Received']): lines.append(f"Received: {r['Received'].date()}")
    if pd.notna(r['Planned']): lines.append(f"Planned: {r['Planned'].date()}")
    if pd.notna(r['Analyses']): lines.append(f"Analyses completed: {r['Analyses'].date()}")
    if pd.notna(r['Approved']): lines.append(f"Approval analyses: {r['Approved'].date()}")
    if pd.notna(r['DueDate']): lines.append(f"Due date: {r['DueDate'].date()}")
    return "<br>".join(lines)
    
def filter_by_sample_type(df, sample_type=None):
    if 'Type of samples' not in df.columns:
        raise KeyError("The dataframe does not contain a 'Type of samples' column.")
    
    if sample_type==None:
        sample_type = df['Type of samples'].unique()
    
    # Convert single string input to list
    if isinstance(sample_type, str):
        sample_type = [sample_type]

    # Check if all input values exist in the column
    unique_types = df['Type of samples'].unique()
    missing = [s for s in sample_type if s not in unique_types]
    
    if missing:
        raise ValueError(f"The following values were not found in 'Type of samples': {missing}")

    return df[df['Type of samples'].isin(sample_type)]

