import os
import json
import pandas as pd
import gspread
from dotenv import load_dotenv
from gspread_dataframe import get_as_dataframe
from oauth2client.service_account import ServiceAccountCredentials

# Load environment variables from .env
load_dotenv()

def load_data_from_gsheets():

    # Read the JSON string from .env and parse it
    credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if not credentials_json:
        raise ValueError("Missing GOOGLE_CREDENTIALS_JSON in environment.")

    # Convert JSON string to dictionary
    credentials_dict = json.loads(credentials_json)

    # --- Auth & Setup ---
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    client = gspread.authorize(credentials)
    spreadsheet = client.open("disease_stats")

    # --- Read Sheets ---
    laos_data = get_as_dataframe(spreadsheet.worksheet("laos_data")).dropna(how='all')
    laos_regions = get_as_dataframe(spreadsheet.worksheet("laos_regions")).dropna(how='all')
    weather_df = get_as_dataframe(spreadsheet.worksheet("weather_data")).dropna(how='all')
    news_df = get_as_dataframe(spreadsheet.worksheet("news_data")).dropna(how='all')
    neighbours_data = get_as_dataframe(spreadsheet.worksheet("neighbours_data")).dropna(how='all')

    # --- Clean Headers ---
    for df in [laos_data, laos_regions, weather_df, news_df, neighbours_data]:
        df.columns = df.columns.str.strip()

    # --- Convert Date Columns ---
    laos_data['reported_date'] = pd.to_datetime(laos_data['reported_date'], errors='coerce')
    news_df['date'] = pd.to_datetime(news_df['date'], errors='coerce')
    weather_df['timestamp'] = pd.to_datetime(weather_df['timestamp'], errors='coerce', dayfirst=True)
    weather_df['sunset'] = pd.to_datetime(weather_df['sunset'], errors='coerce', dayfirst=True)
    weather_df['sunrise'] = pd.to_datetime(weather_df['sunrise'], errors='coerce', dayfirst=True)

    # --- Merge Region Info ---
    laos_df = pd.merge(
        laos_data,
        laos_regions.rename(columns={'capital': 'location'}),
        on='location',
        how='left'
    )

    return laos_df, laos_regions, weather_df, news_df, neighbours_data

