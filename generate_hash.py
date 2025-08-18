import os

import bcrypt

# Gerar hash da senha
password = os.getenv('PASSWORD_TO_HASH', 'CHANGE_THIS_PASSWORD')
salt = bcrypt.gensalt()
hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

print(hashed_password.decode('utf-8'))
