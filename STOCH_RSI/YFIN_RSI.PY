import yfinance as yf
import pandas as pd
import time
import threading
from datetime import datetime
import datetime

rsi_values = None
formatted_rsi = None
smoothed_stoch_rsi_k = None

def get_candle_data():
    try:
        data = yf.download(tickers='^NSEI', period='5d', interval='5m')

        # Check if the DataFrame is empty
        if data.empty:
            print("No data available for the specified parameters.")
            get_candle_data()
            return None
        
        # Set Pandas display option to show all rows
        pd.set_option('display.max_rows', None)

        candle_df = data[['Open', 'High', 'Low', 'Close']].copy()
        # Round the numbers to one decimal place
        candle_df = candle_df.round(1)
        print(candle_df)
        

        return candle_df

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def calculate_rsi(candle_df):
    global rsi_values

    # Convert the 'intc' column to numeric if it contains string values
    candle_df['Close'] = pd.to_numeric(candle_df['Close'], errors='coerce')

    # Replace this with your actual price data from candle_df
    close_prices = candle_df['Close']

    period = 14  # You can change this to your desired period

    # Calculate price changes
    candle_df['price_change'] = candle_df['Close'].diff()

    # Calculate gains (positive price changes) and losses (negative price changes)
    candle_df['gain'] = candle_df['price_change'].apply(lambda x: x if x > 0 else 0)
    candle_df['loss'] = candle_df['price_change'].apply(lambda x: -x if x < 0 else 0)

    # Calculate average gains and average losses over the specified period
    avg_gain = candle_df['gain'][:period].mean()
    avg_loss = candle_df['loss'][:period].mean()

    # Calculate RS (Relative Strength) for the first RSI value
    rs = avg_gain / avg_loss

    # Calculate RSI for the first period
    rsi = 100 - (100 / (1 + rs))

    # Create lists to store RSI values
    rsi_values = [rsi]

    # Create a list to store RSI values with NaN for the first 14 periods
    rsi_values = [None] * period

    # Calculate RSI for the remaining periods
    for i in range(period, len(candle_df)):
        price_change = candle_df['price_change'][i]
        gain = price_change if price_change > 0 else 0
        loss = -price_change if price_change < 0 else 0

        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        rsi_values.append(rsi)

        # Create a DataFrame with 'time' and 'smoothk' columns to store the RSI values
    result_df = pd.DataFrame({'smoothk': rsi_values})

    # Set Pandas display option to show all rows
    pd.set_option('display.max_rows', None)


def calculate_stoch_rsi(stoch_period=14, smoothing_period=7):
    global rsi_values, formatted_rsi, smoothed_stoch_rsi_k

    # Calculate the RSI's highest high and lowest low over the StochRSI period
    rsi_high = pd.Series(rsi_values).rolling(window=stoch_period).max()
    rsi_low = pd.Series(rsi_values).rolling(window=stoch_period).min()

    # Calculate the StochRSI %K value
    stoch_rsi_k = (pd.Series(rsi_values) - rsi_low) / (rsi_high - rsi_low)

    # Apply smoothing using a simple moving average (SMA)
    smoothed_stoch_rsi_k = stoch_rsi_k.rolling(window=smoothing_period).mean()

   


def calculate_atr(candle_df, period=14):
    # Convert 'inth' (low) and 'intc' (close) columns in candle_df to numeric
    candle_df['High'] = pd.to_numeric(candle_df['High'], errors='coerce')
    candle_df['Close'] = pd.to_numeric(candle_df['Close'], errors='coerce')
    candle_df['Low'] = pd.to_numeric(candle_df['Low'], errors='coerce')

    atr_values = []  # List to store ATR values

    for i in range(len(candle_df)):
        if i == 0:
            atr_values.append(candle_df['High'].iloc[i] - candle_df['Low'].iloc[i])
        else:
            tr = max(candle_df['High'].iloc[i] - candle_df['Low'].iloc[i],
                     abs(candle_df['High'].iloc[i] - candle_df['Close'].iloc[i - 1]),
                     abs(candle_df['High'].iloc[i] - candle_df['Close'].iloc[i - 1]))
            atr_values.append((atr_values[-1] * (period - 1) + tr) / period)

    # Create a DataFrame with 'time' and 'smoothk' columns to store the RSI values
    atr_df = pd.DataFrame({'atr': atr_values})

    return atr_df


