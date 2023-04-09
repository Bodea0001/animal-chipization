from fastapi import FastAPI, status
from fastapi.encoders import jsonable_encoder
from  fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from routers import registration
from routers import accounts
from routers import locations
from routers import animal_types
from routers import animals
from routers import visited_locations
from routers import areas


app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder({"detail": exc.errors()})
    )


app.include_router(registration.router)
app.include_router(accounts.router)
app.include_router(locations.router)
app.include_router(animal_types.router)
app.include_router(animals.router)
app.include_router(visited_locations.router)
app.include_router(areas.router)
