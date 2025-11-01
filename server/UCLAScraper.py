
import csv
import time
import re
from time import sleep

import queue

#threads
from threading import Thread
from concurrent.futures import ThreadPoolExecutor

#SELENIUM DRIVERS
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#beautiful soup
from bs4 import BeautifulSoup


def waitTillJqueryComplete(driver, debug, timeout=15):
    try:
        wait = Webself.driverWait(driver,timeout=timeout)
        wait.until(lambda d: d.execute_script("return (typeof jQuery !== 'undefined') && (jQuery.active === 0)"))
    except:
        print(f"ERRRRr: {debug}")
        return False

def parseStatus(text: str):
    texts = text.split("\n",1)
    status = texts[0]
    if status[0] == "O":
        return [status] + re.findall(r'\d+', texts[1])[:2]  
    elif status == "Closed":
        return [status] + ((raw := re.findall(r'\d+', texts[1]) + [0])[:1] + [int(raw[1]) + int(raw[0])])[::-1]
    else:
        return [status, 0, 0]

def parseTime(text: str):
    lines = text.split("\n")
    if(len(lines) == 1): 
        return ['','']
    returned = ['','']
    for line in lines:
        if(line[0] == '-'):
            returned[1] += line[1:]
        else:
            returned[0] += line

    return returned

def parseLocation(text: str):
    texts = text.split("\n")
    output = ""
    if (len(texts) > 1):
        for text in texts:
            output += text + ", "
    else:
        output = text
        return output
    return output[:-2]

def parseInstructor(text: str):
    texts = text.split("\n")
    output = ""
    for t in texts:
        output += t + "; "
    return output[:-2]

