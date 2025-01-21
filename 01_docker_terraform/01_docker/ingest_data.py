#!usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse
from time import time
from typing import Iterator, Optional

import pandas as pd
from sqlalchemy import create_engine

class ParquetChunker:
    def __init__(self, filepath: str, chunksize: int):
        self.filepath = filepath
        self.chunksize = chunksize
        self.total_rows = pd.read_parquet(filepath, columns=[]).shape[0]
        self.current_row = 0
    
    def __iter__(self) -> Iterator[pd.DataFrame]:
        return self
    
    def __next__(self) -> pd.DataFrame:
        if self.current_row >= self.total_rows:
            raise StopIteration
            
        chunk = pd.read_parquet(
            self.filepath,
            rows=slice(self.current_row, self.current_row + self.chunksize)
        )
        
        self.current_row += self.chunksize
        return chunk

def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    url = params.url

    parquet_name = "output.parquet"
    csv_name = "output.csv"

    os.system(f"wget {url} -O {parquet_name}")

    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

    # Workaround
    df = pd.read_parquet(parquet_name)
    df.to_csv(csv_name, index=False)

    df_iter = pd.read_csv(csv_name, iterator=True, chunksize=100000)
    df = next(df_iter)
    df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
    df['tpep_dropoff_datetime'] = pd.to_datetime(df['tpep_dropoff_datetime'])
    df.head(0).to_sql(table_name, con=engine, if_exists='replace')

    df.to_sql(table_name, con=engine, if_exists='append')

    while True:
        try:
            t_start = time()
            df = next(df_iter)
            df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
            df['tpep_dropoff_datetime'] = pd.to_datetime(df['tpep_dropoff_datetime'])
            df.to_sql(table_name, con=engine, if_exists='append')

            print(f"Inserted {len(df)} rows in {time() - t_start} seconds")
        except StopIteration:
            break

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ingest CSV data to Postgres')

    parser.add_argument('--user', type=str, help='Postgres user name')
    parser.add_argument('--password', type=str, help='Postgres password')
    parser.add_argument('--host', type=str, help='Postgres host')
    parser.add_argument('--port', type=int, help='Postgres port')
    parser.add_argument('--db', type=str, help='Postgres database name')
    parser.add_argument('--table_name', type=str, help='Postgres table name')
    parser.add_argument('--url', type=str, help='URL of the CSV file')

    args = parser.parse_args()

    main(args)