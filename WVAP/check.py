import json
import time

with open('formatted_final_mtm.txt', 'w') as file:
    file.write(str(formatted_final_mtm))

pwd3 = 100


def ll():
    while True:
        pwd = open('formatted_final_mtm.txt', 'r').read()
        # Check if the content is not empty
        if pwd:
            # Convert the content to a float
            numeric_value = float(pwd)
            print(numeric_value)
        else:
            pwd = 0

        time.sleep(0.1)


ll()

