from datetime import date
import json
from os import remove
import td_config as td
import api_keys
import pandas as pd
import requests
import logging
import urls
import datetime
import os
import time
from utilties import progressBar

def get_fundamental_update(symbol):
    #TD API limits request to 120 per second. That is maxium 2 request per second, so sleep here.
    time.sleep(0.5)
    #Define payload
    payload = {
            'apikey' : api_keys.APIKEY_FUNDAMENTAL,
            'symbol': symbol,
            'projection':'fundamental',
    }

    try:
        td_response = requests.get(url=urls.get_fundamental_endpoint(), params=payload)
        content = td_response.json()
        content_dict = content[symbol]['fundamental']
        df = pd.DataFrame(content_dict, index=[0])
        return df
    except Exception as ex:
        return ex


if __name__ == '__main__':
    #Create today's date for later file naming use.
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    #Create start time to track script running time.
    startTime = datetime.datetime.now()
    #Set logging.
    logging.basicConfig(filename=td.REPORTS_DATA_PATH + today +'_fundamental.log', level=logging.DEBUG )
    #Print some information about start of the script
    print("Script Started at {}".format(startTime.strftime("%Y/%m/%d, %H:%M:%S")))
    logging.info("Script Started at {}".format(startTime.strftime("%Y/%m/%d, %H:%M:%S")))
    #Read in stock list.
    stock_list = list(pd.read_csv(td.REFERENCES_DATA_PATH + 'us_exchanges_instruments.csv')['symbol'])
    #Inital storage variables
    all_fundamental = pd.DataFrame([])
    failed_list = []

    """
    This script will try to get fundamental data for 4 times. 
    During the process, the successed stock will be removed from the list, so next try will only on stocks that failed last time.
    After 4 tries, the remaining stocks will be write to fail list file, stamped with date and stored in Report directory.
    """    

    for i in range(4):
        #Print number of attemps.
        print('This is {} try.'.format(i))
        #Go through list to fectch stock's fundamental info. Here we used a progress bar for better visual.
        for symbol in progressBar(stock_list, prefix='Progress:', suffix='Complete', length= 50):
            #This will return either a dataframe contians fundamental data, or an expection object which means the request failed.
            df = get_fundamental_update(symbol)
            #Check if df contians fundamental data or expection.
            if isinstance(df, pd.DataFrame): #If successed
                #Store this stock's fundamental in storage variablE.
                all_fundamental = all_fundamental.append(df)
                #Remove this symbol from list so it won't be request next time.
                failed_list.append(symbol)
                #Put something in log.
                logging.info(symbol + ' Completed')
            else:
                #This stock has failed on request, log it.
                logging.warning(symbol +' Failed because' + str(df))
    

    #Now after trying for 4 times, we could write the result to file. 
    all_fundamental.to_csv(td.FUNDAMENTAL_DATA_PATH + today +'.csv')
    #Write the failed stocks into fail for record.
    with open(td.REPORTS_DATA_PATH + today + '_fundamental_failed_list.txt','w') as f:
        for symbol in failed_list:
            f.write("%s\n" %symbol)
    f.close()

    #Print out script ending time and total execution time.
    endtime = datetime.datetime.now()
    print("Script Started at {}".format(endtime.strftime("%Y/%m/%d, %H:%M:%S")))
    logging.info("Script Started at {}".format(endtime.strftime("%Y/%m/%d, %H:%M:%S")))
    print("Script Took {} to run".format(endtime - startTime))
    logging.info("Script Took {} to run".format(endtime - startTime))

