import pandas as pd
import os
from tqdm import tqdm

# Use the hourly file in ../../../../assets/weather/ to create a dataframe containing the weather data
path = "../../../../assets/weather/"

weather_df = pd.DataFrame(
    columns=["city", "date", "temperature", "relative_humidity"]
)

# 1. iterate over the file name in the folder
for file_name in tqdm(os.listdir(path), desc="Reading weather data"):
    # the file name should contain "hourly_data_"
    if "hourly_data_" not in file_name:
        continue

    # 2. read the file
    df = pd.read_csv(path + file_name, sep=",")

    # 3. make the timestamp a datetime object instead of a string
    df['date'] = pd.to_datetime(df['date'])

    # 4. add the weather data to the dataframe
    # 4.1. get the city name from the file name
    city = file_name.replace("hourly_data_", "").replace(".csv", "")

    # 4.2 create a dataframe with the file information
    df["city"] = city

    print(df.head())

    # Print NA
    print(df.isna().sum())

    # 4.3. add the data to the dataframe
    weather_df = pd.concat([weather_df, df], ignore_index=True)

# 5. save the dataframe to ../../../../assets/weather.csv
weather_df.to_csv("../../../../assets/weather.csv", index=False)
