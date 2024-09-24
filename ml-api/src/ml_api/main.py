from fastapi import FastAPI
from ml_api.api.router import router

app = FastAPI()

app.include_router(router)


print("Hello, World!")
