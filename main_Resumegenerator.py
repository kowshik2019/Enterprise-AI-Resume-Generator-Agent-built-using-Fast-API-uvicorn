
# ============================================================
# ENTERPRISE AI RESUME GENERATOR AGENT SYSTEM
# Capstone Project — Multi-Agent FastAPI Application
# Author: Kowshik
# ============================================================
 
# ============================================================
# STAGE 1: APP INITIALIZATION
# ============================================================

import os
import json
import logging
from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from app_demo import VALID_API_KEY
from  openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

app = FastAPI(
    title="AI Resume Generator API", 
    description="Multi-agent AI system for ATS optimized resume generation",
    version="1.0"
    )

client = OpenAI(api_key=os.getenv("OpenAI_API_Key"))

# ============================================================
# STAGE 2: SECURITY CONFIG
# ============================================================

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Security(API_KEY_HEADER)):
    
    print(f"DEBUG — Received key: {repr(api_key)}")
    print(f"DEBUG — Type: {type(api_key)}")
    print(f"DEBUG — Length: {len(api_key) if api_key else 0}")
    
    if api_key == "enterprise-resume-secret-key":
        print("DEBUG — MATCH SUCCESS")
        return api_key
    
    print("DEBUG — MATCH FAILED")
    raise HTTPException(status_code=403, detail="Invalid API Key")

# ============================================================
# STAGE 3: REQUEST MODEL
# ============================================================

class Experience(BaseModel):
    title: str
    company: str
    years: float
    description: str

class Education(BaseModel):
    degree: str
    institution: str
    year: int

class UserProfile(BaseModel):
    name: str
    email: str
    target_role: str
    skills: list[str]
    experience: list[Experience]
    education: list[Education]
    projects: list[str]
    certifications: list[str]

# ============================================================
# STAGE 4: LOGGING FUNCTION
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("__name__")

def log_step(agent:str, status:str,details:str= ""):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"[{timestamp}] [{agent}] {status}] {details}"
    logger.info(message)
    with open("logs.txt", "a") as f:
        f.write(message + "\n")

# ============================================================
# SHARED LLM HELPER — call_openai() helper fucntion to call our open AI API Key
# Used by all 4 agents — OpenAI key, so call_openai() not call_claude()
# ============================================================

def call_openai(system_prompt:str, user_prompt:str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt}
        ],
        temperature = 0.4
    )
    return  response.choices[0].message.content

def parse_json_response(raw: str) -> dict:
    """
    Robustly parses JSON from LLM response.
    Handles all markdown fence variants GPT returns.
    """
    if not raw or not raw.strip():
        raise ValueError("LLM returned an empty response")
    
    cleaned = raw.strip()
    
    # Remove all markdown fence variations
    # Handles: ```json, ```JSON, ```, ` ``` `
    if "```" in cleaned:
        parts = cleaned.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            if part.startswith("{") or part.startswith("["):
                cleaned = part
                break

    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        log_step("Parser", "ERROR", f"Raw response was: {repr(raw[:200])}")
        raise ValueError(f"Error parsing response from LLM:{str(e)}")

def safe_join(value, separator: str = ", ") -> str:
    """
    Safely joins a list into a string.
    Handles list of strings, list of dicts, or None.
    """
    if not value:
        return ""
    if isinstance(value, list):
        return separator.join([str(item) for item in value])
    return str(value)


# ============================================================
# STAGE 5: PROFILE ANALYZER AGENT
# ============================================================

def profile_analyzer_agent(profile: UserProfile) -> dict:

    log_step("ProfileAnalyzer", "STARTED", f"Analyzing profile for {profile.name}")

    system_prompt = """You are an expert career analyst specializing in tech and data roles.
        You must respond with ONLY a raw JSON object. No markdown. No ```json fences. No explanation.
        Start your response directly with { and end with }.
        You are an expert career analyst speciaizing in tech and data roles.
        Analyze the candidate profile and return ONLY Valid JSON with no markdown,no explanation.
        Return exactly these keys: 
            - candidate_level: one of Junior / Mid-level / Senior/ Principal
            - primary_domain: string (eg: Data Engineering, Machine Learning, Software Engineering)
            - years_experience: integer
            - key_strengths: list of exactly 3 strings
            - career_summary_hint:  a single sentence describing the candidate's career arc"""

    user_message = f"""
    Candidate Name: {profile.name}
    Target Role: {profile.target_role}
    Skills: {', '.join(profile.skills)}
    Experience: {json.dumps([e.model_dump() for e in profile.experience])}
    Education: {json.dumps([e.model_dump() for e in profile.education])}
    Certifications: {', '.join(profile.certifications)}
    Projects: {', '.join(profile.projects)}
    """

    raw = call_openai(system_prompt, user_message)
    result = parse_json_response(raw)

    log_step("ProfileAnalyzer", "COMPLETED", 
             f"Candidate level: {result['candidate_level']} | Domain: {result['primary_domain']}"
             )
    return result

