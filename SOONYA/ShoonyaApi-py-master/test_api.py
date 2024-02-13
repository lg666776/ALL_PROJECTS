import asyncio
from NorenRestApiPy.NorenApi import NorenApi
import logging
import pyotp

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)

class ShoonyaApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/', websocket='wss://api.shoonya.com/NorenWSTP/')        

    async def start_websocket_async(self, subscribe_callback=None, socket_open_callback=None):
        await self.start_websocket(subscribe_callback=subscribe_callback, socket_open_callback=socket_open_callback)

api = ShoonyaApiPy()

# Your credentials
Qr_code = '4M4I4T6A63G22WRV64W2X546M44OK656'
user = 'FA87766'
pwd = 'Lg666776@500'
factor2 = pyotp.TOTP(Qr_code).now()
vc = 'FA87766_U'
app_key = 'ed5b4b44cf139d74b2a5b4ff7480ad48'
imei = 'abc1234'

# Make the API call to login
ret = api.login(userid=user, password=pwd, twoFA=factor2, vendor_code=vc, api_secret=app_key, imei=imei)

lp_value = None

async def event_handler_feed_update(tick_data):
    global lp_value
    lp_value = tick_data['lp']
    print(lp_value)

async def open_callback():
    # subscribe to a single token
    await api.subscribe('NSE|11536')

async def run():
    await api.start_websocket_async(subscribe_callback=event_handler_feed_update, socket_open_callback=open_callback)

    while lp_value is None:
        await asyncio.sleep(0.1)

    # Wait for some time to receive updates and print the LP value
    while True:
        await asyncio.sleep(0.1)

        if lp_value is not None:
            print(f"LP value: {lp_value}")

# Run the asyncio event loop
loop = asyncio.get_event_loop()
loop.run_until_complete(run())
loop.close()



