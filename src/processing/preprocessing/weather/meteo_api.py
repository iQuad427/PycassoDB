import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry

# Set up the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
open_meteo = openmeteo_requests.Client(session=retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://archive-api.open-meteo.com/v1/archive"

coordinates = {
    "Hasselt": [50.930965, 5.338333],
    "Brussels": [50.85045, 4.34878],
    "Antwerp": [51.21989, 4.40346],
    "Ghent": [51.05, 3.71667],
    "Charleroi": [50.41136, 4.44448],
}

for city, coordinate in coordinates.items():
    params = {
        # Brussels coordinates
        "latitude": coordinate[0],
        "longitude": coordinate[1],
        "hourly": ["temperature_2m", "relative_humidity_2m"],
        "start_date": "2022-08-22",
        "end_date": "2023-09-13"
    }
    responses = open_meteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    print(f"Coordinates {response.Latitude()}°E {response.Longitude()}°N")
    print(f"Elevation {response.Elevation()} m asl")
    print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()

    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s"),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s"),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        ),
        "temperature": hourly_temperature_2m,
        "relative_humidity": hourly_relative_humidity_2m
    }

    hourly_dataframe = pd.DataFrame(data=hourly_data)
    print(hourly_dataframe)

    # Create a dataframe with hourly data and save it to a csv file
    hourly_dataframe.to_csv(f"./assets/weather/hourly_data_{city.lower()}.csv", index=False)
