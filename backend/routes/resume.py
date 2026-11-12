import os
import time
import uuid
from pydantic import BaseModel
import asyncio
import aiofiles
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from services.resume_parser import parse_resume_file
from services.gemini_service import parse_resume_with_gemini
from models.schemas import ResumeProfile

router = APIRouter(prefix="/resume", tags=["resume"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt"}
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
UPLOAD_MAX_AGE_SECONDS = 7 * 24 * 3600


class ParseTextRequest(BaseModel):
    text: str = ""


def cleanup_old_uploads():
    """Delete uploaded resumes older than a week (called at startup)."""
    now = time.time()
    for name in os.listdir(UPLOAD_DIR):
        path = os.path.join(UPLOAD_DIR, name)
        try:
            if os.path.isfile(path) and now - os.path.getmtime(path) > UPLOAD_MAX_AGE_SECONDS:
                os.remove(path)
        except OSError:
            pass


cleanup_old_uploads()


@router.post("/upload", response_model=ResumeProfile)
async def upload_resume(file: UploadFile = File(...)):
    """Upload and parse a resume file. Returns structured profile data."""
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_ext}. Use PDF, DOCX, or TXT."
        )

    # Save uploaded file
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}{file_ext}")

    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        if len(content) > MAX_UPLOAD_BYTES:
            await f.close()
            os.remove(file_path)
            raise HTTPException(status_code=413, detail="Resume file too large (max 10 MB).")
        await f.write(content)

    try:
        # Extract raw text from file
        raw_text = parse_resume_file(file_path)

        if not raw_text or len(raw_text) < 50:
            raise HTTPException(status_code=400, detail="Could not extract text from resume. Please try a different format.")

        # Use Gemini to parse into structured profile
        profile = await asyncio.to_thread(parse_resume_with_gemini, raw_text)
        profile.raw_text = raw_text
        profile.resume_path = file_path

        return profile

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume parsing failed: {str(e)}")
    finally:
        # Keep file for auto-apply, but clean path is tracked
        pass


@router.post("/parse-text", response_model=ResumeProfile)
async def parse_resume_text(body: ParseTextRequest):
    """Parse a resume from raw text input."""
    text = body.text
    if not text or len(text) < 50:
        raise HTTPException(status_code=400, detail="Resume text too short.")
    
    try:
        profile = await asyncio.to_thread(parse_resume_with_gemini, text)
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing failed: {str(e)}")
