import dash
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
from dash import dcc
from dash import html
from dash import dcc, html, callback
from dash.dependencies import Input, Output
from dash import dash_table
from dash.dependencies import Input, Output, State
from dash import dash_table
import io
import base64


dash.register_page(__name__,
                   path='/Distinction',
                   name='Distinction Analysis',
                   title='New heatmaps',
                   description='Learn all about the heatmap.'
)






# Define function to categorize students based on CGPA
def categorize_students(cgpa):
    if cgpa > 7.75:
        return 'First Class with Distinction'
    elif cgpa > 6.75:
        return 'First Class'
    elif cgpa > 6.25:
        return 'Higher Second Class'
    elif cgpa > 5.5:
        return 'Second Class'
    elif cgpa > 0:
        return 'All Clear'
    else:
        return 'Fail'

# Create the layout for the app
layout = html.Div(children=[
    html.H1(children='Distribution of Student Results'),
    # Upload component for CSV
    dcc.Upload(
        id='upload-component',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
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
    dcc.Graph(
        id='result-bar-graph'
    ),
    html.H3(children='Click a bar to see the data for that category:'),
    dash_table.DataTable(
        id='data-table',
        columns=[{"name": "Nameofthestudent", "id": "Nameofthestudent"},
                 {"name": "Percentage", "id": "Percentage"},
                 {"name": "CGPA", "id": "CGPA"},
                 {"name": "Distinction Score", "id": "Distinction_score"}],
        style_cell={'textAlign': 'center'},
        style_data_conditional=[{
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
        }],
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        }
    ),
    # Display the top 5 students by CGPA in a DataTable
    html.H3(children='Top Five Students by CGPA:'),
    dash_table.DataTable(
        id='top-five-table',
        columns=[{"name": "Nameofthestudent", "id": "Nameofthestudent"},
                 {"name": "CGPA", "id": "CGPA"},
                 {"name": "Distinction Score", "id": "Distinction_score"}],
        style_cell={'textAlign': 'center'},
        style_data_conditional=[{
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
        }],
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        }
    )
])

# Callback to update data table, graph, and top-five-table based on uploaded file and click data
@callback(
    [Output('data-table', 'data'),
     Output('result-bar-graph', 'figure'),
     Output('top-five-table', 'data')],
    [Input('upload-component', 'contents'),
     Input('upload-component', 'filename'),
     Input('result-bar-graph', 'clickData')]
)
def update_data(contents, filename, clickData):
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        try:
            if 'csv' in filename:
                # Read the uploaded file as DataFrame
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
                # Perform data processing and visualization
                df['CGPA'] = df.iloc[:, 7] / 9.5
                df['Distinction_score'] = df['CGPA'].apply(categorize_students)
                result_counts = df.groupby('Distinction_score').size()
                fig = go.Figure(data=[go.Bar(x=result_counts.index, y=result_counts.values,
                                             marker_color=['#00bfff', '#0066ff', '#1a75ff', '#4d94ff', '#b3d9ff', '#ff6666'])])
                fig.update_layout(
                    title='Distribution of Student Results',
                    xaxis_title='Result Category',
                    yaxis_title='Number of Students'
                )
                topper_list = df.sort_values(by='CGPA', ascending=False).head(5)[
                    ["Nameofthestudent", "CGPA", "Distinction_score"]]

                if clickData is not None:
                    selected_result = clickData['points'][0]['x']
                    filtered_data = df.loc[df['Distinction_score'] == selected_result]
                    return (
                        filtered_data[["Nameofthestudent", "Percentage", "CGPA", "Distinction_score"]].to_dict('records'),
                        fig,
                        topper_list.to_dict('records')
                    )
                else:
                    return (
                        df[["Nameofthestudent", "Percentage", "CGPA", "Distinction_score"]].to_dict('records'),
                        fig,
                        topper_list.to_dict('records')
                    )
        except Exception as e:
            print(e)
            return [], {}, []
    else:
        return [], {}, []
