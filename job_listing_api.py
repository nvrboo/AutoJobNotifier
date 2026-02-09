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
            print(job)
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
                'remote': job.get('isRemote'),
                'easy_apply': job.get('applyUrl').startswith('http://www.indeed.com'),
                'source': 'indeed'
            }
            print(job_data)
            formatted_data.append(job_data)

        return formatted_data

    @staticmethod
    def fetch_linkedin_jobs_with_apify(titles: list, geoid: int = None, radius: int = None, level: str = "entry_level"):
        client = ApifyClient(config.APIFY_TOKEN)

        if titles:
            if titles[0]['search_days_limit'] <= 3:
                posted_limit = '24h'
            elif titles[0]['search_days_limit'] <= 14:
                posted_limit = 'week'
            else:
                posted_limit = 'month'

        experience_level = ''
        if level == "entry_level":
            experience_level = 'entry'
        elif level in ["mid_level", "senior_level"]:
            experience_level = 'mid-senior'

        input = {
            # "easyApply": True,
            # "under10Applicants": True,
            "experienceLevel": [experience_level],
            "geoIds": [str(geoid)],
            "jobTitles": [],
            "maxItems": 5,
            "postedLimit": posted_limit,
            "sortBy": "date",
            "workplaceType": []
        }

        input['jobTitles'] = [i['title'] for i in titles if i.get('remote') is False]
        run = client.actor("harvestapi/linkedin-job-search").call(run_input=input, logger=False)

        dataset_id = run["defaultDatasetId"]
        data = client.dataset(dataset_id).list_items().items

        input['jobTitles'] = [i['title'] for i in titles if i.get('remote') is True]
        input['workplaceType'] = ["remote"]
        run = client.actor("harvestapi/linkedin-job-search").call(run_input=input, logger=False)

        dataset_id = run["defaultDatasetId"]
        data += client.dataset(dataset_id).list_items().items

        formatted_data = []

        for job in data:
            print(job)
            job_data = {
                'url': job['linkedinUrl'],
                'apply_url': job.get('applyMethod', {}).get('companyApplyUrl'),
                'title': job['title'],
                'company': job.get('company').get('name'),
                'location': job.get('locations', [{}])[0].get('parsed', {}).get('text'),
                'description': job.get('descriptionText', ''),
                'attributes': [],
                'benefits': job.get('benefits'),
                'posted_time': datetime.datetime.strptime(job.get('postedDate'), "%Y-%m-%dT%H:%M:%S.%fZ"),
                'applicants': job.get('applicants'),
                'remote': job.get('workplaceType') == 'remote',
                'easy_apply': job.get('easyApplyUrl') is not None,
                'source': 'linkedin'
            }
            print(job_data)
            formatted_data.append(job_data)

        return formatted_data

