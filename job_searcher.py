import datetime
import threading

import config
from ai_tool import AITool
from database_api import DatabaseAPI
from job_listing_api import JobListingAPI
from webhook_sender import WebhookSender


class JobSearcher:
    def __init__(self, apify_token: str, open_ai_token: str, database_url: str,
                 top_jobs_webhook: str, average_jobs_webhook: str, low_score_jobs_webhook: str,
                 job_titles: list, search_id: int,
                 person_info: list, person_experience: list, person_skills: dict,
                 location: str = None, linkedin_geoid: str = None, radius: int = None,
                 ignore_companies: list = None):
        self.apify_token = apify_token
        self.open_ai_token = open_ai_token
        self.database_url = database_url
        self.top_jobs_webhook = top_jobs_webhook
        self.average_jobs_webhook = average_jobs_webhook
        self.low_score_jobs_webhook = low_score_jobs_webhook
        self.job_titles = job_titles.copy()
        self.search_id = search_id
        self.person_info = person_info
        self.person_experience = person_experience
        self.person_skills = person_skills
        self.radius = radius
        self.location = location
        self.linkedin_geoid = linkedin_geoid
        self.ignore_companies = ignore_companies
        if ignore_companies is None:
            self.ignore_companies = []
        self.database_api = DatabaseAPI(self.database_url)
        self.database_api.init_db()
        self.database_api.ensure_schema()

    def search(self, listings: list):
        jobs = []
        for i in range(len(self.job_titles)):
            job_parameters = self.job_titles[i]
            self.job_titles[i]['search_days_limit'] = 3
            search_title = job_parameters['title']
            is_remote = job_parameters.get('remote', False)
            formatted_search_title = f'{search_title}{" Remote" if is_remote else ""}'
            db_search_title = f'{formatted_search_title} {self.search_id} ({", ".join(listings)})'
            self.job_titles[i]['formatted_search_title'] = formatted_search_title
            self.job_titles[i]['db_search_title'] = db_search_title
            last_search_time = self.database_api.get_last_search_time_by_job_search_title(db_search_title)

            if last_search_time is not None:
                if datetime.datetime.now() - last_search_time < datetime.timedelta(hours=23):
                    print(f"- Last search time is less than 1 day for {formatted_search_title}. Skipping")
                    job_parameters['skip'] = True
                    continue
                else:
                    self.job_titles[i]['search_days_limit'] = round((datetime.datetime.now() - last_search_time).seconds / 60 / 60 / 24)
                    if self.job_titles[i]['search_days_limit'] < 1:
                        self.job_titles[i]['search_days_limit'] = 1
            print(f"- Search Days Limit for {formatted_search_title} is {self.job_titles[i]['search_days_limit']} days")

        self.job_titles = [j for j in self.job_titles if not j.get('skip')]
        if not self.job_titles:
            print(f"- Search is cancelled because there are no job titles")
            return
        if "indeed" in listings:
            print(f'- Using Indeed Search for {len(self.job_titles)} titles')
            indeed_jobs = JobListingAPI.fetch_indeed_jobs_with_apify(self.job_titles, self.location, self.radius)
            jobs += indeed_jobs
            print(f'- Found {len(indeed_jobs)} jobs using Indeed')
        if 'linkedin' in listings:
            print(f'- Using LinkedIn Search for {len(self.job_titles)} titles')
            linkedin_jobs = JobListingAPI.fetch_linkedin_jobs_with_apify(self.job_titles, self.linkedin_geoid, self.radius)
            jobs += linkedin_jobs
            print(f'- Found {len(linkedin_jobs)} jobs using LinkedIn')
        print(f'- Found {len(jobs)} jobs in total')
        if not jobs:
            print(f"- No jobs found")
            pseudo_url = f'https://{datetime.datetime.now().timestamp()}'
            self.database_api.add_job(
                pseudo_url,
                None, 'NoJob', [f"{i['db_search_title']}" for i in self.job_titles], None, None, None, [], [], datetime.datetime.now(),
                datetime.datetime.now())
            self.database_api.mark_processed(pseudo_url)

        for job in jobs:
            job_url = job['url']

            if self.database_api.is_processed(job_url):
                print(f'- Job is already processed: {job['title']}')
                continue

            if job['company'] in self.ignore_companies:
                print(f'- Ignoring by company: {job['title']}')
                continue

            print(f'- New job found: {job['title']}')

            self.database_api.add_job(
                job['url'],
                job['apply_url'],
                job['title'],
                [f"{i['db_search_title']}" for i in self.job_titles],
                job['company'],
                job['location'],
                job['description'],
                job['attributes'],
                job['benefits'],
                job['posted_time'],
                datetime.datetime.now())

            threading.Thread(target=self.__generate_overview_and_send_webhook,
                             args=(job,)).start()
            self.database_api.mark_processed(job['url'])

    def __generate_overview_and_send_webhook(self, job):
        ai_overview = AITool.make_overview(job['title'],
                                           job['description'],
                                           job['company'],
                                           job['location'],
                                           self.person_info,
                                           self.person_experience,
                                           self.person_skills)

        webhook_url = self.average_jobs_webhook

        if ai_overview['fit_score'] >= 80:
            webhook_url = self.top_jobs_webhook

        if ai_overview['apply'] == 'NO':
            webhook_url = self.low_score_jobs_webhook

        WebhookSender.send_job(webhook_url,
                               job['url'],
                               job['apply_url'],
                               job['title'],
                               job['company'],
                               job['location'],
                               job['description'],
                               job['attributes'],
                               job['benefits'],
                               job['posted_time'].timestamp(),
                               job['source'],
                               ai_overview
                               )


