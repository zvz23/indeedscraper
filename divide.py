import sqlite3
import db
import os

def save_urls(urls: list, db_name: str):
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.executemany(f"INSERT OR IGNORE INTO urls(JOB, LOCATION, COUNTRY, URL) VALUES(?, ?, ?, ?)", urls)

db_count = 6
source_db = 'indeed.db'
urls = db.get_all_urls_row()

db_one_urls = urls[0:15181]
db_two_urls = urls[15181: 30362]
db_three_urls = urls[30362:45543]
db_four_urls = urls[45543:60724]
db_five_urls = urls[60724:75905]
db_six_urls = urls[75905:]

save_urls(db_one_urls, 'dbs\\indeed1.db')
save_urls(db_two_urls, 'dbs\\indeed2.db')
save_urls(db_three_urls, 'dbs\\indeed3.db')
save_urls(db_four_urls, 'dbs\\indeed4.db')
save_urls(db_five_urls, 'dbs\\indeed5.db')
save_urls(db_six_urls, 'dbs\\indeed6.db')

    