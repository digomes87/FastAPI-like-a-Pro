#!/usr/bin/env python3
"""Script para testar verificação de senha com hash específico."""

import bcrypt

def test_password_verification():
    """Testa verificação de senha com o hash do banco."""
    # Hash do banco de dados
    stored_hash = "$2b$12$imWVKN1EZ3Alqm/8GCCAGupx.4ksF5bOetKH1Sa5o7WH1DU7UD/6a"
    
    # Senhas para testar
    passwords_to_test = [
        "secret",
        "TestPass123!",
        "testpass123",
        "password",
        "admin",
        "test123"
    ]
    
    print(f"Hash armazenado: {stored_hash}")
    print("\nTestando senhas:")
    
    for password in passwords_to_test:
        try:
            # Verificar se a senha corresponde ao hash
            is_valid = bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
            status = "✅ VÁLIDA" if is_valid else "❌ INVÁLIDA"
            print(f"  '{password}' -> {status}")
            
            if is_valid:
                print(f"\n🎉 SENHA ENCONTRADA: '{password}'")
                return password
        except Exception as e:
            print(f"  '{password}' -> ❌ ERRO: {e}")
    
    print("\n❌ Nenhuma senha testada funcionou")
    return None

if __name__ == "__main__":
    test_password_verification()