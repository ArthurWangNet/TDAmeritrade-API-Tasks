def get_fundamental_endpoint(symbol):
    return r'https://api.tdameritrade.com/v1/instruments'

def get_price_history_endpoint(symbol):
    return r'https://api.tdameritrade.com/v1/marketdata/{}/pricehistory'.format(symbol)

