import datetime
from datetime import timedelta, date
import pandas as pd
import requests
import json
import time
import logging
import td_config as td
import urls
from utilties import progressBar, get_symbol_list
import api_keys

def get_minute_bar(symbol, start_time, end_time):
    #TD API limits request to 120 per second. That is maxium 2 request per second, so sleep here.
    time.sleep(0.5)

    payload = {
        'apikey' : api_keys.APIKEY_MINUTE,
        'periodType' : 'day',
        #'period' : '10',
        'frequencyType': 'minute',
        'frequency': '1',
        'startDate': start_time,
        'endDate': end_time,
    }

    try:
        td_response = requests.get(url=urls.get_price_history_endpoint(symbol=symbol), params=payload)
        content = td_response.json()
        df = pd.DataFrame(content['candles'])
        return df
    except Exception as ex:
        return ex


if __name__ == '__main__':    
    #Create today's date for later file naming use.
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    #Create start time to track script running time.
    startTime = datetime.datetime.now()
    #Set logging.
    logging.basicConfig(filename=td.REPORTS_DATA_PATH + today +'_minute_bar.log', level=logging.DEBUG )
    #Print some information about start of the script
    print("Script Started at {}".format(startTime.strftime("%Y/%m/%d, %H:%M:%S")))
    logging.info("Script Started at {}".format(startTime.strftime("%Y/%m/%d, %H:%M:%S")))
    #Read in stock list
    stock_list = get_symbol_list()
    stock_list.sort()

    #Initial start time and end time, both in epoch format
    start_date = '1601182800000'
    end_date = '1603515600000'

    #Initial Failed List
    failed_list = []
    for i in range(4):
        #Initial Failed List at beginning of each trail.
        failed_list = []
        print('Request No.' + i + '. Total sotcks number is: ' + len(stock_list))
        #Start request each symbol.
        for symbol in progressBar(stock_list, prefix='Progress:', suffix='Complete', length=50):
        #This will return either a dataframe contains minute data, or an expection object which means request failed.
            df = get_minute_bar(symbol=symbol,start_time=start_date, end_time=end_date)
            #If success:
            if isinstance(df, pd.DataFrame):
                df.to_csv(td.RAW_MINUTE_DATA_PATH + symbol + '.csv')
                print(symbol + ' Completed.', end="\r", flush=True)
            else:
                failed_list.append(symbol)
                print(symbol +' Failed')
                logging.warning(symbol + ' Failed bacause' + str(df))

        #Reset Stock list to not successed symbol for next trail.
        stock_list = failed_list

    #Write report
    with open(td.REPORTS_DATA_PATH + today + '_minute_bar_failed_list.txt', 'w') as f:
        for symbol in failed_list:
            f.write("%s\n" %symbol)
    f.close()

    #Print out script ending time and total execution time.
    endtime = datetime.datetime.now()
    print("Script Started at {}".format(endtime.strftime("%Y/%m/%d, %H:%M:%S")))
    logging.info("Script Started at {}".format(endtime.strftime("%Y/%m/%d, %H:%M:%S")))
    print("Script Took {} to run".format(endtime - startTime))
    logging.info("Script Took {} to run".format(endtime - startTime))


