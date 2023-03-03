from fastapi import FastAPI

from routers import registration
from routers import accounts


app = FastAPI()


app.include_router(registration.router)
app.include_router(accounts.router)