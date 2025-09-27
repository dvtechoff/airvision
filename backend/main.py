from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from dotenv import load_dotenv

from routes import current, forecast, weather, realtime, test

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="TEMPO Air Quality API",
    description="Real-time air quality monitoring using NASA TEMPO satellite data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003", "https://tempo-air-quality.vercel.app","http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(current.router, prefix="/api", tags=["current"])
app.include_router(forecast.router, prefix="/api", tags=["forecast"])
app.include_router(weather.router, prefix="/api", tags=["weather"])
app.include_router(realtime.router, prefix="/api", tags=["realtime"])
app.include_router(test.router, prefix="/api", tags=["test"])

@app.get("/")
async def root():
    return {
        "message": "TEMPO Air Quality API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "current": "/api/current?city=New York",
            "forecast": "/api/forecast?city=New York", 
            "weather": "/api/weather?city=New York",
            "realtime": "/api/realtime/process?city=New York",
            "cache_stats": "/api/realtime/cache/stats",
            "batch_process": "/api/realtime/batch/process?cities=New York,Los Angeles",
            "test_openaq": "/api/test/openaq?city=New York",
            "test_tempo": "/api/test/tempo?city=New York",
            "test_all_sources": "/api/test/data-sources?city=New York"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "tempo-air-quality-api"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
