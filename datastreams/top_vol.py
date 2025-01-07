import requests
import time
from termcolor import cprint

BINANCE_FUTURES_24HR_URL = "https://fapi.binance.com/fapi/v1/ticker/24hr"

# Define rank-based styles: for ranks 1..10
# (color, background, and attrs for termcolor)
RANK_STYLES = [
    # 1st place (rank=1): White on Red, blinking + bold
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
    # 7th place: Black on_white
    ('grey',  'on_white',  []),
    # 8th place: Grey on_red
    ('grey',  'on_red',    []),
    # 9th place: White on_grey
    ('white', 'on_grey',   []),
    # 10th place: Yellow on_blue
    ('yellow','on_blue',   [])
]

def fetch_all_symbols_by_volume():
    """
    Fetch all USDT-M futures symbols from Binance and return a list
    sorted by descending quoteVolume.
    """
    resp = requests.get(BINANCE_FUTURES_24HR_URL).json()
    # Sort by quoteVolume descending
    sorted_list = sorted(resp, key=lambda x: float(x["quoteVolume"]), reverse=True)
    return sorted_list

def print_top_10(sorted_list):
    """
    Print the top 10 symbols with big, colorful, flashy highlights.
    """
    cprint("=== TOP 10 BINANCE FUTURES (USDT-M) BY 24H VOLUME ===", 'cyan', attrs=['bold', 'blink'])
    header_str = f"{'Rank':<6} {'Symbol':<12} {'24h QuoteVolume (USDT)':>26}"
    cprint(header_str, 'white', 'on_grey', attrs=['bold'])

    for i, item in enumerate(sorted_list[:10], start=1):
        rank = i
        symbol = item["symbol"]
        qv = float(item["quoteVolume"])

        # Choose style based on rank
        if rank <= len(RANK_STYLES):
            fg_color, bg_color, style_attrs = RANK_STYLES[rank - 1]
        else:
            # Fallback if we had more than 10, not likely for top 10
            fg_color, bg_color, style_attrs = ('white', None, [])

        line_str = f"{rank:<6} {symbol:<12} {qv:>26,.2f}"

        # Print with cprint using the chosen style
        cprint(line_str, fg_color, bg_color, attrs=style_attrs)


def main():
    # One-time fetch & display
    sorted_symbols = fetch_all_symbols_by_volume()
    print_top_10(sorted_symbols)

    # -----------------------------------------------------------------
    # If you want this to run periodically (e.g., every 10 minutes),
    # uncomment the following block:
    #
    while True:
        time.sleep(600)  # 600s = 10 minutes
        sorted_symbols = fetch_all_symbols_by_volume()
        print_top_10(sorted_symbols)

if __name__ == "__main__":
    main()
