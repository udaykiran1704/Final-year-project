import dash
import pandas as pd
import base64
import io
from flask import Flask
from dash import dcc, html, callback, Output, Input
import plotly.graph_objs as go
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# To create meta tag for each page, define the title, image, and description.
dash.register_page(__name__,
                   path='/',  # '/' is home page and it represents the URL
                   name='Overall',  # name of page, commonly used as name of link
                   title='Index'  # title that appears on the browser's tab
                   )

# Initialize the Flask app
server = Flask(__name__)

# Initialize the Dash app
app = dash.Dash(__name__, server=server)

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
    html.Div(id='classification-report')
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
            colors = ['rgba(31, 119, 180, 0.8)', 'rgba(255, 127, 14, 0.8)', 'rgba(44, 160, 44, 0.8)',
                      'rgba(214, 39, 40, 0.8)']
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
@callback(Output('passing-percentages-graph', 'figure'), [Input('upload-data1', 'contents')])
def update_passing_percentages_graph(contents):
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
@callback(Output('failing-percentages-graph', 'figure'), [Input('upload-data1', 'contents')])
def update_failing_percentages_graph(contents):
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
@callback(Output('failing-students-table', 'children'), [Input('upload-data1', 'contents')])
def update_failing_students_table(contents):
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

            failing_students_data.append(html.Tr([
                html.Td(row['Nameofthestudent']),
                html.Td(', '.join(failing_subjects))
            ]))

        return [
            html.Thead(html.Tr([html.Th('Student Name'), html.Th('Failing Subjects')])),
            html.Tbody(failing_students_data)
        ]

    return []


# Define the update function for classification report
@callback(Output('classification-report', 'children'), [Input('upload-data1', 'contents')])
def update_classification_report(contents):
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded_content = base64.b64decode(content_string).decode('utf-8')
        df = pd.read_csv(io.StringIO(decoded_content))
        
        pass_marks = 12  # Set the pass marks threshold
        
        # Prepare the data for classification
        X = df.iloc[:, 2:6]
        y = (X >= pass_marks).sum(axis=1)
        y = y.apply(lambda x: 'Pass' if x >= 3 else 'Fail')
        
        # Split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train the decision tree classifier
        classifier = DecisionTreeClassifier()
        classifier.fit(X_train, y_train)
        
        # Make predictions on the test set
        y_pred = classifier.predict(X_test)
        
        # Generate the classification report
        report = classification_report(y_test, y_pred, zero_division=1)
        
        return html.Pre(report)
    
    return []




if __name__ == '__main__':
    app.run_server(debug=True)
