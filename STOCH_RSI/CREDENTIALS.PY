user = 'FA87766'
pwd = 'Lg@741154'

# Create a dictionary to store these values
user_pass = {
    'user': user,
    'pwd': pwd
}

with open('pass.txt', 'w') as file:
    file.write(user_pass['pwd'])

with open('user.txt', 'w') as file:
    file.write(user_pass['user'])

