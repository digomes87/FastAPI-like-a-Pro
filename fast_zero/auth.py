from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.settings import Settings

settings = Settings()

# Configuração do contexto de criptografia
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# Configuração do OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha em texto plano corresponde ao hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Gera o hash da senha."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Cria um token de acesso JWT."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> User:
    """Obtém o usuário atual a partir do token JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get('sub')
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = session.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    return user


def authenticate_user(session: Session, username_or_email: str, password: str):
    """Autentica um usuário verificando username/email e senha.

    Args:
        session: Sessão do banco de dados
        username_or_email: Username ou email do usuário
        password: Senha em texto plano

    Returns:
        User object se autenticado com sucesso, False caso contrário
    """
    # Tenta encontrar o usuário por username ou email
    user = (
        session.query(User)
        .filter(
            (User.username == username_or_email)
            | (User.email == username_or_email)
        )
        .first()
    )

    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user
