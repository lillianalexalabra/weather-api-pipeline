import os
import requests
import time
import pandas as pd

API_URL = "https://api.weatherapi.com/v1/current.json"

ZIP_CODES = [
    "90045",  # Los Angeles, CA
    "10001",  # New York, NY
    "60601",  # Chicago, IL
    "98101",  # Seattle, WA
    "33101",  # Miami, FL
    "77001",  # Houston, TX
    "85001",  # Phoenix, AZ
    "19101",  # Philadelphia, PA
    "78201",  # San Antonio, TX
    "75201",  # Dallas, TX
    "95101",  # San Jose, CA
    "78701",  # Austin, TX
    "32099",  # Jacksonville, FL
    "28201",  # Charlotte, NC
    "43085",  # Columbus, OH
    "76101",  # Fort Worth, TX
    "46201",  # Indianapolis, IN
    "94601",  # Oakland, CA
    "37201",  # Nashville, TN
    "73101",  # Oklahoma City, OK
]


def fetch_weather(api_key, zip_codes):
    results = []
    for zip_code in zip_codes:
        response = requests.get(API_URL, params={"key": api_key, "q": zip_code})
        data = response.json()
        results.append({
            "zip_code": zip_code,
            "city": data["location"]["name"],
            "region": data["location"]["region"],
            "temp_f": data["current"]["temp_f"],
            "condition": data["current"]["condition"]["text"],
        })
        print(f"{zip_code} - {data['location']['name']}: {data['current']['temp_f']}°F")
        time.sleep(1)
    return results


def main():
    api_key = os.environ["WEATHER_API_KEY"]
    results = fetch_weather(api_key, ZIP_CODES)
    df = pd.DataFrame(results)
    print(df.to_string(index=False))
    print(f"\nShape: {df.shape[0]} rows x {df.shape[1]} columns")
    df.to_csv("weather_data.csv", index=False)
    print("Saved to weather_data.csv")


if __name__ == "__main__":
    main()
