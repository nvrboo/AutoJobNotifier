import datetime

import requests
from apify_client import ApifyClient

import config

class JobListingAPI:

    @staticmethod
    def fetch_indeed_jobs_with_apify(titles: list, location: str = None, radius: int = None, level: str = "entry_level"):
        client = ApifyClient(config.APIFY_TOKEN)

        urls = []
        for job_parameters in titles:
            if job_parameters['search_days_limit'] > 14:
                job_parameters['search_days_limit'] = 14
            elif job_parameters['search_days_limit'] > 7:
                job_parameters['search_days_limit'] = 7
            elif job_parameters['search_days_limit'] > 3:
                job_parameters['search_days_limit'] = 3
            elif job_parameters['search_days_limit'] > 1:
                job_parameters['search_days_limit'] = 1
            elif job_parameters['search_days_limit'] < 1:
                job_parameters['search_days_limit'] = 1
            remote = job_parameters.get('remote', False)
            url_level = ''
            if level == "entry_level":
                url_level = 'ENTRY_LEVEL'
            elif level == "mid_level":
                url_level = 'MID_LEVEL'
            elif level == "senior_level":
                url_level = 'SENIOR_LEVEL'
            url = f'https://www.indeed.com/jobs?q={job_parameters['title'].replace(' ', '+')}&fromage={job_parameters['search_days_limit']}&commuteTime={radius}&sc=0kf%3A{'attr%28DSQF7%29' if remote else ''}explvl%28{url_level}%29%3B'
            if not remote:
                url += f'&l={location.replace(',', '%2C').replace(' ', '+')}'
            urls.append(url)

        input = {
            "enableUniqueJobs": True,
            "maxRowsPerUrl": 10,
            "urls": urls
        }

        run = client.actor("borderline/indeed-scraper").call(run_input=input, logger=False)

        dataset_id = run["defaultDatasetId"]
        data = client.dataset(dataset_id).list_items().items

        formatted_data = []

        for job in data:
            job_data = {
                'url': job['jobUrl'],
                'apply_url': job.get('applyUrl', job['jobUrl']),
                'title': job['title'],
                'company': job.get('companyName'),
                'location': job['location']['formattedAddressLong'],
                'description': job.get('descriptionText', ''),
                'attributes': job.get('attributes', []),
                'benefits': job.get('benefits'),
                'posted_time': datetime.datetime.strptime(job.get('datePublished'), "%Y-%m-%d"),
                'source': 'indeed'
            }
            formatted_data.append(job_data)

        return formatted_data

    @staticmethod
    def fetch_linkedin_jobs_with_apify(titles: list, geoid: int = None, radius: int = None, level: str = "entry_level"):
        client = ApifyClient(config.APIFY_TOKEN)

        urls = []
        for job_parameters in titles:
            remote = job_parameters.get('remote', False)
            url_level = ''
            if level == "entry_level":
                url_level = 'f_E=2'
            elif level == "mid_level":
                url_level = 'f_E=4'
            elif level == "senior_level":
                url_level = 'f_E=4'
            url = f'https://www.linkedin.com/jobs/search/?keywords={job_parameters['title'].replace(" ", "%20")}&f_TPR=r{job_parameters['search_days_limit']*60*60}'
            if not remote:
                url += f'&distance={radius}&geoId={geoid}'
            else:
                url += f'&f_WT=2'
            url += f'&{url_level}'
            print(url)
            urls.append(url)

        input = {
          "count": 100,
          "scrapeCompany": True,
          "urls": urls
        }

        run = client.actor("curious_coder/linkedin-jobs-scraper").call(run_input=input, logger=False)

        dataset_id = run["defaultDatasetId"]
        data = client.dataset(dataset_id).list_items().items

        formatted_data = []

        for job in data:
            job_data = {
                'url': job['link'],
                'apply_url': job.get('applyUrl', job['link']),
                'title': job['title'],
                'company': job.get('companyName'),
                'location': job['location'],
                'description': job.get('descriptionText', ''),
                'attributes': [],
                'benefits': job.get('benefits'),
                'posted_time': datetime.datetime.strptime(job.get('postedAt'), "%Y-%m-%d"),
                'source': 'linkedin'
            }
            formatted_data.append(job_data)

        return formatted_data

