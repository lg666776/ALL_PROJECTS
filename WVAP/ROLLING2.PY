# Specify the file path where the data is stored
file_path = 'tokens.txt'

# Create a dictionary to store the values
token = {}

# Open the file in read mode
with open(file_path, 'r') as file:
    # Read each line in the file
    for line in file:
        # Split each line by ':' to separate the key and value
        key, value = line.strip().split(': ')
        # Remove double quotes if present
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]  # Remove double quotes
        # Store as a string
        token[key] = value

# Assuming ce_token is a list with one element
ce_token_value = token['ce_token']
print("Original Value:", ce_token_value)

# Extracting the string without single quotes using slicing
extracted_string = ce_token_value[0][1:-1]
print("Extracted String:", extracted_string)






