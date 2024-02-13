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


def nifty_strikes():
    global ce_tsym, pe_tsym
    ret = api.get_quotes(exchange='NSE', token='26000')
    ltp = ret.get("lp")
    ltp = float(ltp) 

    month = current_month_abbrev 

    ce_atm = ltp
    pe_atm = ltp


    ce_otm3 = ltp + 100
    pe_otm3 = ltp - 100

    ce_atm_strike = int(round(ce_atm/50,0)*50)
    ce_atm_txt = f'NIFTY {month} {ce_atm_strike} CE'
    
    # Search for CE options
    ce_atm_res = api.searchscrip('NFO', ce_atm_txt)
    ce_atm_df = pd.DataFrame(ce_atm_res['values'])

    # Extract the 'weekly' value from the first row
    ce_atm_tsym = ce_atm_df.loc[0, 'tsym']
    ce_atm_tysm_df = ce_atm_df[ce_atm_df['tsym'] == ce_atm_tsym].sort_values(by='tsym')
    ce_atm_symbol = ce_atm_tysm_df['tsym'].tolist()

    pe_atm_strike = int(round(pe_atm/50,0)*50)
    pe_atm_txt = f'NIFTY {month} {pe_atm_strike} PE'
    
    # Search for CE options
    pe_atm_res = api.searchscrip('NFO', pe_atm_txt)
    pe_atm_df = pd.DataFrame(pe_atm_res['values'])

    # Extract the 'weekly' value from the first row
    pe_atm_tsym = pe_atm_df.loc[0, 'tsym']
    pe_atm_tysm_df = pe_atm_df[pe_atm_df['tsym'] == pe_atm_tsym].sort_values(by='tsym')
    pe_atm_symbol = pe_atm_tysm_df['tsym'].tolist()
    

    ce_otm_strike = int(round(ce_otm3/50,0)*50)
    pe_otm_strike = int(round(pe_otm3/50,0)*50)

    ce_otm_txt = f'NIFTY {month} {ce_otm_strike} CE'
    pe_otm_txt = f'NIFTY {month} {pe_otm_strike} PE'

    # Search for CE options
    ce_otm_res = api.searchscrip('NFO', ce_otm_txt)
    ce_otm_df = pd.DataFrame(ce_otm_res['values'])

    # Search for PE options
    pe_otm_res = api.searchscrip('NFO', pe_otm_txt)
    pe_otm_df = pd.DataFrame(pe_otm_res['values'])
    
    # Extract the 'weekly' value from the first row
    ce_otm_tsym = ce_otm_df.loc[0, 'tsym']
    pe_otm_tsym = pe_otm_df.loc[0, 'tsym']

    # Filter and sort CE DataFrame for the value in first_row_weekly
    ce_otm_tysm_df = ce_otm_df[ce_otm_df['tsym'] == ce_otm_tsym].sort_values(by='tsym')
    ce_otm_symbol = ce_otm_tysm_df['tsym'].tolist()
        
    # Filter and sort PE DataFrame for 'W1' weekly values
    pe_otm_tsym_df = pe_otm_df[pe_otm_df['tsym'] == pe_otm_tsym].sort_values(by='tsym')
    pe_otm_symbol = pe_otm_tsym_df['tsym'].tolist()

    if ce_atm_symbol:
        ce_atm_symbol = ce_atm_symbol[0]
        print(ce_atm_symbol)

    if ce_otm_symbol:
        ce_otm_symbol = ce_otm_symbol[0]
        print(ce_otm_symbol)

    if pe_atm_symbol:
        pe_atm_symbol = pe_atm_symbol[0]
        print(pe_atm_symbol)

    if pe_otm_symbol:
        pe_otm_symbol = pe_otm_symbol[0]
        print(pe_otm_symbol)

    
schedule.every().day.at("17:28:30").do(nifty_strikes)

# Run the scheduler
while True:
    schedule.run_pending()
    time.sleep(1)

