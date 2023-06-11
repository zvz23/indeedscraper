import undetected_chromedriver as uc
import parsel
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from send_email import send_email
from urls import *
from export import export_conditions_jobs_to_csv
from dotenv import load_dotenv
import os
import sys
import json
import db
import argparse
import datetime
import time

load_dotenv()
# Sets the profile to selenium to persist browser data

PROFILE_PATH = None
PROFILE_NAME = 'indeed'

# Platform independent profile setting

if sys.platform == 'linux' or sys.platform == 'linux2':
    PROFILE_PATH = os.path.join('~/.config/google-chrome', PROFILE_NAME)
elif sys.platform == 'win32':
    PROFILE_PATH = os.path.join(os.getenv('LOCALAPPDATA'), 'Google', 'Chrome', 'User Data', PROFILE_NAME)
elif sys.platform == 'darwin':
    PROFILE_PATH = os.path.join('~/Library/Application Support/Google/Chrome', PROFILE_NAME)


SERVER_NAME = os.environ.get('SERVER_NAME')
EMAIL = os.environ.get('EMAIL')
PASSWORD = os.environ.get('PASSWORD')

MONTHS = {
    '202305': 'May 2023',
    '202304': 'April 2023',
    '202303': 'March 2023',
    '202302': 'February 2023',
    '202301': 'January 2023',
    '202212': 'December 2022',
    '202211': 'November 2022',
    '202210': 'October 2022',
    '202209': 'September 2022',
    '202208': 'August 2022',
    '202207': 'July 2022',
    '202206': 'June 2022',
    '202205': 'May 2022'
}

DEFAULT_JOB_DATA = {
    "competition_score": "N/A",
    "jobs": "N/A",
    "job_seekers": "N/A",
    "average_salary": "N/A",
    "employers": "N/A",
    "resumes": "N/A",
    "resumes_added": "N/A",
    "reported_years_of_experience": {
        "0 - 2": "N/A",
        "3 - 5": "N/A",
        "6 - 10": "N/A",
        "11 - 20": "N/A",
        "21+": "N/A"
    },
    "reported_educational_level": {
        "High School": "N/A",
        "Associate": "N/A",
        "Bachelor": "N/A",
        "Master": "N/A"
    },
    "common_employers": [],
    "common_locations": []
}

# Waits for a specified time until the loading element is not present or visible to the DOM
# The loading element will show on the first load of the website and if you select another date in the select option

def wait_invi(driver: uc.Chrome, seconds: float):
    WebDriverWait(driver, seconds).until(
        EC.invisibility_of_element_located((By.XPATH, "//div[contains(@class, 'ia-ThreeBounces')]"))
    )

def wait_vis(driver: uc.Chrome, seconds: float):
    WebDriverWait(driver, seconds).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'ia-ThreeBounces')]"))
    )


def wait_loading(driver: uc.Chrome, seconds: float):
    WebDriverWait(driver, seconds).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'ia-ThreeBounces')]"))
    )
    WebDriverWait(driver, seconds).until(
        EC.invisibility_of_element_located((By.XPATH, "//div[contains(@class, 'ia-ThreeBounces')]"))
    )

# Gets the selected month from the select input of the website

def get_selected_month(driver: uc.Chrome):
    return driver.execute_script('return document.querySelector(\'select[name="monthSelect"] option:checked\').label')



def validate_date(date: str):
    try:
        year = int(date[:4])
        if not (year >= 2019):
            return False
        month = int(date[4:])
        date = datetime.datetime(year, month, 1)
        return True
    except ValueError:
        return False


# Parses the data from the current page
# Parsing the html and searching specfic datas using xpath
# Note: If there is an inacurracy of the datas this is the function you will need to modify (MUST know how to use XPATH)

