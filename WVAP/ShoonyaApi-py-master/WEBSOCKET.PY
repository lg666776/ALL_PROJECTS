import asyncio
from NorenRestApiPy.NorenApi import NorenApi
import logging
import pyotp

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)

class ShoonyaApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/', websocket='wss://api.shoonya.com/NorenWSTP/')        

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

import logging
from logging.handlers import RotatingFileHandler
import asyncio
from NorenRestApiPy.NorenApi import NorenApi

feed_opened = False
lp_value = None

def event_handler_feed_update(tick_data):
    global lp_value
    lp_value = tick_data['lp']
    logging.info(f"LP value: {lp_value}")

def open_callback():
    global feed_opened
    feed_opened = True

async def subscribe_and_wait():
    api.start_websocket(subscribe_callback=event_handler_feed_update, socket_open_callback=open_callback)

    while not feed_opened:
        await asyncio.sleep(0.1)

    # subscribe to a single token
    api.subscribe('NSE|11536')

    while lp_value is None:
        await asyncio.sleep(0.1)

    return lp_value

# Configure logging to log to a file
log_filename = "updates.log"
logging.basicConfig(level=logging.INFO)
handler = RotatingFileHandler(log_filename, maxBytes=1024*1024, backupCount=1)
formatter = logging.Formatter("%(asctime)s - %(message)s")
handler.setFormatter(formatter)
logging.getLogger().addHandler(handler)

# Run the code in an asyncio event loop
loop = asyncio.get_event_loop()
lp_value = loop.run_until_complete(subscribe_and_wait())
loop.close()

logging.info("Final LP value: %s", lp_value)


