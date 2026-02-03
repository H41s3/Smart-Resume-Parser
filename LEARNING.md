# Smart Resume Parser - Complete Learning Guide

A comprehensive guide to understanding this project and how software engineers read code.

---

## TABLE OF CONTENTS

1. [Project Architecture Overview](#1-project-architecture-overview)
2. [How The Data Flows](#2-how-the-data-flows)
3. [Backend Files Explained](#3-backend-files-explained)
4. [Frontend Files Explained](#4-frontend-files-explained)
5. [How Software Engineers Read Code](#5-how-software-engineers-read-code)
6. [What To Memorize vs What To Google](#6-what-to-memorize-vs-what-to-google)
7. [Cheat Sheet For Explaining This Project](#7-cheat-sheet-for-explaining-this-project)

---

## 1. PROJECT ARCHITECTURE OVERVIEW

```
resume_parser/
├── app/                          # BACKEND (Python/FastAPI)
│   ├── main.py                   # App entry point - starts the server
│   ├── api/
│   │   └── routes.py             # API endpoints (where requests come in)
│   ├── core/
│   │   └── config.py             # Settings (file size limits, allowed types)
│   ├── models/
│   │   └── schemas.py            # Data structures (what the JSON looks like)
│   └── services/                 # Business logic (the actual work)
│       ├── document_extractor.py # Extracts text from PDF/DOCX
│       ├── resume_parser.py      # NLP parsing (the brain)
│       └── resume_scorer.py      # Calculates score
│
├── frontend/                     # FRONTEND (React/Vite)
│   └── src/
│       ├── App.jsx               # Main component (controls everything)
│       └── components/
│           ├── FileUpload.jsx    # Drag & drop upload UI
│           └── ResumeDisplay.jsx # Shows parsed results
│
├── requirements.txt              # Python dependencies
└── package.json (in frontend/)   # JavaScript dependencies
```

### KEY CONCEPT: Separation of Concerns

Each file has ONE job:
- document_extractor.py → ONLY extracts text from files
- resume_parser.py      → ONLY parses text into structured data
- resume_scorer.py      → ONLY calculates scores
- routes.py             → ONLY handles HTTP requests

This makes code easier to:
- Test (test each piece separately)
- Debug (know exactly where to look)
- Modify (change one thing without breaking others)

---

## 2. HOW THE DATA FLOWS

```
USER UPLOADS FILE
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND (React)                                           │
│                                                             │
│  App.jsx                                                    │
│    └── handleFileUpload()                                   │
│          └── fetch('/api/v1/parse', { file })              │
└─────────────────────────────────────────────────────────────┘
       │
       ▼ HTTP POST Request
┌─────────────────────────────────────────────────────────────┐
│  BACKEND (FastAPI)                                          │
│                                                             │
│  routes.py: @router.post("/parse")                         │
│       │                                                     │
│       ▼                                                     │
│  document_extractor.extract_text_from_bytes(file_bytes)    │
│       │                                                     │
│       ▼ Returns: "John Doe\njohn@email.com\nSkills:..."    │
│                                                             │
│  resume_parser.parse(raw_text)                             │
│       │                                                     │
│       ▼ Returns: ParsedResume(contact=..., skills=...)     │
│                                                             │
│  ResumeScorer.score(parsed_data)                           │
│       │                                                     │
│       ▼ Returns: {total_score: 85, grade: "A", ...}        │
│                                                             │
│  Return JSON Response                                       │
└─────────────────────────────────────────────────────────────┘
       │
       ▼ HTTP Response (JSON)
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND (React)                                           │
│                                                             │
│  App.jsx                                                    │
│    └── setResumeData(response.data)                        │
│    └── setScoreData(response.score)                        │
│                                                             │
│  ResumeDisplay.jsx                                          │
│    └── Renders the data beautifully                        │
└─────────────────────────────────────────────────────────────┘
```

### SIMPLE VERSION:
File → Text → Structured Data → Score → JSON → Display

---

## 3. BACKEND FILES EXPLAINED

### 3.1 main.py - The Entry Point

```python
# What it does:
app = FastAPI(...)                    # Creates the API application
app.add_middleware(CORSMiddleware...) # Allows frontend to talk to backend
app.include_router(router, prefix="/api/v1")  # Mounts routes at /api/v1
```

CORS = Cross-Origin Resource Sharing
- Frontend runs on localhost:3000
- Backend runs on localhost:8000
- Without CORS, browser blocks the request (security feature)
- CORS middleware says "it's okay, let them talk"


### 3.2 config.py - Settings

```python
class Settings(BaseSettings):
    app_name: str = "Smart Resume Parser"
    max_file_size: int = 10 * 1024 * 1024  # 10MB in bytes
    allowed_extensions: set[str] = {".pdf", ".docx"}
    spacy_model: str = "en_core_web_sm"
```

WHY USE THIS:
- Change settings in ONE place
- Can override with .env file (for production)
- Other files import: `from app.core.config import settings`


### 3.3 schemas.py - Data Structures

```python
# These define the SHAPE of data

class ContactInfo(BaseModel):
    name: str | None = None      # str | None means "string or nothing"
    email: str | None = None
    phone: str | None = None

class ParsedResume(BaseModel):
    contact: ContactInfo         # Nested object
    skills: list[str]            # List of strings
    experience: list[WorkExperience]

class ParseResponse(BaseModel):  # What the API returns
    success: bool
    data: ParsedResume | None
    score: ResumeScore | None
    error: str | None
```

WHY PYDANTIC:
- Automatic validation (rejects bad data)
- Auto-generates API documentation at /docs
- Converts Python objects to JSON automatically


### 3.4 document_extractor.py - Text Extraction

```python
class DocumentExtractor:
    
    def extract_text_from_bytes(cls, content: bytes, file_type: str) -> str:
        """
        INPUT:  Raw file bytes + file extension
        OUTPUT: Plain text string
        """
        if file_type == ".pdf":
            # Use PyMuPDF library
            doc = fitz.open(stream=content, filetype="pdf")
            for page in doc:
                text += page.get_text()
                
        elif file_type == ".docx":
            # Use python-docx library
            doc = Document(BytesIO(content))
            for paragraph in doc.paragraphs:
                text += paragraph.text
```

THIS FILE ONLY CARES ABOUT: Converting files to text
IT DOESN'T KNOW ABOUT: Parsing, scoring, or APIs


### 3.5 resume_parser.py - The NLP Brain (Most Important!)

```python
class ResumeParser:
    
    # CONFIGURATION: What to look for
    TECH_SKILLS = ["Python", "Java", "React", ...]  # 150+ skills
    DEGREE_PATTERNS = [r"bachelor", r"master", r"ph\.?d"]
    SECTION_HEADERS = {
        "experience": ["experience", "work history", ...],
        "education": ["education", "academic", ...],
    }
    
    def __init__(self):
        # Load spaCy NLP model (pre-trained on English text)
        self.nlp = spacy.load("en_core_web_sm")
        
        # Set up skill matcher
        self.skill_matcher = PhraseMatcher(self.nlp.vocab)
        # Add all skills as patterns to match
```

THE MAIN METHOD:
```python
def parse(self, text: str) -> ParsedResume:
    # Step 1: Process text with NLP
    doc = self.nlp(text)
    # Now 'doc' has entities, parts of speech, etc.
    
    # Step 2: Extract each section
    contact = self._extract_contact_info(text, doc)
    skills = self._extract_skills(text, doc)
    experience = self._extract_experience(text)
    education = self._extract_education(text)
    
    # Step 3: Return structured data
    return ParsedResume(
        contact=contact,
        skills=skills,
        experience=experience,
        education=education,
        ...
    )
```

HOW EACH EXTRACTION WORKS:

```python
# EMAIL: Use regex (pattern matching)
email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
email = re.search(email_pattern, text)
# Matches: john.doe@company.com

# NAME: Use spaCy's Named Entity Recognition
for entity in doc.ents:
    if entity.label_ == "PERSON":
        name = entity.text
# spaCy knows "John Doe" is a person, "Google" is an organization

# SKILLS: Use PhraseMatcher
matches = self.skill_matcher(doc)
# Finds all occurrences of "Python", "React", etc. in text

# SECTIONS: Find headers, extract text between them
def _get_section_text(self, text, section_name):
    # Find "EXPERIENCE" or "Work History" header
    # Return everything until next header
```


### 3.6 resume_scorer.py - Scoring Logic

```python
class ResumeScorer:
    
    # Points available per section
    WEIGHTS = {
        "contact": 15,      # Name, email, phone = 15 points max
        "skills": 20,       # More skills = more points
        "experience": 30,   # Most important section
        "education": 15,
        "certifications": 5,
        "languages": 5,
    }
    # Total: 100 points (before bonuses)
```

SCORING LOGIC:
```python
# Skills scoring
if len(skills) >= 10:
    score = 20  # Full points
elif len(skills) >= 7:
    score = 15
elif len(skills) >= 4:
    score = 10
else:
    score = 5

# Bonuses (extra points)
if has_masters_or_phd:
    bonus += 5
if has_certifications:
    bonus += 3

# Final grade
if total >= 90: grade = "A+"
elif total >= 80: grade = "A"
elif total >= 70: grade = "B"
...
```


### 3.7 routes.py - API Endpoints

```python
@router.post("/parse")
async def parse_resume(
    file: UploadFile = File(...),        # Required file upload
    include_score: bool = Query(True),   # Optional query param
):
    # 1. VALIDATE
    if file_ext not in settings.allowed_extensions:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    # 2. EXTRACT TEXT
    raw_text = document_extractor.extract_text_from_bytes(content, file_ext)
    
    # 3. PARSE
    parsed_data = resume_parser.parse(raw_text)
    
    # 4. SCORE
    score_data = ResumeScorer.score(parsed_data)
    
    # 5. RETURN
    return ParseResponse(success=True, data=parsed_data, score=score_data)
```

ALL ENDPOINTS:
| Method | Endpoint       | Purpose                    |
|--------|----------------|----------------------------|
| GET    | /health        | Check if server is running |
| POST   | /parse         | Upload file, get JSON      |
| POST   | /parse/text    | Send text, get JSON        |
| POST   | /export/json   | Download as .json file     |
| POST   | /export/csv    | Download as .csv file      |

---

## 4. FRONTEND FILES EXPLAINED

### 4.1 App.jsx - Main Component

```jsx
function App() {
    // STATE: Data that changes and causes re-renders
    const [resumeData, setResumeData] = useState(null)
    const [scoreData, setScoreData] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
```

WHAT IS STATE:
- Variables that, when changed, make React update the UI
- useState(null) = starts as null
- setResumeData(newData) = updates the value AND re-renders

THE API CALL:
```jsx
const handleFileUpload = async (file) => {
    setLoading(true)              // Show spinner
    
    const formData = new FormData()
    formData.append('file', file) // Attach file
    
    const response = await fetch('/api/v1/parse', {
        method: 'POST',
        body: formData,
    })
    
    const data = await response.json()
    
    if (data.success) {
        setResumeData(data.data)  // Store parsed data
        setScoreData(data.score)  // Store score
    } else {
        setError(data.error)      // Store error message
    }
    
    setLoading(false)             // Hide spinner
}
```

CONDITIONAL RENDERING:
```jsx
return (
    <div>
        {!resumeData ? (
            // No data yet → show upload form
            <FileUpload onUpload={handleFileUpload} loading={loading} />
        ) : (
            // Have data → show results
            <ResumeDisplay data={resumeData} score={scoreData} />
        )}
    </div>
)
```


### 4.2 FileUpload.jsx - Upload Component

```jsx
function FileUpload({ onUpload, loading }) {
    // PROPS: Data passed from parent (App.jsx)
    // onUpload = function to call when file is selected
    // loading = boolean to show spinner
```

DRAG AND DROP:
```jsx
const handleDrop = (e) => {
    e.preventDefault()                    // Stop browser from opening file
    const file = e.dataTransfer.files[0]  // Get the dropped file
    handleFile(file)                      // Process it
}

const handleFile = (file) => {
    // Validate file type
    if (!validTypes.includes(file.type)) {
        alert('Please upload a PDF or DOCX')
        return
    }
    onUpload(file)  // Call parent's function
}
```


### 4.3 ResumeDisplay.jsx - Results Display

```jsx
function ResumeDisplay({ data, score }) {
    // DESTRUCTURE: Pull out nested properties
    const { contact, skills, experience, education } = data
```

CONDITIONAL SECTIONS:
```jsx
{/* Only show skills section if there are skills */}
{skills && skills.length > 0 && (
    <Section title="Skills">
        {skills.map((skill, index) => (
            <span key={index}>{skill}</span>
        ))}
    </Section>
)}
```

WHY key={index}:
- React needs unique IDs to track list items
- Helps React update efficiently when list changes


### 4.4 vite.config.js - Build Configuration

```javascript
export default {
    server: {
        port: 3000,
        proxy: {
            '/api': {
                target: 'http://localhost:8000',
            },
        },
    },
}
```

WHAT PROXY DOES:
- Frontend: localhost:3000
- Backend: localhost:8000
- When frontend calls `/api/v1/parse`
- Proxy forwards to `localhost:8000/api/v1/parse`
- So you don't need full URL in fetch()

---

## 5. HOW SOFTWARE ENGINEERS READ CODE

### THE TRUTH: You Don't Read Every Line

Engineers read in LAYERS:

**LAYER 1: The "What" (30 seconds)**
Look at file names, folder names, function names.
```
services/resume_parser.py → "Parses resumes"
services/resume_scorer.py → "Scores resumes"
```

**LAYER 2: The "How" (2-5 minutes)**
Look at function signatures, skip the body.
```python
def parse(self, text: str) -> ParsedResume:
    # I don't need to read inside yet
    # I know: takes text, returns ParsedResume
```

**LAYER 3: The "Details" (only when needed)**
You ONLY dive deep when:
- Fixing a bug in that code
- Adding a feature that touches it
- Something isn't working

### READING PATTERNS

**Pattern 1: Top-Down**
Start from entry point, follow the calls.
```
routes.py: /parse endpoint
    → calls document_extractor.extract_text_from_bytes()
        → calls resume_parser.parse()
            → calls _extract_contact_info()
```

**Pattern 2: Bottom-Up**
Start from the problem, search backwards.
```
"Skills aren't detected"
    → Search for "skills"
    → Find _extract_skills() method
    → Read just that method
```

**Pattern 3: Follow the Data**
Track what happens to data at each step.
```
File bytes → raw text → ParsedResume object → JSON
```

---

## 6. WHAT TO MEMORIZE VS WHAT TO GOOGLE

### DON'T MEMORIZE:

| Thing | Why |
|-------|-----|
| Regex patterns | Google "email regex python" |
| Library APIs | Check docs (spacy.io, fastapi.tiangolo.com) |
| CSS classes | Tailwind docs, copy-paste |
| Exact syntax | IDE autocomplete helps |

### DO UNDERSTAND:

| Thing | Why |
|-------|-----|
| Data flow | Know where to look when debugging |
| File responsibilities | Know where to make changes |
| Common patterns | Recognize try/except, if/else, loops |
| Naming conventions | _method = private, ClassName = class |

### WHAT SENIOR ENGINEERS DO:

1. Google constantly ("python read docx file")
2. Read documentation
3. Use IDE features (Ctrl+Click to jump to definition)
4. Skim first, dive later
5. Recognize patterns ("oh, this is a service class")

---

## 7. CHEAT SHEET FOR EXPLAINING THIS PROJECT

### THE ELEVATOR PITCH (30 seconds):
"It's a resume parser that uses NLP. You upload a PDF or Word doc, and it
extracts structured data like name, skills, and work history. It also scores
the resume and gives improvement suggestions. The backend is Python with
FastAPI and spaCy for NLP. The frontend is React."

### WHEN ASKED "How does it work?":
"The user uploads a file to the /parse endpoint. First, we extract the raw
text from the PDF or DOCX. Then spaCy, an NLP library, processes the text
to identify entities like names and organizations. We use regex for emails
and phone numbers, and pattern matching for skills against a list of 150+
technologies. Finally, we calculate a score based on completeness and
return everything as JSON."

### WHEN ASKED "How does skill extraction work?":
"We have a predefined list of technical skills like Python, React, AWS.
spaCy's PhraseMatcher scans the resume text and flags any matches. We also
look for a Skills section header and parse whatever's listed there."

### WHEN ASKED "How does the scoring work?":
"Each section has a weight - experience is worth 30 points, skills 20 points,
and so on. We check how complete each section is. More skills = more points.
More detailed job descriptions = more points. There are also bonus points for
advanced degrees and certifications. The final score determines the grade."

### WHEN ASKED "Why these technologies?":
- FastAPI: Modern Python framework, fast, auto-generates docs
- spaCy: Industry-standard NLP library, pre-trained English model
- Pydantic: Data validation, works great with FastAPI
- React: Popular frontend library, component-based
- Tailwind: Utility CSS, fast to style without writing CSS files
- Vite: Fast build tool for React, better than Create React App

---

## QUICK REFERENCE

### START THE PROJECT:
```bash
# Terminal 1: Backend
cd resume_parser
source parser/bin/activate
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd resume_parser/frontend
npm run dev
```

### KEY URLS:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### PROJECT GITHUB:
https://github.com/H41s3/Smart-Resume-Parser

---

*Remember: You don't need to know every line of code. You need to know
WHERE things are and HOW they connect. The details you can always look up.*

---

## 8. REAL-WORLD CONCEPTS YOU'LL USE EVERYWHERE

### 8.1 Environment Variables & .env Files

In production, you NEVER hardcode secrets (API keys, database passwords).

```python
# BAD - Never do this
DATABASE_URL = "postgresql://user:password123@localhost/db"
API_KEY = "sk-1234567890"

# GOOD - Use environment variables
import os
DATABASE_URL = os.getenv("DATABASE_URL")
API_KEY = os.getenv("API_KEY")
```

**.env file (never commit this!):**
```
DATABASE_URL=postgresql://user:password123@localhost/db
API_KEY=sk-1234567890
DEBUG=false
```

**In our project:**
```python
# config.py uses pydantic-settings which auto-reads .env
class Settings(BaseSettings):
    spacy_model: str = "en_core_web_sm"  # Default value
    
    class Config:
        env_file = ".env"  # Load from .env file
```

**Why this matters:**
- Different values for development vs production
- Secrets never go in code (security!)
- Easy to change without modifying code


### 8.2 HTTP Status Codes (Memorize These!)

| Code | Meaning | When to use |
|------|---------|-------------|
| 200 | OK | Success |
| 201 | Created | Successfully created resource (POST) |
| 400 | Bad Request | Client sent invalid data |
| 401 | Unauthorized | Not logged in |
| 403 | Forbidden | Logged in but not allowed |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Validation failed |
| 500 | Internal Server Error | Server crashed |

**In our code:**
```python
raise HTTPException(status_code=400, detail="Invalid file type")
# Returns: {"detail": "Invalid file type"} with status 400
```


### 8.3 async/await (Modern Python & JavaScript)

```python
# SYNCHRONOUS (blocking) - waits for each line
def get_data():
    result1 = fetch_from_database()    # Wait...
    result2 = fetch_from_api()         # Wait...
    return result1, result2

# ASYNCHRONOUS (non-blocking) - can do other things while waiting
async def get_data():
    result1 = await fetch_from_database()   # Start this
    result2 = await fetch_from_api()        # Start this
    return result1, result2
```

**Why async matters:**
- Web servers handle MANY requests at once
- While waiting for database, can handle other requests
- FastAPI is async by default (that's why `async def`)

**In JavaScript (same concept):**
```javascript
// Promise with .then()
fetch('/api/data').then(response => response.json())

// async/await (cleaner)
const response = await fetch('/api/data')
const data = await response.json()
```


### 8.4 REST API Conventions

| Method | Purpose | Example |
|--------|---------|---------|
| GET | Read data | GET /users → List all users |
| POST | Create new | POST /users → Create user |
| PUT | Update (full) | PUT /users/1 → Replace user 1 |
| PATCH | Update (partial) | PATCH /users/1 → Update some fields |
| DELETE | Remove | DELETE /users/1 → Delete user 1 |

**URL patterns:**
```
/users          → Collection (all users)
/users/123      → Single resource (user with ID 123)
/users/123/posts → Nested resource (posts by user 123)
```

**Our project uses:**
```
POST /api/v1/parse      → Create parsed result from file
POST /api/v1/parse/text → Create parsed result from text
GET  /api/v1/health     → Read server status
```


### 8.5 Type Hints in Python

```python
# Without types (works but unclear)
def greet(name):
    return f"Hello {name}"

# With types (clear what goes in and out)
def greet(name: str) -> str:
    return f"Hello {name}"

# Optional values (can be None)
def greet(name: str | None = None) -> str:
    if name is None:
        return "Hello stranger"
    return f"Hello {name}"

# Complex types
def process(items: list[str]) -> dict[str, int]:
    return {item: len(item) for item in items}
```

**Why use types:**
- IDE autocomplete works better
- Catch bugs before running code
- Documentation built into code
- Pydantic uses them for validation


### 8.6 Try/Except Error Handling

```python
# Basic pattern
try:
    result = risky_operation()
except SomeError as e:
    handle_error(e)
finally:
    cleanup()  # Always runs

# Real example from our code
try:
    raw_text = document_extractor.extract_text_from_bytes(content, file_ext)
    parsed_data = resume_parser.parse(raw_text)
    return ParseResponse(success=True, data=parsed_data)
except ValueError as e:
    return ParseResponse(success=False, error=str(e))
except Exception as e:
    return ParseResponse(success=False, error=f"Unexpected error: {e}")
```

**Best practices:**
- Catch specific exceptions first, generic last
- Always log errors in production
- Don't silently swallow errors (empty except block)


### 8.7 Virtual Environments (Why We Use Them)

```bash
# Problem: System Python + global packages = chaos
pip install django==3.0    # Project A needs this
pip install django==4.0    # Project B needs this - CONFLICT!

# Solution: Each project has its own environment
python -m venv myproject_env
source myproject_env/bin/activate
pip install django==4.0    # Only for this project
```

**Our project:**
```bash
python -m venv parser      # Create environment named "parser"
source parser/bin/activate # Activate it
pip install -r requirements.txt  # Install project dependencies
```

**How to tell it's active:**
```bash
(parser) $ which python
/path/to/project/parser/bin/python  # Uses local Python, not system
```


### 8.8 Git Workflow (How Teams Work)

```bash
# 1. Create branch for your feature
git checkout -b feature/add-docx-support

# 2. Make changes, commit often
git add .
git commit -m "Add DOCX extractor"
git commit -m "Update routes to handle DOCX"

# 3. Push branch to GitHub
git push -u origin feature/add-docx-support

# 4. Create Pull Request on GitHub
# Team reviews your code

# 5. After approval, merge to main
git checkout main
git pull
git merge feature/add-docx-support

# 6. Delete feature branch
git branch -d feature/add-docx-support
```

**Commit message conventions:**
```
feat: Add DOCX support          # New feature
fix: Handle empty files         # Bug fix
docs: Update README             # Documentation
refactor: Simplify parser logic # Code improvement
test: Add unit tests            # Testing
chore: Update dependencies      # Maintenance
```


### 8.9 Debugging Techniques

**Python:**
```python
# Print debugging
print(f"DEBUG: variable = {variable}")
print(f"DEBUG: type = {type(variable)}")

# Better: Use logging
import logging
logging.debug(f"Processing file: {filename}")
logging.error(f"Failed to parse: {e}")

# Best: Use debugger
breakpoint()  # Code stops here, you can inspect variables
```

**JavaScript:**
```javascript
// Print debugging
console.log('data:', data)
console.log('type:', typeof data)

// Inspect objects
console.table(arrayOfObjects)
console.dir(complexObject)

// Debugger (stops execution)
debugger;
```

**Browser DevTools:**
- F12 → Network tab → See all API requests
- F12 → Console → See errors and logs
- F12 → Sources → Set breakpoints


### 8.10 Testing (What You'll Write at Work)

```python
# Unit test - test ONE function in isolation
def test_extract_email():
    text = "Contact me at john@example.com"
    result = extract_email(text)
    assert result == "john@example.com"

# Integration test - test components working together
def test_parse_endpoint():
    response = client.post("/api/v1/parse", files={"file": pdf_file})
    assert response.status_code == 200
    assert response.json()["success"] == True
```

**Testing mindset:**
- Test the happy path (normal use)
- Test edge cases (empty input, huge input)
- Test error cases (invalid file, missing fields)


### 8.11 Docker (Containerization Basics)

```dockerfile
# Dockerfile - recipe to build container
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

**Why Docker:**
- "Works on my machine" → Works everywhere
- Same environment in dev, staging, production
- Easy to deploy to cloud (AWS, GCP, etc.)

```bash
# Build image
docker build -t resume-parser .

# Run container
docker run -p 8000:8000 resume-parser
```


### 8.12 Authentication (What You'll Implement Later)

**JWT (JSON Web Token) - Most common:**
```
1. User logs in with username/password
2. Server validates, returns JWT token
3. Client stores token (localStorage or cookie)
4. Client sends token with every request
5. Server validates token, allows access
```

**The token looks like:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjN9.abc123
```

**Protected endpoint:**
```python
@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    # Only runs if valid token provided
    return {"message": f"Hello {current_user.name}"}
```


### 8.13 Database Patterns (ORMs)

Instead of writing raw SQL, use an ORM (Object-Relational Mapping):

```python
# Raw SQL (avoid in application code)
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# With ORM (SQLAlchemy)
user = session.query(User).filter(User.id == user_id).first()

# With ORM (Django)
user = User.objects.get(id=user_id)
```

**Common ORMs:**
- Python: SQLAlchemy, Django ORM
- JavaScript: Prisma, Sequelize, TypeORM


### 8.14 Dependency Injection

Instead of creating objects inside functions, pass them in:

```python
# Tightly coupled (hard to test)
class ResumeService:
    def __init__(self):
        self.parser = ResumeParser()  # Created inside
    
# Dependency injection (easy to test)
class ResumeService:
    def __init__(self, parser: ResumeParser):
        self.parser = parser  # Passed in

# Now you can inject a mock for testing
mock_parser = MockResumeParser()
service = ResumeService(parser=mock_parser)
```

**FastAPI uses Depends() for this:**
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

---

## 9. INTERVIEW TALKING POINTS

When discussing this project in interviews:

**Technical decisions:**
- "I chose FastAPI because it's async, has automatic API documentation, and great Pydantic integration."
- "spaCy was chosen over NLTK because it has pre-trained models and better entity recognition out of the box."
- "I used Pydantic for data validation because it integrates seamlessly with FastAPI and provides type safety."

**Challenges faced:**
- "The hardest part was parsing work experience - resumes have inconsistent formats, so I used multiple patterns."
- "I had to balance accuracy vs speed - spaCy's large model is more accurate but slower, so I made it configurable."

**What you'd improve:**
- "I'd add database storage to save parsed resumes."
- "I'd implement user authentication for a multi-user system."
- "I'd add OCR for image-based PDFs using Tesseract."
- "I'd fine-tune the NLP model on resume-specific data for better accuracy."

---

*This knowledge transfers to ANY tech job. Learn these patterns once, use them everywhere.*
