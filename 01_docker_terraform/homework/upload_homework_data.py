#!usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from time import time

import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(f'postgresql://postgres:postgres@localhost:5433/ny_taxi')

raw_data = {
    "taxi": {
        "url": "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-10.csv.gz",
        "csv_path": "taxi.csv",
        "table_name": "green_taxi_data",
    },
    "zones": {
        "url": "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv",
        "csv_path": "zones.csv",
        "table_name": "zones",
    }
}

# Zones data
os.system(f"wget {raw_data['zones']['url']} -O {raw_data['zones']['csv_path']}")
df = pd.read_csv(raw_data['zones']['csv_path'])
df.to_sql(raw_data['zones']['table_name'], con=engine, if_exists='replace')

# Green taxi data
os.system(f"wget {raw_data['taxi']['url']} -O {raw_data['taxi']['csv_path']}.gz")
os.system(f"gzip -d -f {raw_data['taxi']['csv_path']}.gz")
df_iter = pd.read_csv(raw_data['taxi']['csv_path'], iterator=True, chunksize=100000)

# Create table
df = next(df_iter)
df['lpep_pickup_datetime'] = pd.to_datetime(df['lpep_pickup_datetime'])
df['lpep_dropoff_datetime'] = pd.to_datetime(df['lpep_dropoff_datetime'])
df.head(0).to_sql(raw_data['taxi']['table_name'], con=engine, if_exists='replace')

# Insert data
while True:
    try:
        t_start = time()
        
        df['lpep_pickup_datetime'] = pd.to_datetime(df['lpep_pickup_datetime'])
        df['lpep_dropoff_datetime'] = pd.to_datetime(df['lpep_dropoff_datetime'])
        df.to_sql(raw_data['taxi']['table_name'], con=engine, if_exists='append')
        print(f"Inserted {len(df)} rows in {time() - t_start:3f} seconds")
        
        df = next(df_iter)
        
    except StopIteration:
        break