class UCLAScraper:
    BASE_URL = "https://sa.ucla.edu/ro/public/soc"
    def __init__(self, term: str, headless: bool):
        self.term = term
        self.headless = headless
        self.self.driver = None

    #so it can be used with with
    def __enter__(self):
        chrome_options = Options()
        chrome_options.page_load_strategy = 'normal'
        if self.headless:
            chrome_options.add_argument("--headless=new")
        
        try:
            self.self.driver = webself.driver.Chrome(options=chrome_options)
            self.self.driver.implicitly_wait(0.5)
        except Exception as e:
            raise Exception(f"Failed to start Webself.driver: {e}")
    
    #so it can be used with with
    def __exit__(self):
        if self.self.driver:
            self.self.driver.quit()

    #gets URL for specific subject
    """ args

    subjectID : ID for subject ex. MATH, COM SCI
    term : term we are searching in ex. 25F, 26W

    """
    def get_url(self, subjectID : str):
        formattedSubj = subjectID.ljust(7,'+')
        url = (
            self.BASE_URL + 
            f"/Results?t={self.term}"
            f"&sBy=subject"
            f"&subj={formattedSubj}"
            f"&catlg="
            f"&cls_no="
        )
        return url

    #getting  row content given BS of the row
    def get_row_content(self, row : BeautifulSoup):
        return {
            "lec_dis" : row.select_one('.sectionColumn a').get_text(strip=True, separator=', '),
            "status" : (status := parseStatus(row.select_one('.statusColumn').get_text('\n')))[0],
            "enrolled_spots" : status[1],
            "total_spots" : status[2],
            "waitlist_status" : row.select_one('.waitlistColumn').get_text(strip=True),
            "days" : row.select_one('.dayColumn').get_text(strip=True, separator=", "),
            "start_time" : (times := parseTime(row.select_one('div[id*="-days_data"] + p').get_text(separator="\n")))[0],
            "location" : times[1],
            "units" : row.select_one('.unitsColumn').get_text(strip=True),
            "instructors" : row.select_one('.instructorColumn').get_text(separator=', ', strip = True)
        }

    def scrapeExpandedHTML(self, lec_writer, shadow_host):
        #steal that HTML
        html_content = self.driver.execute_script("return arguments[0].shadowRoot.innerHTML;", shadow_host) 
        soup = BeautifulSoup(html_content, 'lxml')

        #parsing
        class_containers = soup.select('.row-fluid.class-title')
        for cls in class_containers:
            class_id = cls.get('id')
            
            #gets lec / disc container
            children_div = soup.find('div', id=f"{class_id}-children")
            if not children_div:
                continue

            # find all rows
            all_rows = children_div.select('.row-fluid.data_row')
            
            #parser
            for row in all_rows:    
                try:
                    section_list = {"classId":class_id, **self.get_row_content(row)}
                    lec_writer.writerow(section_list)
                except AttributeError:
                    # This happens if a row is missing a column, we can safely skip it
                    continue


    #searches for each section and writes it to csv file
    def searchSection(self, lec_writer, debug):
        #find all sections
        shadow_host = self.driver.find_element(By.XPATH, '//*[@id="block-ucla-campus-mainpagecontent"]/div[2]/div/div/div/div/ucla-sa-soc-app')
        shadow_root = shadow_host.shadow_root

        #find number of pages
        try:
            pg = shadow_root.find_element(By.CSS_SELECTOR, '[class="jPag-pages"]')
            pgB = pg.find_elements(By.CSS_SELECTOR, '[style="width: 32px;"]')
            pgs = len(pgB)
        except:
            pgs = 1 # if UNO pages

        #1. Loop through all pages
        for i in range(pgs):
            # get shadow stuff
            shadow_host = self.driver.find_element(By.XPATH, '//*[@id="block-ucla-campus-mainpagecontent"]/div[2]/div/div/div/div/ucla-sa-soc-app')
            shadow_root = shadow_host.shadow_root

            try:
                if pgs > 1:
                    # getting current page button :star:
                    cpgB = shadow_root.find_element(By.CSS_SELECTOR, '[class="jPag-pages"]').find_elements(By.CSS_SELECTOR, '[style="width: 32px;"]')
                    cpgB[i].click()
                    #wait for next page to load
                    waitTillJqueryComplete(self.driver, debug)
            except Exception as e:
                print(debug)
                break

        
            # 2. Expand all sections on the current page
            try:
                expand_all_button = shadow_root.find_element(By.CSS_SELECTOR, '[id="expandAll"]')
                #JS CLICK!!!
                self.driver.execute_script("arguments[0].click();", expand_all_button)
            except Exception as e:
                print(debug)
                continue
            
            #wait for expansion
            waitTillJqueryComplete(self.driver, debug)

            #3. steal HTML
            html_content = self.driver.execute_script("return arguments[0].shadowRoot.innerHTML;", shadow_host) 
            soup = BeautifulSoup(html_content, 'lxml')

            #4. parse.
            #parses the lec / disc
            class_containers = soup.select('.row-fluid.class-title')
            for cls in class_containers:
                class_id = cls.get('id')
                
                #gets lec / disc container
                children_div = soup.find('div', id=f"{class_id}-children")
                if not children_div:
                    continue

                # find all rows
                all_rows = children_div.select('.row-fluid.data_row')
                
                #parser
                for row in all_rows:    
                    try:
                        section_list = {"classId":class_id, **self.get_row_content(row)}
                        lec_writer.writerow(section_list)
                    except AttributeError:
                        # This happens if a row is missing a column, we can safely skip it
                        continue



    #searches for subject, searches for each section, writes it to csv file
    def scrapeSubject(self, subject: str, term):
        print(f"scraping {subject} {term}")
        #open up csv file
        section_keys = ["classId", "lec_dis", "status", "total_spots", "enrolled_spots", "waitlist_status", "days", "start_time", "end_time", "location", "units", "instructors"]
        output_path = "./server/section_data/" + subject + ".csv"
        with open(output_path, "w", newline='') as section_file:
            section_writer = csv.DictWriter(section_file, section_keys)
            section_writer.writeheader()

            #scrape
            url = self.get_url(subject,term)
            self.driver.get(url)

            self.searchSection(self.driver, section_writer, subject)

            self.driver.implicitly_wait(0.5)
            section_file.close()
            sleep(0.5)
            self.driver.quit()