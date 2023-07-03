import dash
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
from dash import dcc
from dash import html
from dash import dcc, html,callback
from dash.dependencies import Input, Output
import numpy as np
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import base64
import io

# To create meta tag for each page, define the title, image, and description.

dash.register_page(__name__,
                   path='/Placement',  # '/' is home page and it represents the url
                   name='Placement',  # name of page, commonly used as name of link
)


# Load data

# Define the layout
layout = html.Div(children=[
    html.H1(children='Student Performance'),
    html.Div(children='''Placement by Gender'''),

    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select CSV File')
        ]),
        style={
            'width': '50%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple=False
    ),

    dcc.Graph(id='placement-graph')
])

# Callback function to process the uploaded file
@callback(
    Output('placement-graph', 'figure'),
    Input('upload-data', 'contents'),
    Input('upload-data', 'filename')
)
def update_graph(contents, filename):
    if contents is not None:
        content_type, content_string = contents.split(',')

        # Decode and read the CSV file
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

        # Perform your data processing
        df['Placement'] = df['Placement'].apply(lambda x: 1 if x == 'placed' else 0)
        df['Placement Status'] = df['Placement'].apply(lambda x: 'placed' if x == 1 else 'unplaced')
        

        # Calculate the count of placements by gender and placement status
        placement_counts = df.groupby(['Gender', 'Placement Status']).size().reset_index(name='Count')

# Create the figure
        fig = px.bar(placement_counts, x='Gender', y='Count', color='Placement Status',
             barmode='group', height=400)

        return fig

    # If no file is uploaded, return an empty figure
    return go.Figure()
