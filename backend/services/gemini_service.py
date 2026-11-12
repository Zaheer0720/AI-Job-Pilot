import google.generativeai as genai
import json
import os
import re
import threading
import time
from typing import List, Dict, Any
from models.schemas import ResumeProfile, JobListing


_model_cache = {}

JSON_CONFIG = {"response_mime_type": "application/json"}


def configure_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set. Please add your GEMINI_API_KEY in the .env file.")
    model_name = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    key = (api_key, model_name)
    if key not in _model_cache:
        genai.configure(api_key=api_key, transport="rest")
        _model_cache[key] = _ThrottledModel(genai.GenerativeModel(model_name))
    return _model_cache[key]


# Free tier allows ~15 requests/min; space calls out (override with GEMINI_MIN_INTERVAL seconds)
_MIN_INTERVAL = float(os.getenv("GEMINI_MIN_INTERVAL", "4.5"))
_MAX_RETRIES = 3
_throttle_lock = threading.Lock()
_last_call = 0.0


class _ThrottledModel:
    """Wraps a Gemini model: spaces out requests and retries on 429 quota errors."""

    def __init__(self, model):
        self._model = model

    def generate_content(self, *args, **kwargs):
        global _last_call
        for attempt in range(_MAX_RETRIES + 1):
            with _throttle_lock:
                wait = _MIN_INTERVAL - (time.monotonic() - _last_call)
                if wait > 0:
                    time.sleep(wait)
                _last_call = time.monotonic()
            try:
                return self._model.generate_content(*args, **kwargs)
            except Exception as e:
                msg = str(e)
                quota = "429" in msg or "quota" in msg.lower() or "ResourceExhausted" in type(e).__name__
                if not quota or attempt == _MAX_RETRIES:
                    raise
                m = re.search(r"retry in ([\d.]+)s", msg)
                time.sleep(min(float(m.group(1)) + 1 if m else 20, 60))


def parse_resume_with_gemini(resume_text: str) -> ResumeProfile:
    """Use Gemini to extract structured profile data from raw resume text."""
    model = configure_gemini()

    prompt = f"""
You are an expert resume parser. Analyze the following resume text and extract all information into a structured JSON object.

Resume Text:
---
{resume_text}
---

Return ONLY valid JSON (no markdown, no explanation) with this exact structure:
{{
  "name": "Full Name",
  "email": "email@example.com",
  "phone": "+1234567890",
  "location": "City, Country",
  "summary": "Professional summary text",
  "skills": ["Skill1", "Skill2"],
  "experience": [
    {{
      "title": "Job Title",
      "company": "Company Name",
      "duration": "Jan 2020 - Dec 2022",
      "years": 2,
      "description": "What they did",
      "technologies": ["tech1", "tech2"]
    }}
  ],
  "education": [
    {{
      "degree": "Bachelor of Science",
      "field": "Computer Science",
      "institution": "University Name",
      "year": "2018"
    }}
  ],
  "certifications": ["Cert1", "Cert2"],
  "languages": ["English", "Hindi"],
  "linkedin_url": "",
  "github_url": "",
  "portfolio_url": "",
  "years_of_experience": 5,
  "job_titles": ["Software Engineer", "Backend Developer"]
}}
"""

    response = model.generate_content(prompt, generation_config=JSON_CONFIG)
    text = response.text.strip()

    # Remove markdown code blocks if present
    text = re.sub(r'^```(?:json)?\s*', '', text)
    text = re.sub(r'\s*```$', '', text)

    data = json.loads(text)
    data["raw_text"] = resume_text
    return ResumeProfile(**data)


