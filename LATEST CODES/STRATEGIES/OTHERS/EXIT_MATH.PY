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




    def math_calculation():

        ce_token = 0
        pe_token = 0
        ce_lp = 0
        pe_lp = 0

        try:
            with open('ce_token.txt', 'r') as file:
                ce_token = file.read()
        except FileNotFoundError as e:
            print(f"Error reading ce_ws_token.txt: {e}")
        try:
            with open('pe_token.txt', 'r') as file:
                pe_token = file.read()
        except FileNotFoundError as e:
            print(f"Error reading pe_ws_token.txt: {e}")
        try:
            with open('qty.txt', 'r') as file:
                qty = file.read()
        except FileNotFoundError as e:
            print(f"Error reading ce_ws_token.txt: {e}")
        
            # Check if ce_token has a value
        if ce_token:
            try:
                ce_res = api.get_quotes(exchange='NFO', token=str(ce_token))
                ce_lp = ce_res.get("lp")
                ce_lp = float(ce_lp)
            except Exception as e:
                print(f"Error processing ce_token: {e}")
        
        else:
            print("No valid ce_token value")
                   
         # Check if pe_token has a value
        if pe_token:
            try:
                pe_res = api.get_quotes(exchange='NFO', token=str(pe_token))
                pe_lp = pe_res.get("lp")
                pe_lp = float(pe_lp)
              
            except Exception as e:
                print(f"Error processing pe_token: {e}")
        else:
            print("No valid pe_token value")

        combined_premium_points = ce_lp + pe_lp
        formatted_premium = f'{combined_premium_points:.2f}'  # Format to display with 2 decimal places
        
        # Convert formatted_premium and qty to float before multiplication
        formatted_premium_float = float(formatted_premium)
        qty_float = float(qty)
        
        combined_premium_amount = formatted_premium_float * qty_float


        # Calculate 20% of formatted_amount
        exit_limit = - 0.2 * combined_premium_amount
        formatted_exit_limit = f'{exit_limit:.2f}'


        # Calculate 20% of formatted_amount
        max_exit_lmt = - 0.5 * combined_premium_amount
        for_max_exit_limit = f'{max_exit_lmt:.2f}'

        if float(for_max_exit_limit) > -2000.0:
            for_max_exit_limit = '-2000.00' 
        else:
            for_max_exit_limit = for_max_exit_limit
            print(for_max_exit_limit)
        


            


        
math_calculation()

