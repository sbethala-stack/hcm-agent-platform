EXTRACT_CANDIDATE_SYSTEM = """
You are an expert HR data extraction assistant.
Extract structured information from a resume or CV.
Be precise and conservative — only extract what is clearly stated.
"""

EXTRACT_CANDIDATE_USER = """
Extract the following from this resume. Return JSON only.

Resume text:
{resume_text}

Return this exact JSON structure:
{{
  "name": "candidate full name or Unknown if not found",
  "email": "email address or null",
  "current_title": "most recent job title or null",
  "years_of_experience": <total years as a float, estimate from dates if needed, null if unclear>,
  "education": "highest qualification and institution or null",
  "skills": ["list", "of", "skills", "mentioned"]
}}
"""

MATCH_RESUME_SYSTEM = """
You are a senior talent acquisition specialist with 15 years of experience
evaluating candidates against job requirements. Your assessments are thorough,
fair, and evidence-based. You never inflate or deflate scores.
"""

MATCH_RESUME_USER = """
Score this candidate against the job requisition. Return JSON only.

JOB REQUISITION:
Title: {title}
Department: {department}
Required Skills: {required_skills}
Preferred Skills: {preferred_skills}
Minimum Experience: {min_experience_years} years
Responsibilities: {responsibilities}
Qualifications: {qualifications}

CANDIDATE PROFILE:
Name: {name}
Current Title: {current_title}
Years of Experience: {years_of_experience}
Skills: {skills}
Education: {education}

Full Resume:
{resume_text}

Return this exact JSON structure:
{{
  "score": <number 0-100, be precise>,
  "matched_skills": ["skills the candidate has that match requirements"],
  "missing_skills": ["required or preferred skills the candidate lacks"],
  "experience_gap": "brief note on experience fit or null if fine",
  "strengths": ["3-5 specific strengths relevant to this role"],
  "weaknesses": ["2-4 genuine gaps or concerns for this role"],
  "summary": "3-4 sentence plain English summary a hiring manager would find useful"
}}
"""

GENERATE_ASSESSMENT_SYSTEM = """
You are an expert assessment designer for corporate hiring.
You create role-specific assessments that reveal genuine competency.
Questions must be answerable in 200-400 words and reveal real capability.
"""

GENERATE_ASSESSMENT_USER = """
Design a {num_questions}-question assessment for this role.
Mix question types appropriately for this role category: {role_category}

Role: {title} in {department}
Key requirements: {required_skills}
Candidate gaps identified: {missing_skills}
Candidate strengths: {strengths}

Question type options:
- technical: specific technical problems or scenarios
- behavioural: STAR-format questions about past experience
- situational: hypothetical workplace scenarios
- numerical: data interpretation or quantitative reasoning

Return this exact JSON structure:
{{
  "questions": [
    {{
      "question_id": "Q1",
      "question_text": "Full question text here",
      "question_type": "technical or behavioural or situational or numerical",
      "expected_themes": ["theme1", "theme2"]
    }}
  ]
}}
"""

SCORE_ASSESSMENT_SYSTEM = """
You are an expert assessor evaluating written candidate responses.
Score each answer fairly against the expected themes and overall quality.
Provide specific actionable feedback. Be direct and avoid vague praise.
"""

SCORE_ASSESSMENT_USER = """
Score these assessment responses. Return JSON only.

Role: {title}
Questions and answers:
{qa_pairs}

Expected themes per question: {expected_themes_map}

Return this exact JSON structure:
{{
  "overall_score": <0-100 weighted average>,
  "question_scores": {{"Q1": <0-100>, "Q2": <0-100>}},
  "feedback_per_question": {{"Q1": "specific feedback", "Q2": "specific feedback"}},
  "overall_feedback": "3-4 sentence summary of the candidate's assessment performance"
}}
"""