#!/usr/bin/env python3
"""Script para criar usuário de teste com senha conhecida."""

import bcrypt
import psycopg2
from datetime import datetime

def create_test_user():
    """Cria um usuário de teste com senha conhecida."""
    # Senha conhecida
    password = "testpass123"
    
    # Gerar hash da senha
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    print(f"Senha: {password}")
    print(f"Hash gerado: {password_hash}")
    
    # Conectar ao banco de dados
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="fast_zero",
            user="fast_zero_user",
            password="fast_zero_password"
        )
        
        cursor = conn.cursor()
        
        # Deletar usuário se já existir
        cursor.execute("DELETE FROM users WHERE email = 'logintest@example.com';")
        
        # Inserir novo usuário
        cursor.execute("""
            INSERT INTO users (username, email, password, first_name, last_name, is_active, is_verified, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """, (
            'logintest',
            'logintest@example.com',
            password_hash,
            'Login',
            'Test',
            True,
            True,
            datetime.now(),
            datetime.now()
        ))
        
        conn.commit()
        print("\n✅ Usuário de teste criado com sucesso!")
        print("Email: logintest@example.com")
        print("Senha: testpass123")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao criar usuário: {e}")

if __name__ == "__main__":
    create_test_user()