def call_entry_conditions(candle_df, atr_df):
    global smoothed_stoch_rsi_k, store_low, ce_sl, ce_tgt, formatted_store_low, store_low
    # Convert 'inth' (low) and 'intc' (close) columns in candle_df to numeric
    candle_df['inth'] = pd.to_numeric(candle_df['High'], errors='coerce')
    candle_df['intc'] = pd.to_numeric(candle_df['Close'], errors='coerce')
    candle_df['intl'] = pd.to_numeric(candle_df['Low'], errors='coerce')

    # Reset the index to make the 'time' column a regular column again
    candle_df_reset = candle_df.reset_index()

    # Find the index of the data point corresponding to 9:15 AM
    start_time_index = candle_df_reset.index[candle_df_reset['Datetime'] == '09:15'].tolist()
    if not start_time_index:
        return None

    # Get the index to start from 9:15 AM
    start_index = start_time_index[0]

    # Initialize a variable to keep track of the previous value of formatted_rsi_float
    prev_formatted_rsi_float = None

    atr = 0 
    store_low = None

    # Loop through each candle data starting from 9:15 AM
    for i in range(start_index, len(candle_df_reset)):
        # Check if the index 'i' is within the valid range of smoothed_stoch_rsi_k
        if 0 <= i < len(smoothed_stoch_rsi_k):
            # Access a specific element in the Series and convert it to a float
            formatted_rsi_float = float(smoothed_stoch_rsi_k.iloc[i])

            if prev_formatted_rsi_float is not None:
                if prev_formatted_rsi_float >= 0.70 and formatted_rsi_float < 0.70:
    
                    sell_entry_condition = True 

                    if sell_entry_condition:
                        # This is where you execute your buy action
                        store_low = candle_df_reset['Low'].iloc[i]
                        atr = atr_df['atr'].iloc[i]

                        # Format to display only two decimal places
                        formatted_atr = "{:.2f}".format(atr)
                        formatted_store_low = "{:.2f}".format(store_low)

                        # Convert formatted_atr to a float if it's not already
                        formatted_atr = float(formatted_atr)
                        formatted_store_low = float(formatted_store_low)
                        sl = formatted_atr
                        tgt = formatted_atr * 2

                        if formatted_store_low and formatted_atr:
                            ce_sl = formatted_store_low + sl
                            ce_tgt = formatted_store_low - tgt
                            
                            print('SELL CONDITION MET AT',candle_df_reset['Datetime'].iloc[i], 'RSI', formatted_rsi_float, 'STORE LOW', formatted_store_low, 
                                  'ATR', formatted_atr, 'SL', ce_sl, 'TGT', ce_tgt)

                elif prev_formatted_rsi_float <= 0.70 and formatted_rsi_float > 0.70:
                    store_low = None
                    atr = 0
                    formatted_store_low = 0
                    

            # Update the previous value with the current value
            prev_formatted_rsi_float = formatted_rsi_float


def put_entry_conditions(candle_df, atr_df):
    global smoothed_stoch_rsi_k, formatted_store_high, pe_sl, pe_tgt, store_high

    # Convert 'inth' (low) and 'intc' (close) columns in candle_df to numeric
    candle_df['inth'] = pd.to_numeric(candle_df['High'], errors='coerce')
    candle_df['intc'] = pd.to_numeric(candle_df['Close'], errors='coerce')
    candle_df['intl'] = pd.to_numeric(candle_df['Low'], errors='coerce')

    # Reset the index to make the 'time' column a regular column again
    candle_df_reset = candle_df.reset_index()

    # Find the index of the data point corresponding to 9:15 AM
    start_time_index = candle_df_reset.index[candle_df_reset['Datetime'] == '09:15'].tolist()
    if not start_time_index:
        return None

    # Get the index to start from 9:15 AM
    start_index = start_time_index[0]

    # Initialize a variable to keep track of the previous value of formatted_rsi_float
    prev_formatted_rsi_float = None

    atr = 0
    store_high = None


    # Loop through each candle data starting from 9:15 AM
    for i in range(start_index, len(candle_df_reset)):
        # Check if the index 'i' is within the valid range of smoothed_stoch_rsi_k
        if 0 <= i < len(smoothed_stoch_rsi_k):
            # Access a specific element in the Series and convert it to a float
            formatted_rsi_float = float(smoothed_stoch_rsi_k.iloc[i])

            if prev_formatted_rsi_float is not None:
                if prev_formatted_rsi_float <= 0.30 and formatted_rsi_float > 0.30:
                                        
                    buy_entry_condition = True  # Modify this as needed

                    if buy_entry_condition:
                        # This is where you execute your buy action
                        store_high = candle_df_reset['High'].iloc[i]
                        atr = atr_df['atr'].iloc[i]

                        # Format to display only two decimal places
                        formatted_atr = "{:.2f}".format(atr)
                        formatted_store_high = "{:.2f}".format(store_high)

                        # Convert formatted_atr to a float if it's not already
                        formatted_atr = float(formatted_atr)
                        formatted_store_high = float(formatted_store_high)
                        sl = formatted_atr
                        tgt = formatted_atr * 2

                        if formatted_store_high and formatted_atr:
                            pe_sl = formatted_store_high - sl
                            pe_tgt = formatted_store_high + tgt

                            print('BUY CONDITION MET AT',candle_df_reset['Datetime'].iloc[i], 'RSI', formatted_rsi_float, 'STORE HIGH', formatted_store_high, 
                                  'ATR', formatted_atr, 'SL', pe_sl, 'TGT', pe_tgt)

                elif prev_formatted_rsi_float >= 0.30 and formatted_rsi_float < 0.30:
                    store_high = None
                    atr = 0
                    formatted_store_high = 0

            # Update the previous value with the current value
            prev_formatted_rsi_float = formatted_rsi_float

def fetch_candle_data_loop():

    interval = 5

    while True:
        # Fetch candle data (replace this with your implementation)
        candle_df = get_candle_data()

        if candle_df is not None:
            calculate_rsi(candle_df)
            calculate_stoch_rsi(stoch_period=14, smoothing_period=7)
            atr_df = calculate_atr(candle_df)
            put_entry_conditions(candle_df, atr_df)
            call_entry_conditions(candle_df, atr_df)
            

        # Wait for the next 5-minute mark
        next_update_time = get_next_interval_mark(interval)
        time_to_sleep = (next_update_time - datetime.datetime.now()).total_seconds()
        time.sleep(time_to_sleep)


def get_next_interval_mark(interval):
    now = datetime.datetime.now()
    current_minute = now.minute
    remainder = current_minute % interval
    if remainder == 0:
        next_interval_mark = now.replace(second=0, microsecond=0) + datetime.timedelta(minutes=interval)
    else:
        next_interval_mark = now.replace(second=0, microsecond=0) + datetime.timedelta(minutes=interval - remainder)

    return next_interval_mark



if __name__ == "__main__":
    fetch_candle_data_thread = threading.Thread(target=fetch_candle_data_loop)
    # Start the threads
    fetch_candle_data_thread.start()
