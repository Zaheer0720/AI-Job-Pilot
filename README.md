# 🤖 AI Job Hunter

An AI-powered job application automation tool that uses **Google Gemini** to analyze your resume, search multiple job portals, rank matches, and auto-fill/submit applications.

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📄 **Resume Analysis** | Upload PDF/DOCX/TXT → Gemini extracts skills, experience, education |
| 🔍 **Multi-Portal Search** | Searches LinkedIn, Indeed, Glassdoor, ZipRecruiter simultaneously |
| 🎯 **AI Match Scoring** | Gemini scores each job 0-100% against your profile |
| 🤖 **Auto-Apply** | Playwright browser automation fills and submits forms |
| ✉️ **Cover Letter Gen** | AI generates personalized cover letters per job |
| 📸 **Screenshots** | Captures proof of each filled application |

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Google Gemini API key ([Get one free](https://aistudio.google.com/app/apikey))

### Setup

```bash
# 1. Run setup script (Windows)
setup.bat

# 2. Configure environment
copy .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 3. Launch the app
start.bat
```

Then open **http://localhost:5173** in your browser.

## 📖 How It Works

```
1. Upload Resume (PDF/DOCX/TXT)
       ↓
2. Gemini AI parses → extracts name, skills, experience, education
       ↓
3. Gemini generates optimized job search queries
       ↓
4. JobSpy scrapes LinkedIn + Indeed + Glassdoor + ZipRecruiter
       ↓
5. Gemini scores each job (0-100% match)
       ↓
6. You select jobs to apply to
       ↓
7. Playwright opens browser, Gemini fills each form field
       ↓
8. Application submitted (or paused for review)
```

## ⚙️ Configuration

### `.env` file

```env
# Required
GEMINI_API_KEY=your_key_here

# Optional: LinkedIn credentials for more results
LINKEDIN_EMAIL=you@email.com
LINKEDIN_PASSWORD=yourpassword

# Optional: SerpAPI for enhanced search
SERP_API_KEY=your_serp_key
```

## 🛡️ Safety Features

- **Auto-Submit OFF by default** — forms are filled but NOT submitted unless you explicitly enable it
- **Human-like delays** — random delays between actions to avoid detection
- **Screenshot proof** — captures each application state
- **Polite delays** — 5-15 second gaps between applications
- **Confirmation prompt** — warns before enabling auto-submit

## 📁 Project Structure

```
ai-job-hunter/
├── backend/                    # FastAPI Python backend
│   ├── main.py                 # App entry point
│   ├── routes/                 # API endpoints
│   │   ├── resume.py           # /resume/upload
│   │   ├── jobs.py             # /jobs/search
│   │   └── apply.py            # /apply/run
│   ├── services/
│   │   ├── gemini_service.py   # All Gemini AI calls
│   │   ├── resume_parser.py    # PDF/DOCX extraction
│   │   ├── job_scrapers/       # Multi-portal scraping
│   │   └── auto_apply.py       # Playwright automation
│   └── models/schemas.py       # Pydantic data models
├── frontend/                   # React + Vite frontend
│   └── src/
│       ├── pages/              # Home, Dashboard
│       └── components/         # UI components
├── setup.bat                   # One-click setup
├── start.bat                   # Launch app
└── .env.example                # Config template
```

## 🌐 API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/resume/upload` | POST | Upload & parse resume |
| `/jobs/search` | POST | Search jobs across portals |
| `/apply/run` | POST | Auto-apply to selected jobs |
| `/apply/cover-letter` | POST | Generate cover letter |
| `/docs` | GET | Interactive API docs (Swagger) |

## ⚠️ Important Notes

> **Terms of Service**: Automated job applications may violate the ToS of LinkedIn, Indeed, and other portals. Use responsibly and review applications before submitting.

> **LinkedIn**: May require manual login via the browser window if anti-bot detection triggers.

> **Naukri.com**: Not directly supported by jobspy. Use LinkedIn/Indeed for Indian job market, or add your Naukri credentials in the config.

## 🤝 Extending

To add a new job portal, create a scraper in `backend/services/job_scrapers/` and register it in `aggregator.py`.
