from NorenRestApiPy.NorenApi import NorenApi
import pyotp

# Start of our program
Qr_code = '4M4I4T6A63G22WRV64W2X546M44OK656'
otp = pyotp.TOTP(Qr_code).now()

# Credentials
user = 'FA87766'
pwd = 'Lg@741154'
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

output = api.get_limits()
cash_value = float(output['cash'])  # Convert to a float for calculation
print("Account Balance:", cash_value)



def check_prints():
    global buy_avgprc, sell_avgprc, trade_details_file, sell_trade_details_file, formatted_buy_sl, formatted_sell_sl, buy_order_details, buy_sl, buy_tgt, sell_sl, sell_tgt
    print(buy_order_details)
    print('............................................')
    print('buy_avgprc', buy_avgprc)
    print('BUY_ATR', formatted_buy_sl)
    buy_sl = trade_details_file.get('Buy_SL', 0)
    print('BUY_STOP_LOSS', buy_sl)
    buy_tgt = trade_details_file.get('Buy_Target', 0)
    print('BUY_TARGET', buy_tgt)
    print('............................................')
    print('sell_avgprc', sell_avgprc)
    print('SELL_ATR', formatted_sell_sl)
    sell_sl = sell_trade_details_file.get('Sell_SL', 0)
    print('SELL_STOP_LOSS', sell_sl)
    sell_tgt = trade_details_file.get('Sell_Target', 0)
    print('SELL_TARGET', sell_tgt)