from urllib.parse import parse_qsl, parse_qs ,urlparse, urlunsplit, urlencode
import sys
import db
import os
import csv

url = 'https://google.com?q=asdas'
BASE_URL = 'https://employers.indeed.com/hiring-insights?q=replace&l=replace&country=replace'

def generate_job_url(job: str, location: str, country: str = 'US'):
    parsed_url = urlparse(BASE_URL)
    return urlunsplit(
        (
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            urlencode({'q': job, 'l': location, 'country': country}),
                      None)
        )


def set_date_url(url: str, month: str):
    parsed_url = urlparse(url)
    query = parse_qsl(parsed_url.query)
    query.append(('month', month))
    date_url = urlunsplit(
        (
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        urlencode(query),
        None)
    )
    return date_url


def generate_and_save_job_urls_from_location(job: str):
    if not os.path.exists('locations.csv'):
        raise FileNotFoundError('Cannot find locations.csv')
    with open('locations.csv', 'r') as csv_file:
        reader = csv.reader(csv_file)
        for r in reader:
            job_url = generate_job_url(job, r[0])
            db.save_url(job, r[0], 'US', job_url)

def generate_and_save_urls_from_jobs_and_locations_csv():
    if not os.path.exists('locations.csv'):
        raise FileNotFoundError('Cannot find locations.csv')
    
    if not os.path.exists('jobs.csv'):
        raise FileNotFoundError('Cannot find jobs.csv')
    jobs = []
    locations = []
    with open('jobs.csv', 'r') as f:
        jobs = f.read().split('\n')
    with open('locations.csv', 'r') as f:
        locations = f.read().split('\n')

    for location in locations:
        temp_urls = []
        for job in jobs:
            temp_urls.append([job, location, 'US', generate_job_url(job, location)])
        db.save_urls(temp_urls)


def add_url_cmd():
    job = ''
    while job == '':
        job = input("Enter job: ").strip().lower()
        if job == '':
            print("Invalid job. Please enter again.")
    location = ''
    while location == '':
        location = input("Enter location: ").strip().lower()
        if location == '':
            print("Invalid location. Please enter again.")
    country = ''
    country = input("Enter counry (Press enter for default: US): ").strip().upper()
    url = None
    if country == '':
        url = generate_job_url(job, location)
    else:
        url = generate_job_url(job, location, country)
    db.save_url(job, location, country, url)
    print("URL SUCESSFULLY ADDED: ", url)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'add':
            add_url_cmd()

        else:
            print("INVALID COMMAND")


