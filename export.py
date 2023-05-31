import csv
import datetime
import json

import db

def format_row(job_info: dict):
    row = [job_info['LOCATION'], job_info['JOB'], job_info['MONTH'], job_info['YEAR']]
    job_dict = json.loads(job_info['JOB_DETAILS'])
    row.append(job_dict['competition_score'])
    row.append(job_dict['jobs'])
    row.append(job_dict['job_seekers'])
    row.append(job_dict['average_salary'])
    row.append(job_dict['employers'])
    row.append(job_dict['resumes'])
    row.append(job_dict['resumes_added'])

    experiences = job_dict['reported_years_of_experience']
    row.append('N/A' if '0 - 2' not in experiences else experiences['0 - 2'])
    row.append('N/A' if '3 - 5' not in experiences else experiences['3 - 5'])
    row.append('N/A' if '6 - 10' not in experiences else experiences['6 - 10'])
    row.append('N/A' if '11 - 20' not in experiences else experiences['11 - 20'])
    row.append('N/A' if '21+' not in experiences else experiences['21+'])
    
    
    educations = job_dict['reported_educational_level']
    row.append('N/A' if 'High School' not in educations else educations['High School'])
    row.append('N/A' if 'Associate' not in educations else educations['Associate'])
    row.append('N/A' if 'Bachelor' not in educations else educations['Bachelor'])
    row.append('N/A' if 'Master' not in educations else educations['Master'])
    row.append('N/A' if 'Doctorate' not in educations else educations['Doctorate'])

    return row

def export_all_jobs_to_csv():
    now = datetime.datetime.now()
    date_time = now.strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"jobs_{date_time}.csv"
    jobs = db.get_all_job_datas()
    with open(filename, 'w', encoding='utf-8', newline='') as csv_file:
        writer = csv.writer(csv_file)
        headers = ['location', 'job_title', 'month', 'year', 'competition_score', 'jobs', 'job_seekers', 'average_salary', 'employers', 'resumes', 'resumes_added', 'experience_lessthan2', 'experience_3to5', 'experience_6to10', 'experience_11to20', 'experience_21plus', 'education_HS', 'education_associate', 'education_bachelors', 'education_masters', 'education_doctorate']
        writer.writerow(headers)
        for job in jobs:
            writer.writerow(format_row(job))


def export_conditions_jobs_to_csv(job='', location='', month='', year=''):
    now = datetime.datetime.now()
    date_time = now.strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"jobs_{date_time}.csv"
    jobs = db.get_jobs_datas_conditions(job=job, location=location, month=month, year=year)
    if len(jobs) == 0:
        return None
    with open(filename, 'w', encoding='utf-8', newline='') as csv_file:
        writer = csv.writer(csv_file)
        headers = ['location', 'job_title', 'month', 'year', 'competition_score', 'jobs', 'job_seekers', 'average_salary', 'employers', 'resumes', 'resumes_added', 'experience_lessthan2', 'experience_3to5', 'experience_6to10', 'experience_11to20', 'experience_21plus', 'education_HS', 'education_associate', 'education_bachelors', 'education_masters', 'education_doctorate']
        writer.writerow(headers)
        for job in jobs:
            writer.writerow(format_row(job))
    return filename
        
        

