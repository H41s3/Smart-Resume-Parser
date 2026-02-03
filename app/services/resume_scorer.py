"""Resume scoring and ranking service."""

from app.models.schemas import ParsedResume


class ResumeScorer:
    """Score and rank resumes based on completeness and quality."""

    # Weights for different sections (total = 100)
    WEIGHTS = {
        "contact": 15,
        "summary": 10,
        "skills": 20,
        "experience": 30,
        "education": 15,
        "certifications": 5,
        "languages": 5,
    }

    # Bonus points for exceptional resumes
    BONUSES = {
        "many_skills": 5,      # 10+ skills
        "senior_exp": 5,       # 5+ years experience (5+ jobs)
        "advanced_degree": 5,  # Masters/PhD
        "certifications": 3,   # Has certifications
        "complete_contact": 2, # All contact fields filled
    }

    @classmethod
    def score(cls, resume: ParsedResume) -> dict:
        """
        Calculate a comprehensive score for a parsed resume.

        Args:
            resume: ParsedResume object with extracted data.

        Returns:
            Dictionary with score breakdown and total score.
        """
        scores = {}
        breakdown = {}

        # Contact score (15 points max)
        contact_score = 0
        contact_fields = 0
        if resume.contact:
            if resume.contact.name:
                contact_score += 5
                contact_fields += 1
            if resume.contact.email:
                contact_score += 5
                contact_fields += 1
            if resume.contact.phone:
                contact_score += 3
                contact_fields += 1
            if resume.contact.linkedin:
                contact_score += 2
                contact_fields += 1
        scores["contact"] = min(contact_score, cls.WEIGHTS["contact"])
        breakdown["contact"] = {
            "score": scores["contact"],
            "max": cls.WEIGHTS["contact"],
            "details": f"{contact_fields}/4 fields"
        }

        # Summary score (10 points max)
        summary_score = 0
        if resume.summary:
            length = len(resume.summary)
            if length >= 200:
                summary_score = 10
            elif length >= 100:
                summary_score = 7
            elif length >= 50:
                summary_score = 5
            else:
                summary_score = 3
        scores["summary"] = summary_score
        breakdown["summary"] = {
            "score": scores["summary"],
            "max": cls.WEIGHTS["summary"],
            "details": f"{len(resume.summary or '')} chars"
        }

        # Skills score (20 points max)
        skills_count = len(resume.skills)
        if skills_count >= 10:
            skills_score = 20
        elif skills_count >= 7:
            skills_score = 15
        elif skills_count >= 4:
            skills_score = 10
        elif skills_count >= 1:
            skills_score = 5
        else:
            skills_score = 0
        scores["skills"] = skills_score
        breakdown["skills"] = {
            "score": scores["skills"],
            "max": cls.WEIGHTS["skills"],
            "details": f"{skills_count} skills found"
        }

        # Experience score (30 points max)
        exp_count = len(resume.experience)
        exp_with_details = sum(
            1 for exp in resume.experience
            if exp.title and exp.company and (exp.description or exp.highlights)
        )
        if exp_count >= 3 and exp_with_details >= 2:
            exp_score = 30
        elif exp_count >= 2 and exp_with_details >= 1:
            exp_score = 22
        elif exp_count >= 1:
            exp_score = 15
        else:
            exp_score = 0
        scores["experience"] = exp_score
        breakdown["experience"] = {
            "score": scores["experience"],
            "max": cls.WEIGHTS["experience"],
            "details": f"{exp_count} positions, {exp_with_details} with details"
        }

        # Education score (15 points max)
        edu_count = len(resume.education)
        edu_with_degree = sum(1 for edu in resume.education if edu.degree)
        if edu_count >= 1 and edu_with_degree >= 1:
            edu_score = 15
        elif edu_count >= 1:
            edu_score = 10
        else:
            edu_score = 0
        scores["education"] = edu_score
        breakdown["education"] = {
            "score": scores["education"],
            "max": cls.WEIGHTS["education"],
            "details": f"{edu_count} entries"
        }

        # Certifications score (5 points max)
        cert_count = len(resume.certifications)
        cert_score = min(cert_count * 2, 5)
        scores["certifications"] = cert_score
        breakdown["certifications"] = {
            "score": scores["certifications"],
            "max": cls.WEIGHTS["certifications"],
            "details": f"{cert_count} certifications"
        }

        # Languages score (5 points max)
        lang_count = len(resume.languages)
        lang_score = min(lang_count * 2, 5)
        scores["languages"] = lang_score
        breakdown["languages"] = {
            "score": scores["languages"],
            "max": cls.WEIGHTS["languages"],
            "details": f"{lang_count} languages"
        }

        # Calculate base score
        base_score = sum(scores.values())

        # Calculate bonuses
        bonuses = {}
        bonus_total = 0

        if skills_count >= 10:
            bonuses["many_skills"] = cls.BONUSES["many_skills"]
            bonus_total += cls.BONUSES["many_skills"]

        if exp_count >= 5:
            bonuses["senior_exp"] = cls.BONUSES["senior_exp"]
            bonus_total += cls.BONUSES["senior_exp"]

        # Check for advanced degrees
        advanced_degrees = ["master", "mba", "ph.d", "phd", "doctorate"]
        has_advanced = any(
            any(adv in (edu.degree or "").lower() for adv in advanced_degrees)
            for edu in resume.education
        )
        if has_advanced:
            bonuses["advanced_degree"] = cls.BONUSES["advanced_degree"]
            bonus_total += cls.BONUSES["advanced_degree"]

        if cert_count >= 1:
            bonuses["certifications"] = cls.BONUSES["certifications"]
            bonus_total += cls.BONUSES["certifications"]

        if contact_fields >= 4:
            bonuses["complete_contact"] = cls.BONUSES["complete_contact"]
            bonus_total += cls.BONUSES["complete_contact"]

        # Final score (capped at 100)
        total_score = min(base_score + bonus_total, 100)

        # Determine grade
        if total_score >= 90:
            grade = "A+"
        elif total_score >= 80:
            grade = "A"
        elif total_score >= 70:
            grade = "B"
        elif total_score >= 60:
            grade = "C"
        elif total_score >= 50:
            grade = "D"
        else:
            grade = "F"

        return {
            "total_score": total_score,
            "grade": grade,
            "base_score": base_score,
            "bonus_score": bonus_total,
            "breakdown": breakdown,
            "bonuses": bonuses,
            "suggestions": cls._get_suggestions(scores, resume)
        }

    @classmethod
    def _get_suggestions(cls, scores: dict, resume: ParsedResume) -> list[str]:
        """Generate improvement suggestions based on scores."""
        suggestions = []

        if scores["contact"] < 10:
            suggestions.append("Add more contact information (LinkedIn, phone)")

        if scores["summary"] < 7:
            suggestions.append("Write a more detailed professional summary (150+ words)")

        if scores["skills"] < 15:
            suggestions.append("List more technical skills relevant to your field")

        if scores["experience"] < 22:
            suggestions.append("Add more details to work experience (achievements, metrics)")

        if scores["education"] < 10:
            suggestions.append("Include education details with degree and institution")

        if len(resume.certifications) == 0:
            suggestions.append("Consider adding relevant certifications")

        return suggestions
