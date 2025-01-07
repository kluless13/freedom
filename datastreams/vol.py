import requests
import time
from termcolor import cprint

BINANCE_FUTURES_24HR_URL = "https://fapi.binance.com/fapi/v1/ticker/24hr"
BINANCE_FUTURES_KLINES_URL = "https://fapi.binance.com/fapi/v1/klines"

###############################################################################
# COLOR / FLASH STYLES
###############################################################################
# Rank-based styles for the top 10
# (foreground color, background color, list of attributes)
RANK_STYLES = [
    # 1st place: White on Red, blinking + bold
    ('white', 'on_red',   ['blink', 'bold']),
    # 2nd place: White on Magenta, bold
    ('white', 'on_magenta', ['bold']),
    # 3rd place: White on_yellow
    ('white', 'on_yellow', []),
    # 4th place: White on_green
    ('white', 'on_green',  []),
    # 5th place: White on_blue
    ('white', 'on_blue',   []),
    # 6th place: White on_cyan
    ('white', 'on_cyan',   []),
    # 7th place: Grey on_white
    ('grey',  'on_white',  []),
    # 8th place: Grey on_red
    ('grey',  'on_red',    []),
    # 9th place: White on_grey
    ('white', 'on_grey',   []),
    # 10th place: Yellow on_blue
    ('yellow','on_blue',   [])
]


###############################################################################
# HELPER FUNCTIONS
###############################################################################
def fetch_all_symbols_24hr():
    """
    Fetch the 24hr stats for *all* USDT-M futures symbols from Binance.
    Returns a list of dicts. Each item includes fields like symbol, quoteVolume, etc.
    """
    resp = requests.get(BINANCE_FUTURES_24HR_URL).json()
    # Filter to only symbols that end with "USDT" to avoid BUSD or coin-margined.
    usdt_symbols_data = [item for item in resp if item["symbol"].endswith("USDT")]
    return usdt_symbols_data

def fetch_kline_quote_volume(symbol, interval, limit):
    """
    Fetch 'limit' klines for a given symbol & interval (e.g. '1m' or '1d'),
    then sum up the quoteVolume (index 7 in the returned kline array).
    """
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    data = requests.get(BINANCE_FUTURES_KLINES_URL, params=params).json()

    total_quote_vol = 0.0
    for kline in data:
        # index 7 is quoteVolume
        quote_vol = float(kline[7])
        total_quote_vol += quote_vol
    return total_quote_vol

def get_10min_volume(symbol):
    """
    Sum the last 10 one-minute klines → ~10-minute volume.
    """
    return fetch_kline_quote_volume(symbol, interval="1m", limit=10)

def get_1month_volume(symbol):
    """
    Approx sum of last 30 daily klines → ~1 month volume.
    """
    return fetch_kline_quote_volume(symbol, interval="1d", limit=30)

def get_3month_volume(symbol):
    """
    Approx sum of last 90 daily klines → ~3 months volume.
    """
    return fetch_kline_quote_volume(symbol, interval="1d", limit=90)


###############################################################################
# MAIN LOGIC
###############################################################################
def fetch_all_volumes_for_all_symbols():
    """
    1) Get all symbols + their 24h volume from /ticker/24hr
    2) For each symbol, also fetch 10min, 1mth, 3mth volumes
    3) Return a list of dicts like:
       {
         'symbol': 'BTCUSDT',
         'vol_10min': float,
         'vol_24h': float,   # from 24hr ticker
         'vol_1mth': float,
         'vol_3mth': float
       }
    """
    data_24hr = fetch_all_symbols_24hr()

    results = []
    for item in data_24hr:
        symbol = item["symbol"]
        vol_24h = float(item["quoteVolume"])  # rolling 24h quoteVolume

        # We can skip low-volume or illiquid symbols if desired, but let's keep all
        # For each symbol, fetch 3 more volumes:
        try:
            vol_10min = get_10min_volume(symbol)
            vol_1mth  = get_1month_volume(symbol)
            vol_3mth  = get_3month_volume(symbol)
        except Exception as e:
            # If any error, set volumes to 0
            cprint(f"Error fetching klines for {symbol}: {e}", 'red')
            vol_10min = 0.0
            vol_1mth  = 0.0
            vol_3mth  = 0.0

        results.append({
            "symbol": symbol,
            "vol_10min": vol_10min,
            "vol_24h":   vol_24h,
            "vol_1mth":  vol_1mth,
            "vol_3mth":  vol_3mth
        })
    return results

def print_top_10_by_24h(results_list):
    """
    Sort results_list by vol_24h descending, print the top 10 in a flashy table:
      Rank, Symbol, 10-min vol, 24h vol, 1mth vol, 3mth vol
    """
    # Sort
    sorted_list = sorted(results_list, key=lambda x: x["vol_24h"], reverse=True)

    cprint("\n=== TOP 10 USDT-M FUTURES ===", 'cyan', attrs=['bold', 'blink'])
    header = f"{'Rank':<6} {'Symbol':<10} {'10min':>14} {'24h':>18} {'1mth':>18} {'3mth':>18}"
    cprint(header, 'white', 'on_grey', attrs=['bold'])

    top_10 = sorted_list[:10]
    for i, row in enumerate(top_10, start=1):
        rank = i
        symbol = row["symbol"]
        vol10m = row["vol_10min"]
        vol24  = row["vol_24h"]
        vol1m  = row["vol_1mth"]
        vol3m  = row["vol_3mth"]

        if rank <= len(RANK_STYLES):
            fg, bg, attrs = RANK_STYLES[rank-1]
        else:
            fg, bg, attrs = ('white', None, [])

        line_str = (
            f"{rank:<6} {symbol:<10} "
            f"{vol10m:>14,.2f} "
            f"{vol24:>18,.2f} "
            f"{vol1m:>18,.2f} "
            f"{vol3m:>18,.2f}"
        )
        # Print with color style
        cprint(line_str, fg, bg, attrs=attrs)


def main():
    cprint("Fetching all volumes for all symbols...\n", 'green', attrs=['bold'])
    all_data = fetch_all_volumes_for_all_symbols()
    print_top_10_by_24h(all_data)

    # -----------------------------------------------------------------
    # If you want this to run periodically (e.g., every 10 minutes),
    # uncomment the following block:
    #
    while True:
        time.sleep(600)  # 600s = 10 minutes
        all_data = fetch_all_volumes_for_all_symbols()
        print_top_10_by_24h(all_data)

if __name__ == "__main__":
    main()
