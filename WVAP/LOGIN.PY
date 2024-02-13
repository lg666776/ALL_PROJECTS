from NorenRestApiPy.NorenApi import NorenApi
import pyotp
from datetime import datetime
import datetime

# Start of our program
Qr_code = '4M4I4T6A63G22WRV64W2X546M44OK656'
otp = pyotp.TOTP(Qr_code).now()

# Credentials
user = open('user.txt', 'r').read()
pwd = open('pass.txt', 'r').read()
factor2 = otp
vc = 'FA87766_U'
app_key = 'ed5b4b44cf139d74b2a5b4ff7480ad48'
imei = 'abc1234'

global api


def login():
    class ShoonyaApiPy(NorenApi):
        def __init__(self):
            NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/',
                              websocket='wss://api.shoonya.com/NorenWSTP/')

    api = ShoonyaApiPy()
    # Make the API call
    res = api.login(userid=user, password=pwd, twoFA=otp, vendor_code=vc, api_secret=app_key, imei=imei)
    with open('session_token.txt', 'w') as file:
        file.write(res['susertoken'])
    print(res)
    return api


if __name__ == '__main__':
    api = login()

ret = api.searchscrip(exchange='NSE', searchtext='NIF')
print(ret)
