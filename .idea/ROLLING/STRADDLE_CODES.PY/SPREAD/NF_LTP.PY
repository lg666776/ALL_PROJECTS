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


def ce_sell_exit():
    global ce_order_details, ce_exit_order_details, qty, ce_exit_trigger, ce_exit_avprc

    ce_token = None


    try:
        with open('ce_token.txt', 'r') as file:
            ce_token = file.read()
    except FileNotFoundError as e:
        print(f"Error reading ce_token.txt: {e}")


    while True:
        try:
            ce_res = api.get_quotes(exchange='BFO', token=str(ce_token))
            ce_lp = ce_res.get("lp")

            if ce_lp is not None:
                ce_lp = float(ce_lp)
                ce_trigger_prc = ce_lp * 0.20
                ce_trigger = ce_lp + ce_trigger_prc
                ce_exit_trigger = f'{round(ce_trigger):.2f}'

                for orderno, order_info in ce_order_details.items():
                    if isinstance(order_info, dict):  # Check if order_info is a dictionary
                        ce_symbol = order_info.get('ce_tsym')
                        ret = api.place_order(buy_or_sell='B', product_type='M', 
                                              exchange='BFO', tradingsymbol=ce_symbol,
                                              quantity=qty, discloseqty=0, price_type='LMT', price=ce_exit_trigger,
                                              retention='DAY', remarks='ce_exit_order')
                        ce_exit_orderno = ret['norenordno']

                        while True:
                            order_history = api.single_order_history(orderno=ce_exit_orderno)
                            
                            if order_history:
                                status = order_history[0].get('status')
                                if status == 'COMPLETE':
                                    if ce_exit_orderno not in ce_exit_order_details:
                                        ce_exit_order_details[ce_exit_orderno] = {
                                            'Status': 'COMPLETE',
                                            'trantype': 'B',  
                                            'remarks': 'ce_exit_order',  
                                            }
                                       
                                        # Exit the loop once ce_order_details is populated
                                        break
                # Return the order details dictionar
                return ce_exit_order_details
            else:
                print("Warning: 'lp' attribute is None for ce_token:")

        except Exception as e:
            print('An error occurred while fetching ce_lp for ce_token')

        # Add a short delay before retrying
        time.sleep(1)

