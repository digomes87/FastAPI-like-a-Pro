import asyncio
from fast_zero.async_services import get_async_user_service
from fast_zero.database import get_async_session
from fast_zero.schemas import UserCreate
from fast_zero.async_auth import authenticate_user

async def test_auth():
    async with get_async_session() as session:
        user_service = get_async_user_service(session)
        
        # Tentar criar usuário de teste
        try:
            user = await user_service.create_user(UserCreate(
                username='testuser',
                email='test@example.com',
                password='TestPass123!'
            ))
            print(f'Usuário criado: {user.username}, {user.email}')
        except Exception as e:
            print(f'Erro ao criar usuário (pode já existir): {e}')
        
        # Testar autenticação por email
        user = await authenticate_user(session, 'test@example.com', 'TestPass123!')
        print(f'Autenticação por email: {user}')
        
        # Testar autenticação por username
        user = await authenticate_user(session, 'testuser', 'TestPass123!')
        print(f'Autenticação por username: {user}')
        
        # Testar autenticação com senha incorreta
        user = await authenticate_user(session, 'test@example.com', 'WrongPassword')
        print(f'Autenticação com senha incorreta: {user}')

if __name__ == '__main__':
    asyncio.run(test_auth())