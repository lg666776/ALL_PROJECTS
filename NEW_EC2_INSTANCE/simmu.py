import asyncio
import time

import threading
ltp1 = None


# Function to simulate LTP updates in a loop
def simulate_ltp_updates():
    global ltp1
    # Simulate LTP updates
    ltp_values = [100, 102, 98, 103, 108, 110, 105, 106, 107, 102, 109, 110, 101, 102, 105, 110, 107, 103, 108, 150]

    # Initialize an index to keep track of the current LTP value
    index = 0

    # Simulate fetching LTP values in a while loop
    while index < len(ltp_values):
        ltp1 = ltp_values[index]

        # Increment the index to move to the next LTP value
        index += 1

        # Sleep for 0.1 seconds between iterations (asynchronous sleep)
        time.sleep(1)


# Function to simulate real-time LTP updates
def simulate_real_time_ltp_updates():
    global ltp1
    previous_ltp = None
    candle_high = 109

    # Simulate a continuous loop (replace this with a real-time data source or event-driven system)
    while True:
        # Simulate fetching the new LTP value (replace this with your real-time data fetch function)
        print(f"Previous LTP: {previous_ltp}")
        new_ltp = ltp1
        if previous_ltp and new_ltp:
            if new_ltp < candle_high:
                if previous_ltp >= candle_high:
                    print(f"Condition met: NEW LTP {new_ltp} crossed below the candle low from above.")

        # Update the ltp variable with the new LTP value
        previous_ltp = new_ltp

        # Print the previous and current LTP values
        print(f"New LTP: {new_ltp}")

        # Sleep for 0.1 seconds (asynchronous sleep)
        time.sleep(1)




# Run the asynchronous event loop
if __name__ == "__main__":
    ltp_data_thread = threading.Thread(target=simulate_ltp_updates)
    amt_loop_thread = threading.Thread(target=simulate_real_time_ltp_updates)

     
    # Start the threads
    ltp_data_thread.start()
    amt_loop_thread.start()

