# Smart Resume Parser

A full-stack NLP-powered resume parsing application. Upload a PDF or DOCX resume and get structured data with scoring and improvement suggestions.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)
![React](https://img.shields.io/badge/React-18-61DAFB)
![spaCy](https://img.shields.io/badge/spaCy-3.8-09A3D5)

## Features

- **Multi-format Support**: PDF and DOCX files
- **Contact Extraction**: Name, email, phone, LinkedIn, location
- **Skills Detection**: 150+ technical skills auto-detected
- **Experience Parsing**: Job titles, companies, dates, descriptions
- **Education Extraction**: Degrees, institutions, fields of study
- **Resume Scoring**: 0-100 score with grade (A+ to F)
- **Improvement Suggestions**: Actionable tips to improve your resume
- **Export Options**: Download as JSON or CSV
- **Modern UI**: React frontend with drag & drop upload

## Tech Stack

### Backend
- **FastAPI** - Modern async Python web framework
- **spaCy** - Industrial-strength NLP
- **PyMuPDF** - PDF text extraction
- **python-docx** - DOCX text extraction
- **Pydantic** - Data validation

### Frontend
- **React 18** - UI library
- **Vite** - Fast build tool
- **Tailwind CSS** - Utility-first styling

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/H41s3/Smart-Resume-Parser.git
cd Smart-Resume-Parser
```

### 2. Set up Backend

```bash
# Create virtual environment
python -m venv parser
source parser/bin/activate  # Windows: parser\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

### 3. Set up Frontend

```bash
cd frontend
npm install
```

### 4. Run the Application

**Terminal 1 - Backend:**
```bash
source parser/bin/activate
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 5. Open in Browser

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/parse` | Parse resume file (PDF/DOCX) |
| POST | `/api/v1/parse/text` | Parse plain text |
| POST | `/api/v1/export/json` | Export as JSON file |
| POST | `/api/v1/export/csv` | Export as CSV file |

### Example Request

```bash
curl -X POST "http://localhost:8000/api/v1/parse" \
  -F "file=@resume.pdf"
```

### Example Response

```json
{
  "success": true,
  "data": {
    "contact": {
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "(555) 123-4567",
      "linkedin": "linkedin.com/in/johndoe"
    },
    "skills": ["Python", "React", "AWS", "Docker"],
    "experience": [
      {
        "title": "Senior Software Engineer",
        "company": "Tech Corp",
        "start_date": "Jan 2020",
        "end_date": "Present",
        "highlights": ["Led team of 5", "Reduced latency by 40%"]
      }
    ],
    "education": [
      {
        "degree": "Bachelor's",
        "field_of_study": "Computer Science",
        "institution": "MIT"
      }
    ]
  },
  "score": {
    "total_score": 85,
    "grade": "A",
    "suggestions": [
      "Add more certifications",
      "Include a professional summary"
    ]
  }
}
```

## Project Structure

```
Smart-Resume-Parser/
├── app/                          # Backend (FastAPI)
│   ├── main.py                   # App entry point
│   ├── api/
│   │   └── routes.py             # API endpoints
│   ├── core/
│   │   └── config.py             # Configuration
│   ├── models/
│   │   └── schemas.py            # Pydantic models
│   └── services/
│       ├── document_extractor.py # PDF/DOCX text extraction
│       ├── resume_parser.py      # NLP parsing logic
│       └── resume_scorer.py      # Scoring algorithm
│
├── frontend/                     # Frontend (React)
│   ├── src/
│   │   ├── App.jsx               # Main component
│   │   └── components/
│   │       ├── FileUpload.jsx    # Drag & drop upload
│   │       └── ResumeDisplay.jsx # Results display
│   ├── package.json
│   └── vite.config.js
│
├── requirements.txt              # Python dependencies
├── LEARNING.md                   # Comprehensive project guide
├── TODO.md                       # Roadmap
└── README.md
```

## Scoring System

| Section | Max Points |
|---------|------------|
| Contact Info | 15 |
| Skills | 20 |
| Experience | 30 |
| Education | 15 |
| Summary | 10 |
| Certifications | 5 |
| Languages | 5 |

**Bonus points** for: 10+ skills, advanced degrees, certifications.

**Grades**: A+ (90+), A (80+), B (70+), C (60+), D (50+), F (<50)

## Configuration

Create a `.env` file in the root directory:

```env
DEBUG=false
SPACY_MODEL=en_core_web_sm
MAX_FILE_SIZE=10485760
```

## Extending

### Add Custom Skills

Edit `TECH_SKILLS` in `app/services/resume_parser.py`:

```python
TECH_SKILLS = [
    "Your Custom Skill",
    ...
]
```

### Use Larger NLP Model

```bash
python -m spacy download en_core_web_lg
```

Then set `SPACY_MODEL=en_core_web_lg` in `.env`.

## Learning

See [LEARNING.md](LEARNING.md) for a comprehensive guide covering:
- Project architecture
- How each file works
- How software engineers read code
- Real-world concepts (async/await, REST, Docker, etc.)
- Interview talking points

## Roadmap

See [TODO.md](TODO.md) for upcoming features:
- [ ] Database storage
- [ ] User authentication
- [ ] Batch upload
- [ ] Docker deployment

## License

MIT

## Contributing

Pull requests welcome! Please read the code style in existing files.
