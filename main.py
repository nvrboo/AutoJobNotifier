import config
from job_searcher import JobSearcher


if __name__ == '__main__':
    searcher = JobSearcher(config.APIFY_TOKEN, config.OPENAI_API_KEY, config.DATABASE_URL,
                           config.top_jobs_webhook_url, config.jobs_webhook_url, config.low_score_jobs_webhook_url,
                           [], 1,
                           config.PERSON_INFO, config.PERSON_EXPERIENCE, config.PERSON_SKILLS,
                           config.LOCATION, config.LINKEDIN_GEOID, config.RADIUS,
                           config.ignore_companies)
    searcher.job_titles = config.job_titles['support'] + config.job_titles['dev'] + config.job_titles['testing'] + config.job_titles['internships']
    searcher.search(['indeed'])
    # searcher.job_titles = config.job_titles['dev'] + config.job_titles['testing'] + config.job_titles['internships']
    # searcher.search(['linkedin'])
