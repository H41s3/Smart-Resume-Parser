# Smart Resume Parser

An NLP-powered REST API that extracts structured information from PDF resumes. Built with FastAPI and spaCy.

## Features

- **Contact Extraction**: Name, email, phone, LinkedIn URL, location
- **Skills Detection**: Technical skills, programming languages, frameworks, tools
- **Experience Parsing**: Job titles, companies, dates, descriptions, highlights
- **Education Extraction**: Degrees, institutions, fields of study, graduation dates
- **Additional Info**: Certifications, spoken languages, professional summary

## Tech Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **spaCy** - Industrial-strength NLP library
- **PyMuPDF** - PDF text extraction
- **Pydantic** - Data validation and serialization

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/H41s3/Smart-Resume-Parser.git
cd Smart-Resume-Parser
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Download spaCy model

```bash
python -m spacy download en_core_web_sm
```

## Usage

### Start the server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints

#### Health Check

```bash
GET /api/v1/health
```

#### Parse PDF Resume

```bash
POST /api/v1/parse
```

Upload a PDF file to extract structured data.

**Example with curl:**

```bash
curl -X POST "http://localhost:8000/api/v1/parse" \
  -H "accept: application/json" \
  -F "file=@resume.pdf"
```

**Example with Python:**

```python
import requests

with open("resume.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/parse",
        files={"file": f}
    )
    data = response.json()
    print(data)
```

#### Parse Plain Text

```bash
POST /api/v1/parse/text
```

Parse resume from plain text input.

### Response Format

```json
{
  "success": true,
  "data": {
    "contact": {
      "name": "John Doe",
      "email": "john.doe@email.com",
      "phone": "(555) 123-4567",
      "linkedin": "linkedin.com/in/johndoe",
      "location": "San Francisco, CA"
    },
    "summary": "Experienced software engineer with 5+ years...",
    "skills": [
      "Python",
      "JavaScript",
      "React",
      "Node.js",
      "PostgreSQL",
      "AWS",
      "Docker"
    ],
    "experience": [
      {
        "company": "Tech Corp",
        "title": "Senior Software Engineer",
        "start_date": "Jan 2020",
        "end_date": "Present",
        "description": "Led development of microservices architecture",
        "highlights": [
          "Reduced API latency by 40%",
          "Mentored team of 5 junior developers"
        ]
      }
    ],
    "education": [
      {
        "institution": "University of California",
        "degree": "Bachelor's",
        "field_of_study": "Computer Science",
        "end_date": "2018"
      }
    ],
    "certifications": [
      "AWS Certified Solutions Architect"
    ],
    "languages": [
      "English",
      "Spanish"
    ]
  }
}
```

## Project Structure

```
smart-resume-parser/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── api/
│   │   └── routes.py        # API endpoints
│   ├── core/
│   │   └── config.py        # Configuration
│   ├── models/
│   │   └── schemas.py       # Pydantic models
│   └── services/
│       ├── pdf_extractor.py # PDF text extraction
│       └── resume_parser.py # NLP parsing logic
├── requirements.txt
├── .gitignore
└── README.md
```

## Configuration

Environment variables can be set in a `.env` file:

```env
DEBUG=false
SPACY_MODEL=en_core_web_sm
MAX_FILE_SIZE=10485760
```

## Extending the Parser

### Adding Custom Skills

Edit `TECH_SKILLS` list in `app/services/resume_parser.py`:

```python
TECH_SKILLS = [
    # Add your custom skills
    "Your Skill",
    ...
]
```

### Using a Different spaCy Model

For better accuracy, use a larger model:

```bash
python -m spacy download en_core_web_lg
```

Then set the environment variable:

```env
SPACY_MODEL=en_core_web_lg
```

## Limitations

- Only supports PDF files (text-based, not scanned images)
- Best results with well-formatted resumes
- English language only (by default)
- May require tuning for specific resume formats

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
