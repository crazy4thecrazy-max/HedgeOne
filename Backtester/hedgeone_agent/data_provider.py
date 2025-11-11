import pandas as pd
from .config import fyers # Import the global fyers client

def get_historical_data(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """ Fetches historical data from Fyers and formats it for Backtrader. """
    print(f"Fetching data for {symbol} from {start_date} to {end_date}...")
    try:
        historical_data = {
            "symbol": symbol, "resolution": "D", "date_format": "1",
            "range_from": start_date, "range_to": end_date, "cont_flag": "1"
        }
        response = fyers.history(data=historical_data)
        
        if not response:
            print(f"No response from Fyers for {symbol}.")
            return pd.DataFrame()

        if response.get("s") != "ok":
            print(f"Error fetching data for {symbol}: {response.get('message')}")
            return pd.DataFrame()
        
        # --- 1. GET THE LIST OF CANDLES ---
        candles = response.get('candles', [])
        
        # --- 2. CHECK IF THE LIST IS EMPTY (MOVED UP) ---
        if not candles:
            print(f"No candle data returned for {symbol}.")
            return pd.DataFrame()

        # --- 3. THIS IS THE CRITICAL FIX ---
        # Assign column names as defined by Fyers API v3 response
        df = pd.DataFrame(
            candles, 
            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
        )
        # --- END OF FIX ---

        # The rest of your code will now work correctly
        if 'timestamp' in df.columns:
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
        elif 'date' in df.columns:
            df['datetime'] = pd.to_datetime(df['date'])
        else:
            # This 'else' block will likely not be needed anymore, 
            # but is fine as a fallback.
            df['datetime'] = pd.to_datetime(df.index)

        df.set_index('datetime', inplace=True)

        # Best-effort rename (fallbacks)
        colmap = {}
        if 'open' in df.columns: colmap['open'] = 'Open'
        if 'high' in df.columns: colmap['high'] = 'High'
        if 'low' in df.columns: colmap['low'] = 'Low'
        if 'close' in df.columns: colmap['close'] = 'Close'
        if 'volume' in df.columns: colmap['volume'] = 'Volume'
        if colmap:
            df.rename(columns=colmap, inplace=True)

        # Ensure we only return OHLCV
        wanted = ['Open', 'High', 'Low', 'Close', 'Volume']
        available = [c for c in wanted if c in df.columns]
        df = df[available].sort_index()
        
        # This check is now more accurate.
        if 'Open' not in df.columns:
             print(f"Data fetched for {symbol}, but 'Open' column is missing after processing.")
             return pd.DataFrame()
             
        print(f"Successfully fetched {len(df)} rows for {symbol}.")
        return df
    except Exception as e:
        print(f"Exception in get_historical_data: {e}")
        return pd.DataFrame()