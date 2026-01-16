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

top_jobs_webhook_url = get_env("TOP_JOBS_WEBHOOK_URL")
jobs_webhook_url = get_env("JOBS_WEBHOOK_URL")
low_score_jobs_webhook_url = get_env("LOW_SCORE_JOBS_WEBHOOK_URL")

APIFY_TOKEN = get_env("APIFY_TOKEN")
OPENAI_API_KEY = get_env("OPENAI_API_KEY")

LOCATION = get_env("LOCATION")
LINKEDIN_GEOID = get_env("LINKEDIN_GEOID", int)
RADIUS = get_env("RADIUS", int)

job_titles = [
    # Pure help desk/support
    {"title": "IT Support Specialist", "remote": False},
    {"title": "Help Desk Technician", "remote": False},
    {"title": "Technical Support Specialist", "remote": False},
    {"title": "IT Assistant", "remote": False},
    {"title": "Application Support Analyst", "remote": False},
    {"title": "Desktop Support Technician", "remote": False},
    {"title": "Network Technician", "remote": False},
    {"title": "End User Support Technician", "remote": False},

    # Dev/Programming
    {"title": "Junior Software Developer", "remote": False},
    {"title": "Junior Software Developer", "remote": True},
    {"title": "Junior Web Developer", "remote": False},
    {"title": "Junior Web Developer", "remote": True},
    {"title": "Entry-Level Programmer", "remote": False},
    {"title": "Entry-Level Programmer", "remote": True},
    {"title": "Python Software Developer", "remote": False},
    {"title": "Python Software Developer", "remote": True},

    # Testing
    {"title": "QA Tester", "remote": False},
    {"title": "QA Tester", "remote": True},
    {"title": "Automation Tester", "remote": False},
    {"title": "Automation Tester", "remote": True},

    # Interns
    {"title": "IT Intern", "remote": False},
    {"title": "Technology Intern", "remote": False},
    {"title": "QA Intern", "remote": False},
    {"title": "Developer Intern", "remote": False},
]


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
You are a no-BS hiring coach for a person ({LOCATION}). Analyze this job posting against his skills
PERSON'S INFORMATION:{"".join([f"\n- {i}" for i in PERSON_INFO])}
EXPERIENCE:{"".join([f"\n- {i}" for i in PERSON_EXPERIENCE])}
PERSON'S SKILLS:{skills_block}

OUTPUT EXACTLY THIS JSON (no extra text):

{{
  "seniority_risk": "NONE|LOW|MEDIUM|HIGH",
  "missing_skills": ["0-5 gaps"],
  "matching_skills": ["2-5 Person's strengths that map DIRECTLY to JD needs"],
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
