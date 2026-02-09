import config
from job_searcher import JobSearcher


if __name__ == '__main__':
    searcher = JobSearcher(config.APIFY_TOKEN, config.OPENAI_API_KEY, config.DATABASE_URL,
                           config.get_env('TOP_JOBS_WEBHOOK_URL_1'), config.get_env('JOBS_WEBHOOK_URL_1'), config.get_env('LOW_SCORE_JOBS_WEBHOOK_URL_1'),
                           [], 1,
                           config.get_env('PERSON_INFO_1', list), config.get_env('PERSON_EXPERIENCE_1', list), config.get_env('PERSON_SKILLS_1', dict),
                           config.get_env('LOCATION'), config.get_env('LINKEDIN_GEOID'), config.get_env('RADIUS_1'),
                           config.ignore_companies,
                           config.get_env('TOP_JOB_ROLE_ID'), config.get_env('GOOD_JOB_ROLE_ID'), config.get_env('EASY_APPLY_ROLE_ID'))
    searcher.job_titles = config.job_titles['support'] + config.job_titles['coding_tutor'] + config.job_titles['dev'] + config.job_titles['testing'] + config.job_titles['internships']
    searcher.search(['indeed'])
    searcher.job_titles = config.job_titles['coding_tutor'] + config.job_titles['dev'] + config.job_titles['testing'] + config.job_titles['internships']
    searcher.search(['linkedin'])
