

# Enterprise AI Resume Generator Agent System

A production-grade, multi-agent AI application built with FastAPI and OpenAI GPT-4o.
Automatically analyzes candidate profiles, optimizes for ATS, generates professional resume content,
and reviews quality — all in one API call.

---

## Business Problem

Job seekers spend hours manually tailoring resumes for each application.
Most resumes fail ATS (Applicant Tracking System) filters before a human ever reviews them.
No existing open tool provides end-to-end intelligent resume generation + ATS scoring + quality review in a single, secure, API-driven pipeline.

This system solves that by orchestrating four specialized AI agents in sequence.

---

## Architecture

```
POST /generate-resume
        ↓
FastAPI Endpoint (Uvicorn)
        ↓
Security Layer (X-API-Key validation)
        ↓
Orchestrator
   ├── Agent 1: Profile Analyzer   → candidate level, domain, strengths
   ├── Agent 2: ATS Optimizer      → ATS score, missing keywords, tips
   ├── Agent 3: Resume Writer      → summary, bullets, skills, projects
   └── Agent 4: Reviewer           → grammar, professionalism, approval
        ↓
Structured JSON Response
        ↓
Logs (console + logs.txt)
```

All agents call OpenAI GPT-4o via the shared `call_openai()` function.

---

## Project Structure

```
capstone_resume_agent/
├── main.py              # Full application (all 11 stages)
├── requirements.txt     # Python dependencies
├── .env                 # API keys (create this — do not commit)
├── logs.txt             # Auto-generated at runtime
└── README.md            # This file
```

---

## Setup Instructions

### Step 1 — Clone / create project folder

```bash
mkdir capstone_resume_agent
cd capstone_resume_agent
```

### Step 2 — Create virtual environment

```bash
python -m venv venv
source venv/bin/activate          # Mac/Linux
venv\Scripts\activate             # Windows
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Create your .env file

Open API Key loaded in .env file

```
OPENAI_API_KEY=sk-your-openai-api-key-here
APP_API_KEY=enterprise-resume-secret-key
```

> **IMPORTANT:** Never commit `.env` to GitHub. Add it to `.gitignore`.

### Step 5 — Run the application

```bash
uvicorn main:app --reload --port 8000
```

You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

---

## Testing the API

### Health Check (no auth required)

```bash
curl http://localhost:8000/
```

Expected response:
```json
{
  "status": "running",
  "service": "Enterprise AI Resume Generator",
  "version": "1.0.0"
}
```

### Generate Resume (POST with API key)

```bash
curl -X POST http://localhost:8000/generate-resume \
  -H "Content-Type: application/json" \
  -H "X-API-Key: enterprise-resume-secret-key" \
  -d '{
    "name": "Koushik Red",
    "email": "koushikred@example.com",
    "target_role": "Senior Data Engineer",
    "skills": ["Python", "PySpark", "Snowflake", "dbt", "Airflow", "AWS", "Kafka"],
    "experience": [
      {
        "title": "Data Engineer",
        "company": "Acme Corp",
        "years": 4.0,
        "description": "Built ETL pipelines processing 10M records daily using PySpark and Airflow"
      }
    ],
    "education": [
      {
        "degree": "M.S. Computer Science",
        "institution": "University of Texas at Arlington",
        "year": 2018
      }
    ],
    "projects": [
      "Real-time fraud detection pipeline using Kafka and Spark Structured Streaming",
      "RAG-based medical Q&A system using ChromaDB and BioBERT"
    ],
    "certifications": ["AWS Solutions Architect", "Google Professional Data Engineer"]
  }'
```

### Interactive API Docs (Swagger UI)

Open in browser: `http://localhost:8000/docs`

---

## Sample Response Structure

```json
{
  "candidate": "Jane Smith",
  "target_role": "Senior Data Engineer",
  "profile_analysis": {
    "candidate_level": "Senior",
    "primary_domain": "Data Engineering",
    "years_experience": 4,
    "key_strengths": ["..."],
    "career_summary_hint": "..."
  },
  "ats_optimization": {
    "ats_score": 82,
    "missing_keywords": ["Delta Lake", "Databricks"],
    "recommended_keywords": ["..."],
    "formatting_suggestions": ["..."],
    "role_alignment_tips": ["..."]
  },
  "resume_content": {
    "professional_summary": "...",
    "experience_bullets": ["Led...", "Built...", "Designed..."],
    "skills_section": {
      "Programming": ["Python", "PySpark"],
      "Cloud": ["AWS", "Snowflake"]
    },
    "project_descriptions": ["..."]
  },
  "review": {
    "grammar_issues": [],
    "consistency_score": 94,
    "professionalism_score": 91,
    "formatting_feedback": ["..."],
    "final_recommendation": "...",
    "approved": true
  },
  "generated_at": "2024-01-15T10:30:00"
}
```

---

## Security

- Every `/generate-resume` request requires the `X-API-Key` header.
- Incorrect or missing key returns HTTP 403 Forbidden.
- API key is loaded from `.env` — never hardcoded.

---

## Logging

Every agent execution is logged to:
- Console (stdout)
- `logs.txt` in the project root

Log format: `[TIMESTAMP] [AGENT] [STATUS] detail`

Example:
```
[2026-05-24 10:30:00] [Orchestrator] [STARTED] Pipeline initiated for Jane Smith targeting Senior Data Engineer
[2024-05-24 10:30:01] [ProfileAnalyzer] [STARTED] Analyzing profile for Jane Smith
[2024-05-24 10:30:03] [ProfileAnalyzer] [COMPLETED] Level=Senior | Domain=Data Engineering
[2024-05-24 10:30:03] [ATSOptimizer] [STARTED] Running ATS analysis for role: Senior Data Engineer
[2024-05-24 10:30:05] [ATSOptimizer] [COMPLETED] ATS Score=82 | Missing Keywords=2
[2024-05-24 10:30:05] [ResumeWriter] [STARTED] Generating resume content
[2024-05-24 10:30:08] [ResumeWriter] [COMPLETED] Summary generated | Bullets=6
[2024-05-24 10:30:08] [Reviewer] [STARTED] Reviewing resume quality
[2024-05-24 10:30:10] [Reviewer] [COMPLETED] Approved=True | Professionalism=91
[2024-05-24 10:30:10] [Orchestrator] [COMPLETED] All 4 agents finished — assembling final response
[2024-05-24 10:30:10] [API] [SUCCESS] Resume successfully generated for Jane Smith
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI |
| ASGI Server | Uvicorn |
| LLM Backend | OpenAI GPT-4o |
| Data Validation | Pydantic |
| Authentication | APIKeyHeader |
| Environment Config | python-dotenv |
| Logging | Python logging + file handler |

---

## Key Design Decisions

**Why OpenAI (not Claude)?** The project uses `call_openai()` exclusively because the API key provided is an OpenAI key. The `call_openai()` function is the correct shared helper — `call_claude()` is not applicable here.

**Why 4 separate agents?** Each agent has a single, well-defined responsibility (separation of concerns). This makes the system testable, debuggable, and extensible — adding a new agent (e.g. Cover Letter Writer) requires no changes to existing agents.

**Why FastAPI?** FastAPI provides automatic Swagger docs at `/docs`, async support, Pydantic validation, and production-readiness — all critical for an enterprise-grade system.