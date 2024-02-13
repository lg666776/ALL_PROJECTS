user = 'FA87766'
pwd = 'Lg@741154'

with open('pass.txt', 'w') as file:
    file.write(str(pwd))

with open('user.txt', 'w') as file:
    file.write(str(user))
