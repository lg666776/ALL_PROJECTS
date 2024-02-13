from NorenRestApiPy.NorenApi import NorenApi
from datetime import datetime
from datetime import datetime, timedelta
import pandas as pd
import pickle
import os
import time
import threading
import datetime
import math
import time
import pandas as pd  

bnf_lp = 0
atmstrike = 0
pe_token_read = 0

ab = 0

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
    print('PE OHLC LOGIN SUCESSFULL')
    print('LOGIN TIME', current_time)
    return api


if __name__ == '__main__':
    api = login()



def atm_loop():
    global bnf_lp, atmstrike, pe_token_read
 
    while True:
        try:
            with open('ce_closing_prc.txt', 'r') as file:
                ce_closing_price = file.read().strip()
                print("File Content:", ce_closing_price)
                ce_closing_price = float(ce_closing_price)
        except FileNotFoundError:
            ce_closing_price = 0
        except ValueError as e:
            print("Error:", e)
            ce_closing_price = 0

        time.sleep(0.01)





if __name__ == "__main__":
    # Create and start the threads for TCS data and Candle data
    amt_loop_thread = threading.Thread(target=atm_loop)
    amt_loop_thread.start()
