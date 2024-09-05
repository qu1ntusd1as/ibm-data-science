# Import necessary libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
from dash import no_update

# Load the SpaceX data into a pandas DataFrame
spacex_data = pd.read_csv("spacex_launch_dash.csv")
max_payload_value = spacex_data['Payload Mass (kg)'].max()
min_payload_value = spacex_data['Payload Mass (kg)'].min()

# Initialize the Dash app
app = dash.Dash(__name__)

# Create layout elements
launch_sites_options = [{'label': 'All Sites', 'value': 'All Sites'}]
for site in spacex_data["Launch Site"].unique():
    launch_sites_options.append({'label': site, 'value': site})

# Define the app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'fontSize': 40}),
    
    # Dropdown for selecting launch sites
    dcc.Dropdown(id='site-dropdown', options=launch_sites_options, value='All Sites', 
                 placeholder="Select a Launch Site", searchable=True),
    html.Br(),

    # Pie chart showing launch success counts
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    # Range slider for payload selection
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(id='payload-slider', min=0, max=10000, step=1000, 
                    value=[min_payload_value, max_payload_value], 
                    marks={2500: '2500 (Kg)', 5000: '5000 (Kg)', 7500: '7500 (Kg)'}),
    
    # Scatter plot for payload vs. launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])

# Callback for updating pie chart based on selected site
@app.callback(Output('success-pie-chart', 'figure'),
              Input('site-dropdown', 'value'))
def update_pie_chart(selected_site):
    if selected_site == 'All Sites':
        data_by_site = spacex_data.groupby('Launch Site')['class'].sum().reset_index()
        pie_chart = px.pie(data_by_site, values='class', names='Launch Site', 
                           title='Total Successful Launches by Site')
    else:
        site_data = spacex_data[spacex_data['Launch Site'] == selected_site]['class'].value_counts().reset_index()
        site_data.columns = ['Outcome', 'Count']
        pie_chart = px.pie(site_data, values='Count', names='Outcome', 
                           title=f'Success vs. Failure for {selected_site}')
    return pie_chart

# Callback for updating scatter plot based on site and payload range
@app.callback(Output('success-payload-scatter-chart', 'figure'),
              [Input('site-dropdown', 'value'), 
               Input('payload-slider', 'value')])
def update_scatter_plot(selected_site, payload_range):
    filtered_data = spacex_data[(spacex_data['Payload Mass (kg)'] >= payload_range[0]) & 
                                (spacex_data['Payload Mass (kg)'] <= payload_range[1])]

    if selected_site != 'All Sites':
        filtered_data = filtered_data[filtered_data['Launch Site'] == selected_site]
    
    scatter_plot = px.scatter(filtered_data, x='Payload Mass (kg)', y='class', 
                              color='Booster Version Category', 
                              title='Payload vs. Success for Launches')
    return scatter_plot

# Run the app
if __name__ == '__main__':
    app.run_server()
