import pandas as pd
import geopandas as gpd

# Read the data
df = pd.read_csv('../../../../assets/processed.csv', sep=";")
# Make the timestamp a datetime object instead of a string
df['timestamps_UTC'] = pd.to_datetime(df['timestamps_UTC'])

# Read the weather data
weather_df = pd.read_csv('../../../../assets/weather.csv', sep=",")
# Make the timestamp a datetime object instead of a string
weather_df['date'] = pd.to_datetime(weather_df['date'])

city_locations = {
    "hasselt": [50.930965, 5.338333],
    "brussels": [50.85045, 4.34878],
    "antwerp": [51.21989, 4.40346],
    "ghent": [51.05, 3.71667],
    "charleroi": [50.41136, 4.44448],
}

# Create a geodataframe with the city locations
print("Creating a geodataframe with the city locations")
city_locations_df = pd.DataFrame.from_dict(city_locations, orient='index', columns=['lat', 'lon'])

city_locations_gdf = gpd.GeoDataFrame(
    city_locations_df, geometry=gpd.points_from_xy(city_locations_df.lon, city_locations_df.lat)
)

# Create a geodataframe with the vehicle locations
print("Creating a geodataframe with the vehicle locations")
df_gdf = gpd.GeoDataFrame(
    df, geometry=gpd.points_from_xy(df.lon, df.lat)
)

# Use the above geodataframes to create a geodataframe with the closest city for each vehicle
print("Use the above geodataframes to create a geodataframe with the closest city for each vehicle")
df_gdf['closest_city'] = df_gdf.geometry.apply(lambda x: city_locations_gdf.distance(x).idxmin())

print(df_gdf.head())
