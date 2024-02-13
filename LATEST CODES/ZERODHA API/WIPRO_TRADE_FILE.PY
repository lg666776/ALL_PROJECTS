import datetime
from kiteconnect import KiteConnect
import math

api_key = input("Enter your API key: ")
api_secret = input("Enter your API secret key: ")

kite = KiteConnect(api_key=api_key)

def get_access_token():
    # Get the access token URL
    access_token_url = kite.login_url()
    access_token_url = access_token_url.replace("YOUR_API_KEY", api_key)
    print("Login URL: " + access_token_url)

    # Manually authorize and obtain the access token
    request_token = input("Enter the request token from the redirected URL: ")
    data = kite.generate_session(request_token, api_secret=api_secret)
    access_token = data["access_token"]
    kite.set_access_token(access_token)
    print("Access token set successfully.")


def check_access_token_expiry():
    token_expiry = datetime.datetime.fromtimestamp(kite.ltp("NSE:WIPRO")['NSE:WIPRO']['timestamp'])
    current_time = datetime.datetime.now()
    if current_time >= token_expiry:
        print("Access token has expired.")
    else:
        print("Access token is valid.")


# Function to calculate quantity based on margin and leverage
def calculate_quantity(margin, leverage, live_price):
    effective_margin = margin / leverage
    quantity = math.floor(effective_margin / live_price)
    return int(quantity)


