from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
from bs4 import BeautifulSoup
from pprint import PrettyPrinter as pprint

def get_javascript_rendered_site(url):
    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
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

URL = "https://duckduckgo.com/hiring"
html = get_javascript_rendered_site(URL)
jobs_dict = scrape_jobs_to_dict(html)
print_dict(jobs_dict)
