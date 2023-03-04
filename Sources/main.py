from fastapi import FastAPI

from routers import registration
from routers import accounts
from routers import locations
from routers import animal_types


app = FastAPI()


app.include_router(registration.router)
app.include_router(accounts.router)
app.include_router(locations.router)
app.include_router(animal_types.router)
