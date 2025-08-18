#!/usr/bin/env python3
import bcrypt

# Hash armazenado no banco de dados
stored_hash = "$2b$12$Z8svNDdtPsNMXyVlHDXg/OaFhMlzF55axYWUejJsZeRbW9vWmvDuG"

# Senha fornecida pelo usuário
password = 'E@#$%^&12(),.?":{}|<!a'

# Verificar se a senha corresponde ao hash
if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
    print("✅ Senha CORRETA - corresponde ao hash")
else:
    print("❌ Senha INCORRETA - não corresponde ao hash")
    
print(f"Senha testada: {password}")
print(f"Hash no banco: {stored_hash}")