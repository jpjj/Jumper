import time
from geopy.geocoders import Nominatim
from geopy import distance
import pandas as pd
import streamlit as st


def add_geocodes(data):
    for i, row in data.iterrows():
        if pd.isna(row["Lat"]) or pd.isna(row["Lat"]):
            st.write(f"Finding missing geocode for address {row['Address']}...")
            geocode = geocode_address(row["Address"])
            data.at[i, "Lat"] = geocode[0][0]
            data.at[i, "Lon"] = geocode[0][1]


def geocode_address(address):
    geolocator = Nominatim(user_agent="Simon_TWTSP")
    geocode = []
    location = None
    while not location:
        time.sleep(1)
        try:
            location = geolocator.geocode(address)
        except Exception as e:
            st.write(f"Error: {e}, retrying...")
    if location:
        geocode.append((location.latitude, location.longitude))
    else:
        raise ValueError(f"Could not find geocode for address {address}")
    return geocode


def get_duration(origin, destination, speed, fix_time):
    """
    speed as km/h
    fix_time as minutes
    """
    result = int(distance.distance(origin, destination).km / speed * 3600)
    if result > 0:
        return result + fix_time * 60
    return 0


def fetch_distance_matrix(geocodes, speed, fix_time):
    """
    speed as km/h
    """
    origins = geocodes
    destinations = geocodes
    matrix = [
        [0 for _ in range(len(origins))] for _ in range(len(destinations))
    ]
    for i, origin in enumerate(origins):
        for j, destination in enumerate(destinations):
            if origin != (None, None) and destination != (None, None):
                matrix[i][j] = get_duration(
                    origin, destination, speed, fix_time
                )
            else:
                matrix[i][j] = float("inf")
    return matrix
