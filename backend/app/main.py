from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import ai_providers, wp_sites, projects, posts, jobs

app = FastAPI(
    title="WordPress AI Writer",
    description="AI-powered WordPress post generation tool",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ai_providers.router)
app.include_router(wp_sites.router)
app.include_router(projects.router)
app.include_router(posts.router)
app.include_router(jobs.router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "WordPress AI Writer"}


@app.get("/")
async def root():
    return {
        "message": "WordPress AI Writer API",
        "docs": "/docs",
        "health": "/health",
    }
