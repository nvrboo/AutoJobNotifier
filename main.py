import requests
import json
import psycopg2
from psycopg2.extras import RealDictCursor
import datetime

from database_api import DatabaseAPI
from job_listing_api import JobListingAPI
from webhook_sender import WebhookSender
from ai_tool import AITool
import config

DatabaseAPI.init_db()
DatabaseAPI.ensure_schema()

for job_title in config.job_titles:
    print(f"> Searching: {job_title}")

    last_search_time = DatabaseAPI.get_last_search_time_by_job_search_title(job_title)
    search_days_limit = 7

    if last_search_time is not None:
        if datetime.datetime.now() - last_search_time < datetime.timedelta(hours=23):
            print(f"- Last search time is less than 1 day. Skipping")
            continue
        else:
            search_days_limit = int((datetime.datetime.now() - last_search_time).days)
            print(f"- Search Days Limit: {search_days_limit}")

    jobs = []

    jobs += JobListingAPI.fetch_indeed_jobs_with_apify(job_title, config.LOCATION, 15, "35", str(search_days_limit))
    jobs += JobListingAPI.fetch_linkedin_jobs_with_apify(job_title, 35, search_days_limit)

    if not jobs:
        pseudo_url = f'https://{datetime.datetime.now().timestamp()}'
        DatabaseAPI.add_job(
            pseudo_url,
            None, 'NoJob', job_title, None, None, None, [], [], datetime.datetime.now(), datetime.datetime.now())
        DatabaseAPI.mark_processed(pseudo_url)

    for job in jobs:
        job_url = job['url']

        if DatabaseAPI.is_processed(job_url):
            if job_title not in DatabaseAPI.get_job_field_value(job_url, 'original_search_titles'):
                DatabaseAPI.add_search_title(job['url'], job_title)

            continue

        if job['company'] in config.ignore_companies:
            print(f'- Ignoring by company: {job['title']}')
            continue

        print(f'- Job found: {job['title']}')

        DatabaseAPI.add_job(
            job['url'],
            job['apply_url'],
            job['title'],
            job_title,
            job.get('company'),
            job['location'],
            job['description'],
            job['attributes'],
            job['benefits'],
            job['posted_time'],
            datetime.datetime.now())

        ai_overview = AITool.make_overview(job['title'],
                                           job['description'],
                                           job['company'],
                                           job['location'])

        webhook_url = config.jobs_webhook_url

        if ai_overview['fit_score'] >= 80:
            webhook_url = config.top_jobs_webhook_url

        if ai_overview['apply'] == 'NO':
            webhook_url = config.low_score_jobs_webhook_url

        WebhookSender.send_job(webhook_url,
                               job['url'],
                               job['apply_url'],
                               job_title,
                               job['title'],
                               job.get('company'),
                               job['location'],
                               job['description'],
                               job['attributes'],
                               job['benefits'],
                               job['posted_time'].timestamp(),
                               job['source'],
                               ai_overview
                               )

        DatabaseAPI.mark_processed(job_url)
