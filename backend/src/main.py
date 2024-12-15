from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from postgres.database import database
from routes.users_route import users_router
from routes.documents_route import documents_router
from typing import Annotated
from users.users_model import authenticate_user, create_access_token
from users.users_schema import Token
import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    await database.initialize_schema()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)
app.include_router(users_router)
app.include_router(documents_router)


@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token, token_type="bearer")


if __name__ == "__main__":
    print(database.database_url)
    uvicorn.run(app, host="0.0.0.0")