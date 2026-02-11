import json
import os

from dotenv import load_dotenv

load_dotenv()


def get_env(key, value_type=None):
    print(f'Loading {key} environment variables')
    value = os.environ.get(key)
    if value is None:
        raise RuntimeError(f"Missing env var: {key}")

    if value_type in [list, dict]:
        raw = value.strip()
        if not raw:
            raise RuntimeError(f"{key} is empty/whitespace (len={len(value)})")
        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            # safe debug: don't print raw
            raise RuntimeError(
                f"{key} invalid JSON. len={len(value)} first_char={ord(raw[0])} first_char_repr={repr(raw[0])}"
            ) from e
    if value_type == int:
        return int(value)
    return value


DATABASE_URL = get_env("DATABASE_URL")

APIFY_TOKEN = get_env("APIFY_TOKEN")
OPENAI_API_KEY = get_env("OPENAI_API_KEY")

top_job_min_ai_score = 80

database_fields = [
    'id SERIAL PRIMARY KEY',
    'url TEXT',
    'apply_url TEXT',
    'job_title TEXT',
    'search_titles JSON',
    'company TEXT',
    'location TEXT',
    'description TEXT',
    'attributes JSON',
    'benefits JSON',
    'posted_time TIMESTAMP',
    'search_time TIMESTAMP',
    'processed BOOLEAN DEFAULT FALSE',
]

job_titles = {
    # Pure help desk/support
    'support': [{"title": "IT Support Specialist", "remote": False},
                {"title": "Help Desk Technician", "remote": False},
                {"title": "Technical Support Specialist", "remote": False},
                {"title": "IT Assistant", "remote": False},
                {"title": "Application Support Analyst", "remote": False},
                {"title": "Desktop Support Technician", "remote": False},
                {"title": "Network Technician", "remote": False},
                {"title": "End User Support Technician", "remote": False}],

    # Coding Tutor
    'coding_tutor': [{"title": "Coding Tutor", "remote": False},
                     {"title": "Coding Tutor", "remote": True},],

    # Dev/Programming
    'dev': [{"title": "Junior Software Developer", "remote": False},
            {"title": "Junior Software Developer", "remote": True},
            {"title": "Junior Web Developer", "remote": False},
            {"title": "Junior Web Developer", "remote": True},
            {"title": "Entry-Level Programmer", "remote": False},
            {"title": "Entry-Level Programmer", "remote": True},
            {"title": "Python Software Developer", "remote": False},
            {"title": "Python Software Developer", "remote": True},
            {"title": "Python Back-end Developer", "remote": False},
            {"title": "Python Back-end Developer", "remote": True}],

    # Testing
    'testing': [{"title": "QA Tester", "remote": False},
                {"title": "QA Tester", "remote": True},
                {"title": "Automation Tester", "remote": False},
                {"title": "Automation Tester", "remote": True}],

    # Interns
    'internships': [{"title": "IT Intern", "remote": False},
                    {"title": "Technology Intern", "remote": False},
                    {"title": "QA Intern", "remote": False},
                    {"title": "Developer Intern", "remote": False}]
}

IGNORE_COMPANIES = get_env('IGNORE_COMPANIES', list)

ai_overview_prompt = """
You are a no-BS hiring coach for a person. 
- Analyze this job posting against his skills. 
- You must consider hard requirements writen in job description when analyzing the job. 
- Consider missing skills of a person while analyzing. 
- If a job lists required skills that can't be easily learned overnight, don't give a job too high of a score
PERSON'S INFORMATION:{info}
EXPERIENCE:{experience}
PERSON'S SKILLS:{skills}

OUTPUT EXACTLY THIS JSON (no extra text):

{{
  "seniority_risk": "NONE|LOW|MEDIUM|HIGH",
  "missing_skills": ["0-5 gaps. most important ones go first"],
  "matching_skills": ["2-5 Person's strengths that map DIRECTLY to the listed requirements"],
  "overview": "1-3 sentences: What job does + person's daily tasks in simple words."
  "fit_score": 0-100,
  "apply": "YES"|"NO",
  "apply_reason": "2 sentences why (yes/no)",
}}
"""

fit_score_ember_colors = {
    0: '7a0000',
    20: 'd60000',
    35: 'fa6400',
    50: 'fab700',
    70: '09c702',
    90: '0037ff'
}
