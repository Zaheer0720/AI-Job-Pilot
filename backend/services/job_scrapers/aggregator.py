import os
import uuid
from typing import List
from jobspy import scrape_jobs
from models.schemas import JobListing, JobSearchRequest


def scrape_jobs_jobspy(
    search_term: str,
    location: str,
    portals: List[str],
    results: int = 20,
    remote: bool = False,
    job_type: str = "",
    hours_old: int = 72,
) -> List[JobListing]:
    """
    Use jobspy to scrape multiple job portals at once.
    jobspy supports: linkedin, indeed, glassdoor, zip_recruiter
    """
    # Only portals jobspy supports natively; unknown ones (e.g. naukri) are ignored
    supported = {"linkedin", "indeed", "glassdoor", "zip_recruiter"}
    sites = [p for p in dict.fromkeys(portals) if p in supported]
    if not sites:
        return []

    kwargs = {}
    if job_type in {"fulltime", "parttime", "internship", "contract"}:
        kwargs["job_type"] = job_type
    if remote:
        kwargs["is_remote"] = True

    try:
        jobs_df = scrape_jobs(
            site_name=sites,
            search_term=search_term,
            location=location or os.getenv("DEFAULT_LOCATION", "India"),
            results_wanted=results,
            hours_old=hours_old,
            linkedin_fetch_description=True,
            **kwargs,
        )

        if jobs_df is None or jobs_df.empty:
            return []

        job_listings = []
        for _, row in jobs_df.iterrows():
            min_sal = row.get("min_amount", "")
            max_sal = row.get("max_amount", "")
            salary = ""
            if min_sal and str(min_sal) not in ["None", "nan", ""]:
                salary = f"{min_sal} - {max_sal}" if max_sal else str(min_sal)

            job = JobListing(
                id=str(uuid.uuid4()),
                title=str(row.get("title", "")).strip() or "Unknown Title",
                company=str(row.get("company", "")).strip() or "Unknown Company",
                location=str(row.get("location", "")).strip(),
                portal=str(row.get("site", "unknown")),
                url=str(row.get("job_url", "")).strip(),
                description=str(row.get("description", ""))[:3000],
                salary=salary,
                job_type=str(row.get("job_type", "")).strip(),
                posted_date=str(row.get("date_posted", "")).strip(),
                easy_apply=bool(row.get("is_easy_apply", False)),
            )
            if job.url:  # Only add jobs with valid URLs
                job_listings.append(job)

        return job_listings

    except Exception as e:
        print(f"JobSpy scraping error for '{search_term}': {e}")
        return []


def search_all_portals(
    queries: List[str],
    request: JobSearchRequest,
) -> List[JobListing]:
    """Search across all configured job portals and deduplicate results."""
    all_jobs = []
    seen_urls = set()

    for query in queries[:3]:  # Use top 3 queries to avoid too many requests
        jobs = scrape_jobs_jobspy(
            search_term=query,
            location=request.location,
            portals=request.portals,
            results=request.results_per_portal,
            remote=request.remote,
            job_type=request.job_type,
            hours_old=request.hours_old,
        )

        for job in jobs:
            if job.url and job.url not in seen_urls:
                seen_urls.add(job.url)
                all_jobs.append(job)

    return all_jobs
