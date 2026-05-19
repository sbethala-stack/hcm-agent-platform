from core.models import JobRequisition

REQUISITIONS: list[JobRequisition] = [
    JobRequisition(
        requisition_id="REQ-001",
        title="Software Engineer II",
        department="Engineering",
        required_skills=["Python", "REST APIs", "SQL", "Git", "Unit Testing"],
        preferred_skills=["FastAPI", "Docker", "AWS", "PostgreSQL", "CI/CD"],
        min_experience_years=2.0,
        description=(
            "We are looking for a Software Engineer II to join our backend platform team. "
            "You will design, build, and maintain scalable microservices that power our "
            "core product."
        ),
        responsibilities=[
            "Design and implement backend microservices using Python and FastAPI",
            "Write clean, well-tested code with >80% unit test coverage",
            "Participate in code reviews and contribute to engineering standards",
            "Debug and resolve production issues with on-call rotation",
            "Collaborate with product managers to refine technical requirements",
        ],
        qualifications=[
            "2+ years of professional software engineering experience",
            "Strong proficiency in Python",
            "Experience building and consuming REST APIs",
            "Solid understanding of relational databases and SQL",
            "Familiarity with Git and collaborative development workflows",
        ],
    ),
    JobRequisition(
        requisition_id="REQ-002",
        title="HR Business Partner",
        department="Human Resources",
        required_skills=[
            "Employee Relations",
            "Performance Management",
            "HRIS Systems",
            "Stakeholder Management",
            "Employment Law",
        ],
        preferred_skills=[
            "Organisational Development",
            "Change Management",
            "Talent Analytics",
            "Oracle HCM",
            "Coaching",
        ],
        min_experience_years=4.0,
        description=(
            "We are seeking an experienced HR Business Partner to work alongside senior "
            "leadership across two business units. You will act as a trusted advisor on "
            "people matters, aligning HR strategy with business objectives."
        ),
        responsibilities=[
            "Partner with business leaders to develop and execute people strategies",
            "Lead employee relations cases including investigations and disciplinaries",
            "Drive the annual performance review and calibration process",
            "Support organisational design, restructuring, and change programmes",
            "Analyse people data to identify trends and recommend interventions",
        ],
        qualifications=[
            "4+ years of HR generalist or HRBP experience",
            "Strong working knowledge of employment law",
            "Experience managing complex employee relations cases",
            "Proficiency with an HRIS system such as Oracle HCM or Workday",
            "CIPD Level 5 or equivalent HR qualification preferred",
        ],
    ),
    JobRequisition(
        requisition_id="REQ-003",
        title="Finance Analyst",
        department="Finance",
        required_skills=[
            "Financial Modelling",
            "Excel",
            "Variance Analysis",
            "Management Reporting",
            "Budgeting and Forecasting",
        ],
        preferred_skills=[
            "Power BI",
            "SQL",
            "SAP",
            "Python",
            "IFRS Standards",
        ],
        min_experience_years=2.0,
        description=(
            "We are hiring a Finance Analyst to support the FP&A team in delivering "
            "monthly management accounts, annual budgets, and ad-hoc financial analysis."
        ),
        responsibilities=[
            "Prepare monthly management accounts and variance commentary",
            "Maintain and develop financial models for budgeting and forecasting",
            "Support the annual budget and quarterly reforecast cycles",
            "Produce financial dashboards and reports for senior stakeholders",
            "Identify opportunities to improve financial processes and controls",
        ],
        qualifications=[
            "2+ years of experience in a finance analyst or similar role",
            "Advanced Excel skills including financial modelling",
            "Strong analytical skills with attention to detail",
            "Part-qualified or newly qualified ACA/ACCA/CIMA preferred",
            "Experience with an ERP system such as SAP or Oracle",
        ],
    ),
]

REQUISITIONS_BY_ID: dict[str, JobRequisition] = {
    r.requisition_id: r for r in REQUISITIONS
}