import json

from openai import OpenAI

import config


client = OpenAI(api_key=config.OPENAI_API_KEY)

class AITool:

    @staticmethod
    def make_overview(title, description, company, location, retries: int = 3):
        for _ in range(retries):
            try:
                response = client.responses.create(
                    model="gpt-5.1",
                    prompt_cache_retention="24h",
                    # temperature=0,
                    input=[
                        {
                            "role": "system",
                            "content": config.ai_overview_prompt
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