# ============================================================
# STAGE 6: ATS OPTIMIZATION AGENT
# ============================================================

def ats_optimization_agent(profile: UserProfile, profile_analysis: dict) -> dict:
    log_step("ATSOptimizer", "STARTED", f"Optimizing for ATS keywords in {profile.target_role}")

    system_prompt = """
        You are a senior ATS keyword optimization expert.
        You must respond with ONLY a raw JSON object. No markdown. No ```json fences. No explanation.
        Start your response directly with { and end with }.

        You are an expert resume optimizer specializing in ATS systems for tech roles.
        Based on the candidate profile and analysis, suggest a list of 10 high-impact keywords to include in the resume.
        Return exactly these keys:
            -ats_score: integer between 0-100 indicating how well the current profile matches typical ATS keyword requirements for the target role
            -missing_keywords: list of 10 strings representing the most important keywords missing from the profile that would improve ATS matching
            -recommeded_keywords: list of 10 strings representing the most important keywords the candidate should add to their resume to improve ATS matching
            -formatting_suggestions: list of 5 strings with specific suggestions to improve resume formatting for ATS
            -role_alignment_tips: list of 5 strings with specific tips to better align the resume with the target role"""

    user_message = f"""
       Target Role: {profile.target_role}
       Candidate Level: {profile_analysis.get('candidate_level')}
       Primary Domain: {profile_analysis.get('primary_domain')}
       Key Strengths: {safe_join(profile_analysis.get('key_strengths'))}
       Current Skills: {', '.join(profile.skills)}
       Certifications: {', '.join(profile.certifications)}
       Projects: {'; '.join(profile.projects)}
       Experience: {json.dumps([e.model_dump() for e in profile.experience])}
    """

    raw = call_openai(system_prompt, user_message)
    result = parse_json_response(raw)

    log_step("ATSOptimizer", "COMPLETED", 
             f"ATS Score={result.get('ats_score')} | "
             f"Missing Keywords= {len(result.get('missing_keywords', []))}")
    return result

# ============================================================
# STAGE 7: RESUME WRITER AGENT
# ============================================================

def resume_writer_agent(
        profile: UserProfile,
        profile_analysis: dict,
        ats_data: dict) -> dict:
    log_step("ResumeWriter", "STARTED", f"Generating professional resume content for {profile.name}")

    system_prompt = """
    You are a senior professional resume writer with 15 years of experience.
    Write compelling, ATS-optimized resume content using strong action verbs.
    Quantify achievements wherever possible.
    You must respond with ONLY a raw JSON object. No markdown. No ```json fences. No explanation.
    Start your response directly with { and end with }
    
    You are a professional resume writer specializing in tech roles with over 15 years of experience. 
    Write compelling, ATS Optimized resume content using strong action verbs.
    Quanntify achievements wherever possible.
    Return Only valid JSON wit no markdown and no explanations.
    Return exactly these keys:
    -professional_summary: a 3-4 sentence professional summary highlighting the candidate's career arc, key strengths, and value proposition for the target role
    -experience_bullets: a list of 5-7 bullet points describing the candidate's most impressive and relevant experience, using strong action verbs and quantifying achievements where possible
    -skills_section: a]]dict where keys are category and values are list of skill strings
    -project_descriptions: List of strings one polished description per project"""

    user_message = f"""
    Candidate Name: {profile.name}
    Target Role: {profile.target_role}
    Candidate Level: {profile_analysis.get('candidate_level')}
    Primary Domain: {profile_analysis.get('primary_domain')}
    Key Strengths: {safe_join(profile_analysis.get('key_strengths'))}
    Career Summary Hint: {profile_analysis.get('career_summary_hint')}
    ATS Keywords to Include: {safe_join(ats_data.get('recommended_keywords'))}
    Current Skills: {', '.join(profile.skills)}
    Certifications: {', '.join(profile.certifications)}
    Experience: {json.dumps([e.model_dump() for e in profile.experience])}
    Projects: {'; '.join(profile.projects)}
    """

    raw = call_openai(system_prompt, user_message)
    result = parse_json_response(raw)

    log_step("ResumeWriter", "COMPLETED", 
             f"Resume generated for {profile.name} |"
             f"Bullets= {len(result.get('experience_bullets', []))} | "
             f"Skills= {len(result.get('skills_section', {}).get('Technical Skills', []))}")
    return result

