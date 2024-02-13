import pickle
import os
import time
from datetime import datetime
import threading
import datetime
import requests

infy_lp_value = None
infy_quantity = None
atr = 0


def avg_atr():
    global atr
    atr = 30


def ltp_quantity_loop():
    global infy_lp_value, infy_quantity, atr

    while True:
        try:
            # Read data from data_infy.pickle
            with open('data_infy.pickle', 'rb') as file:
                try:
                    data_infy = pickle.load(file)
                    if isinstance(data_infy, dict):
                        infy_lp_value = data_infy.get('infy_lp_value')
                        # Initialize the original quantity
                        original_quantity = data_infy.get('infy_quantity')

                        # Define the new variables
                        atr_75_prc = infy_lp_value * 0.0075
                        atr_100_prc = infy_lp_value * 0.0100
                        atr_150_prc = infy_lp_value * 0.0125
                        atr_200_prc = infy_lp_value * 0.0150

                        if atr <= atr_75_prc:
                            # Keep the original quantity
                            infy_quantity = original_quantity
                        elif atr > atr_75_prc and atr <= atr_100_prc:
                            # Keep 75% of the original quantity
                            infy_quantity = int(original_quantity * 0.75)
                        elif atr > atr_100_prc and atr <= atr_150_prc:
                            # Keep 50% of the original quantity
                            infy_quantity = int(original_quantity * 0.50)
                        elif atr > atr_150_prc and atr <= atr_200_prc:
                            # Keep 25% of the original quantity
                            infy_quantity = int(original_quantity * 0.25)
                        else:
                            # Keep 15% of the original quantity
                            infy_quantity = int(original_quantity * 0.15)

                except EOFError:
                    infy_lp_value = 0

        except FileNotFoundError:
            infy_lp_value = None

        except Exception as e:
            infy_lp_value = None

        time.sleep(0.01)


def print11():
    global infy_quantity, atr, infy_lp_value

    while True:
        print(infy_quantity)
        print(infy_lp_value)
        time.sleep(1)  # Add a sleep time to control the rate of printing


avg_atr()
# Create a thread for the print11 function
print11_thread = threading.Thread(target=print11)

# Start the thread
print11_thread.start()
# Create a thread for the ltp_quantity_loop function
ltp_quantity_thread = threading.Thread(target=ltp_quantity_loop)

# Start the thread
ltp_quantity_thread.start()


def mtm_loop():
    global buy_price, seling_price, infy_quantity, infy_lp_value, mtm_dictionary_file

    while True:
        if buy_price > 0:
            if infy_lp_value == 0:
                buy_mtm = 0  # Set buy_mtm to 0 when infy_lp_value is 0
            else:
                buy_mtm = infy_lp_value - buy_price

            final_buy_mtm = buy_mtm * infy_quantity
        else:
            buy_mtm = 0
            final_buy_mtm = 0

        if seling_price > 0:
            if infy_lp_value == 0:
                sell_mtm = 0  # Set sell_mtm to 0 when infy_lp_value is 0
            else:
                sell_mtm = seling_price - infy_lp_value
            final_sell_mtm = sell_mtm * infy_quantity
        else:
            sell_mtm = 0
            final_sell_mtm = 0

        # Create a dictionary to store these values
        mtm_dictionary = {
            'FINAL_Buy_MTM': final_buy_mtm,
            'FINAL_SELL_MTM': final_sell_mtm
        }
        # Assign values to the keys in trade_details_file
        mtm_dictionary_file.update(mtm_dictionary)
        save_data(MTM_DICT, mtm_dictionary_file)

        max_buy_mtm = mtm_dictionary_file.get('FINAL_Buy_MTM', 0)
        max_sell_mtm = mtm_dictionary_file.get('FINAL_SELL_MTM', 0)

        max_mtm = max_buy_mtm + max_sell_mtm
        formatted_final_mtm = f'{max_mtm:.2f}'  # Format to display with 2 decimal places
        print(formatted_final_mtm)

        time.sleep(1)  # Add a sleep time to control the rate of calculation and printing


def ltp_quantity_loop():
    global infy_lp_value, infy_quantity, atr_df

    while True:
        try:
            # Read data from data_infy.pickle
            with open('data_infy.pickle', 'rb') as file:
                try:
                    data_infy = pickle.load(file)
                    if isinstance(data_infy, dict):
                        infy_lp_value = data_infy.get('infy_lp_value')
                        # Initialize the original quantity
                        original_quantity = data_infy.get('infy_quantity')


                        # Define the new variables
                        atr_75_prc = infy_lp_value * 0.0075
                        atr_100_prc = infy_lp_value * 0.0100
                        atr_150_prc = infy_lp_value * 0.0125
                        atr_200_prc = infy_lp_value * 0.0150

                        if atr_df <= atr_75_prc:
                            # Keep the original quantity
                            infy_quantity = original_quantity
                        elif atr_df > atr_75_prc and atr_df <= atr_100_prc:
                            # Keep 75% of the original quantity
                            infy_quantity = int(original_quantity * 0.75)
                        elif atr_df > atr_100_prc and atr_df <= atr_150_prc:
                            # Keep 50% of the original quantity
                            infy_quantity = int(original_quantity * 0.50)
                        elif atr_df > atr_150_prc and atr_df <= atr_200_prc:
                            # Keep 25% of the original quantity
                            infy_quantity = int(original_quantity * 0.25)
                        else:
                            # Keep 15% of the original quantity
                            infy_quantity = int(original_quantity * 0.15)

                except EOFError:
                    infy_lp_value = 0

        except FileNotFoundError:
            infy_lp_value = 0

        except Exception as e:
            infy_lp_value = 0

        time.sleep(0.1)


  while True:
        if buy_price == 0:
            buy_mtm = previous_buy_mtm
            final_buy_mtm = previous_final_buy_mtm
        elif infy_lp_value == 0:
            buy_mtm = previous_buy_mtm
            final_buy_mtm = previous_final_buy_mtm
        else:
            buy_mtm = infy_lp_value - buy_price
            final_buy_mtm = buy_mtm * infy_quantity

        if sell_price == 0:
            sell_mtm = previous_sell_mtm
            final_sell_mtm = previous_final_sell_mtm
        elif infy_lp_value == 0:
            sell_mtm = previous_sell_mtm
            final_sell_mtm = previous_final_sell_mtm
        else:
            sell_mtm = sell_price - infy_lp_value
            final_sell_mtm = sell_mtm * infy_quantity

print('......................BPRC', buy_price)
print('......................SPRC', sell_price)

print('BUY PRICE', buy_price)
print('SELL PRICE', sell_price)
print('MTM', formatted_final_mtm)
last_valid_final_buy_mtm


last_valid_final_buy_mtm = 0  # Initialize last valid final buy MTM

while True:
    if infy_lp_value != 0:
        buy_mtm = infy_lp_value - buy_price
        final_buy_mtm = buy_mtm * infy_quantity

        # Add the new final buy MTM to the last valid value
        last_valid_final_buy_mtm += final_buy_mtm

    # If buy_price is 0, continue using the last_valid_final_buy_mtm
    else:
        continue

    # Assume buy_price changes in the next iteration for this example
    buy_price = 0  # Set buy_price to 0 for simplicity
