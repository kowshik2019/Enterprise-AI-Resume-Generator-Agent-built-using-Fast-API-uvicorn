
Enterprise-AI-Resume-Generator-Agent-built-using-Fast-API-uvicorn at http://localhost:8000 (port 8000)

The Business Problem 
Problem: Job seekers — especially career changers and senior professionals — spend hours tailoring resumes to each job description. 
Most resumes fail before a human sees them — ATS filters reject them on keywords alone. Job seekers have no reliable, automated way to analyze their profile, optimize keywords, write professional content, and review quality in one step. This system solves that with a secure, production-grade multi-agent API
Most resumes fail ATS (Applicant Tracking System) filters before a human ever sees them. No current free/open tool does end-to-end intelligent resume generation + ATS scoring + quality review in one automated pipeline.
Our solution: An API-first, multi-agent AI system that:

Takes a raw user profile (skills, experience, education, projects)
Analyzes the candidate's level and domain
Scores and optimizes for ATS keyword matching
Writes a polished, professional resume
Reviews it for grammar, consistency, and professionalism
Returns a structured JSON response — ready to render into a PDF or UI


Architecture (All Required Stages)
Here is the flow your main.py must follow, stage by stage:
1. APP INITIALIZATION        → Create FastAPI app, set title/version
2. SECURITY CONFIG           → API Key auth via HTTP header (X-API-Key)
3. REQUEST MODEL             → Pydantic model for incoming user profile
4. LOGGING FUNCTION          → log_step() writes to logs.txt + console
5. PROFILE ANALYZER AGENT    → OpenAI call → candidate level, domain, years
6. ATS OPTIMIZATION AGENT    → OpenAI call → missing keywords, ATS score
7. RESUME WRITER AGENT       → OpenAI call → summary, bullets, skills, projects
8. REVIEWER AGENT            → OpenAI call → grammar, consistency, final score
9. ORCHESTRATOR              → Calls all 4 agents in sequence, builds result
10. ROOT ENDPOINT (GET /)    → Health check
11. MAIN API ENDPOINT        → POST /generate-resume → runs orchestrator

Architecture workflow Diagram

<img width="1440" height="1560" alt="image" src="https://github.com/user-attachments/assets/e4970ee3-eebc-4a5e-94df-232019a2f71a" />

Execution Steps in order to run in fastapi uvicorn

# 1. Create and enter project folder
cd project-name

# 2. Install dependencies
pip install -r requirements.txt

# 4. Create .env file (paste your OpenAI API Key here)
OpenAI_API_KEY=YOUR-API-KEY-HERE
API_APP_KEY=NAME-OF-API-APP-GIVEN

# 5. Run the server
uvicorn file_name:app --port 8000

# 6. Open Swagger UI in browser
# → http://localhost:8000/docs ->uthorize your API_APP_KEY_NAME and input data under post method to get the desired status code 200 with the generated ouptut

Output Screenshots:

<img width="1385" height="516" alt="image" src="https://github.com/user-attachments/assets/94bde598-698c-4d92-8100-294ad5c57774" />

<img width="1895" height="778" alt="image" src="https://github.com/user-attachments/assets/44bd61f9-7c57-422c-8223-a383cc61cd26" />

<img width="1086" height="524" alt="image" src="https://github.com/user-attachments/assets/d077c06f-c683-4d1e-bc5a-83be71f64849" />

<img width="1077" height="516" alt="image" src="https://github.com/user-attachments/assets/dd142e22-19ad-4b0f-819a-9ee603691eca" />

<img width="321" height="135" alt="image" src="https://github.com/user-attachments/assets/15ee12cc-0647-41e3-bb90-b3a61635d211" /> -> Now it is authorised

<img width="1888" height="760" alt="image" src="https://github.com/user-attachments/assets/ee6d260e-6535-4394-b07f-c7d809f7b43c" />

curl
<img width="1890" height="785" alt="image" src="https://github.com/user-attachments/assets/69c1a3e9-4f5a-4e57-91d5-35d94b77cf0e" />

<img width="1878" height="785" alt="image" src="https://github.com/user-attachments/assets/dd843285-02cf-4056-b536-7ac0d2d8b8a2" />

<img width="1912" height="856" alt="image" src="https://github.com/user-attachments/assets/c8fb7154-f8c9-4890-b230-31752b2e9020" />

After executing the raw Input we get the status code 200 reponse with the expected output
