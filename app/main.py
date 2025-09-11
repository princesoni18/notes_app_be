from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.utils.database import connect_to_mongo,close_mongo_connection
from app.routers import auth, notes
from contextlib import asynccontextmanager

# Database events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()


app = FastAPI(title="Notes API", description="A simple notes API with authentication", version="1.0.0",lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(notes.router, prefix="/api/notes", tags=["Notes"])

@app.get("/")
async def root():
    return {"message": "Welcome to Notes API"}


@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

# This is important for Vercel
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
