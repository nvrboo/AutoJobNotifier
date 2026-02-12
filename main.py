import config
from job_searcher import JobSearcher


if __name__ == '__main__':
    searcher = JobSearcher(config.APIFY_TOKEN, config.OPENAI_API_KEY, config.DATABASE_URL,
                           config.get_env('TOP_JOBS_WEBHOOK_URL'), config.get_env('JOBS_WEBHOOK_URL'), config.get_env('LOW_SCORE_JOBS_WEBHOOK_URL'),
                           [], 1,
                           config.get_env('PERSON_INFO', list), config.get_env('PERSON_EXPERIENCE', list), config.get_env('PERSON_SKILLS', dict),
                           config.get_env('LOCATION'), config.get_env('LINKEDIN_GEOID'), config.get_env('RADIUS'),
                           config.IGNORE_COMPANIES,
                           config.get_env('TOP_JOB_ROLE_ID'), config.get_env('GOOD_JOB_ROLE_ID'), config.get_env('EASY_APPLY_ROLE_ID'))
    searcher.job_titles = config.job_titles['support'] + config.job_titles['coding_tutor'] + config.job_titles['dev'] + config.job_titles['testing'] + config.job_titles['internships']
    searcher.search(['indeed'])
    searcher.job_titles = config.job_titles['support'] + config.job_titles['coding_tutor'] + config.job_titles['dev'] + config.job_titles['testing'] + config.job_titles['internships']
    searcher.search(['linkedin'])