def generate_search_queries(profile: ResumeProfile) -> List[str]:
    """Generate optimized job search queries from resume profile."""
    model = configure_gemini()

    prompt = f"""
Based on this candidate profile, generate 5 optimized job search queries for job portals.
Focus on their most recent/relevant roles and key skills.

Profile:
- Name: {profile.name}
- Job Titles: {', '.join(profile.job_titles)}
- Key Skills: {', '.join(profile.skills[:15])}
- Years of Experience: {profile.years_of_experience}
- Location: {profile.location}

Return ONLY a JSON array of 5 search query strings, ordered from most specific to broadest.
Example: ["Senior Python Developer Machine Learning", "Python Backend Engineer", ...]
"""

    response = model.generate_content(prompt, generation_config=JSON_CONFIG)
    text = response.text.strip()
    text = re.sub(r'^```(?:json)?\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    queries = json.loads(text)
    return [q for q in queries if isinstance(q, str) and q.strip()] if isinstance(queries, list) else []


def score_job_match(profile: ResumeProfile, job: JobListing) -> Dict[str, Any]:
    """Score how well a job matches the candidate's profile."""
    model = configure_gemini()

    prompt = f"""
Score how well this job matches the candidate. Return a JSON object only.

CANDIDATE:
- Skills: {', '.join(profile.skills[:20])}
- Job Titles: {', '.join(profile.job_titles)}
- Years Experience: {profile.years_of_experience}
- Location: {profile.location}

JOB:
- Title: {job.title}
- Company: {job.company}
- Location: {job.location}
- Description: {job.description[:1500]}

Return ONLY valid JSON:
{{
  "score": 85,
  "reasons": ["Matches 8/10 required skills", "Title aligns with experience", "Location is compatible"],
  "missing_skills": ["Kubernetes", "AWS"],
  "strengths": ["Strong Python background", "5+ years relevant experience"]
}}

Score from 0-100. Be realistic and accurate.
"""

    response = model.generate_content(prompt, generation_config=JSON_CONFIG)
    text = response.text.strip()
    text = re.sub(r'^```(?:json)?\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    return json.loads(text)


def generate_cover_letter(profile: ResumeProfile, job: JobListing) -> str:
    """Generate a personalized cover letter for a job application."""
    model = configure_gemini()

    prompt = f"""
Write a professional, personalized cover letter for this job application.

CANDIDATE:
- Name: {profile.name}
- Email: {profile.email}
- Summary: {profile.summary}
- Key Skills: {', '.join(profile.skills[:10])}
- Years Experience: {profile.years_of_experience}
- Recent Role: {profile.experience[0]['title'] if profile.experience else 'Professional'}

JOB:
- Title: {job.title}
- Company: {job.company}
- Description: {job.description[:1000]}

Write a compelling 3-paragraph cover letter. Be specific, professional, and enthusiastic.
Do not use generic phrases. Reference specific skills and job requirements.
"""

    response = model.generate_content(prompt)
    return response.text.strip()


def fill_form_field(field_label: str, field_type: str, profile: ResumeProfile, context: str = "") -> str:
    """Use Gemini to intelligently fill a form field based on resume data."""
    model = configure_gemini()

    profile_summary = f"""
Name: {profile.name}
Email: {profile.email}
Phone: {profile.phone}
Location: {profile.location}
Skills: {', '.join(profile.skills[:15])}
Years of Experience: {profile.years_of_experience}
Current/Recent Title: {profile.job_titles[0] if profile.job_titles else ''}
Summary: {profile.summary[:300]}
LinkedIn: {profile.linkedin_url}
GitHub: {profile.github_url}
"""

    prompt = f"""
You are helping fill out a job application form. Based on the candidate's profile, provide the EXACT value to enter for this form field.

CANDIDATE PROFILE:
{profile_summary}

FORM FIELD:
- Label: {field_label}
- Type: {field_type}
- Context: {context}

Rules:
1. Return ONLY the value to enter, nothing else
2. For select/dropdown fields, return the option text that best matches
3. Use ONLY facts present in the candidate profile. Never invent facts.
4. If the profile does not clearly answer the field, return exactly: SKIP
5. Always return SKIP for work authorization, visa/sponsorship, citizenship, legal, criminal-record,
   disability, gender/ethnicity/veteran status, salary expectation, notice period and
   relocation questions: the candidate must answer these personally.
6. For "years of experience" fields, return a number only if it follows from the profile
7. Keep answers concise and professional

Value to enter:"""

    response = model.generate_content(prompt)
    value = response.text.strip()
    return "" if value.upper() == "SKIP" else value
