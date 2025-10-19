from fyers_apiv3 import fyersModel
# DO NOT FORGET TO INSTALL THIS LIBRARY
# `pip install fyers_apiv3`

client_id = "YYYYYYY-100"
access_token = "XXXXXXXXXXXXX"

# Initialize the FyersModel instance with your client_id, access_token, and enable async mode
fyers = fyersModel.FyersModel(client_id=client_id, token=access_token,is_async=False, log_path="")

# state = {
#         'name': '',
#         'symbol': '',
#         'expiryData': [],
#         'expiry': ''
#         'option_data': [],
#         'future_data': {}
#         }

def getExpiryList(symbol):
    # returns a list of expiries with following structure
    # [
    #   {
    #     "date": "25-04-2024",
    #     "expiry": "1714039200"
    #   },
    #   {
    #     "date": "30-05-2024",
    #     "expiry": "1717063200"
    #   },
    #   {
    #     "date": "27-06-2024",
    #     "expiry": "1719482400"
    #   }
    # ]

    response = fyers.optionchain(data={'symbol':symbol})
    if response['code']==200:
        return response['data']['expiryData']
    return response


def getOptionData(symbol, expiry=''):    # `expiry` is timestamp in seconds ('expiry' value from getExpiryList; '' for current expiry
    # returns a list of option chain data with following structure
    # [
    #  {
    #     "ask": 34.9,
    #     "bid": 34.35,
    #     "fyToken": "1011240425139431",
    #     "ltp": 34.8,
    #     "ltpch": 2.7,
    #     "ltpchp": 8.41,
    #     "oi": 99575,
    #     "oich": -3325,
    #     "oichp": -3.23,
    #     "option_type": "CE",
    #     "prev_oi": 102900,
    #     "strike_price": 3860,
    #     "symbol": "NSE:TCS24APR3860CE",
    #     "volume": 202650
    #   },
    # ]

    response = fyers.optionchain(data={'symbol':symbol, 'timestamp': expiry})
    if response['code']==200:
        return response['data']['optionsChain'][1:]     # [0] gives equity data
    return response

def getEquityData(symbol, expiry=''):
    # return equity data with following structure
    # {
    #     "ask": 3880.15,
    #     "bid": 3880.05,
    #     "description": "TATA CONSULTANCY SERV LT",
    #     "ex_symbol": "TCS",
    #     "exchange": "NSE",
    #     "fp": 3876.65,
    #     "fpch": 14.2,
    #     "fpchp": 0.37,
    #     "fyToken": "101000000011536",
    #     "ltp": 3880.15,
    #     "ltpch": 15.55,
    #     "ltpchp": 0.4,
    #     "option_type": "",
    #     "strike_price": -1,
    #     "symbol": "NSE:TCS-EQ"
    # }

    response = fyers.optionchain(data={'symbol':symbol, 'expiry': expiry})
    if response['code']==200:
        return response['data']['optionsChain'][0]     # [0] gives equity data
    return response
