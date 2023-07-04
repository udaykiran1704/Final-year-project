"""import base64
import io
import dash
import pandas as pd
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import plotly.graph_objs as go
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
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
import plotly.graph_objs as go
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
# To create meta tag for each page, define the title, image, and description.
dash.register_page(__name__,
                   path='/Predictive1 ',  # '/' is home page and it represents the url
                   name='Prediction1',  # name of page, commonly used as name of link
                  
                   )

# page 1 data

# Define the app layout
layout = html.Div([
    dcc.Upload(
        id='upload-data',
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
        id='student-dropdown',
        options=[],
        value=None
    ),
    dcc.Graph(
        id='prediction-graph',
        figure={}
    )
])

# Define the update function for dropdown options and prediction graph
@callback(
    Output('student-dropdown', 'options'),
    Input('upload-data', 'contents')
)
def update_dropdown_options(contents):
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded_content = base64.b64decode(content_string).decode('utf-8')
        df = pd.read_csv(io.StringIO(decoded_content))

        options = [{'label': student, 'value': student} for student in df['Nameofthestudent']]

        return options

    return []


@callback(
    Output('prediction-graph', 'figure'),
    Input('student-dropdown', 'value'),
    State('upload-data', 'contents')
)
def update_prediction_graph(selected_student, contents):
    if contents is not None and selected_student is not None:
        content_type, content_string = contents.split(',')
        decoded_content = base64.b64decode(content_string).decode('utf-8')
        df = pd.read_csv(io.StringIO(decoded_content))

        student_data = df[df['Nameofthestudent'] == selected_student]
        decision_tree_model = train_decision_tree_model(df)
        prediction = predict_passing_status(student_data, decision_tree_model)

        pass_counts = len(prediction[prediction == 'Pass'])
        fail_counts = len(prediction[prediction == 'Fail'])

        data = [
            go.Bar(
                x=['Pass', 'Fail'],
                y=[pass_counts, fail_counts]
            )
        ]

        layout = go.Layout(
            title='Predicted Passing Status',
            xaxis=dict(title='Passing Status'),
            yaxis=dict(title='Count')
        )

        return {'data': data, 'layout': layout}

    return {}


def train_decision_tree_model(df):
    pass_marks = 12  # Set the pass marks threshold

    # Prepare the data for classification
    X = df.iloc[:, 2:6]
    y = (X >= pass_marks).sum(axis=1)
    y = y.apply(lambda x: 'Pass' if x >= 3 else 'Fail')

    # Train the decision tree classifier
    classifier = DecisionTreeClassifier()
    classifier.fit(X, y)

    return classifier


def predict_passing_status(student_data, model):
    X_student = student_data.iloc[:, 2:6]
    prediction = model.predict(X_student)

    return prediction

"""