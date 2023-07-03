import dash
from dash import dcc, html, callback, Output, Input
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output, dash_table, no_update
import pandas as pd
import io
import base64
import plotly.express as px
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objs as go
from dash import dcc
from dash import html
from flask import Flask
import base64
import io



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

dash.register_page(__name__,
                   path='/Failure',  # represents the url text
                   name='Failure Analysis',  # name of page, commonly used as name of link
                   title='Analysis'  # epresents the title of browser's tab
)

# page 2 data




# Define the layout of the application
layout = html.Div(children=[
    html.H1(children='Student Performance'),

    html.Div(children='''
        Bar graph of student performance based on number of subjects failed.
    '''),

    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
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

    html.Hr(),

    dcc.Graph(id='student-performance-graph'),  # Add the Graph component

    html.Div(id='selected-category-data')
])

def process_uploaded_data(contents):
    content_type, content_string = contents.split(',')
    decoded_data = base64.b64decode(content_string)
    global df
    df = pd.read_csv(io.StringIO(decoded_data.decode('utf-8')))
    
    # Create a new column to indicate number of subjects failed
    df['Subjects Failed'] = df.iloc[:, 2:6].apply(lambda row: sum(row < 12), axis=1)
    
    # Define function to categorize students based on number of subjects failed
    def categorize_students(num_subjects_failed):
        if num_subjects_failed == 1:
            return 'Fail in one subject'
        elif num_subjects_failed == 2:
            return 'Fail in two subjects'
        elif num_subjects_failed == 3:
            return 'Fail in three subjects'
        elif num_subjects_failed == 4:
            return 'Fail in four subjects'
        else:
            return 'All clear'

    # Apply the categorization function to the 'Subjects Failed' column
    df['Result'] = df['Subjects Failed'].apply(categorize_students)

    # Group the data by the 'Result' column and count the number of students in each group
    result_counts = df.groupby('Result').size().reset_index(name='Counts')


    # Create a bar graph visualization using Plotly Express
    fig = px.bar(result_counts, x='Result', y='Counts', color="Result")
    fig.update_layout(
        xaxis_title='Result',
        yaxis_title='No of Students',
        title='FAILURE AS PER SUBJECTS'
    )
    
    return fig

def filter_data(selected_category):
    # Define the logic to filter the data based on the selected category
    # You need to implement this based on your specific requirements
    # Return the filtered data as a pandas DataFrame
    
    # Example logic: Filtering based on the 'Result' column
    filtered_df = df[df['Result'] == selected_category]
    return filtered_df.iloc[:, [1, 2, 3, 4, 5]] 

# Define a callback function to process the uploaded data and update the graph
@callback(
    Output('student-performance-graph', 'figure'),
    [Input('upload-data', 'contents')]
)
def update_graph(contents):
    if contents is not None:
        fig = process_uploaded_data(contents)
        return fig
    else:
        # Default graph
        return {}

# Define a callback function to update the DataTable based on the selected category
@callback(
    Output('selected-category-data', 'children'),
    [Input('student-performance-graph', 'clickData')]
)
def update_table(clickData):
    if clickData is not None:
        selected_category = clickData['points'][0]['x']
        filtered_data = filter_data(selected_category)
        table = html.Table([
            html.Thead(html.Tr([html.Th(col) for col in filtered_data.columns])),
            html.Tbody([
                html.Tr([html.Td(filtered_data.iloc[i][col]) for col in filtered_data.columns]) 
                for i in range(len(filtered_data))
            ])
        ])
        return table
    else:
        return html.Div()

