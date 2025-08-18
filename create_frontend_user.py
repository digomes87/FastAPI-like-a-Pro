import bcrypt
import psycopg2
from psycopg2.extras import RealDictCursor

# Gerar hash da senha
password = "testpass123"
salt = bcrypt.gensalt()
hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

print(f"Password: {password}")
print(f"Hashed: {hashed_password.decode('utf-8')}")

# Conectar ao banco e inserir usuário
try:
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="fast_zero",
        user="fast_zero_user",
        password="fast_zero_password"
    )
    
    cursor = conn.cursor()
    
    # Deletar usuário existente
    cursor.execute("DELETE FROM users WHERE email = %s", ('frontend@example.com',))
    
    # Inserir novo usuário
    cursor.execute("""
        INSERT INTO users (username, email, password, is_active, is_verified) 
        VALUES (%s, %s, %s, %s, %s)
    """, ('frontend@example.com', 'frontend@example.com', hashed_password.decode('utf-8'), True, True))
    
    conn.commit()
    print("Usuário criado com sucesso!")
    
except Exception as e:
    print(f"Erro: {e}")
finally:
    if conn:
        conn.close()