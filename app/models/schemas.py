"""Pydantic schemas for API request/response models."""

from pydantic import BaseModel, EmailStr, Field


class ContactInfo(BaseModel):
    """Extracted contact information."""

    name: str | None = None
    email: str | None = None
    phone: str | None = None
    linkedin: str | None = None
    location: str | None = None


class WorkExperience(BaseModel):
    """Single work experience entry."""

    company: str | None = None
    title: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None
    highlights: list[str] = Field(default_factory=list)


class Education(BaseModel):
    """Single education entry."""

    institution: str | None = None
    degree: str | None = None
    field_of_study: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    gpa: str | None = None


class ParsedResume(BaseModel):
    """Complete parsed resume data."""

    contact: ContactInfo = Field(default_factory=ContactInfo)
    summary: str | None = None
    skills: list[str] = Field(default_factory=list)
    experience: list[WorkExperience] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    raw_text: str | None = None


class ScoreBreakdown(BaseModel):
    """Score breakdown for a section."""

    score: int
    max: int
    details: str


class ResumeScore(BaseModel):
    """Resume scoring result."""

    total_score: int
    grade: str
    base_score: int
    bonus_score: int
    breakdown: dict[str, ScoreBreakdown]
    bonuses: dict[str, int]
    suggestions: list[str]


class ParseResponse(BaseModel):
    """API response for resume parsing."""

    success: bool
    data: ParsedResume | None = None
    score: ResumeScore | None = None
    error: str | None = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
