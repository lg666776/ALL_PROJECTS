from NorenRestApiPy.NorenApi import NorenApi
from datetime import datetime
from datetime import datetime, timedelta
from datetime import datetime
import pandas as pd
import pickle
import os
import time
import threading
import datetime
import math
import time
import pandas as pd 
import schedule
import time
global api

# Credentials
user = open('user.txt', 'r').read()
pwd = open('pass.txt', 'r').read()

# Get the current date and time
current_date_time = datetime.datetime.now()
# Extract the month from the current date
current_month_abbrev = current_date_time.strftime("%b").upper()

print("Current Month:", current_month_abbrev)


def login():
    class ShoonyaApiPy(NorenApi):
        def __init__(self):
            NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/',
                              websocket='wss://api.shoonya.com/NorenWSTP/')

    api = ShoonyaApiPy()
    # Make the API call
    # res = api.login(userid=user, password=pwd, twoFA=otp, vendor_code=vc, api_secret=app_key, imei=imei)
    session_token = open('session_token.txt', 'r').read()
    api.set_session(user, pwd, session_token)
    # Get the current time
    current_time = datetime.datetime.now().time()
    print('ROLLING LOGIN SUCESSFULL')
    print('LOGIN TIME', current_time)
    return api


if __name__ == '__main__':
    api = login()


ce_specific_tsym = None

def opt():
    global ce_tsym, pe_tsym, ce_specific_tsym
    ret = api.get_quotes(exchange='BSE', token='1')
    ltp = ret.get("lp")
    ltp = float(ltp)  

    pe_otm3 = ltp - 200
    ce_otm3 = ltp + 200

    ce_strike = int(round(pe_otm3/100,0)*100)
    pe_strike = int(round(ce_otm3/100,0)*100)

    month = current_month_abbrev

    ce_syn = ce_strike
    pe_syn = pe_strike

    ce_txt = f'SENSEX {month} {ce_syn} CE'
    pe_txt = f'SENSEX {month} {pe_syn} PE'

    # Search for CE options
    ce_res = api.searchscrip('BFO', ce_txt)
    ce_df = pd.DataFrame(ce_res['values'])

    # Search for PE options
    pe_res = api.searchscrip('BFO', pe_txt)
    pe_df = pd.DataFrame(pe_res['values'])
    
    # Extract the 'weekly' value from the first row
    ce_tsym = ce_df.loc[0, 'tsym']
    pe_tsym = pe_df.loc[0, 'tsym']

        # Filter and sort CE DataFrame for the value in first_row_weekly
    ce_filtered_df = ce_df[ce_df['tsym'] == ce_tsym].sort_values(by='tsym')
    ce_tsym_values = ce_filtered_df['tsym'].tolist()
        
       
        # Filter and sort PE DataFrame for 'W1' weekly values
    pe_filtered_df = pe_df[pe_df['tsym'] == pe_tsym].sort_values(by='tsym')
    pe_tsym_values = pe_filtered_df['tsym'].tolist()
      

    if ce_tsym_values:
        ce_specific_tsym = ce_tsym_values[0]
        print(ce_specific_tsym)
        
    if pe_tsym_values:
        pe_specific_tsym = pe_tsym_values[0]
        print(pe_specific_tsym)

def place():
    global ce_specific_tsym
    qty = 10
    ret = api.place_order(buy_or_sell='B', product_type='I',
                                  exchange='BFO', tradingsymbol=ce_specific_tsym,
                                  quantity=qty, discloseqty=0, price_type='MKT',
                                  retention='DAY', remarks='ce_order')
    orderno = ret['norenordno']
    print(orderno)

    

schedule.every().day.at("14:45:20").do(opt)
schedule.every().day.at("14:45:30").do(place)




# Run the scheduler
while True:
    schedule.run_pending()
    time.sleep(1)
