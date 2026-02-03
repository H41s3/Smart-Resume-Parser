"""NLP-based resume parsing service."""

import re
import spacy
from spacy.matcher import Matcher, PhraseMatcher

from app.models.schemas import (
    ContactInfo,
    Education,
    ParsedResume,
    WorkExperience,
)


class ResumeParser:
    """Parse resume text using NLP to extract structured information."""

    # Common technical skills to look for
    TECH_SKILLS = [
        # Programming Languages
        "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "C", "Go", "Rust",
        "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R", "MATLAB", "Perl", "SQL",
        "Objective-C", "Dart", "Lua", "Haskell", "Clojure", "Elixir", "F#",
        # Web Technologies
        "HTML", "CSS", "SASS", "LESS", "React", "Angular", "Vue", "Svelte",
        "Node.js", "Express", "Next.js", "Nuxt.js", "Gatsby", "Django", "Flask",
        "FastAPI", "Spring", "Spring Boot", "Rails", "Laravel", "ASP.NET",
        "jQuery", "Bootstrap", "Tailwind CSS", "Material UI", "Redux", "MobX",
        # Mobile
        "React Native", "Flutter", "iOS", "Android", "SwiftUI", "Xamarin",
        # Databases
        "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch", "SQLite",
        "Oracle", "SQL Server", "DynamoDB", "Cassandra", "Neo4j", "MariaDB",
        "Firebase", "Supabase", "CouchDB", "InfluxDB", "TimescaleDB",
        # Cloud & DevOps
        "AWS", "Azure", "GCP", "Google Cloud", "Docker", "Kubernetes", "K8s",
        "Jenkins", "GitLab CI", "GitHub Actions", "CircleCI", "Travis CI",
        "Terraform", "Ansible", "Puppet", "Chef", "Linux", "Unix", "Bash",
        "Nginx", "Apache", "Cloudflare", "Heroku", "Vercel", "Netlify",
        "AWS Lambda", "S3", "EC2", "RDS", "CloudFormation", "EKS", "ECS",
        # Data & ML
        "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy", "Keras",
        "NLP", "Machine Learning", "Deep Learning", "Computer Vision", "AI",
        "Data Science", "Big Data", "Spark", "Hadoop", "Tableau", "Power BI",
        "OpenCV", "NLTK", "spaCy", "Hugging Face", "LangChain", "OpenAI",
        "Data Analysis", "Data Engineering", "ETL", "Airflow", "Kafka", "Flink",
        # Testing
        "Jest", "Mocha", "Pytest", "JUnit", "Selenium", "Cypress", "Playwright",
        "Unit Testing", "Integration Testing", "E2E Testing", "TDD", "BDD",
        # Other Tools & Concepts
        "Git", "GitHub", "GitLab", "Bitbucket", "SVN",
        "REST API", "GraphQL", "gRPC", "WebSocket", "OAuth", "JWT",
        "Microservices", "Serverless", "Event-Driven", "Domain-Driven Design",
        "Agile", "Scrum", "Kanban", "JIRA", "Confluence", "Trello", "Asana",
        "CI/CD", "DevOps", "SRE", "Monitoring", "Logging", "Prometheus", "Grafana",
        "RabbitMQ", "SQS", "SNS", "Celery", "Redis Queue",
        "Figma", "Sketch", "Adobe XD", "Photoshop", "Illustrator",
        "VS Code", "IntelliJ", "PyCharm", "Vim", "Emacs",
    ]

    # Education degree patterns
    DEGREE_PATTERNS = [
        r"(?i)(bachelor'?s?|b\.?s\.?|b\.?a\.?|b\.?e\.?|b\.?tech)",
        r"(?i)(master'?s?|m\.?s\.?|m\.?a\.?|m\.?e\.?|m\.?tech|mba)",
        r"(?i)(ph\.?d\.?|doctorate|doctoral)",
        r"(?i)(associate'?s?|a\.?s\.?|a\.?a\.?)",
        r"(?i)(diploma|certificate)",
    ]

    # Common section headers
    SECTION_HEADERS = {
        "experience": [
            "experience", "work experience", "employment", "work history",
            "professional experience", "career history", "employment history"
        ],
        "education": [
            "education", "academic", "qualifications", "academic background",
            "educational background", "academic qualifications"
        ],
        "skills": [
            "skills", "technical skills", "core competencies", "competencies",
            "expertise", "technologies", "proficiencies", "abilities"
        ],
        "summary": [
            "summary", "profile", "objective", "professional summary",
            "career objective", "about me", "overview"
        ],
        "certifications": [
            "certifications", "certificates", "licenses", "credentials",
            "professional certifications"
        ],
    }

    def __init__(self, spacy_model: str = "en_core_web_sm"):
        """Initialize the parser with spaCy model."""
        try:
            self.nlp = spacy.load(spacy_model)
        except OSError:
            # Download model if not available
            from spacy.cli import download
            download(spacy_model)
            self.nlp = spacy.load(spacy_model)

        self._setup_matchers()

    def _setup_matchers(self):
        """Set up spaCy matchers for pattern matching."""
        # Phrase matcher for skills
        self.skill_matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        skill_patterns = [self.nlp.make_doc(skill) for skill in self.TECH_SKILLS]
        self.skill_matcher.add("SKILLS", skill_patterns)

    def parse(self, text: str, include_raw_text: bool = False) -> ParsedResume:
        """
        Parse resume text and extract structured information.

        Args:
            text: Raw resume text content.
            include_raw_text: Whether to include raw text in output.

        Returns:
            ParsedResume object with extracted information.
        """
        # Process text with spaCy
        doc = self.nlp(text)

        # Extract all components
        contact = self._extract_contact_info(text, doc)
        skills = self._extract_skills(text, doc)
        experience = self._extract_experience(text)
        education = self._extract_education(text)
        summary = self._extract_summary(text)
        certifications = self._extract_certifications(text)
        languages = self._extract_languages(text, doc)

        return ParsedResume(
            contact=contact,
            summary=summary,
            skills=skills,
            experience=experience,
            education=education,
            certifications=certifications,
            languages=languages,
            raw_text=text if include_raw_text else None,
        )

    def _extract_contact_info(self, text: str, doc) -> ContactInfo:
        """Extract contact information from resume."""
        contact = ContactInfo()

        # Extract email
        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        email_match = re.search(email_pattern, text)
        if email_match:
            contact.email = email_match.group()

        # Extract phone number
        phone_patterns = [
            r"(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
            r"\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}",
        ]
        for pattern in phone_patterns:
            phone_match = re.search(pattern, text)
            if phone_match:
                contact.phone = phone_match.group()
                break

        # Extract LinkedIn URL
        linkedin_pattern = r"(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+"
        linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
        if linkedin_match:
            contact.linkedin = linkedin_match.group()

        # Extract name (usually first PERSON entity or first line)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                contact.name = ent.text
                break

        # If no name found via NER, try first non-empty line
        if not contact.name:
            lines = text.strip().split("\n")
            for line in lines[:5]:  # Check first 5 lines
                line = line.strip()
                if line and not re.search(email_pattern, line) and len(line) < 50:
                    # Likely a name if it's short and not an email
                    if not any(char.isdigit() for char in line):
                        contact.name = line
                        break

        # Extract location (GPE entities)
        locations = []
        for ent in doc.ents:
            if ent.label_ in ["GPE", "LOC"]:
                locations.append(ent.text)
        if locations:
            contact.location = ", ".join(locations[:2])  # Take first 2 locations

        return contact

    def _extract_skills(self, text: str, doc) -> list[str]:
        """Extract skills from resume."""
        skills = set()

        # Use phrase matcher
        matches = self.skill_matcher(doc)
        for match_id, start, end in matches:
            skill = doc[start:end].text
            skills.add(skill)

        # Also look for skills section and extract from there
        skills_section = self._get_section_text(text, "skills")
        if skills_section:
            # Split by common delimiters and clean
            for delimiter in [",", ";", "•", "●", "○", "|", "\n"]:
                if delimiter in skills_section:
                    parts = skills_section.split(delimiter)
                    for part in parts:
                        cleaned = part.strip()
                        if cleaned and len(cleaned) < 50:
                            skills.add(cleaned)

        return sorted(list(skills))

    def _extract_experience(self, text: str) -> list[WorkExperience]:
        """Extract work experience from resume."""
        experiences = []
        exp_section = self._get_section_text(text, "experience")

        if not exp_section:
            return experiences

        # Split into potential job entries
        # Look for patterns like dates or company names
        date_pattern = r"(?:\d{1,2}/\d{4}|\w+\s+\d{4}|\d{4})\s*[-–—to]+\s*(?:\d{1,2}/\d{4}|\w+\s+\d{4}|\d{4}|present|current)"

        # Split by lines and group into experiences
        lines = exp_section.split("\n")
        current_exp = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if line contains a date range (likely start of new experience)
            date_match = re.search(date_pattern, line, re.IGNORECASE)

            if date_match or self._looks_like_job_title(line):
                # Save previous experience
                if current_exp and (current_exp.company or current_exp.title):
                    experiences.append(current_exp)

                current_exp = WorkExperience()

                # Extract dates if present
                if date_match:
                    dates = date_match.group()
                    date_parts = re.split(r"[-–—]|to", dates, flags=re.IGNORECASE)
                    if len(date_parts) >= 1:
                        current_exp.start_date = date_parts[0].strip()
                    if len(date_parts) >= 2:
                        current_exp.end_date = date_parts[1].strip()

                # Try to extract title and company from line
                line_without_date = re.sub(date_pattern, "", line, flags=re.IGNORECASE).strip()
                if " at " in line_without_date.lower():
                    parts = re.split(r"\s+at\s+", line_without_date, flags=re.IGNORECASE)
                    current_exp.title = parts[0].strip()
                    if len(parts) > 1:
                        current_exp.company = parts[1].strip()
                elif "|" in line_without_date:
                    parts = line_without_date.split("|")
                    current_exp.title = parts[0].strip()
                    if len(parts) > 1:
                        current_exp.company = parts[1].strip()
                elif "," in line_without_date:
                    parts = line_without_date.split(",")
                    current_exp.title = parts[0].strip()
                    if len(parts) > 1:
                        current_exp.company = parts[1].strip()
                else:
                    current_exp.title = line_without_date

            elif current_exp:
                # Add to description/highlights
                if line.startswith(("•", "-", "*", "●", "○")):
                    highlight = line.lstrip("•-*●○ ").strip()
                    if highlight:
                        current_exp.highlights.append(highlight)
                elif current_exp.description:
                    current_exp.description += " " + line
                else:
                    current_exp.description = line

        # Don't forget last experience
        if current_exp and (current_exp.company or current_exp.title):
            experiences.append(current_exp)

        return experiences[:10]  # Limit to 10 experiences

    def _extract_education(self, text: str) -> list[Education]:
        """Extract education information from resume."""
        education_list = []
        edu_section = self._get_section_text(text, "education")

        if not edu_section:
            # Try to find education anywhere in text
            edu_section = text

        # Look for degree patterns
        lines = edu_section.split("\n")
        current_edu = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if line contains a degree
            has_degree = any(re.search(pattern, line) for pattern in self.DEGREE_PATTERNS)

            if has_degree:
                if current_edu:
                    education_list.append(current_edu)

                current_edu = Education()

                # Try to extract degree type
                for pattern in self.DEGREE_PATTERNS:
                    match = re.search(pattern, line)
                    if match:
                        current_edu.degree = match.group()
                        break

                # Extract field of study (often after "in" or after degree)
                in_match = re.search(r"(?:in|of)\s+([A-Za-z\s]+?)(?:\s*[,|\n]|$)", line, re.IGNORECASE)
                if in_match:
                    current_edu.field_of_study = in_match.group(1).strip()

                # Look for year
                year_match = re.search(r"(19|20)\d{2}", line)
                if year_match:
                    current_edu.end_date = year_match.group()

            elif current_edu and not current_edu.institution:
                # Next line might be institution
                if not any(re.search(pattern, line) for pattern in self.DEGREE_PATTERNS):
                    current_edu.institution = line

        if current_edu:
            education_list.append(current_edu)

        return education_list[:5]  # Limit to 5 education entries

    def _extract_summary(self, text: str) -> str | None:
        """Extract professional summary/objective."""
        summary_section = self._get_section_text(text, "summary")
        if summary_section:
            # Clean up and limit length
            summary = " ".join(summary_section.split())
            return summary[:1000] if len(summary) > 1000 else summary
        return None

    def _extract_certifications(self, text: str) -> list[str]:
        """Extract certifications from resume."""
        certs = []
        cert_section = self._get_section_text(text, "certifications")

        if cert_section:
            lines = cert_section.split("\n")
            for line in lines:
                line = line.strip().lstrip("•-*●○ ")
                if line and len(line) < 200:
                    certs.append(line)

        return certs[:20]  # Limit to 20 certifications

    def _extract_languages(self, text: str, doc) -> list[str]:
        """Extract spoken languages from resume."""
        languages = set()

        # Common languages
        common_languages = [
            "English", "Spanish", "French", "German", "Chinese", "Mandarin",
            "Japanese", "Korean", "Portuguese", "Italian", "Russian", "Arabic",
            "Hindi", "Dutch", "Swedish", "Norwegian", "Danish", "Finnish",
            "Polish", "Turkish", "Vietnamese", "Thai", "Indonesian",
        ]

        text_lower = text.lower()
        for lang in common_languages:
            if lang.lower() in text_lower:
                languages.add(lang)

        # Also check for LANGUAGE entities from spaCy
        for ent in doc.ents:
            if ent.label_ == "LANGUAGE":
                languages.add(ent.text)

        return sorted(list(languages))

    def _get_section_text(self, text: str, section_name: str) -> str | None:
        """Extract text from a specific section of the resume."""
        headers = self.SECTION_HEADERS.get(section_name, [])
        if not headers:
            return None

        # Build pattern to find section header
        header_pattern = r"(?i)(?:^|\n)\s*(" + "|".join(re.escape(h) for h in headers) + r")\s*:?\s*\n"

        # Find all section starts
        all_headers = []
        for section, hdrs in self.SECTION_HEADERS.items():
            pattern = r"(?i)(?:^|\n)\s*(" + "|".join(re.escape(h) for h in hdrs) + r")\s*:?\s*\n"
            for match in re.finditer(pattern, text):
                all_headers.append((match.start(), match.end(), section))

        all_headers.sort(key=lambda x: x[0])

        # Find our section
        section_start = None
        section_end = None

        for i, (start, end, sec_name) in enumerate(all_headers):
            if sec_name == section_name:
                section_start = end
                # Section ends at next header or end of text
                if i + 1 < len(all_headers):
                    section_end = all_headers[i + 1][0]
                else:
                    section_end = len(text)
                break

        if section_start is not None:
            return text[section_start:section_end].strip()

        return None

    def _looks_like_job_title(self, line: str) -> bool:
        """Check if a line looks like a job title."""
        job_indicators = [
            "engineer", "developer", "manager", "director", "analyst",
            "consultant", "specialist", "coordinator", "administrator",
            "architect", "designer", "lead", "senior", "junior", "intern",
            "associate", "executive", "officer", "president", "vp",
        ]
        line_lower = line.lower()
        return any(indicator in line_lower for indicator in job_indicators)
