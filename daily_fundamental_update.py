from datetime import date
from os import remove
import td_config as td
import pandas as pd
import requests
import logging
import urls
from utilities import progressBar
import datetime
import os
import time

def get_fundamental_update(symbol):
    time.sleep(0.5)
    #Define payload
    payload = {
            'apikey' : td.api_key_fundamental,
            'symbol': symbol,
            'projection':'fundamental',
    }

    try:
        td_response = requests.get(url=urls.get_fundamental_endpoint(), params=payload)
        content = td_response.json()
        content_dict = content[symbol]['fundamental']
        return pd.DataFrame(content.dict, index=[0])
    except Exception as ex:
        return ex


if __name__ == '__main__':
    today = datetime.datetime.now().strftime('%Y-%m-%d')

    logging.basicConfig(filename=td.REPORTS_DATA_PATH + today +'_fundamental.log', level=logging.DEBUG )
    
    stock_list = list(pd.read_csv(td.REFERENCES_DATA_PATH + 'us_exchanges_instruments.csv')['symbol'])
    
    all_fundamental = pd.DataFrame([])
    
    failed_list = []

    for i in range(4):
        print('This is {} try.'.format(i))
        for symbol in progressBar(stock_list, prefix='Progress:', suffix='Complete', length= 50):
            df = get_fundamental_update(symbol)
            if isinstance(df, pd.DataFrame):
                all_fundamental = all_fundamental.append(df)
                stock_list.remove(symbol)
                logging.info(symbol + ' Completed')
            else:
                logging.warning(symbol +' Failed because' + df)
    

    #Now after trying for 4 times, we could write the result to file.
    all_fundamental.to_csv(td.FUNDAMENTAL_DATA_PATH + today +'.csv')
    with open(td.REPORTS_DATA_PATH + today + '_fundamental_failed_list.txt') as f:
        for symbol in stock_list:
            f.write("%s\n" %symbol)
    f.close()
    


