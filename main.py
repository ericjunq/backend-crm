from fastapi import FastAPI
from routers.auth_routers import auth_router
from routers.client_routers import client_router
from routers.token_routers import token_router
from database import Base, engine

app = FastAPI()

app.include_router(auth_router)
app.include_router(client_router)
app.include_router(token_router)

Base.metadata.create_all(bind=engine)