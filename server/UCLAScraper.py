
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


def waitTillJqueryComplete(driver, debug = "debug", timeout=15):
    try:
        wait = WebDriverWait(driver,timeout=timeout)
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
        self.driver = None

    #so it can be used with with
    def __enter__(self):
        chrome_options = Options()
        chrome_options.page_load_strategy = 'eager'
        if self.headless:
            chrome_options.add_argument("--headless=new")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(0.5)
        except Exception as e:
            raise Exception(f"Failed to start Webself.driver: {e}")
        
        return self
    
    #so it can be used with with
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver:
            self.driver.quit()

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

    def scrape_expanded_HTML(self, lec_writer, shadow_host):
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

    def scrape_HTML(self, lec_writer):
        # get shadow stuff
            shadow_host = self.driver.find_element(By.XPATH, '//*[@id="block-ucla-campus-mainpagecontent"]/div[2]/div/div/div/div/ucla-sa-soc-app')
            shadow_root = shadow_host.shadow_root

            #wait for expansion
            waitTillJqueryComplete(self.driver)

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
    
    #searches for each section and writes it to csv file
    def scrape_all(self, lec_writer, subject):    
        
        start = time.perf_counter()

        url = self.get_url(subject)
        self.driver.get(url)

        #gets shadow stuff
        shadow_host = self.driver.find_element(By.XPATH, '//*[@id="block-ucla-campus-mainpagecontent"]/div[2]/div/div/div/div/ucla-sa-soc-app')
        shadow_root = shadow_host.shadow_root

        #find number of pages
        try:
            pg = shadow_root.find_element(By.CSS_SELECTOR, '[class="jPag-pages"]')
            pgB = pg.find_elements(By.CSS_SELECTOR, '[style="width: 32px;"]')
            pgs = len(pgB)
        except:
            pgs = 1 # if UNO pages
        
        unloaded_tabs = self.driver.window_handles
        unpaged_tabs = self.driver.window_handles
        paged_tabs = self.driver.window_handles

        handles = self.driver.window_handles
        
        #opens multiple tabs
        for i in range(pgs-1):
            self.driver.execute_script(f"window.open('{url}');")
            new_handles = set(self.driver.window_handles)
            new_window_handle = (new_handles - set(handles)).pop() # Get the single new handle
            handles.append(new_window_handle)

        
        self.driver.execute_script(f"window.open('about:blank');")

        #cycle through all tabs putting it on the right page
        for i in range(pgs):
            self.driver.switch_to.window(handles[i])
            shadow_host = self.driver.find_element(By.XPATH, '//*[@id="block-ucla-campus-mainpagecontent"]/div[2]/div/div/div/div/ucla-sa-soc-app')
            shadow_root = shadow_host.shadow_root

            cpgB = shadow_root.find_element(By.CSS_SELECTOR, '[class="jPag-pages"]').find_elements(By.CSS_SELECTOR, '[style="width: 32px;"]')
            cpgB[i].click()

        #cycle through all tabs, expanding them
        for i in range(pgs):
            self.driver.switch_to.window(handles[i])
            waitTillJqueryComplete(self.driver)

            try:
                expand_all_button = shadow_root.find_element(By.CSS_SELECTOR, '[id="expandAll"]')
                #JS CLICK!!!
                self.driver.execute_script("arguments[0].click();", expand_all_button)
            except Exception as e:
                print(subject)
                continue
            


        #1. Loop through all pages
        for handle in handles:
            self.driver.switch_to.window(handle)
            
            self.scrape_HTML(lec_writer)

            self.driver.close()
        
        self.driver.switch_to.window(self.driver.window_handles[0])

        end = time.perf_counter()
        print("TT scrape: " + f"{end-start}")   

    #searches for subject, searches for each section, writes it to csv file
    def scrape_subject(self, subject: str):
        print(f"scraping {subject} {self.term}")
        #open up csv file
        section_keys = ["classId", "lec_dis", "status", "total_spots", "enrolled_spots", "waitlist_status", "days", "start_time", "end_time", "location", "units", "instructors"]
        output_path = "./server/section_data/" + subject + ".csv"
        startF = time.perf_counter()
        with open(output_path, "w", newline='') as section_file:
            section_writer = csv.DictWriter(section_file, section_keys)
            section_writer.writeheader()

            #scrape
            self.scrape_all(section_writer, subject)

            start = time.perf_counter()

            self.driver.implicitly_wait(0.5)
            section_file.close()

            end = time.perf_counter()
            print("TT close driver and sec file: " + f"{end-start}")
        endF = time.perf_counter()
        print("total time: " + f"{endF-startF}")