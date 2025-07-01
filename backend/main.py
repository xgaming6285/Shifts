from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.routers import workers, shifts, tracking, google_sheets
from app.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Work Shifts Tracker",
    description="A comprehensive work shifts tracking system",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(workers.router, prefix="/api/workers", tags=["workers"])
app.include_router(shifts.router, prefix="/api/shifts", tags=["shifts"])
app.include_router(tracking.router, prefix="/api/tracking", tags=["tracking"])
app.include_router(google_sheets.router, prefix="/api/google-sheets", tags=["google-sheets"])

@app.get("/")
async def root():
    return {"message": "Work Shifts Tracker API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 