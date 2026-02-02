"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import settings

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    ## Smart Resume Parser API

    An NLP-powered API that extracts structured information from PDF resumes.

    ### Features

    - **Contact Extraction**: Name, email, phone, LinkedIn, location
    - **Skills Detection**: Technical skills, programming languages, tools
    - **Experience Parsing**: Job titles, companies, dates, descriptions
    - **Education Extraction**: Degrees, institutions, fields of study
    - **Additional Info**: Certifications, languages

    ### Usage

    Upload a PDF resume to `/api/v1/parse` and receive structured JSON data.

    ### Example Response

    ```json
    {
      "success": true,
      "data": {
        "contact": {
          "name": "John Doe",
          "email": "john@example.com",
          "phone": "(555) 123-4567"
        },
        "skills": ["Python", "JavaScript", "React"],
        "experience": [...],
        "education": [...]
      }
    }
    ```
    """,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1", tags=["Resume Parsing"])


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/api/v1/health",
    }
