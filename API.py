import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()
MAPBOX_TOKEN = os.getenv('MAPBOX_API_KEY')
API = os.getenv('GOOGLE_API_KEY')

class AirlinkAPI:
    cities = {
        'New York': {'lat': 40.7128, 'lon': -74.0060},
        'Los Angeles': {'lat': 34.0522, 'lon': -118.2437},
        'Chicago': {'lat': 41.8781, 'lon': -87.6298},
        'Houston': {'lat': 29.7604, 'lon': -95.3698},
        'Phoenix': {'lat': 33.4484, 'lon': -112.0740},
        'Chongqing': {'lat': 29.5638, 'lon': 106.5516},
        'Shanghai': {'lat': 31.2304, 'lon': 121.4737},
        'Moscow': {'lat': 55.7558, 'lon': 37.6173},
        'Beijing': {'lat': 39.9042, 'lon': 116.4074},
        'Dhaka': {'lat': 23.8103, 'lon': 90.4125},
        'Istanbul': {'lat': 41.0082, 'lon': 28.9784},
        'Mumbai': {'lat': 19.0760, 'lon': 72.8777},
        'Delhi': {'lat': 28.7041, 'lon': 77.1025},
        'Bangalore': {'lat': 12.9716, 'lon': 77.5946},
        'Tokyo': {'lat': 35.6895, 'lon': 139.6917},
        'London': {'lat': 51.5074, 'lon': -0.1278},
        'Paris': {'lat': 48.8566, 'lon': 2.3522},
        'São Paulo': {'lat': -23.5505, 'lon': -46.6333},
        'Seoul': {'lat': 37.5665, 'lon': 126.9780},
        'Singapore': {'lat': 1.2902, 'lon': 103.8519}
    }

    @staticmethod
    def get_pollutant_concentrations(latitude, longitude):
        url = f"https://airquality.googleapis.com/v1/currentConditions:lookup?key={API}"
        request_body = {
            "location": {
                "latitude": latitude,
                "longitude": longitude
            },
            "extraComputations": [
                "POLLUTANT_CONCENTRATION"
            ],
            "languageCode": "en"
        }
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=request_body, headers=headers)

        print(f"Response Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("API Response:", data)
            records = []
            if 'pollutants' in data:
                for pollutant in data['pollutants']:
                    records.append({
                        'Pollutant': pollutant['displayName'],
                        'Concentration': pollutant['concentration']['value'],
                        'Units': pollutant['concentration']['units']
                    })
            return pd.DataFrame(records)
        else:
            print("Failed to fetch data:", response.text)
            return pd.DataFrame()

    @staticmethod
    def get_air_quality_data(latitude, longitude, start_date, end_date):
        start_datetime = datetime.strptime(start_date.split('T')[0], '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date.split('T')[0], '%Y-%m-%d')

        # API constraint
        if (end_datetime - start_datetime).days > 7:
            end_datetime = start_datetime + timedelta(days=7)

        start_time = start_datetime.isoformat() + 'Z'
        end_time = end_datetime.isoformat() + 'Z'

        url = f"https://airquality.googleapis.com/v1/history:lookup?key={API}"
        request_body = {
            "location": {"latitude": latitude, "longitude": longitude},
            "period": {"startTime": start_time, "endTime": end_time}
        }
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=request_body, headers=headers)



        if response.status_code == 200:
            data = response.json()
            records = []
            if 'hoursInfo' in data:
                for hour in data['hoursInfo']:
                    region_code = hour.get('regionCode', 'Unknown Region')
                    for index in hour.get('indexes', []):
                        records.append({
                            'Date': hour['dateTime'],
                            'Region': region_code,
                            'AQI Code': index['code'],
                            'AQI': index['aqi'],
                            'AQI Display': index['aqiDisplay'],
                            'Air Quality Category': index['category'],
                            'Dominant Pollutant': index['dominantPollutant'],
                            'Color Red': index['color'].get('red', 'N/A'),
                            'Color Green': index['color'].get('green', 'N/A'),
                            'Color Blue': index['color'].get('blue', 'N/A')
                        })
                return pd.DataFrame(records)
            else:
                print("No detailed indexes or region code found in response.")
        else:
            print("Failed to fetch data:", response.text)
        return pd.DataFrame()