# ============================================================
# STAGE 8: REVIEWER AGENT
# ============================================================

def reviewer_agent(resume_content: dict, profile: UserProfile) -> dict:
    log_step("ReviewerAgent", "STARTED", f"Reviewing generated resume content for quality and coherence")

    system_prompt = """
    You are a senior HR professional and resume quality reviewer.
    Review the resume content critically for grammar, consistency, and enterprise professionalism.
    Be specific and constructive in all feedback.
    You must respond with ONLY a raw JSON object. No markdown. No ```json fences. No explanation.
    Start your response directly with { and end with }
    
    You are a meticulous resume reviewer with expertise in tech resumes. 
    Review the generated resume content for quality, coherence, and impact.
    Provide constructive feedback and suggestions for improvement.
    Return only valid JSON with no markdown and no explanations.
    Return exactly these keys:
    -overall_quality: integer score between 0-100 evaluating the overall quality of the resume content
    -coherence_score: integer score between 0-100 evaluating how coherent and well-structured the resume is
    -impact_score: integer score between 0-100 evaluating how impactful and compelling the resume content is
    -improvement_suggestions: list of 5 specific suggestions to improve the resume content"""

    user_message = f"""
    Professional Summary: {resume_content.get('professional_summary')}
    Experience Bullets: {', '.join(resume_content.get('experience_bullets', []))}
    Skills Section: {json.dumps(resume_content.get('skills_section', {}))}
    Project Descriptions: {', '.join(resume_content.get('project_descriptions', []))}
    """

    raw = call_openai(system_prompt, user_message)
    result = parse_json_response(raw)

    log_step("ReviewerAgent", "COMPLETED", 
             f"Review completed | Overall Quality={result.get('overall_quality')} | "
             f"Coherence={result.get('coherence_score')} | Impact={result.get('impact_score')}")
    return result

# ============================================================
# STAGE 9: ORCHESTRATOR
# ============================================================

def orchestrator(profile: UserProfile) -> dict:
    log_step("Orchestrator", "STARTED", 
             f"Starting resume generation process for {profile.name}"
             f"Target Role: {profile.target_role}")
    
    #Step 1 - Analyze candidate's profile
    profile_analysis = profile_analyzer_agent(profile)

    # Step 2: Run ATS optimization using profile analysis
    ats_data = ats_optimization_agent(profile, profile_analysis)

    #Step 3: Write resume using profile analysis and ATS optimization data
    resume_content = resume_writer_agent(profile, profile_analysis, ats_data)

    # Step 4: Review the generated resume content for quality and coherence
    review = reviewer_agent(resume_content, profile)

    log_step("Orchestrator", "COMPLETED", 
             f"All 4 agentsfinsihed -assembling final completion")
    
    return {
        "candidate": profile.name,
        "email": profile.email,
        "target_role": profile.target_role,
        "profile_analysis": profile_analysis,
        "ats_optimization": ats_data,
        "resume_content": resume_content,
        "review": review,
        "generated_at": datetime.now().isoformat()
    }

# ============================================================
# STAGE 10: ROOT ENDPOINT — Health Check
# ============================================================

@app.get("/")
def root():
    return {
        "message": "Welcome to the AI Resume Generator API! Visit /generate-resume to create your resume.",
        "status":"running",
        "service": "Enterprise AI Resume Generator",
        "version": "1.0.0",
        "agents":[
            "Profile Analyzer Agent",
            "ATS Optimization Agent",
            "Resume Writer Agent",
            "Reviewer Agent"
        ],
        "llm_provider": "OpenAI GPT-4o"
    }

# ============================================================
# STAGE 11: MAIN API ENDPOINT
# ============================================================

@app.post("/generate-resume")
def generate_resume(
    profile: UserProfile, 
    api_key: str = Depends(verify_api_key)
):
    log_step("API", "RECEIVED REQUEST", 
             f"Generating resume for {profile.name} with target role {profile.target_role}")
    try:
        result = orchestrator(profile)
        log_step("API", "SUCCESS SENDING RESPONSE", 
                 f"Resume generation completed for {profile.name}")
        return result
    
    except json.JSONDecodeError as e:
        log_step("API", "ERROR", f"JSON parsing error: {str(e)}")
        raise HTTPException(
            status_code=422, 
            detail=f"Error parsing response from LLM:{str(e)}"
        )

    except Exception as e:
        log_step("API", "ERROR", f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"An unexpected error occurred: {str(e)}"
        )

