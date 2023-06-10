import sqlite3

"""
Sqlite is used to save the data and to avoid duplicates

TABLE STRUCTURE:

Table: jobs

ID INT AUTOINCREMENT NOT NULL
JOB TEXT NOT NULL
LOCATION TEXT NOT NULL
MONTH TEXT NOT NULL
YEAR TEXT NOT NULL
JOB_DETAILS NOT NULL

The JOB_DETAILS column is to store the json formatted datas of the job

Table: urls

ID INT AUTOINCREMENT NOT NULL
URL UNIQUE NOT NULL
IS_FINISHED INTEGER
"""

DB_NAME = 'indeed.db'
JOBS_TABLE_NAME = 'jobs'
URLS_TABLE_NAME = 'urls'


def save_url(job: str, location: str, country: str, url: str):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(f"INSERT OR IGNORE INTO {URLS_TABLE_NAME}(JOB, LOCATION, COUNTRY, URL) VALUES(?, ?, ?, ?)", [job, location, country, url])
    
def save_urls(urls: list):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.executemany(f"INSERT OR IGNORE INTO {URLS_TABLE_NAME}(JOB, LOCATION, COUNTRY, URL) VALUES(?, ?, ?, ?)", urls)

def is_url_exists(url: str):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT ID FROM {URLS_TABLE_NAME} WHERE URL=?", [url])
        if cursor.fetchone() is None:
            return False
        return True

# Sets the IS_FINISHED to 1, this function is called when it was able to get all datas from all months
# This is to avoid getting datas again from specific url
def set_finished_url(url: str):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE {URLS_TABLE_NAME} SET IS_FINISHED=? WHERE URL=?", [1, url])

# This will remove all job datas if its URL is not set to 1 in the urls table
def clean_unfinished():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.row_factory = sqlite3.Row
        cursor.execute(f"SELECT URL FROM {URLS_TABLE_NAME} WHERE IS_FINISHED IS NULL")
        rows = cursor.fetchall()
        for r in rows:
            url = r['URL']
            cursor.execute(f"DELETE FROM {JOBS_TABLE_NAME} WHERE URL=?", [url])
            print("DELETED")
        conn.commit()

def set_all_unfinished():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE {URLS_TABLE_NAME} SET IS_FINISHED = NULL")
        rows = cursor.fetchall()
        for r in rows:
            url = r['URL']
            cursor.execute(f"DELETE FROM {JOBS_TABLE_NAME} WHERE URL=?", [url])
            print("DELETED")
        conn.commit()


# WARNING: This will clear all job datas
def clear_jobs():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {JOBS_TABLE_NAME}")

# WARNING: This will clear all urls
def clear_urls():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {URLS_TABLE_NAME}")

def save_job_data(url: str, job: str, location: str, month: str, year: str, job_details: str):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(f"INSERT OR IGNORE INTO {JOBS_TABLE_NAME}(URL, JOB, LOCATION, MONTH, YEAR, JOB_DETAILS) VALUES(?, ?, ?, ?, ?, ?)", [url, job, location, month, year, job_details])

def is_job_data_exists(url: str, job: str, location: str, month: str, year: str):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(F"SELECT ID FROM {JOBS_TABLE_NAME} WHERE URL=? AND JOB=? AND LOCATION=? AND MONTH=? AND YEAR=?", [url, job, location, month, year])
        if cursor.fetchone() is None:
            return False
        return True
    
def get_all_job_datas():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.row_factory = sqlite3.Row
        cursor.execute(f"SELECT * FROM {JOBS_TABLE_NAME}")
        return cursor.fetchall()
    
def get_jobs_datas_conditions(job='', location='', month='', year=''):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.row_factory = sqlite3.Row
        query = f"SELECT * FROM {JOBS_TABLE_NAME}"
        
        conditions = []
        if job:
            conditions.append(f"JOB='{job}'")
        if location:
            conditions.append(f"LOCATION='{location}'")
        if month:
            conditions.append(f"MONTH='{month}'")
        if year:
            conditions.append(f"YEAR='{year}'")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions) + " COLLATE NOCASE"
        
        cursor.execute(query)
        return cursor.fetchall()
    
def get_all_urls():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT URL FROM {URLS_TABLE_NAME}")
        return [r[0] for r in cursor.fetchall()]

def get_all_urls_row():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT JOB, LOCATION, COUNTRY, URL FROM {URLS_TABLE_NAME}")
        return cursor.fetchall()
    
def get_all_urls_with_conditions(job: str = None, location: str = None, country: str = None):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        query = f"SELECT URL FROM {URLS_TABLE_NAME}"
        
        conditions = []
        conditions.append("IS_FINISHED IS NULL")
        if job:
            conditions.append(f"JOB='{job}'")
        if location:
            conditions.append(f"LOCATION='{location}'")
        if country:
            conditions.append(f"COUNTRY='{country}'")

        
        if conditions:
            query += " WHERE " + " AND ".join(conditions) + " COLLATE NOCASE"
        cursor.execute(query)
        return [r[0] for r in cursor.fetchall()]
    
def get_all_unfinished_urls():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT URL FROM {URLS_TABLE_NAME} WHERE IS_FINISHED IS NULL")
        return [r[0] for r in cursor.fetchall()]
    