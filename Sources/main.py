from fastapi import FastAPI

from routers import registration
from routers import accounts
from routers import locations


app = FastAPI()


app.include_router(registration.router)
app.include_router(accounts.router)
app.include_router(locations.router)
