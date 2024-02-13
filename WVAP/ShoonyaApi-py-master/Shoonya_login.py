from NorenRestApiPy.NorenApi import  NorenApi
import logging
import pyotp
import pandas as pd
from datetime import datetime, timedelta
import timeit

class ShoonyaApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/', websocket='wss://api.shoonya.com/NorenWSTP/')        
        global api
        api = self
#enable dbug to see request and responses
logging.basicConfig(level=logging)

#start of our program
Qr_code = '4M4I4T6A63G22WRV64W2X546M44OK656'
api = ShoonyaApiPy()
otp = pyotp.TOTP(Qr_code).now()

#credentials
user    = 'FA87766'
pwd     = 'Lg666776*#'
factor2 = otp
vc      = 'FA87766_U'
app_key = 'ed5b4b44cf139d74b2a5b4ff7480ad48'
imei    = 'abc1234'

#make the api call
ret = api.login(userid=user, password=pwd, twoFA=otp, vendor_code=vc, api_secret=app_key, imei=imei)


def get_time_series(exchange, token, days, interval):
    #start of our program
    now = datetime.now()

    now = now.replace(hour=0, minute=0, second=0, microsecond=0)

    prev_day = now - timedelta(days=days)

    prev_day_timestamp = prev_day.timestamp()

    ret = api.get_time_price_series(exchange=exchange, token=token, starttime=prev_day_timestamp, interval=interval)
    if ret:
       candle_df = pd.DataFrame(ret, columns=['time', 'inth', 'intl', 'intc', 'intv'])
       return candle_df
      
    
     

# Fetch candle data
candle_df = get_time_series('NSE', '3045', 5, 5)



# Extract columns 'time', 'inth', 'intl', 'intc', 'intv' as separate variables
time_values = candle_df['time']
high_values = candle_df['inth']
low_values = candle_df['intl']
close_values = candle_df['intc']
volume = candle_df['intv']