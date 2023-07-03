
import dash
import plotly.express as px
import pandas as pd
from dash import dcc, html
from dash import dcc, html, callback, Output, Input
import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import base64
import io


# To create meta tag for each page, define the title, image, and description.

dash.register_page(__name__,
                   path='/Attendance',  # '/' is home page and it represents the url
                   name='Attendance',  # name of page, commonly used as name of link
)




# Define the layout
layout = html.Div(
    children=[
        html.H1('Attendance Distribution'),
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
            }
        ),
        dcc.Graph(id='bar-chart'),
    ]
)

# Define the callback function to read and process the uploaded CSV file
@callback(
    Output('bar-chart', 'figure'),
    Input('upload-data', 'contents'),
    Input('upload-data', 'filename')
)
def update_bar_chart(contents, filename):
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        try:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            
            # Assign 1 for Present and 0 for Absent in the Attendance column
            df['Attendance'] = df.iloc[:, 9].apply(lambda x: 1 if x == 'Present' else 0)
            
            # Convert multiple columns to numeric type
            columns_to_convert = ['HPC', 'DL', 'SDN', 'BI']
            df[columns_to_convert] = df[columns_to_convert].apply(pd.to_numeric, errors='coerce')
            
            # Assign feature columns
            feature_cols = ['HPC', 'SDN', 'BI', 'DL']
            X = df[feature_cols]  # Features
            
            # Assign target variable
            y = df['Attendance']
            
            # Split the dataset into training and testing sets
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Create a Decision Tree Classifier object
            clf = DecisionTreeClassifier()
            
            # Train the classifier on the training data
            clf.fit(X_train, y_train)
            
            # Predict the classes for the test data
            y_test_pred = clf.predict(X_test)
            
            # Calculate the accuracy of the model
            accuracy = accuracy_score(y_test, y_test_pred)
            
            # Create a DataFrame with the test data and predicted classes
            df_test = X_test.copy()
            df_test['Attendance'] = y_test
            df_test['Predicted Result'] = y_test_pred
            
            # Count the occurrences of each class in the test data
            class_counts = df_test['Predicted Result'].value_counts().reset_index()
            class_counts.columns = ['Attendance', 'Count']
            colors = ['red', 'green', 'blue', 'orange']

            # Create the bar chart
            fig = px.bar(
                class_counts, 
                x='Attendance', 
                y='Count', 
                color='Attendance',
                title='Attendance Distribution'
            )
            
            # Customize the x-axis labels
            fig.update_layout(xaxis={'tickmode': 'array', 'tickvals': [0, 1], 'ticktext': ['Absent', 'Present']})
            
            return fig
        
        except Exception as e:
            print(e)
            return "There was an error processing the file."
    
    return {}



