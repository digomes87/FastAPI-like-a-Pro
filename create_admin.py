import asyncio
from fast_zero.async_services import get_async_user_service
from fast_zero.database import get_async_session
from fast_zero.schemas import UserCreate

async def create_admin():
    async with get_async_session() as session:
        user_service = get_async_user_service(session)
        try:
            user = await user_service.create_user(UserCreate(
                username='admin',
                email='admin@example.com',
                password='secret'
            ))
            print(f'Admin criado: {user.username}, {user.email}')
        except Exception as e:
            print(f'Erro: {e}')

if __name__ == '__main__':
    asyncio.run(create_admin())