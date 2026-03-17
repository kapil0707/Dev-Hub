from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.events import router as events_router

app = FastAPI(title="DevHub Analytics Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events_router, prefix="/events")

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "analytics"}
