import datetime

import requests
from apify_client import ApifyClient

import config

class JobListingAPI:

    @staticmethod
    def fetch_indeed_jobs_with_hasdata(job_title: str, location: str):
        headers = {
            "Content-Type": "application/json",
            "x-api-key": config.HASDATA_API_KEY
        }
        params = {
            "keyword": job_title,
            "location": location,
            "sort": "date",
            "domain": "www.indeed.com"
        }
        try:
            response = requests.get("https://api.hasdata.com/scrape/indeed/listing", headers=headers, params=params, timeout=10)
            print(f"Status for {job_title}: {response.status_code}")
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            print(f"Request failed for {job_title}: {e}")
            return []
        except ValueError:
            print(f"Invalid JSON for {job_title}")
            return []

        if 'jobs' in data:
            return data['jobs']
        return []

    @staticmethod
    def fetch_indeed_jobs_with_apify(job_title: str, location: str, max_rows: int, radius: str, from_days: int, level: str = "entry_level"):
        client = ApifyClient(config.APIFY_TOKEN)

        input = {
            "country": "us",
            "query": job_title,
            "location": location,
            "maxRows": max_rows,
            "radius": radius,
            "level": level,
            "sort": "relevance",
            "fromDays": from_days,
            "enableUniqueJobs": True,
            "urls": []
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
    def fetch_linkedin_jobs_with_apify(job_title: str, radius: int, days_limit: float):
        client = ApifyClient(config.APIFY_TOKEN)

        input = {
          "count": 100,
          "scrapeCompany": True,
          "urls": [
            f"https://www.linkedin.com/jobs/search/?distance={radius}&f_E=2&f_TPR=r{days_limit*24*60*60}&geoId=100414609&keywords={job_title.replace(" ", "%20")}&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true"
          ]
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

