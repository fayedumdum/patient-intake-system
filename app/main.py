from fastapi import FastAPI
from app.api.router import router as ingest_router
from app.db.init_db import async_init_db
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    await async_init_db()
    yield


app = FastAPI(title="Patient Intake System", lifespan=lifespan)

app.include_router(ingest_router)
    
    
@app.get("/")
def root():
    return {"status": "running"}