# Main entry point
if __name__ == "__main__":
    get_access_token()

    buy_executed = False
    sell_executed = False
    actual_margin = 25000  # Example actual margin of 25,000 (modified)
    leverage = 5  # Example leverage of 5x

    # Get live price of WIPRO
    ltp = kite.ltp("NSE:WIPRO")["NSE:WIPRO"]["last_price"]

    quantity = calculate_quantity(actual_margin, leverage, ltp)


    def check_buying_conditions(quantity):
        global buy_executed, sell_executed
        if not buy_executed and not sell_executed:
            # Get Stochastic values for the last 15 minutes (14 + 1 candle for upcrossing)
            data = kite.historical_data("NSE:WIPRO", interval="5minute", period=15)
            closes = [candle['close'] for candle in data]

            # Calculate Stochastic indicator
            high = max(closes[:-1])
            low = min(closes[:-1])
            current_close = closes[-1]
            stochastic = 100 * (current_close - low) / (high - low)

            # Check if Stochastic is in the range of 35-65
            if 35 <= stochastic <= 65:
                # Check if Stochastic SmoothK line upcrosses within the range
                if closes[-1] > closes[-2] and closes[-2] <= 35 and closes[-1] > 35:
                    # Check if the last 3 candles meet the VWAP condition
                    candles = kite.historical_data("NSE:WIPRO", interval="5minute", period=3)
                    vwap = sum([candle['volume'] * (candle['high'] + candle['low'] + candle['close']) / 3 for candle in
                                candles]) / sum([candle['volume'] for candle in candles])
                    if candles[1]['high'] > vwap and candles[2]['high'] > vwap:
                        # Enter the buy trade if the high of the third candle breaks
                        if current_close > candles[2]['high']:
                            # Check if a selling trade is active
                            if sell_executed:
                                # Exit the active selling trade
                                exit_sell_trade()
                                sell_executed = False
                            execute_buy_trade("WIPRO", quantity)
                            buy_executed = True

                            # Check for exit condition: 2, 5-minute candles close below VWAP and 2nd candle closes below the low of the first one
                            if len(candles) >= 4:
                                if candles[2]['close'] < vwap and candles[3]['close'] < vwap and candles[3]['close'] < \
                                        candles[2]['low']:
                                    exit_buy_trade()
                                    buy_executed = False


    def check_selling_conditions(quantity):
        global buy_executed, sell_executed
        if not sell_executed and not buy_executed:
            # Get Stochastic values for the last 15 minutes (14 + 1 candle for downcrossing)
            data = kite.historical_data("NSE:WIPRO", interval="5minute", period=15)
            closes = [candle['close'] for candle in data]

            # Calculate Stochastic indicator
            high = max(closes[:-1])
            low = min(closes[:-1])
            current_close = closes[-1]
            stochastic = 100 * (current_close - low) / (high - low)

            # Check if Stochastic is in the range of 65-35
            if 65 >= stochastic >= 35:
                # Check if Stochastic SmoothK line downcrosses within the range
                if closes[-1] < closes[-2] and closes[-2] >= 65 and closes[-1] < 65:
                    # Check if the last 3 candles meet the VWAP condition
                    candles = kite.historical_data("NSE:WIPRO", interval="5minute", period=3)
                    vwap = sum([candle['volume'] * (candle['high'] + candle['low'] + candle['close']) / 3 for candle in
                                candles]) / sum([candle['volume'] for candle in candles])
                    if candles[1]['low'] < vwap and candles[2]['low'] < vwap:
                        # Enter the sell trade if the low of the third candle breaks
                        if current_close < candles[2]['low']:
                            # Check if a buying trade is active
                            if buy_executed:
                                # Exit the active buying trade
                                exit_buy_trade()
                                buy_executed = False
                            execute_sell_trade("WIPRO", quantity)
                            sell_executed = True

                            # Check for exit condition: 2, 5-minute candles close above VWAP and 2nd candle closes above the high of the first one
                            if len(candles) >= 4:
                                if candles[2]['close'] > vwap and candles[3]['close'] > vwap and candles[3]['close'] > \
                                        candles[2]['high']:
                                    exit_sell_trade()
                                    sell_executed = False


    def execute_buy_trade(symbol, quantity):
        # Get the lowest point of the day as stop-loss
        today = datetime.date.today().strftime("%Y-%m-%d")
        lows = kite.historical_data(symbol, interval="5minute", from_date=today, to_date=today, continuous=False)
        stop_loss = lows[0]['low']

        # Place the buy trade using Zerodha API
        kite.place_order(
            tradingsymbol=symbol,
            exchange="NSE",
            transaction_type="BUY",
            quantity=quantity,
            order_type="MARKET",
            product="MIS",
            stoploss=stop_loss
        )
        print("Buy trade executed.")


    def execute_sell_trade(symbol, quantity):
        # Get the highest point of the day as stop-loss
        today = datetime.date.today().strftime("%Y-%m-%d")
        highs = kite.historical_data(symbol, interval="5minute", from_date=today, to_date=today, continuous=False)
        stop_loss = highs[0]['high']

        # Place the sell trade using Zerodha API
        kite.place_order(
            tradingsymbol=symbol,
            exchange="NSE",
            transaction_type="SELL",
            quantity=quantity,
            order_type="MARKET",
            product="MIS",
            stoploss=stop_loss
        )
        print("Sell trade executed.")


    def exit_buy_trade():
        # Exit the active buying trade using Zerodha API
        kite.exit_order(
            order_id=buy_order_id,
            parent_order_id=buy_order_id,
            tradingsymbol="WIPRO",
            exchange="NSE",
            transaction_type="SELL",
            quantity=quantity,
            order_type="MARKET",
            product="MIS"
        )
        print("Buy trade exited.")


    def exit_sell_trade():
        # Exit the active selling trade using Zerodha API
        kite.exit_order(
            order_id=sell_order_id,
            parent_order_id=sell_order_id,
            tradingsymbol="WIPRO",
            exchange="NSE",
            transaction_type="BUY",
            quantity=quantity,
            order_type="MARKET",
            product="MIS"
        )
        print("Sell trade exited.")


    # Check if a buy or sell trade has already been executed today
    trades = kite.orders()
    if not any(trade['transaction_type'] == 'BUY' for trade in trades):
        check_buying_conditions(quantity)
    if not any(trade['transaction_type'] == 'SELL' for trade in trades):
        check_selling_conditions(quantity)

    # Exit all trades at 3:00 PM
    current_time = datetime.datetime.now().time()
    if current_time >= datetime.time(14, 55):
        if buy_executed:
            exit_buy_trade()
        if sell_executed:
            exit_sell_trade()
