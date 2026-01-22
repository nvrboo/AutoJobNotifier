import json
from functools import lru_cache

from openai import OpenAI
from openai.types.shared_params import Reasoning

import config


client = OpenAI(api_key=config.OPENAI_API_KEY)

class AITool:

    @staticmethod
    def make_overview(title, description, company, location, person_info, person_experience, person_skills, retries: int = 3):
        for _ in range(retries):
            try:
                response = client.responses.create(
                    model="gpt-5.1",
                    prompt_cache_retention="24h",
                    # temperature=0,
                    reasoning={"effort": "medium"},
                    input=[
                        {
                            "role": "system",
                            "content": AITool.generate_prompt(person_info, person_experience, person_skills)
                        },
                        {
                            "role": "user",
                            "content": f'Title: {title}\n'
                                       f'Description: {description}\n'
                                       f'Company: {company}\n'
                                       f'Location: {location}',
                        },
                    ]
                )
                return json.loads(response.output_text)
            except Exception as e:
                print(e)
        return None

    @staticmethod
    @lru_cache(maxsize=1024)
    def generate_prompt(person_info, person_experience, person_skills):
        prompt = config.ai_overview_prompt
        info = {"".join([f"\n- {i}" for i in person_info])}
        experience = {"".join([f"\n- {i}" for i in person_experience])}
        skills = "".join(
            f"\n- {category}:" +
            "".join(f"\n    - {item}" for item in items)
            for category, items in person_skills.items()
        )
        prompt.format(info=info, experience=experience, skills=skills)
