"""API routes for resume parsing."""

import csv
import json
from io import StringIO
from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.models.schemas import HealthResponse, ParsedResume, ParseResponse, ResumeScore
from app.services.document_extractor import DocumentExtractor
from app.services.resume_parser import ResumeParser
from app.services.resume_scorer import ResumeScorer

router = APIRouter()

# Initialize services
document_extractor = DocumentExtractor()
resume_parser = ResumeParser(spacy_model=settings.spacy_model)


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy", version=settings.app_version)


@router.post("/parse", response_model=ParseResponse)
async def parse_resume(
    file: UploadFile = File(..., description="Resume file to parse (PDF or DOCX)"),
    include_raw_text: bool = Query(
        False, description="Include raw extracted text in response"
    ),
    include_score: bool = Query(
        True, description="Include resume score and suggestions"
    ),
):
    """
    Parse a resume (PDF or DOCX) and extract structured information.

    Extracts:
    - Contact information (name, email, phone, LinkedIn, location)
    - Professional summary/objective
    - Skills (technical and soft skills)
    - Work experience (company, title, dates, descriptions)
    - Education (institution, degree, field of study)
    - Certifications
    - Languages

    Also provides:
    - Resume score (0-100) with grade
    - Section-by-section breakdown
    - Improvement suggestions

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
            detail=f"Invalid file type. Allowed types: {list(settings.allowed_extensions)}",
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
        # Extract text from document
        raw_text = document_extractor.extract_text_from_bytes(content, file_ext)

        if not raw_text.strip():
            return ParseResponse(
                success=False,
                error="Could not extract text from file. The file may be image-based or corrupted.",
            )

        # Parse the resume
        parsed_data = resume_parser.parse(raw_text, include_raw_text=include_raw_text)

        # Calculate score if requested
        score_data = None
        if include_score:
            score_result = ResumeScorer.score(parsed_data)
            score_data = ResumeScore(**score_result)

        return ParseResponse(success=True, data=parsed_data, score=score_data)

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
    include_score: bool = Query(
        True, description="Include resume score and suggestions"
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

        # Calculate score if requested
        score_data = None
        if include_score:
            score_result = ResumeScorer.score(parsed_data)
            score_data = ResumeScore(**score_result)

        return ParseResponse(success=True, data=parsed_data, score=score_data)
    except Exception as e:
        return ParseResponse(success=False, error=f"Failed to parse resume: {str(e)}")


@router.post("/export/json")
async def export_json(
    file: UploadFile = File(..., description="Resume file to parse and export"),
):
    """
    Parse a resume and export as downloadable JSON file.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    file_ext = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if file_ext not in settings.allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {list(settings.allowed_extensions)}",
        )

    content = await file.read()

    try:
        raw_text = document_extractor.extract_text_from_bytes(content, file_ext)
        parsed_data = resume_parser.parse(raw_text, include_raw_text=False)
        score_result = ResumeScorer.score(parsed_data)

        export_data = {
            "resume": parsed_data.model_dump(),
            "score": score_result,
        }

        json_str = json.dumps(export_data, indent=2)

        # Create filename from original
        base_name = file.filename.rsplit(".", 1)[0] if "." in file.filename else file.filename
        export_filename = f"{base_name}_parsed.json"

        return StreamingResponse(
            iter([json_str]),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={export_filename}"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export: {str(e)}")


@router.post("/export/csv")
async def export_csv(
    file: UploadFile = File(..., description="Resume file to parse and export"),
):
    """
    Parse a resume and export as downloadable CSV file.

    CSV contains flattened resume data suitable for spreadsheets.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    file_ext = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if file_ext not in settings.allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {list(settings.allowed_extensions)}",
        )

    content = await file.read()

    try:
        raw_text = document_extractor.extract_text_from_bytes(content, file_ext)
        parsed_data = resume_parser.parse(raw_text, include_raw_text=False)
        score_result = ResumeScorer.score(parsed_data)

        # Create CSV content
        output = StringIO()
        writer = csv.writer(output)

        # Write header and basic info
        writer.writerow(["Section", "Field", "Value"])
        writer.writerow([])

        # Contact info
        writer.writerow(["Contact", "Name", parsed_data.contact.name or ""])
        writer.writerow(["Contact", "Email", parsed_data.contact.email or ""])
        writer.writerow(["Contact", "Phone", parsed_data.contact.phone or ""])
        writer.writerow(["Contact", "LinkedIn", parsed_data.contact.linkedin or ""])
        writer.writerow(["Contact", "Location", parsed_data.contact.location or ""])
        writer.writerow([])

        # Summary
        writer.writerow(["Summary", "Text", parsed_data.summary or ""])
        writer.writerow([])

        # Skills
        writer.writerow(["Skills", "All Skills", ", ".join(parsed_data.skills)])
        writer.writerow([])

        # Experience
        for i, exp in enumerate(parsed_data.experience, 1):
            writer.writerow([f"Experience {i}", "Title", exp.title or ""])
            writer.writerow([f"Experience {i}", "Company", exp.company or ""])
            writer.writerow([f"Experience {i}", "Start Date", exp.start_date or ""])
            writer.writerow([f"Experience {i}", "End Date", exp.end_date or ""])
            writer.writerow([f"Experience {i}", "Description", exp.description or ""])
            writer.writerow([f"Experience {i}", "Highlights", "; ".join(exp.highlights)])
        writer.writerow([])

        # Education
        for i, edu in enumerate(parsed_data.education, 1):
            writer.writerow([f"Education {i}", "Institution", edu.institution or ""])
            writer.writerow([f"Education {i}", "Degree", edu.degree or ""])
            writer.writerow([f"Education {i}", "Field", edu.field_of_study or ""])
            writer.writerow([f"Education {i}", "End Date", edu.end_date or ""])
        writer.writerow([])

        # Certifications
        writer.writerow(["Certifications", "All", ", ".join(parsed_data.certifications)])
        writer.writerow([])

        # Languages
        writer.writerow(["Languages", "All", ", ".join(parsed_data.languages)])
        writer.writerow([])

        # Score
        writer.writerow(["Score", "Total", score_result["total_score"]])
        writer.writerow(["Score", "Grade", score_result["grade"]])

        csv_content = output.getvalue()

        # Create filename from original
        base_name = file.filename.rsplit(".", 1)[0] if "." in file.filename else file.filename
        export_filename = f"{base_name}_parsed.csv"

        return StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={export_filename}"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export: {str(e)}")
