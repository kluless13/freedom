import os
import pandas as pd
import requests
import numpy as np
from datetime import datetime
from typing import Literal
 
DataType = Literal["candles", "funding", "liquidations", "open_interest"]
 
BASE_URL = "https://moon-crypto-data.s3.eu-central-1.amazonaws.com"
CACHE_FOLDER = ".cache/crypto-data"
 
def _resample(df: pd.DataFrame, timeframe: str, data_type: DataType):
    df = df.reset_index()
 
    df["datetime"] = pd.to_datetime(df["datetime"], unit="ns")
    df.set_index("datetime", inplace=True)
    df.index = df.index.tz_localize("UTC")
 
    aggr = {}
    floats = []
    ints = []
 
    if data_type == "candles":
        aggr = {
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
            "trades": "sum",
        }
        floats = ["open", "high", "low", "close", "volume"]
        ints = ["trades"]
    elif data_type == "funding":
        aggr = {
            "index_price": "last",
            "funding_rate": "last",
            "next_funding_time": "last",
            "mark_price": "last",
            "predicted_rate": "last",
        }
        floats = ["index_price", "funding_rate", "mark_price", "predicted_rate"]
    elif data_type == "liquidations":
        aggr = {
            "short_liq_volume": "sum",
            "long_liq_volume": "sum",
            "short_liqs": "sum",
            "long_liqs": "sum",
            "liq_price": "mean",
        }
        floats = ["short_liq_volume", "long_liq_volume", "liq_price"]
        ints = ["short_liqs", "long_liqs"]
    elif data_type == "open_interest":
        aggr = {
            "open_interest": "last",
        }
        floats = ["open_interest"]
 
    for col in floats:
        df[col] = df[col].astype(np.float64)
    for col in ints:
        df[col] = df[col].astype(np.int64)
 
    df = df.resample(timeframe).agg(aggr).bfill().ffill()
 
    return df
 
def _get_file_path(data_type: DataType, symbol: str):
    return f"{CACHE_FOLDER}/{data_type}/{symbol}.parquet"
 
def _check_cache(data_type: DataType, symbol: str):
    filepath = _get_file_path(data_type, symbol)
    if os.path.exists(filepath):
        return pd.read_parquet(filepath)
    return None
 
def get_data(
    data_type: DataType,
    symbol: str,
    timeframe: str,
    since: datetime | None = None,
    until: datetime | None = None,
):
    cached = _check_cache(data_type, symbol)
    if cached is not None:
        if since is not None and until is not None:
            return _resample(cached, timeframe, data_type).loc[since:until]
        return _resample(cached, timeframe, data_type)
 
    url = f"{BASE_URL}/{data_type}/{symbol}.parquet"
 
    print("Downloading data from", url)
    df = pd.read_parquet(url)
    file_path = _get_file_path(data_type, symbol)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
 
    print("Saving data to", file_path)
    df.to_parquet(file_path)
 
    if since is not None and until is not None:
        return _resample(df, timeframe, data_type).loc[since:until]
    return _resample(df, timeframe, data_type)
 
def get_available_symbols(verbose=False) -> dict[DataType, list[str]]:
    response = requests.get(f"{BASE_URL}/coverage.json")
    coverage = response.json()
 
    if verbose:
        for data_type, symbols in coverage.items():
            print(f"{data_type}:")
            print("\t" + "\n\t".join(symbols))
 
    return coverage
 
available = get_available_symbols(verbose=True)
print(
     get_data(
         "candles",
         "ETH-USDT-PERP",
         "5min",
         datetime.fromisoformat("2024-01-01T00:00:00Z"),
         datetime.fromisoformat("2024-12-31T23:59:59Z"),
     )
    )