def parse_page(selector: parsel.Selector):
    job_details = {}

    competition_score = selector.xpath("//div[@data-testid='competition-score-value']/div/span/text()").get()
    job_details['competition_score'] = 'N/A' if competition_score is None else competition_score.strip()

    jobs = selector.xpath("//div[@data-testid='InsightsWidgetContainer:jobs']//div[@data-shield-id='InsightsNumberWidgetContent-value']/text()").get() 
    job_details['jobs'] = 'N/A' if jobs is None else jobs.strip()

    job_seekers = selector.xpath("//div[@data-testid='InsightsWidgetContainer:job_seekers']//div[@data-shield-id='InsightsNumberWidgetContent-value']/text()").get()
    job_details['job_seekers'] = 'N/A' if job_seekers is None else job_seekers.strip()

    average_salary = selector.xpath("//div[@data-testid='InsightsWidgetContainer:average_salary']//div[@id='average-salary-count']/text()").get()
    job_details['average_salary'] = 'N/A' if average_salary is None else average_salary.strip()

    employers = selector.xpath("//div[@data-testid='InsightsWidgetContainer:employers']//div[@data-shield-id='InsightsNumberWidgetContent-value']/text()").get()
    job_details['employers'] = 'N/A' if employers is None else employers.strip()

    resumes = selector.xpath("//div[@data-testid='InsightsWidgetContainer:resumes']//div[@data-shield-id='InsightsNumberWidgetContent-value']/text()").get()
    job_details['resumes'] = 'N/A' if resumes is None else resumes.strip()

    resumes_added = selector.xpath("//div[@data-testid='InsightsWidgetContainer:resumes_added_or_updated']//div[@data-shield-id='InsightsNumberWidgetContent-value']/text()").get()
    job_details['resumes_added'] = 'N/A' if resumes_added is None else resumes_added.strip()
    
    job_details['reported_years_of_experience'] = {}

    has_reported_experience = selector.xpath("//div[@data-shield-id='InsightsWidgetControlPanelButton:reported_years_of_experience' and @aria-disabled='false']").get()
    if has_reported_experience is not None:
        experience_container_sels = selector.xpath("//span[contains(@id, 'Reportedyearsofexperience')]")
        if len(experience_container_sels) > 0:
            main_experience_container_sel = experience_container_sels[0]
            experience_containers = main_experience_container_sel.xpath(".//tbody//tr")
            for ec in experience_containers:
                year = ec.xpath("./td[1]/text()").get()
                experience = ec.xpath("./td[2]/text()").get()
                job_details['reported_years_of_experience'][year] = experience
    

    job_details['reported_educational_level'] = {}
    
    has_reported_educational_level = selector.xpath("//div[@data-shield-id='InsightsWidgetControlPanelButton:reported_education_level' and @aria-disabled='false']").get()
    if has_reported_educational_level is not None:

        educational_container_sels = selector.xpath("//span[contains(@id, 'Reportededucationlevel')]")
        if len(educational_container_sels) > 0:
            main_educational_container = educational_container_sels[0]
            educational_containers = main_educational_container.xpath(".//tbody//tr")
            for ec in educational_containers:
                level = ec.xpath("./td[1]/text()").get()
                percent = ec.xpath("./td[2]/text()").get()
                job_details['reported_educational_level'][level] = percent


    job_details['common_employers'] = []
    common_employers_containers_sels = selector.xpath("//div[@data-shield-id='InsightsWidgetContainer:most_common_employers']//div[@data-testid='InsightsTopGraphWidgetContent']/a")
    for ce in common_employers_containers_sels:
        employer = ce.xpath("./div[2]/text()").get()
        value = ce.xpath("./div[3]/text()").get()
        job_details['common_employers'].append({
            'employer': employer,
            'value': value
        })
    
    job_details['common_locations'] = []

    common_locations_containers_sels = selector.xpath("//div[@data-shield-id='InsightsWidgetContainer:most_common_locations']//div[@data-testid='InsightsTopGraphWidgetContent']/a")
    for cl in common_locations_containers_sels:
        location = cl.xpath("./div[2]/text()").get()
        value = cl.xpath("./div[3]/text()").get()
        job_details['common_locations'].append({
            'location': location,
            'value': value
        })

    # job_seekrs_per_job = selector.xpath("//div[@data-testid='InsightsWidgetContainer:job_seekers_per_job']//div[@data-shield-id='InsightsNumberWidgetContent-value']/text()").get()
    # job_details['job_seekers_per_job'] = 'N/A' if job_seekrs_per_job is None else job_seekrs_per_job.strip()

    # candidate_devices = selector.xpath("//div[@data-testid='InsightsWidgetContainer:candidate_devices']//div[@data-shield-id='InsightsCandidateDevicesContent-number-mobile-click-count']/text()").get()
    # job_details['candidate_devices'] = 'N/A' if candidate_devices is None else candidate_devices.strip()

    # employers_count = selector.xpath("//div[@data-testid='InsightsWidgetContainer:employers']//div[@data-shield-id='InsightsNumberWidgetContent-value']/text()").get()
    # job_details['employers_count'] = 'N/A' if employers_count is None else employers_count.strip()
    
    # unemployment_percentage = selector.xpath("//div[@data-testid='InsightsWidgetContainer:unemployment_percentage']//div[@data-shield-id='InsightsNumberWidgetContent-value']/text()").get()
    # job_details['unemployment_percentage'] = 'N/A' if unemployment_percentage is None else unemployment_percentage.strip()

    # search_terms_by_clicks_containers_sels = selector.xpath("//div[@data-testid='InsightsWidgetContainer:top_search_terms_by_clicks']//div[@data-testid='InsightsTopGraphWidgetContent']/a")
    # search_terms = []
    # for st in search_terms_by_clicks_containers_sels:
    #     key = st.xpath("./div[2]/text()").get()
    #     value = st.xpath("./div[3]/text()").get()
    #     search_terms.append((key, value))
    
    # job_details['top_search_terms_by_clicks'] = search_terms


    # top_employers_by_clicks_containers_sels = selector.xpath("//div[@data-testid='InsightsWidgetContainer:top_employers_by_clicks']//div[@data-testid='InsightsTopGraphWidgetContent']/a")

    return job_details

