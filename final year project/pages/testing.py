import dash
import plotly.express as px
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# Create the Dash application
app = dash.Dash(__name__)

# Load data
data = pd.read_csv('student_performance.csv')

# Assign 1 for placed and 0 for unplaced in the Placement column
data['Placement'] = data['Placement'].apply(lambda x: 1 if x == 'placed' else 0)

# Categorize placement as placed or unplaced based on the new Placement column
data['Placement Status'] = data['Placement'].apply(lambda x: 'placed' if x == 1 else 'unplaced')

# Calculate the count of placements by gender and placement status
placement_counts = data.groupby(['Gender', 'Placement Status']).size().reset_index(name='Count')

# Create the figure
fig = px.bar(placement_counts, x='Gender', y='Count', color='Placement Status',
             barmode='group', height=400)

# Define the layout
layout = html.Div(children=[
    html.H1(children='Student Performance'),
    html.Div(children='Placement by Gender'),
    dcc.Graph(
        id='placement-graph',
        figure=fig
    )
])

# Set the layout for the app
app.layout = layout

# Run the application
if __name__ == '__main__':
    app.run_server(debug=True)
