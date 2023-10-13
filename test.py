# from seleniumwire.undetected_chromedriver import Chrome, ChromeOptions
from seleniumrequests import Chrome
from selenium.webdriver.chrome.options import Options
import os
import time

profile_path = os.path.join(os.path.expanduser('~'), 'Chrome Profiles', 'Indeed Profile')
print(profile_path)
options = Options()
options.add_argument(f"user-data-dir={profile_path}")
driver = Chrome(options=options)
input("PRESS ENTER TO CONTINUE")
driver.quit()