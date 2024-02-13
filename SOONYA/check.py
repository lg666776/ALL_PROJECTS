exit1_sell_orderno = None  # Initializing the global variable


def set_value():
    global exit1_sell_orderno
    exit1_sell_orderno = 100  # Assigning an integer value


# Calling the functions to set different values
set_value()
print(exit1_sell_orderno)  # Output: 42

