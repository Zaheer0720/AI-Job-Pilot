import asyncio
import os
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
from models.schemas import JobListing, JobSearchRequest, ResumeProfile
from services.gemini_service import generate_search_queries, score_job_match
from services.job_scrapers.aggregator import search_all_portals

router = APIRouter(prefix="/jobs", tags=["jobs"])

SCORE_LIMIT = int(os.getenv("SCORE_LIMIT", "25"))


class SearchRequest(BaseModel):
    """Combined search request: profile + search config"""
    profile: ResumeProfile
    search_config: JobSearchRequest = JobSearchRequest()


class ScoreRequest(BaseModel):
    profile: ResumeProfile
    job: JobListing


@router.post("/search", response_model=List[JobListing])
async def search_jobs(request: SearchRequest):
    """Search for jobs across multiple portals based on resume profile."""
    profile = request.profile
    search_request = request.search_config

    try:
        # Generate optimized search queries using Gemini
        try:
            queries = await asyncio.to_thread(generate_search_queries, profile)
        except Exception as e:
            print(f"Query generation failed, using fallback: {e}")
            queries = []
        if not queries:
            queries = [" ".join(profile.job_titles[:2] + profile.skills[:3]).strip() or "software engineer"]

        # Set location from profile if not specified
        if not search_request.location and profile.location:
            search_request.location = profile.location

        # Search all portals (blocking scrape -> worker thread)
        jobs = await asyncio.to_thread(search_all_portals, queries, search_request)

        if not jobs:
            return []

        # Score jobs concurrently (bounded) without blocking the event loop
        sem = asyncio.Semaphore(5)

        async def score(job: JobListing) -> JobListing:
            try:
                if job.description and len(job.description) > 100:
                    async with sem:
                        score_data = await asyncio.to_thread(score_job_match, profile, job)
                    job.match_score = float(score_data.get("score", 0))
                    job.match_reasons = score_data.get("reasons", [])
                else:
                    job.match_score = 50.0
                    job.match_reasons = ["Description not available for detailed scoring"]
            except Exception as e:
                print(f"Scoring error for {job.title}: {e}")
                job.match_score = 50.0
                job.match_reasons = ["Scoring failed; showing a neutral score"]
            return job

        # Limit to avoid too many API calls
        # Gemini free tier is ~15 requests/min, so cap how many jobs get AI-scored
        scored = await asyncio.gather(*(score(j) for j in jobs[:SCORE_LIMIT]))
        scored_jobs = [j for j in scored if j.match_score >= search_request.min_match_score]

        # Sort by match score descending
        scored_jobs.sort(key=lambda x: x.match_score, reverse=True)

        return scored_jobs

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job search failed: {str(e)}")


@router.post("/score", response_model=Dict[str, Any])
async def score_single_job(request: ScoreRequest):
    """Score a specific job against a resume profile."""
    try:
        result = await asyncio.to_thread(score_job_match, request.profile, request.job)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scoring failed: {str(e)}")
