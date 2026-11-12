import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()

from routes.resume import router as resume_router
from routes.jobs import router as jobs_router
from routes.apply import router as apply_router

app = FastAPI(
    title="AI Job Hunter",
    description="Analyze your resume, search jobs across portals, and auto-apply with AI.",
    version="1.0.0",
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount screenshots as static files
os.makedirs("screenshots", exist_ok=True)
app.mount("/screenshots", StaticFiles(directory="screenshots"), name="screenshots")

# Register routers
app.include_router(resume_router)
app.include_router(jobs_router)
app.include_router(apply_router)


@app.get("/")
async def root():
    return {
        "app": "AI Job Hunter",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
