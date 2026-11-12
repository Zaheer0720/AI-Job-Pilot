from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class JobPortal(str, Enum):
    LINKEDIN = "linkedin"
    NAUKRI = "naukri"
    INDEED = "indeed"
    GLASSDOOR = "glassdoor"
    ZIPRECRUITER = "zip_recruiter"


class ResumeProfile(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    summary: str = ""
    skills: List[str] = []
    experience: List[Dict[str, Any]] = []
    education: List[Dict[str, Any]] = []
    certifications: List[str] = []
    languages: List[str] = []
    linkedin_url: str = ""
    github_url: str = ""
    portfolio_url: str = ""
    years_of_experience: int = 0
    job_titles: List[str] = []
    raw_text: str = ""
    resume_path: str = ""  # Server-side path of the uploaded resume file (inside uploads/)


class JobListing(BaseModel):
    id: str
    title: str
    company: str
    location: str
    portal: str
    url: str
    description: str = ""
    salary: str = ""
    job_type: str = ""
    posted_date: str = ""
    match_score: float = 0.0
    match_reasons: List[str] = []
    easy_apply: bool = False
    application_status: str = "pending"  # pending, applied, failed, skipped


class JobSearchRequest(BaseModel):
    portals: List[str] = ["linkedin", "indeed", "glassdoor", "zip_recruiter"]
    location: str = ""
    job_type: str = "fulltime"
    remote: bool = False
    results_per_portal: int = 20
    min_match_score: float = 60.0
    hours_old: int = 72  # only jobs posted within this many hours


class ApplyRequest(BaseModel):
    job_ids: List[str]
    resume_profile: ResumeProfile
    cover_letter: str = ""
    headless: bool = True
    auto_submit: bool = False  # Safety: defaults to False, user must opt-in


class ApplicationResult(BaseModel):
    job_id: str
    job_title: str
    company: str
    portal: str
    url: str
    status: str  # applied, failed, requires_manual, skipped
    message: str = ""
    screenshot_path: str = ""
