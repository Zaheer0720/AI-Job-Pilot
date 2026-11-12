import os
import sys
import uuid
import asyncio
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
from models.schemas import ApplicationResult, JobListing, ResumeProfile
from services.auto_apply import apply_to_multiple_jobs
from services.gemini_service import generate_cover_letter

router = APIRouter(prefix="/apply", tags=["apply"])

UPLOAD_DIR = os.path.abspath("uploads")

# In-memory task store (use a database if this ever needs to survive restarts)
tasks: Dict[str, Dict[str, Any]] = {}
_background: set = set()  # keep references so running tasks aren't garbage collected


class RunApplyRequest(BaseModel):
    """Request body for /apply/start"""
    jobs: List[JobListing]
    profile: ResumeProfile
    resume_path: str = ""  # optional; defaults to profile.resume_path
    headless: bool = True
    auto_submit: bool = False


class CoverLetterRequest(BaseModel):
    profile: ResumeProfile
    job: JobListing


def _safe_resume_path(path: str) -> str:
    """Only allow resume files that live inside the uploads directory."""
    if not path:
        return ""
    full = os.path.abspath(path)
    if os.path.commonpath([full, UPLOAD_DIR]) != UPLOAD_DIR or not os.path.isfile(full):
        return ""
    return full


def _run_in_own_loop(task: Dict[str, Any], request: RunApplyRequest, resume_path: str):
    """Run Playwright in a worker thread with its own event loop.

    On Windows, uvicorn (especially with reload=True) uses a SelectorEventLoop,
    which cannot spawn subprocesses, so Playwright fails with an empty
    NotImplementedError. A dedicated Proactor loop avoids that.
    """
    loop = asyncio.ProactorEventLoop() if sys.platform == "win32" else asyncio.new_event_loop()
    try:
        loop.run_until_complete(apply_to_multiple_jobs(
            jobs=request.jobs,
            profile=request.profile,
            resume_path=resume_path,
            headless=request.headless,
            auto_submit=request.auto_submit,
            results=task["results"],
        ))
    finally:
        loop.close()


async def _run_task(task_id: str, request: RunApplyRequest, resume_path: str):
    task = tasks[task_id]
    try:
        await asyncio.to_thread(_run_in_own_loop, task, request, resume_path)
    except Exception as e:
        task["error"] = f"Application process failed: {type(e).__name__}: {e}"
    finally:
        task["done"] = True


@router.post("/start", response_model=Dict[str, Any])
async def start_applications(request: RunApplyRequest):
    """
    Start applying to the given jobs in the background.
    Returns a task_id; poll GET /apply/results/{task_id} for progress.
    WARNING: auto_submit=True will actually submit applications!
    """
    if not request.jobs:
        raise HTTPException(status_code=400, detail="No jobs provided")

    resume_path = _safe_resume_path(request.resume_path or request.profile.resume_path)

    task_id = str(uuid.uuid4())
    tasks[task_id] = {"done": False, "total": len(request.jobs), "results": [], "error": ""}

    t = asyncio.create_task(_run_task(task_id, request, resume_path))
    _background.add(t)
    t.add_done_callback(_background.discard)

    return {
        "task_id": task_id,
        "total": len(request.jobs),
        "resume_attached": bool(resume_path),
    }


@router.get("/results/{task_id}", response_model=Dict[str, Any])
async def get_application_results(task_id: str):
    """Progress and results of a background application task."""
    task = tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/cover-letter")
async def generate_cover_letter_endpoint(request: CoverLetterRequest):
    """Generate a cover letter for a specific job."""
    try:
        letter = await asyncio.to_thread(generate_cover_letter, request.profile, request.job)
        return {"cover_letter": letter}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cover letter generation failed: {str(e)}")
