# HCM Agent Platform

An AI agent layer that sits on top of Oracle or SAP HCM systems to automate 
the recruiting pipeline — resume screening, candidate assessment, and interview 
scheduling — while keeping humans in control of every decision that matters.

---

## The Problem It Solves

Recruiters in Oracle HCM or SAP SuccessFactors environments spend significant 
time on work that is repetitive and rule-based: reading resumes, scoring them 
against job descriptions, writing assessment questions, and coordinating 
interview slots. This is time taken away from the work that actually requires 
human judgment.

This platform automates the mechanical parts of the recruiting pipeline by 
sitting as an intelligence layer above the ERP. It reads from and writes back 
to the ERP through its existing REST APIs — no replacement, no migration, no 
disruption to the system of record.

---

## What It Does

A recruiter uploads a candidate's resume and selects a job requisition. 
The agent then runs the full pipeline automatically:

| Step | What happens | Threshold |
|------|-------------|-----------|
| Resume extraction | LLM parses skills, experience, education from PDF | — |
| Match scoring | Candidate scored against JD requirements | — |
| Routing | High scores proceed automatically, low scores go to HM queue | 65% |
| Assessment generation | Role-specific questions generated for the candidate | — |
| Assessment scoring | Candidate responses scored by LLM | 75% |
| Interview scheduling | 12 slots generated across 2 weeks for candidate to pick | — |

Below-threshold candidates are never auto-rejected. Every low-score application 
surfaces a detailed match report in the human review queue for the hiring manager 
to decide.

---

## How It Works

oracle-hcm-recruiting-rag/
│
├── data/
│   ├── oracle_hcm_recruiting_rag_chunks.json         # Implementing Recruiting — 1,123 chunks
│   ├── oracle_hcm_recruiting_rag.md                  # Implementing Recruiting — full markdown
│   ├── oracle_hcm_using_recruiting_rag_chunks.json   # Using Recruiting — 412 chunks
│   └── oracle_hcm_using_recruiting_rag.md            # Using Recruiting — full markdown
│
├── src/
│   ├── ingest.py        # Loads both guides into ChromaDB vector database
│   └── app.py           # Streamlit chat interface
│
├── .env                 # Your OpenAI API key (never committed to GitHub)
├── .gitignore
├── requirements.txt
└── README.md

Resume PDF uploaded
└── extract_candidate     LLM extracts structured profile from raw text
└── match_resume          LLM scores candidate 0-100 against JD
├── score ≥ 65%  →  generate_assessment   LLM generates 5 role-specific questions
│                       └── [candidate submits answers]
│                       └── score_assessment   LLM scores responses
│                            ├── score ≥ 75%  →  schedule_interview   12 slots, 2 weeks
│                            └── score < 75%  →  human_review_queue
└── score < 65%  →  human_review_queue   HM approves or rejects manually

---

## Why This Works on Top of Oracle and SAP

Oracle HCM and SAP SuccessFactors are systems of record with years of data, 
compliance configurations, and workflows built in. Replacing them is a 
multi-year project. This platform doesn't replace them.

The connector layer reads requisitions and candidate data through existing 
ERP REST APIs and writes decisions back. The ERP stays the source of truth. 
The agent adds the intelligence layer on top.

Swapping between Oracle and SAP — or moving from a mock environment to a 
live one — is a single line change in `.env`. No agent code changes. 
No UI changes.

---

## Project Structure

hcm-agent-platform/
│
├── agents/                         # LangGraph agent definitions
│   └── recruiting/                 # Recruiting module agent
│       ├── graph.py                # Pipeline graph — nodes, edges, routing
│       ├── nodes.py                # All agent step functions
│       ├── prompts.py              # All LLM prompts, centralised
│       ├── state.py                # TypedDict state passed between nodes
│       └── init.py
│
├── connectors/                     # ERP adapter layer
│   ├── base.py                     # BaseERPConnector interface (the contract)
│   ├── factory.py                  # Returns correct connector from .env setting
│   ├── mock_erp/                   # In-memory mock with Oracle HCM data shape
│   │   ├── client.py               # MockERPClient — implements BaseERPConnector
│   │   ├── seed_data.py            # 3 realistic job requisitions
│   │   └── init.py
│   ├── oracle_hcm/                 # Real Oracle HCM connector (stub)
│   │   ├── client.py               # OracleHCMClient — fill in when you have access
│   │   └── init.py
│   └── init.py
│
├── core/                           # Shared logic used across all agents
│   ├── models.py                   # Pydantic models — Candidate, JobRequisition,
│   │                               # MatchResult, Assessment, AssessmentScore,
│   │                               # InterviewSlot, ApplicationRecord
│   ├── llm.py                      # Model-agnostic LLM client with retry logic
│   ├── resume_parser.py            # PDF text extraction (pdfplumber + pymupdf)
│   └── init.py
│
├── ui/                             # Streamlit interface
│   ├── session.py                  # Session state helpers shared across pages
│   └── recruiting/                 # Recruiting module pages
│       ├── upload.py               # Resume upload + live pipeline runner
│       ├── review_queue.py         # HM review queue for below-threshold candidates
│       ├── tracker.py              # Application pipeline tracker
│       └── init.py
│
├── config/
│   ├── settings.py                 # All settings loaded from .env via pydantic-settings
│   └── init.py
│
├── app.py                          # Streamlit entry point and navigation
├── requirements.txt
├── .env.example                    # Template — copy to .env and add your keys
├── .gitignore
└── README.md

---

## Roles in Seed Data

Three realistic job requisitions are included for testing:

| ID | Role | Department | Min Experience |
|----|------|-----------|----------------|
| REQ-001 | Software Engineer II | Engineering | 2 years |
| REQ-002 | HR Business Partner | Human Resources | 4 years |
| REQ-003 | Finance Analyst | Finance | 2 years |

Assessment question types are role-specific — technical and behavioural for 
engineering, numerical and situational for finance, behavioural and situational 
for HR.

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.11+ | Core language |
| LangGraph | Agent orchestration and pipeline graph |
| Groq / Llama 3 70B | LLM — free tier, swappable to any model |
| Streamlit | Browser-based UI |
| Pydantic | Data validation and modelling |
| pdfplumber + pymupdf | PDF resume text extraction |
| tenacity | Retry logic for LLM API calls |
| python-dotenv | API key management via .env |

---

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/YOUR-USERNAME/hcm-agent-platform.git
cd hcm-agent-platform
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv
source venv/bin/activate        # Mac / Linux
venv\Scripts\activate           # Windows
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Add your Groq API key**

Copy `.env.example` to `.env` and paste your key:
GROQ_API_KEY=your_key_here
Get a free key at https://console.groq.com

**5. Run the app**
```bash
streamlit run app.py
```
Opens at http://localhost:8501

---

## Expanding the Platform

The architecture is designed for expansion across HCM modules.

**Add a new module (e.g. onboarding):**
1. Create `agents/onboarding/` with `graph.py`, `nodes.py`, `state.py`, `prompts.py`
2. Create `ui/onboarding/` with your Streamlit pages
3. Add the module to the sidebar in `app.py`

Core, connectors, and config are untouched.

**Connect to real Oracle HCM:**
1. Implement `connectors/oracle_hcm/client.py` using Oracle HCM REST API v4
2. Set `ERP_CONNECTOR=oracle` in `.env`

**Swap the LLM:**
Edit `core/llm.py` only. All agent nodes call `call_llm()` — 
nothing else changes.

---

## Planned Future Agents

- Offer drafting agent — post successful interview
- Onboarding agent — document collection, access provisioning
- L&D agent — learning module recommendations (HCM Learning Cloud)
