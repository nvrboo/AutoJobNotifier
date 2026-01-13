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
        raw = value.strip()   # key change
        if not raw:
            raise RuntimeError(f"{key} is empty/whitespace (len={len(value)})")
        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            # safe debug: don't print raw
            raise RuntimeError(
                f"{key} invalid JSON. len={len(value)} first_char={ord(raw[0])} first_char_repr={repr(raw[0])}"
            ) from e
    return value



DATABASE_URL = get_env("DATABASE_URL")

database_fields = [
            'id SERIAL PRIMARY KEY',
            'url TEXT',
            'apply_url TEXT',
            'job_title TEXT',
            'original_search_titles JSON',
            'company TEXT',
            'location TEXT',
            'description TEXT',
            'attributes JSON',
            'benefits JSON',
            'posted_time TIMESTAMP',
            'search_time TIMESTAMP',
            'processed BOOLEAN DEFAULT FALSE',
        ]

top_jobs_webhook_url = get_env("TOP_JOBS_WEBHOOK_URL")
jobs_webhook_url = get_env("JOBS_WEBHOOK_URL")
low_score_jobs_webhook_url = get_env("LOW_SCORE_JOBS_WEBHOOK_URL")

APIFY_TOKEN = get_env("APIFY_TOKEN")
HASDATA_API_KEY = get_env("HASDATA_API_KEY")
OPENAI_API_KEY = get_env("OPENAI_API_KEY")

job_titles = [
    # Pure help desk/support
    "IT Support Specialist",
    "Help Desk Technician",
    "Technical Support Specialist",
    "IT Assistant",
    "Application Support Analyst",
    "Desktop Support Technician",
    "Network Technician",
    "End User Support Technician"

    # Dev/Programming
    "Junior Software Developer",
    "Junior Web Developer",
    "Entry-Level Programmer",
    "Python Software Developer",

    # Testing
    "QA Tester",
    "Automation Tester",

    # Interns
    "IT Intern",
    "Technology Intern",
    "QA Intern",
    "Developer Intern"
]

LOCATION = get_env("LOCATION")

l = LOCATION.split(",")

ignore_companies = ['DataAnnotation']

PERSON_INFO = get_env('PERSON_INFO', list)
PERSON_EXPERIENCE = get_env('PERSON_EXPERIENCE', list)
PERSON_SKILLS = get_env('PERSON_SKILLS', dict)

skills_block = "".join(
    f"\n- {category}:" +
    "".join(f"\n    - {item}" for item in items)
    for category, items in PERSON_SKILLS.items()
)

ai_overview_prompt = f"""
You are a no-BS IT hiring coach for a person (entry-level IT, {LOCATION}). Analyze this job posting against his skills
PERSON'S INFORMATION:{"".join([f"\n- {i}" for i in PERSON_INFO])}
EXPERIENCE:{"".join([f"\n- {i}" for i in PERSON_EXPERIENCE])}
PERSON'S SKILLS:{skills_block}

OUTPUT EXACTLY THIS JSON (no extra text):

{{
  "seniority_risk": "NONE|LOW|MEDIUM|HIGH",
  "missing_skills": ["0-5 gaps"],
  "matching_skills": ["2-5 Person's strengths that map DIRECTLY to JD needs"],
  "overview": "1-3 sentences: What job does + Person's daily tasks in simple words."
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
