import dash
import pandas as pd
from dash import dcc, html, callback, Output, Input
import plotly.express as px
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from flask import Flask
import numpy as np
import plotly.express as px

# To create meta tag for each page, define the title, image, and description.
dash.register_page(__name__,
                   path='/Predictive',  # '/' is home page and it represents the url
                   name='Prediction',  # name of page, commonly used as name of link
                   title='Index',  # title that appears on browser's tab
                   )

# page 1 data

# Load data
df = pd.read_csv('ALL.csv')

# Define conditions and corresponding values
conditions = [
    (df.iloc[:, 1] >= 56) & (df.iloc[:, 2] >= 56) & (df.iloc[:, 3] >= 56),
    (df.iloc[:, 4] >= 56) & (df.iloc[:, 5] >= 56),
    (df.iloc[:, 4] >= 56) & (df.iloc[:, 5] >= 56) & (df.iloc[:, 6] >= 56),
    (df.iloc[:, 4] >= 56) & (df.iloc[:, 5] >= 56) & (df.iloc[:, 7] >= 56),
    (df.iloc[:, 12] >= 56) & (df.iloc[:, 13] >= 56) & (df.iloc[:, 14] >= 56),
    (df.iloc[:, 15] >= 56) & (df.iloc[:, 16] >= 56) & (df.iloc[:, 17] >= 56),
    (df.iloc[:, 18] >= 56) & (df.iloc[:, 19] >= 56),
    (df.iloc[:, 20] >= 56) & (df.iloc[:, 21] >= 56),
    (df.iloc[:, 22] >= 56) & (df.iloc[:, 23] >= 56) & (df.iloc[:, 24] >= 56) & (df.iloc[:, 25] >= 56),
    (df.iloc[:, 7] >= 56) & (df.iloc[:, 8] >= 56) & (df.iloc[:, 9] >= 56) & (df.iloc[:, 10] >= 56) & (df.iloc[:, 11] >= 56)
]
values = [
    'DATA SCIENCE', 'DATA ANALYST', 'BUSINESS ANALYST', 'BACKEND DEVELOPER', 'EMBEDDED ENGINEER',
    'NETWORK ENGINEER', 'FRONTEND DEVELOPER', 'SOFTWARE TESTING', 'SOFTWARE ENGINEER', 'SOFTWARE DEVELOPER'
]

# Create a new column 'Career' based on conditions and values
df['Career'] = np.select(conditions, values, default='OTHER FIELD')

# Store the values of satisfied conditions as a string in a new column 'Satisfied_Conditions'
df['Satisfied_Conditions'] = df.apply(lambda x: ', '.join([value for condition, value in zip(conditions, values) if condition[x.name]]), axis=1)
df.loc[df['Satisfied_Conditions'] == '', 'Satisfied_Conditions'] = 'NON TECHNICAL'

# Create a pie chart using Plotly Express
fig = px.pie(df, names='Career', category_orders={'Career': values + ['OTHER FIELD']})

# Define the layout of the application
layout = html.Div(children=[
    html.H1('Career Distribution'),
    dcc.Graph(
        id='career-pie-chart',
        figure=fig
    ),
    html.H2('Selected Career Names and Conditions:'),
    html.Table(id='selected-names-table')
])

# Define callback function to update the table based on the selected pie values
@callback(
    Output('selected-names-table', 'children'),
    Input('career-pie-chart', 'clickData')
)
def update_table(clickData):
    if clickData is None:
        return []

    selected_career = clickData['points'][0]['label']
    filtered_data = df[df['Career'] == selected_career]
    selected_names = filtered_data['Name'].values
    selected_conditions = filtered_data['Satisfied_Conditions'].values

    rows = []
    for name, conditions in zip(selected_names, selected_conditions):
        row = html.Tr([html.Td(name), html.Td(conditions)])
        rows.append(row)

    table = html.Table([
        html.Thead(html.Tr([html.Th('Selected Names'), html.Th('Satisfied Conditions')])),
        html.Tbody(rows)
    ])

    return table
