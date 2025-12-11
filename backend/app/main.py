from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.client import db_client
from app.api import auth, orgs

@asynccontextmanager
async def lifelong(app: FastAPI):
    # Startup
    db_client.connect()
    yield
    # Shutdown
    db_client.close()

app = FastAPI(title="Multi-Tenant Organization Backend", lifespan=lifelong)

app.include_router(auth.router, tags=["Authentication"])
app.include_router(orgs.router)

@app.get("/")
async def root():
    return {"message": "Service is running"}
