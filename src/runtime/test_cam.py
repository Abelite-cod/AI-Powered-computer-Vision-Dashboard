import bcrypt
hashed = bcrypt.hashpw(b'mypassword', bcrypt.gensalt())
print(hashed)