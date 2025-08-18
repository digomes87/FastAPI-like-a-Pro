#!/usr/bin/env python3
"""Script para testar credenciais de login específicas."""

import asyncio
from fast_zero.database import get_async_session
from fast_zero.async_auth import authenticate_user, verify_password
from fast_zero.async_services import get_async_user_service


async def test_login_credentials():
    """Testa as credenciais específicas do usuário."""
    username = "digomes"
    password = "E@#$%^&12(),.?\":{}|<!a"
    
    print(f"Testando credenciais:")
    print(f"Usuário: '{username}'")
    print(f"Senha: '{password}'")
    print(f"Comprimento da senha: {len(password)} caracteres")
    print()
    
    # Obter sessão do banco de dados
    async for session in get_async_session():
        try:
            # Testar autenticação
            user = await authenticate_user(session, username, password)
            
            if user:
                print("✅ AUTENTICAÇÃO BEM-SUCEDIDA!")
                print(f"ID do usuário: {user.id}")
                print(f"Username: {user.username}")
                print(f"Email: {user.email}")
                print(f"Ativo: {user.is_active}")
                print(f"Verificado: {user.is_verified}")
            else:
                print("❌ FALHA NA AUTENTICAÇÃO")
                
                # Vamos investigar mais detalhadamente
                user_service = get_async_user_service(session)
                user_from_db = await user_service.get_user_by_username(username)
                
                if user_from_db:
                    print(f"\n🔍 Usuário encontrado no banco:")
                    print(f"ID: {user_from_db.id}")
                    print(f"Username: {user_from_db.username}")
                    print(f"Email: {user_from_db.email}")
                    print(f"Ativo: {user_from_db.is_active}")
                    print(f"Verificado: {user_from_db.is_verified}")
                    print(f"Hash da senha: {user_from_db.password[:50]}...")
                    
                    # Testar verificação de senha diretamente
                    password_match = verify_password(password, user_from_db.password)
                    print(f"\n🔐 Verificação direta da senha: {'✅ MATCH' if password_match else '❌ NO MATCH'}")
                    
                    if not password_match:
                        print("\n⚠️  A senha não confere com o hash armazenado!")
                        print("Isso pode indicar que:")
                        print("1. A senha foi alterada após o cadastro")
                        print("2. Houve problema no hash durante o cadastro")
                        print("3. A senha digitada está incorreta")
                else:
                    print(f"\n❌ Usuário '{username}' não encontrado no banco de dados")
                    
        except Exception as e:
            print(f"❌ ERRO durante o teste: {e}")
            import traceback
            traceback.print_exc()
        
        break  # Sair do loop async for


if __name__ == "__main__":
    asyncio.run(test_login_credentials())