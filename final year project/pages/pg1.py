import dash
import pandas as pd
from dash import dcc, html, callback, Output, Input
import plotly.express as px
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import dash
import pandas as pd
import plotly.graph_objs as go
import base64
import io
from flask import Flask
import dash
import pandas as pd
import plotly.graph_objs as go
from dash import dcc, html, callback, Output, Input
from dash.dependencies import State

import base64
import io



# To create meta tag for each page, define the title, image, and description.
dash.register_page(__name__,
                   path='/',  # '/' is home page and it represents the url
                   name='Overall',  # name of page, commonly used as name of link
                   title='Index',  # title that appears on browser's tab
                   
)
# Initialize the Flask app
server = Flask(__name__)

# Initialize the Dash app
app = dash.Dash(__name__, server=server)


# page 1 data


# Define the app layout
layout = html.Div([
    dcc.Upload(
        id='upload-data1',
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
    dcc.Dropdown(
        id='student-dropdown1',
        options=[],
        value=None
    ),
    dcc.Graph(id='live-bar-graph', animate=True),
    dcc.Graph(id='passing-percentages-graph'),
    dcc.Graph(id='failing-percentages-graph'),
    html.Table(id='failing-students-table', className='table'),
    dcc.Interval(
        id='interval-component',
        interval=1000,  # Update every 1 second
        n_intervals=0
    )
])

# Define the update function for dropdown options and bar graph
@callback(
    [Output('student-dropdown1', 'options'), Output('live-bar-graph', 'figure')],
    [Input('student-dropdown1', 'value'), Input('upload-data1', 'contents')]
)
def update_dropdown_options(selected_student, contents):
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded_content = base64.b64decode(content_string).decode('utf-8')
        df = pd.read_csv(io.StringIO(decoded_content))
        
        options = [{'label': student, 'value': student} for student in df['Nameofthestudent']]
        
        if selected_student is not None:
            student_data = df[df['Nameofthestudent'] == selected_student]
            colors = ['rgba(31, 119, 180, 0.8)', 'rgba(255, 127, 14, 0.8)', 'rgba(44, 160, 44, 0.8)', 'rgba(214, 39, 40, 0.8)']
            data = []
            for i, subject in enumerate(df.columns[2:6]):
                data.append(go.Bar(
                    x=[subject],
                    y=[student_data[subject].values[0]],
                    name=subject,
                    marker=dict(color=colors[i])
                ))
            layout = go.Layout(
                title=f'Scores of individual Students in All Subjects',
                xaxis={'title': 'Subjects'},
                yaxis={'title': 'Scores'}
            )
            return options, {'data': data, 'layout': layout}
        
        return options, {'data': [], 'layout': {}}
    
    return [], {'data': [], 'layout': {}}

# Define the update function for passing percentages graph
@callback(Output('passing-percentages-graph', 'figure'), [Input('interval-component', 'n_intervals')], [State('upload-data1', 'contents')])
def update_passing_percentages_graph(n, contents):
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded_content = base64.b64decode(content_string).decode('utf-8')
        df = pd.read_csv(io.StringIO(decoded_content))
        
        pass_counts = []
        
        pass_marks = 12  # Set the pass marks threshold
        
        for column in df.columns[2:6]:
            pass_counts.append(df[df[column] >= pass_marks][column].count())
        
        data = [go.Bar(
            x=df.columns[2:6],
            y=[count / len(df) * 100 for count in pass_counts],
            name='Passing Percentage',
            marker=dict(color='blue')  # Set the color to blue
        )]
        
        layout = go.Layout(
            title='Passing Percentages in All Subjects',
            xaxis={'title': 'Subjects'},
            yaxis={'title': 'Passing Percentage (%)'}
        )
        
        return {'data': data, 'layout': layout}
    
    return {'data': [], 'layout': {}}

# Define the update function for failing percentages graph
@callback(Output('failing-percentages-graph', 'figure'), [Input('interval-component', 'n_intervals')], [State('upload-data1', 'contents')])
def update_failing_percentages_graph(n, contents):
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded_content = base64.b64decode(content_string).decode('utf-8')
        df = pd.read_csv(io.StringIO(decoded_content))
        
        fail_counts = []
        pass_marks = 12  # Set the pass marks threshold
        
        for column in df.columns[2:6]:
            fail_counts.append(df[df[column] < pass_marks][column].count())
        
        data = [go.Bar(
            x=df.columns[2:6],
            y=[count / len(df) * 100 for count in fail_counts],
            name='Failing Percentage',
            marker=dict(color='red')
        )]
        
        layout = go.Layout(
            title='Failing Percentages in All Subjects',
            xaxis={'title': 'Subjects'},
            yaxis={'title': 'Failing Percentage (%)'}
        )
        
        return {'data': data, 'layout': layout}
    
    return {'data': [], 'layout': {}}

# Define the update function for failing students table
@callback(Output('failing-students-table', 'children'), [Input('interval-component', 'n_intervals')], [State('upload-data1', 'contents')])
def update_failing_students_table(n, contents):
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded_content = base64.b64decode(content_string).decode('utf-8')
        df = pd.read_csv(io.StringIO(decoded_content))
        
        pass_marks = 12  # Set the pass marks threshold
        
        failed_students = df.loc[df.iloc[:, 2:6].lt(pass_marks).any(axis=1)]
        failing_students_data = []
        
        for index, row in failed_students.iterrows():
            failing_subjects = []
            for column in df.columns[2:6]:
                if row[column] < pass_marks:
                    failing_subjects.append(column)
            
            failing_students_data.append({
                'Name': row['Nameofthestudent'],
                'Failing Subjects': ', '.join(failing_subjects)
            })
        
        table_data = []
        for data in failing_students_data:
            table_data.append(
                html.Tr([
                    html.Td(data['Name']),
                    html.Td(data['Failing Subjects'])
                ], style={'border': '1px solid #ccc'})
            )
        
        table_header = [
            html.Thead(html.Tr([
                html.Th('Name', style={'border': '1px solid #ccc'}),
                html.Th('Failing Subjects', style={'border': '1px solid #ccc'})
            ]))
        ]
        
        table_body = [html.Tbody(table_data)]
        
        table = html.Table(table_header + table_body, className='table')
        
        return table
    
    return html.Table(className='table')

if __name__ == '__main__':
    app.run_server(debug=True)
