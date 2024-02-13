from NorenRestApiPy.NorenApi import NorenApi
from datetime import datetime
import pandas as pd
import pickle
import os
import time
import threading
import datetime
import schedule


smoothed_stoch_rsi_k = None
rsi_values = None
formatted_rsi = None
formatted_store_high = 0
formatted_store_low = 0
store_low = None
ce_sl = 0
ce_tgt = 0
pe_sl = 0
pe_tgt = 0
nifty_ltp = 0
total_count = 0
total_ce_count = 0
total_pe_count = 0
pe_tsym_values = 0
ce_tsym_values = 0
total_ce_count = 0
total_pe_count = 0


# Get the current date and time
current_date_time = datetime.datetime.now()
# Extract the month from the current date
current_month_abbrev = current_date_time.strftime("%b").upper()

print("Current Month:", current_month_abbrev)


global api

# Credentials
user = open('user.txt', 'r').read()
pwd = open('pass.txt', 'r').read()


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
    print('SENSEX CK LOGIN SUCESSFULL')
    print('LOGIN TIME', current_time)
    return api


if __name__ == '__main__':
    api = login()


def ltp_check():
    while True:
        try:
            with open('nifty_ltp.txt', 'r') as file:
                nifty_ltp = file.read()
                nifty_ltp = float(nifty_ltp)
        except FileNotFoundError as e:
            nifty_ltp = 0
            print(f"Error reading nifty_ltp.txt: {e}")
        except ValueError as e:
            nifty_ltp = 0  # or any default value
            print(f"Error converting to float: {e}")
        
        try:
            with open('finnifty_ltp.txt', 'r') as file:
                finnifty_ltp = file.read()
                finnifty_ltp = float(finnifty_ltp)
        except FileNotFoundError as e:
            finnifty_ltp = 0
            print(f"Error reading finnifty_ltp.txt: {e}")
        except ValueError as e:
            finnifty_ltp = 0  # or any default value
            print(f"Error converting to float: {e}")
         
        try:
            with open('midcap_ltp.txt', 'r') as file:
                midcap_ltp = file.read()
                midcap_ltp = float(midcap_ltp)
        except FileNotFoundError as e:
            midcap_ltp = 0
            print(f"Error reading midcap_ltp.txt: {e}")
        except ValueError as e:
            midcap_ltp = 0  # or any default value
            print(f"Error converting to float: {e}")
        
        try:
            with open('bnf_ltp.txt', 'r') as file:
                bnf_ltp = file.read()
                bnf_ltp = float(bnf_ltp)
        except FileNotFoundError as e:
            bnf_ltp = 0
            print(f"Error reading bnf_ltp.txt: {e}")
        except ValueError as e:
            bnf_ltp = 0  # or any default value
            print(f"Error converting to float: {e}")
        
        print('MIDCAP LTP', midcap_ltp)
        print('FINNIFTY LTP', finnifty_ltp)
        print('BANKNIFTY LTP', bnf_ltp)
        print('NIFTY LTP', nifty_ltp)
        print('...............................')

        time.sleep(1)
    
ltp_check()
    