# Selects the next option of the select element for months

def scroll_select(driver: uc.Chrome):
    select = driver.find_element(By.XPATH, "//select[@name='monthSelect']")
    actions = ActionChains(driver)
    actions.move_to_element(select)
    actions.click()
    actions.pause(0.8)
    actions.send_keys(Keys.ARROW_DOWN)
    actions.pause(0.5)
    actions.send_keys(Keys.ENTER)
    actions.perform()
    wait_vis(driver, 15)
    wait_invi(driver, 15)
    


# Counts the number of options (months) in the select element
# This function is used to determine how many times the scroll_select function to execute

def count_month(selector = parsel.Selector):
    return len(selector.xpath("//select[@name='monthSelect']/option"))

# Scrapes the urls from the database with specific date
def main_date(date: str):
    urls = db.get_all_unfinished_urls()
    if len(urls) == 0:
        print("ALL URLS ARE ALREADY SCRAPED")
        return
    driver = uc.Chrome(user_data_dir=PROFILE_PATH)
    driver.maximize_window()
    for url in urls:
        date_url = set_date_url(url, date)
        print("SCRAPING ", date_url)
        driver.get(date_url)
        wait_invi(driver, 15)
        if 'is not recognized or not supported' in driver.page_source or 'Unable to process your request' in driver.page_source:
            print("URL ERROR ", url)
            continue
        selector = parsel.Selector(text=driver.page_source)
        job = selector.xpath("//input[@id='input-job-title']/@value").get().strip()
        location = selector.xpath("//input[@id='input-job-location']/@value").get().strip()
        month, year = [d.strip().lower() for d in get_selected_month(driver).split(' ')]
        log_message = f"Job: {job} | Location: {location} | {month} {year}"
        print(f"SCRAPING {log_message}")
        if db.is_job_data_exists(url, job, location, month, year):
            print(f"ALREADY EXISTS, SKIPPING {log_message}")
            continue
        selector = parsel.Selector(text=driver.page_source)
        month_data = parse_page(selector)
        print(f"SAVED {log_message}")
        db.save_job_data(url, job, location, month, year, json.dumps(month_data))

    print("FINISHED SCRAPING")
    driver.quit()

def save_defaults(url: str, job: str, location: str):
    for m in MONTHS.keys():
        month, year = MONTHS[m].split(' ')
        db.save_job_data(url, job, location, month, year, json.dumps(DEFAULT_JOB_DATA))

