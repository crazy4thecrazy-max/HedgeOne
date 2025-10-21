import sys
from fyers_apiv3 import fyersModel
from config import CLIENT_ID, ACCESS_TOKEN

try:
    fyers = fyersModel.FyersModel(client_id=CLIENT_ID, token=ACCESS_TOKEN, is_async=False)
    test_response = fyers.get_profile()
    
    if test_response.get('s') != 'ok':
        print(f"Fyers API Error: {test_response.get('message')}")
        sys.stdout.flush()
        exit()
        
    print("Fyers connection successful.")
    sys.stdout.flush()
    
except Exception as e:
    print(f"Error initializing Fyers model: {e}")
    sys.stdout.flush()
    exit()