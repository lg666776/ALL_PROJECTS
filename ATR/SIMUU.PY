

# Initialize LTP and previous LTP to 0
previous_ltp = 102
candle_high = 100  # Replace this with your actual candle high value


# Simulate LTP updates
simulated_ltp_values = [100, 102, 98, 103, 108, 110]


for new_ltp in simulated_ltp_values:
    print(f"Previous LTP: {previous_ltp}")
    # Check if LTP crosses candle high from below
    if new_ltp > candle_high and previous_ltp <= candle_high:
        # Execute your trading strategy here (for this example, we'll print a message)
        print(f"Condition met: LTP {new_ltp} crossed above the candle high from below.")

    # Update the current LTP with the new LTP
    previous_ltp = new_ltp

    # Print the previous and current LTP values
    print(f"New LTP: {new_ltp}")

# Initialize ltp (you can set it to 0 initially)
import time

previous_ltp = 0
simulated_ltp_values = [102]

# Simulate a continuous loop (replace this with a real-time data source or event-driven system)
while True:
    # Simulate fetching the new LTP value (replace this with your real-time data fetch function)
    print(f"Previous LTP: {previous_ltp}")
    new_ltp = simulated_ltp_values

    # Update the ltp variable with the new LTP value
    previous_ltp = new_ltp

    time.sleep(1)

    # Print the previous and current LTP values
    print(f"New LTP: {new_ltp}")

    # Your trading logic here (e.g., check conditions and execute trades)

    import time
    import threading

    ltp1 = 0


    # Function to simulate LTP updates in a loop
    def simulate_ltp_updates():
        global ltp1
        # Simulate LTP updates
        ltp_values = [100, 102, 98, 103, 108, 110, 105, 106, 107, 102, 109, 110, 101, 102, 105, 110]

        # Initialize an index to keep track of the current LTP value
        index = 0

        # Simulate fetching LTP values in a while loop
        while index < len(ltp_values):
            ltp1 = ltp_values[index]

            # Increment the index to move to the next LTP value
            index += 1

            # Sleep for 1 second between iterations
            time.sleep(0.1)


    def simulate_real_time_ltp_updates():
        global ltp1
        previous_ltp = 0
        candle_high = 105

        # Simulate a continuous loop (replace this with a real-time data source or event-driven system)
        while True:
            # Simulate fetching the new LTP value (replace this with your real-time data fetch function)
            print(f"Previous LTP: {previous_ltp}")
            new_ltp = ltp1
            if new_ltp > candle_high and previous_ltp <= candle_high:
                # Execute your trading strategy here (for this example, we'll print a message)
                print(f"Condition met: NEW LTP {new_ltp} crossed above the candle high from below.")

            # Update the ltp variable with the new LTP value
            previous_ltp = new_ltp

            # Print the previous and current LTP values
            print(f"New LTP: {new_ltp}")

            time.sleep(0.1)


    # Create two threads for concurrent execution
    thread1 = threading.Thread(target=simulate_ltp_updates)
    thread2 = threading.Thread(target=simulate_real_time_ltp_updates)

    # Start both threads
    thread1.start()
    thread2.start()

    # Wait for both threads to finish
    thread1.join()
    thread2.join()