def main(urls: list):
    if len(urls) == 0:
        print("THERE IS NO URL OR ALL URLS ARE ALREADY SCRAPED")
        return
    driver = uc.Chrome(user_data_dir=PROFILE_PATH)
    for url in urls:
        print("SCRAPING ", url['URL'])
        for m in MONTHS.keys():
            month_url = set_date_url(url['URL'], m)
            month, year = MONTHS[m].split(' ')
            log_message = f"Job: {url['JOB']} | Location: {url['LOCATION']} | {month} {year}"
            print(f"SCRAPING: {log_message}")
            if db.is_job_data_exists(url['URL'], url['JOB'], url['LOCATION'], month, year):
                print(f"JOB DATA ALREADY EXISTS: {log_message}")
                continue
            driver.get(month_url)
            wait_loading(driver, 10)
            if 'is not recognized or not supported' in driver.page_source or 'Unable to process your request' in driver.page_source:
                print("URL ERROR ", url)
                save_defaults(url['URL'], url['JOB'], url['LOCATION'])
                break
            if "We don't have any data for the requested title" in driver.page_source:
                print("NO DATA ", url)
                save_defaults(url['URL'], url['JOB'], url['LOCATION'])
                break
            selector = parsel.Selector(text=driver.page_source)
            month_data = parse_page(selector)
            print(f"SAVED: {log_message}")
            db.save_job_data(url['URL'], url['JOB'], url['LOCATION'], month, year, json.dumps(month_data))
        db.set_finished_url(url['URL'])
    print("FINISHED SCRAPING.")
    driver.quit()

        

# This function opens the login page of indeed

def login():
    driver = uc.Chrome(user_data_dir=PROFILE_PATH)
    driver.get("https://secure.indeed.com/auth?hl=en_US&co=US")
    input("Press enter if logged in...")
    driver.quit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest='command', required=True,)
    all = subparser.add_parser("all")
    february = subparser.add_parser("february")
    export = subparser.add_parser("export")
    reset = subparser.add_parser("reset")
    clear_db = subparser.add_parser('cleardb')
    login_cmd = subparser.add_parser("login")
    add_url = subparser.add_parser("addurl")
    add_job = subparser.add_parser("addjob")
    add_url_csv = subparser.add_parser("addurlscsv")
    date = subparser.add_parser("date")
    date.add_argument("--date", type=str, required=True)
    export.add_argument("--job", type=str.lower, required=False, default='')
    export.add_argument("--location", type=str.lower, required=False, default='')
    export.add_argument("--month", type=str, required=False, default='')
    export.add_argument("--year", type=str, required=False, default='')
    add_job.add_argument('--job', type=str.lower, required=True)
    all.add_argument('--job', type=str, required=False)

    args = parser.parse_args()
    try:

        if args.command == 'all':
            if args.job:
                urls = db.get_all_urls_with_conditions(job=args.job)
                if len(urls) == 0:
                    print(f"There are no urls for the job: {args.job}, either it is already scraped or you have entered a job that is not available in the database")
                else:
                    print("Scraping urls with the job: ", args.job)
                    main(urls)
            else:
                print("Scraping all urls")
                urls = db.get_all_unfinished_urls_row()
                main(urls)
        elif args.command == 'february':
            print("Scraping February 2023 only")
            main_date('202302')
        elif args.command == 'date':
            if not validate_date(args.date):
                print("Date is invalid. Please follow this format (yearmonth) Example: 202103 that example is March 2021")
            else:
                print("Scraping specific date: ", args.date)
                main_date(args.date)
        elif args.command == 'export':
            print("Exporting...")
            filename = export_conditions_jobs_to_csv(job=args.job, location=args.location, month=args.month, year=args.year)
            if filename is None:
                print("No datas exported. Please check the query")
            else:
                print(f"Finished exporting: {filename}")
        elif args.command == 'reset':
            print("Urls state are now changed to unfinished")
            db.set_all_unfinished()
        elif args.command == 'login':
            print("Opening login page...")
            login()
        elif args.command == 'addurl':
            add_url_cmd()
        elif args.command == 'addurlscsv':
            print("Generating urls from jobs.csv and locations.csv")
            generate_and_save_urls_from_jobs_and_locations_csv()
            print("Finished generating urls from jobs.csv and locations.csv")
        elif args.command == 'addjob':
            print("Generating job urls for: ", args.job)
            generate_and_save_job_urls_from_location(args.job)
            print("Finished generating job urls for: ", args.job)
        elif args.command == 'cleardb':
            action = input("Do you want to CLEAR the database? (Y/N):")
            if action == 'Y':
                db.clear_jobs()
                db.clear_urls()
                print("The database was sucessfully cleared.")
    except Exception as e:
        send_email(f"FROM {SERVER_NAME}", str(e), EMAIL, PASSWORD)
        raise e