
import pandas as pd
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
from time import sleep
import re
import time
import requests
from datetime import datetime, timedelta
import re
from urllib.parse import urljoin, urlparse
import time
from typing import List, Dict, Optional


# Initialize geocoder
geolocator = Nominatim(user_agent="location_lookup")


def load_data():
    disease_data = pd.read_excel("data/dashboard_data.xlsx", sheet_name="dummy")
    disease_codes = pd.read_excel("data/dashboard_data.xlsx", sheet_name="disease name")
    location = pd.read_excel("data/dashboard_data.xlsx", sheet_name="lao province")

    disease_data = disease_data.dropna()
    disease_data = pd.merge(disease_data, location, left_on="location", right_on="Capital")

    #columns to drop
    invalid_names = [None, '', 'no', '0', 0]
    cols_to_drop = [col for col in disease_data.columns if (
            (col in invalid_names) or
            (isinstance(col, str) and col.strip().lower().startswith('unnamed'))
    )]
    disease_data = disease_data.drop(columns=cols_to_drop)

    #update column naming for consistency
    disease_data.columns = disease_data.columns.str.lower().str.strip()
    disease_data['province'] = disease_data['province'].str.replace(
        r'\bprovince\b', '', case=False, regex=True
    ).str.strip().str.replace(r'\s+', ' ', regex=True)

    #fix datatype
    disease_data['reported date'] = pd.to_datetime(disease_data['reported date'])

    #add location coordinates
    results = []
    for loc in disease_data['location'].unique():
        results.append(get_location_info(loc))
        time.sleep(1)  # Important to avoid being blocked

    lookup = dict(zip(disease_data['location'].unique(), results))
    disease_data = disease_data.assign(
        latitude=disease_data['location'].map(lambda x: lookup[x]['latitude']),
        longitude=disease_data['location'].map(lambda x: lookup[x]['longitude'])
    )

    return disease_data



def load_neighbouring_stats_data():
    raw_df = pd.read_csv("data/neighbours_data.csv", header=None)
    data = raw_df[0].str.split(',', expand=True)
    data.columns = ["Year", "Semester", "Region", "Country", "Disease",
                    "Category", "Occurrence Code", "Disease status", "Unknown1", "Unknown2"]
    data = data.dropna(subset=["Category", "Occurrence Code", "Disease status"])
    data = data.drop(['Unknown1', 'Unknown2'], axis=1)
    data = data[data['Category'].isin(['Wild', 'Domestic'])]
    data['Disease'] = data['Disease'].apply(clean_disease_column)
    return data



def clean_disease_column(value):
    value = value.replace('"', '')
    value = re.sub(r'\s*\(.*?\)', '', value)
    return value.strip()



def format_kpi_value(kpi_value, decimals=1, prefix="$"):
    if kpi_value >= 1e6:
        return f"{prefix}{kpi_value / 1e6:.{decimals}f} M"
    elif kpi_value >= 1e3:
        return f"{prefix}{kpi_value / 1e3:.{decimals}f} K"
    else:
        return f"{prefix}{kpi_value:.2f}"



def get_location_info(place):
    try:
        # Add ", Laos" to help with disambiguation
        location = geolocator.geocode(f"{place}, Laos", exactly_one=True)
        if location:
            return {
                'latitude': location.latitude,
                'longitude': location.longitude
            }
    except:
        pass
    return {'latitude': None, 'longitude': None}



def get_laos_regions_dict(data):
    data = data.dropna(subset=['latitude', 'longitude'])

    # Drop duplicates to avoid repeating the same province
    unique_provinces = data[['province', 'latitude', 'longitude', 'capital']].drop_duplicates()

    # Build the dictionary
    laos_regions = {
        row['province']: {
            'lat': row['latitude'],
            'lon': row['longitude'],
            'capital': row['capital']
        }
        for _, row in unique_provinces.iterrows()
    }

    return laos_regions

