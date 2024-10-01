from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from API import AirlinkAPI
import dash_bootstrap_components as dbc
import os


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server




# Function to create the Global Air Quality Heatmap
def create_global_air_quality_heatmap():
   data = []
   for city, coords in AirlinkAPI.cities.items():

       city_data = AirlinkAPI.get_air_quality_data(coords['lat'], coords['lon'],
                                                   (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                                                   datetime.now().strftime('%Y-%m-%d'))


       if not city_data.empty and 'AQI' in city_data.columns:
           aqi_value = city_data.iloc[-1]['AQI']



           red = city_data.iloc[-1].get('Color Red', None)
           green = city_data.iloc[-1].get('Color Green', None)
           blue = city_data.iloc[-1].get('Color Blue', None)


           if red is None or green is None or blue is None:
               color = 'rgb(128, 128, 128)'  # Default to gray if any color component is missing
           else:
               try:
                   red = float(red) * 255
                   green = float(green) * 255
                   blue = float(blue) * 255


                   # Clamp values between 0 and 255
                   red = min(max(red, 0), 255)
                   green = min(max(green, 0), 255)
                   blue = min(max(blue, 0), 255)


                   color = f'rgb({int(red)}, {int(green)}, {int(blue)})'
               except (ValueError, TypeError):
                   color = 'rgb(128, 128, 128)'


           data.append(
               go.Scattermapbox(
                   lat=[coords['lat']],
                   lon=[coords['lon']],
                   mode='markers',
                   marker=go.scattermapbox.Marker(
                       size=14,
                       color=color,
                       opacity=0.7
                   ),
                   text=f'{city}: {aqi_value} AQI',
               )
           )
       else:

           data.append(
               go.Scattermapbox(
                   lat=[coords['lat']],
                   lon=[coords['lon']],
                   mode='markers',
                   marker=go.scattermapbox.Marker(
                       size=14,
                       color='rgb(128, 128, 128)',
                       opacity=0.7
                   ),
                   text=f'{city}: N/A AQI',
               )
           )



   fig = go.Figure(data=data)
   fig.update_layout(
       mapbox=dict(
           accesstoken=os.getenv('MAPBOX_API_KEY'),
           center=dict(lat=20, lon=0),
           zoom=1,
           style="carto-positron"
       ),
       margin={"r": 0, "t": 0, "l": 0, "b": 0},
       showlegend=False
   )
   return fig




#Function for the section that gives health recommendations based on the aqi.
def get_health_recommendation(aqi):
   if aqi <= 50:
       return {
           'level': 'Good',
           'description': ('The air quality is optimal, and poses little to no risk to health. '
                           'People from all groups can engage in outdoor activities without any concern for air pollution. '
                           'This level of air quality supports physical exercise, promotes mental well-being, and contributes to a healthy environment.'),
           'recommendation': 'Engage in outdoor physical activities like running, cycling, or hiking with no restrictions. Optimal air conditions are highly favorable for active lifestyles.',
           'symptoms': 'No noticeable health effects. Breathing is clear and unencumbered.'
       }
   elif 51 <= aqi <= 100:
       return {
           'level': 'Moderate',
           'description': ('The air quality is generally acceptable for most individuals, but for some pollutants, '
                           'there may be a moderate health concern, especially for sensitive groups such as individuals with respiratory issues or the elderly. '
                           'Air pollutants at this level may cause slight discomfort but are unlikely to have long-term effects.'),
           'recommendation': ('Sensitive individuals, particularly those with asthma, allergies, or pre-existing respiratory conditions, '
                              'should consider limiting prolonged or heavy outdoor exertion. Others can proceed with outdoor activities with minimal risk.'),
           'symptoms': 'Mild respiratory discomfort may be experienced by those in sensitive groups; no significant effects for the general public.'
       }
   elif 101 <= aqi <= 150:
       return {
           'level': 'Unhealthy for Sensitive Groups',
           'description': ('Air quality at this level may begin to pose health risks to individuals in sensitive groups. '
                           'People with underlying respiratory or cardiovascular conditions, children, and the elderly are more vulnerable to pollution-related symptoms. '
                           'The general population may not be affected but should remain aware of potential risks.'),
           'recommendation': ('Sensitive groups should avoid outdoor activities, particularly strenuous exercises that increase breathing rates. '
                              'It is advisable to remain indoors or engage in low-exertion activities during peak pollution hours.'),
           'symptoms': ('Symptoms for sensitive individuals may include shortness of breath, increased coughing, or exacerbation of asthma symptoms. '
                        'General population may not experience noticeable effects.')
       }
   elif 151 <= aqi <= 200:
       return {
           'level': 'Unhealthy',
           'description': ('The air quality is deteriorating, posing a risk to the health of the general public. Prolonged exposure to outdoor air at this level '
                           'can result in noticeable adverse health effects for both healthy individuals and those with pre-existing conditions. '
                           'Particulate matter and other pollutants can irritate the respiratory system, leading to decreased lung function.'),
           'recommendation': ('Outdoor activities should be significantly limited. Avoid intense outdoor physical exertion, especially during high pollution periods. '
                              'Consider using air purifiers indoors to mitigate exposure to pollutants.'),
           'symptoms': ('Symptoms may include difficulty breathing, chest tightness, and exacerbation of respiratory conditions. Long-term exposure may have serious health implications.')
       }
   elif 201 <= aqi <= 300:
       return {
           'level': 'Very Unhealthy',
           'description': ('The air quality is at hazardous levels for all population groups, and there is a heightened risk of severe health effects. '
                           'Short-term exposure can cause significant health issues, particularly for individuals with pre-existing respiratory or cardiovascular diseases. '
                           'At this level, toxic pollutants may overwhelm the body’s natural defenses, leading to acute symptoms and longer recovery times.'),
           'recommendation': ('It is advised to stay indoors as much as possible and avoid any outdoor activities. Air filtration systems, such as HEPA filters, should be used indoors. '
                              'Those with respiratory conditions should monitor symptoms closely and seek medical attention if necessary.'),
           'symptoms': ('Severe symptoms may include breathing difficulties, significant chest pain, and an increased risk of heart attacks or other cardiovascular complications. '
                        'Sensitive groups are at risk of life-threatening conditions.')
       }
   else:
       return {
           'level': 'Hazardous',
           'description': ('This level of air quality constitutes an emergency condition for the entire population. Exposure can lead to serious long-term health effects, '
                           'and sensitive groups may experience life-threatening symptoms. Sustained exposure to pollutants such as PM2.5, sulfur dioxide, or ozone at these levels '
                           'can cause irreversible damage to the lungs and cardiovascular system. Immediate action to reduce exposure is critical.'),
           'recommendation': ('Stay indoors with windows and doors closed. Use high-efficiency air purifiers and avoid any outdoor activities. '
                              'Consider evacuating to areas with better air quality if the hazardous conditions persist. Monitor news and government alerts for emergency protocols.'),
           'symptoms': ('Serious health impacts for the entire population. Immediate symptoms may include intense respiratory distress, increased heart rate, and a higher likelihood of medical emergencies. '
                        'Those with respiratory or cardiovascular conditions should seek immediate medical attention if symptoms worsen.')
       }





# dashboard layout design
app.layout = html.Div(style={'backgroundColor': '#f8f9fa', 'minHeight': '100vh', 'padding': '20px'}, children=[
   dbc.Container([
       dbc.Row([
           dbc.Col([
               html.H2("Air Quality Dashboard", className="text-center text-primary mb-4"),
           ], width=12)
       ]),
       dbc.Row([
           dbc.Col([
               html.Label("Select City:"),
               dcc.Dropdown(
                   id='city-dropdown',
                   options=[{'label': city, 'value': city} for city in AirlinkAPI.cities.keys()],
                   value='New York',
                   className='mb-3'
               ),
           ], width=6),
           dbc.Col([
               html.Label("Select Date Range:"),
               dcc.DatePickerRange(
                   id='date-picker-range',
                   start_date=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                   end_date=datetime.now().strftime('%Y-%m-%d'),
                   max_date_allowed=datetime.now(),
                   min_date_allowed=datetime.now() - timedelta(days=365),
                   className='mb-3'
               ),
           ], width=6)
       ]),
   ], fluid=True),


   dbc.Container([
       dbc.Row([
           dbc.Col([
               dbc.Card([
                   dbc.CardHeader(html.H4('Global Air Quality Heatmap')),
                   dbc.CardBody([
                       dcc.Graph(id='global-heatmap', figure=create_global_air_quality_heatmap())
                   ])
               ], className="h-100")
           ], width=6),


           dbc.Col([
               dbc.Card([
                   dbc.CardHeader(html.H4('Historical Air Quality Index')),
                   dbc.CardBody([
                       dcc.Graph(id='historical-air-quality-graph')
                   ])
               ], className="h-100")
           ], width=6),
       ], className="mb-4"),


       dbc.Row([
           dbc.Col([
               dbc.Card([
                   dbc.CardHeader(html.H4('Pollutant Concentrations')),
                   dbc.CardBody([
                       dcc.Graph(id='pollutant-pie-chart')
                   ])
               ], className="h-100")
           ], width=6),


           dbc.Col([
               dbc.Card([
                   dbc.CardHeader(html.H4('Health Recommendations')),
                   dbc.CardBody([
                       html.Div(id='health-recommendation-div', className="text-center")
                   ])
               ], className="h-100")
           ], width=6),
       ])
   ], fluid=True)
])




# Callback for Historical Air Quality Graph
@app.callback(
   Output('historical-air-quality-graph', 'figure'),
   [Input('city-dropdown', 'value'), Input('date-picker-range', 'start_date'), Input('date-picker-range', 'end_date')]
)
def update_historical_graph(selected_city, start_date, end_date):
   coords = AirlinkAPI.cities[selected_city]
   df = AirlinkAPI.get_air_quality_data(coords['lat'], coords['lon'], start_date, end_date)





   if not df.empty and 'AQI' in df.columns:
       fig = px.line(df, x='Date', y='AQI', title=f'Historical Air Quality Index for {selected_city}',
                     labels={"Date": "Date", "AQI": "Air Quality Index (AQI)"})
       return fig
   else:
       return px.line(title='No Data Available')




# Callback for Pollutant Concentration Pie Chart
@app.callback(
   Output('pollutant-pie-chart', 'figure'),
   [Input('city-dropdown', 'value')]
)
def update_pollution_chart(selected_city):
   coords = AirlinkAPI.cities[selected_city]
   df = AirlinkAPI.get_pollutant_concentrations(coords['lat'], coords['lon'])





   if not df.empty and 'Pollutant' in df.columns and 'Concentration' in df.columns:
       # pie chart of pollutant concentrations
       fig = px.pie(df, values='Concentration', names='Pollutant',
                    title=f'Pollutant Concentrations for {selected_city}',
                    labels={"Pollutant": "Pollutant", "Concentration": "Concentration"})
       return fig
   else:
       return px.pie(title='No Data Available')




# Callback for Health Recommendation
@app.callback(
   Output('health-recommendation-div', 'children'),
   [Input('city-dropdown', 'value')]
)
def update_health_recommendation(selected_city):
   coords = AirlinkAPI.cities[selected_city]
   df = AirlinkAPI.get_air_quality_data(coords['lat'], coords['lon'],
                                        (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                                        datetime.now().strftime('%Y-%m-%d'))





   if not df.empty and 'AQI' in df.columns:
       latest_aqi = df.iloc[-1]['AQI']



       # Get health recommendation based on the AQI value
       recommendation = get_health_recommendation(latest_aqi)


       # Return the health recommendations as HTML content
       return html.Div([
           html.H5(f"Air Quality Level: {recommendation['level']}"),
           html.P(f"Description: {recommendation['description']}"),
           html.P(f"Recommendation: {recommendation['recommendation']}"),
           html.P(f"Potential Symptoms: {recommendation['symptoms']}")
       ])


   # If no data is available, show a message
   return html.Div("AQI data not available in the response.")


if __name__ == '__main__':
   port = int(os.environ.get("PORT", 8050))
   app.run_server(debug=True, port=port, host="0.0.0.0")


