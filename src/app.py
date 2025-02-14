from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.database import engine
from src.database.models import Base
from src.routes import admin, otp, business, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Database Initialization
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield
    
    
app = FastAPI(title="WhatsApp OTP Service", version="1.0.0", lifespan=lifespan)

# Enabled CORS 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Included routers
app.include_router(admin.router)
app.include_router(business.router)
app.include_router(otp.router)
app.include_router(auth.router)


@app.get("/")
async def root():
    return {"message": "WhatsApp OTP Service is running!"}
