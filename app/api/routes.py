"""API routes for resume parsing."""

from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from app.core.config import settings
from app.models.schemas import HealthResponse, ParsedResume, ParseResponse
from app.services.pdf_extractor import PDFExtractor
from app.services.resume_parser import ResumeParser

router = APIRouter()

# Initialize services
pdf_extractor = PDFExtractor()
resume_parser = ResumeParser(spacy_model=settings.spacy_model)


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy", version=settings.app_version)


@router.post("/parse", response_model=ParseResponse)
async def parse_resume(
    file: UploadFile = File(..., description="PDF resume file to parse"),
    include_raw_text: bool = Query(
        False, description="Include raw extracted text in response"
    ),
):
    """
    Parse a PDF resume and extract structured information.

    Extracts:
    - Contact information (name, email, phone, LinkedIn, location)
    - Professional summary/objective
    - Skills (technical and soft skills)
    - Work experience (company, title, dates, descriptions)
    - Education (institution, degree, field of study)
    - Certifications
    - Languages

    Returns structured JSON data that can be used for:
    - Applicant tracking systems
    - Candidate matching
    - Resume databases
    """
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    file_ext = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if file_ext not in settings.allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {settings.allowed_extensions}",
        )

    # Read file content
    content = await file.read()

    # Validate file size
    if len(content) > settings.max_file_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.max_file_size // (1024 * 1024)}MB",
        )

    try:
        # Extract text from PDF
        raw_text = pdf_extractor.extract_text_from_bytes(content)

        if not raw_text.strip():
            return ParseResponse(
                success=False,
                error="Could not extract text from PDF. The file may be image-based or corrupted.",
            )

        # Parse the resume
        parsed_data = resume_parser.parse(raw_text, include_raw_text=include_raw_text)

        return ParseResponse(success=True, data=parsed_data)

    except ValueError as e:
        return ParseResponse(success=False, error=str(e))
    except Exception as e:
        return ParseResponse(success=False, error=f"Failed to parse resume: {str(e)}")


@router.post("/parse/text", response_model=ParseResponse)
async def parse_resume_text(
    text: str,
    include_raw_text: bool = Query(
        False, description="Include raw text in response"
    ),
):
    """
    Parse resume from plain text input.

    Useful for:
    - Already extracted text
    - Copy-pasted resume content
    - Testing the parser
    """
    if not text.strip():
        return ParseResponse(success=False, error="No text provided")

    try:
        parsed_data = resume_parser.parse(text, include_raw_text=include_raw_text)
        return ParseResponse(success=True, data=parsed_data)
    except Exception as e:
        return ParseResponse(success=False, error=f"Failed to parse resume: {str(e)}")
