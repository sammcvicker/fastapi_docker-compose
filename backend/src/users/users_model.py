from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from postgres.database import database
from typing import Annotated
from users.users_schema import User, UserInDB, TokenData
from asyncpg.exceptions import UniqueViolationError
import jwt

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "087df75fe34621f28852d4352ea326ffb52cc5eb9baa18dcbc5534c3d7af6abd"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password) -> str:
    return pwd_context.hash(password)


async def get_user_by_username(username: str) -> UserInDB | None:
    query = "SELECT id, username, hashed_password FROM users WHERE username = $1"
    async with database.pool.acquire() as connection:
        row = await connection.fetchrow(query, username)
        if row:
            return UserInDB(
                id=row["id"],
                username=row["username"],
                hashed_password=row["hashed_password"],
            )
        return None


async def authenticate_user(username: str, password: str) -> UserInDB | bool:
    user = await get_user_by_username(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = await get_user_by_username(token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def insert_user(user: User, password: str) -> User:
    query = "INSERT INTO users (username, hashed_password) VALUES ($1, $2)"
    hashed_password = get_password_hash(password)
    try:
        async with database.pool.acquire() as connection:
            await connection.execute(
                query,
                user.username,
                hashed_password,
            )
    except UniqueViolationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    return user
