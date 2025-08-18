import bcrypt

# Gerar hash da senha
password = "testpass123"
salt = bcrypt.gensalt()
hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

print(hashed_password.decode('utf-8'))