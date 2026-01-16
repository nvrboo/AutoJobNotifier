import config
from job_searcher import JobSearcher


if __name__ == '__main__':
    searcher = JobSearcher(config.APIFY_TOKEN, config.OPENAI_API_KEY, config.DATABASE_URL,
                           config.top_jobs_webhook_url, config.jobs_webhook_url, config.low_score_jobs_webhook_url,
                           config.job_titles, 1,
                           config.PERSON_INFO, config.PERSON_EXPERIENCE, config.PERSON_SKILLS,
                           config.LOCATION, config.LINKEDIN_GEOID, config.RADIUS,
                           config.ignore_companies)
    searcher.search(['indeed'])
