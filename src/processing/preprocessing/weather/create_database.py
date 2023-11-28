import time
import pandas
import numpy as np
from tqdm import tqdm


# vectorized haversine function
def haversine(lat1, lon1, lat2, lon2, to_radians=True, earth_radius=6371):
    """
    slightly modified version: of http://stackoverflow.com/a/29546836/2901002

    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees or in radians)

    All (lat, lon) coordinates must have numeric dtypes and be of equal length.
    """
    if to_radians:
        lat1, lon1, lat2, lon2 = np.radians([lat1, lon1, lat2, lon2])

    a = np.sin((lat2 - lat1) / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2.0) ** 2

    return earth_radius * 2 * np.arcsin(np.sqrt(a))  # return the value in km since the earth_radius is in km


cities = {
    "Hasselt": {
        "latitude": 50.930965,
        "longitude": 5.338333,
        "data": "hourly_data_hasselt.csv",
    },
    "Brussels": {
        "latitude": 50.85045,
        "longitude": 4.34878,
        "data": "hourly_data_brussels.csv",
    },
    "Antwerp": {
        "latitude": 51.21989,
        "longitude": 4.40346,
        "data": "hourly_data_antwerp.csv",
    },
    "Ghent": {
        "latitude": 51.05,
        "longitude": 3.71667,
        "data": "hourly_data_ghent.csv",
    },
    "Charleroi": {
        "latitude": 50.41136,
        "longitude": 4.44448,
        "data": "hourly_data_charleroi.csv",
    },
}

# Prepare a dataframe with the latitude and longitude of each city
cities_df = pandas.DataFrame.from_dict(cities, orient='index', columns=['latitude', 'longitude'])

# Recover the pre-processed data
processed_df = pandas.read_csv("../assets/processed.csv", sep=";")
processed_df['timestamps_UTC'] = pandas.to_datetime(processed_df['timestamps_UTC'])

print(cities_df.head())

# Prepare the weather data
with open("../assets/weather.csv", "w") as f:
    for city in cities:
        # Read the weather data
        cities[city]['data'] = pandas.read_csv('../assets/weather/' + cities[city]['data'], sep=",")
        # Make the timestamp a datetime object instead of a string
        cities[city]['data']['date'] = pandas.to_datetime(cities[city]['data']['date'])

    f.write("mapped_veh_id;timestamps_UTC;temperature;humidity\n")

    # Use the weather data to add the weather information to the data
    for index, row in tqdm(processed_df[['mapped_veh_id', 'timestamps_UTC', 'lat', 'lon']].iloc[:].iterrows(), total=len(processed_df)):
        # Use the row location information to decide on which city is the closest
        location = [row.lat, row.lon]

        # Compute distances to all cities using the haversine function
        distances = [*haversine(
            # multiply the number of rows by the number of cities to have a matrix of distances
            np.ones(len(cities_df)) * location[0],
            np.ones(len(cities_df)) * location[1],
            cities_df['latitude'],
            cities_df['longitude']
        )]

        # Keep the closest city
        closest_city = {
            # Recover the name of the city from the cities_df dataframe
            "name": cities_df.iloc[np.argmin(distances)].name,
            "distance": np.min(distances),
        }

        data = cities[closest_city['name']]['data']

        # Select the closest timestamp in the weather data
        closest_timestamp = data.iloc[(data['date'] - row.timestamps_UTC).abs().argsort()[:1]]

        # Add a row to the weather dataframe
        f.write(f"{row.mapped_veh_id};{row.timestamps_UTC};{closest_timestamp['temperature'].values[0]};{closest_timestamp['relative_humidity'].values[0]}\n")
