# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 17:16:35 2024

@author: kbons
"""


import requests
import geopandas as gpd
import pandas as pd
from shapely.geometry import shape
from datetime import datetime
import os

# Function to connect to OTP and get isochrones
def get_isochrone(base_url, lat, lon, modes, date_time, cutoff_minutes, max_walk_distance=None):
    params = {
        'fromPlace': f'{lat},{lon}',
        'mode': ','.join(modes),
        'date': date_time.strftime('%Y-%m-%d'),
        'time': date_time.strftime('%H:%M:%S'),
        'cutoffSec': [m * 60 for m in cutoff_minutes]
    }
    
    if max_walk_distance:
        params['maxWalkDistance'] = max_walk_distance

    response = requests.get(f'{base_url}/otp/routers/default/isochrone', params=params)
    
    if response.status_code == 200:
        return response.json().get('features', [])
    else:
        print(f"Error {response.status_code}: {response.text}")
        return []

# Set base URL for OTP API
otp_base_url = 'http://localhost:8080'

# Load the grid center data
centres = pd.read_csv('C:/Users/kbons/accessibility/INSEE/centers.csv')#, sep=';')

# Function to process isochrones and save to file
def process_and_save_isochrone(features, directory, filename, id_column):
    if features:
        try:
            # Attempt to create GeoDataFrame and extract properties
            gdf = gpd.GeoDataFrame.from_features(features)
            if 'properties' in gdf.columns:
                gdf['minutes'] = gdf['properties'].apply(lambda x: x.get('time', 0) / 60)
            else:
                # Fallback if 'properties' is missing
                print(f"No 'properties' found for ID: {id_column}. Using default values.")
                gdf['minutes'] = 0  # Or any other default/fallback logic you prefer
            
            os.makedirs(directory, exist_ok=True)
            gdf.to_file(f'{directory}/{filename}_{id_column}.shp')
        except KeyError as e:
            print(f"KeyError: {e} for ID: {id_column}. Full feature: {features}")

# Transit Isochrones
for i, row in centres.iterrows():
    features = get_isochrone(
        base_url=otp_base_url,
        lat=row['Y'],
        lon=row['X'],
        modes=['WALK', 'TRANSIT'],
        date_time=datetime(2024, 8, 27, 8, 30),
        cutoff_minutes=[10, 20, 30, 40, 50, 60],
        max_walk_distance=1000
    )
    process_and_save_isochrone(features, './transit_insee', 't', row["ID"])

# Bicycle Isochrones
for i, row in centres.iterrows():
    features = get_isochrone(
        base_url=otp_base_url,
        lat=row['Y'],
        lon=row['X'],
        modes=['BICYCLE'],
        date_time=datetime(2024, 8, 27, 8, 30),
        cutoff_minutes=[10, 20, 30, 40, 50, 60]
    )
    process_and_save_isochrone(features, './bike_insee', 'c', row["ID"])

# Car Isochrones (First Set)
for i, row in centres.iterrows():
    features = get_isochrone(
        base_url=otp_base_url,
        lat=row['Y'],
        lon=row['X'],
        modes=['CAR'],
        date_time=datetime(2024, 8, 27, 8, 30),
        cutoff_minutes=[5, 10, 15, 20, 25, 30]
    )
    if features:
        try:
            gdf = gpd.GeoDataFrame.from_features(features)
            if 'properties' in gdf.columns:
                gdf['minutes'] = 2 * gdf['properties'].apply(lambda x: x.get('time', 0) / 60)
            else:
                print(f"No 'properties' found for ID: {row['ID']}. Using default values.")
                gdf['minutes'] = 0  # Default fallback value

            os.makedirs('./car_a_insee', exist_ok=True)
            gdf.to_file(f'./car_a_insee/c_{row["ID"]}.shp')
        except KeyError as e:
            print(f"KeyError: {e} for ID: {row['ID']}. Full feature: {features}")

# Car Isochrones (Second Set)
for i, row in centres.iterrows():
    features = get_isochrone(
        base_url=otp_base_url,
        lat=row['Y'],
        lon=row['X'],
        modes=['CAR'],
        date_time=datetime(2024, 8, 27, 8, 30),
        cutoff_minutes=[7, 14, 21, 28, 35, 42]
    )
    if features:
        try:
            gdf = gpd.GeoDataFrame.from_features(features)
            if 'properties' in gdf.columns:
                gdf['minutes'] = gdf['properties'].apply(lambda x: x.get('time', 0) / 60 / 0.7)
            else:
                print(f"No 'properties' found for ID: {row['ID']}. Using default values.")
                gdf['minutes'] = 0  # Default fallback value

            os.makedirs('./car_b_insee', exist_ok=True)
            gdf.to_file(f'./car_b_insee/c_{row["ID"]}.shp')
        except KeyError as e:
            print(f"KeyError: {e} for ID: {row['ID']}. Full feature: {features}")
