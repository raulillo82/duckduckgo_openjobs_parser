from selenium import webdriver
from selenium.webdriver.chrome.options import Options as OptionsChrome
from selenium.webdriver.firefox.options import Options as OptionsFirefox
from time import sleep
from bs4 import BeautifulSoup
from pprint import PrettyPrinter as pprint
import requests
from auth import TELEGRAM_BOT_CHATID, TELEGRAM_BOT_TOKEN

def get_javascript_rendered_site(url, driver="Firefox"):
    if driver=="Firefox":
        options_firefox = OptionsFirefox()
        options_firefox.add_argument("--headless")
        driver = webdriver.Firefox(options=options_firefox)
    elif driver=="Chrome":
        options_chrome = OptionsChrome()
        options_chrome.add_argument("--headless")
        driver = webdriver.Chrome(options=options_chrome)
    else:
        print("Wrong browser selected, please use either 'Firefox' (default)" \
                + " or 'Chrome' as arguments for this function")
        exit(1)
    driver.get(url)
    sleep(1)
    html = driver.page_source
    driver.quit()
    return html

def scrape_jobs_to_dict(html):
    soup = BeautifulSoup(html, "html.parser")
    #print(soup.prettify())
    departments_selector = "h2[class*='openPositions_department']"
    departments = [department.get_text() for department
                   in soup.select(departments_selector)]

    jobs_selector = "h3[class*='openPositions_title']"
    jobs = [job.getText() for job
            in soup.select(jobs_selector)]

    jobs_dict = dict(zip(jobs, departments))
    return jobs_dict

def print_dict(mydict):
    pp=pprint()
    print("'Job Title': 'Job Department'")
    print()
    pp.pprint(jobs_dict)

def check_job_in_dict(jobs_dict, job_filter):
    found = False
    for string in job_filter:
        if string in '\t'.join([key.lower() for key in jobs_dict.keys()]):
            found = True
            break
    return found

def telegram_bot_sendtext(jobs_dict):
    """Sends the text message passed as parameter to the telegram bot.
    Returns the response code"""
    message="Duck Duck Go open vacancy found with desired filter!\n"
    message+="Full list of jobs:\n"
    message+="'Job Title' - 'Job Department'\n\n"
    for job, department in jobs_dict.items():
        message += f"{job} - {department}"
        message += "\n"

    params = {
            "chat_id": TELEGRAM_BOT_CHATID,
            "text": message,
            "parse_mode": "MARKDOWN",
            }
    url = "https://api.telegram.org/bot" + TELEGRAM_BOT_TOKEN + "/sendMessage"
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

URL = "https://duckduckgo.com/hiring"
JOB_FILTER = ["cloud", "devops", "dev ops"]
html = get_javascript_rendered_site(URL)
jobs_dict = scrape_jobs_to_dict(html)
#print_dict(jobs_dict)

if check_job_in_dict(jobs_dict, JOB_FILTER):
    telegram_bot_sendtext(jobs_dict)
