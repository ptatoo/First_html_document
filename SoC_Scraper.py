
import csv
import time
import re
from time import sleep

#THREADING
import logging
import threading

#MULTIPRROCESSING
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

#SELENIUM DRIVERS
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#beautiful soup
from bs4 import BeautifulSoup

def waitTillJqueryComplete(driver, timeout=5):
    try:
        wait = WebDriverWait(driver,timeout=timeout)
        wait.until(lambda d: d.execute_script("return (typeof jQuery !== 'undefined') && (jQuery.active === 0)"))
    except:
        print("TS pmo'd the waittimng ro someting")
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

def scrape_subject_wrapper(job_args):
    """
    This function is picklable. It takes a tuple of arguments
    and unpacks them when calling the actual worker function.
    """
    return scrapeSubject(*job_args)

#searches for a particular subject
def searchSubject(subject: str, sub: str, term: str, driver):
    #open schedule of classes
    try:
        driver.get("https://sa.ucla.edu/ro/public/soc")
    except:
        raise Exception("Failed to open website link")
    driver.implicitly_wait(0.5)

    #find search shadow DOM
    shadow_host = driver.find_element(By.XPATH, '//*[@id="block-ucla-campus-mainpagecontent"]/div[2]/div/div/div/div/ucla-sa-soc-app')
    shadow_root = shadow_host.shadow_root
    
    #search for term and click term
    term_drop_down = shadow_root.find_element(By.ID, 'optSelectTerm')
    term_drop_down.click()
    specific_term = term_drop_down.find_element(By.CSS_SELECTOR, f'[data-yeartext="{term}"]')
    specific_term.click()

    #find search bar shadow DOM
    driver.implicitly_wait(0.5)
    shadow_content = shadow_root.find_element(By.CSS_SELECTOR, '[id="select_filter_subject"]')
    shadow_root2 = shadow_content.shadow_root
    search_bar = shadow_root2.find_element(By.CSS_SELECTOR, '[id="IweAutocompleteContainer"]')

    #search for element
    inpt = search_bar.find_element(By.CSS_SELECTOR, '[type="text"]')
    inpt.send_keys(subject)
    drop_down = search_bar.find_element(By.CSS_SELECTOR, '[id="dropdownitems"]')
    drop_down_items = drop_down.find_elements(By.CSS_SELECTOR, '[tabindex="-1"]')

    #click drop down item
    clicked = False
    for drop_down_item in drop_down_items:
        if sub in drop_down_item.text:
            drop_down_item.click()
            clicked = True
    if not clicked:
        for drop_down_item in drop_down_items:
            if sub[1:-1] in drop_down_item.text:
                drop_down_item.click()
                clicked = True

    #click go button
    try:
        go_button = shadow_root.find_element(By.CSS_SELECTOR, '[id="div_btn_go"]')
        go_button.click()
    except:
        print("dude, ts broke")
        return False
    return True

class scrapeThread(threading.Thread):
    def __init__(self, str, term):
        threading.Thread.__init__(self)
        self.str = str
        self.term = term
    def run(self):
        scrapeSubject(self.str, self.term, True)

#searches for each sectionand writes it to csv file
def searchSection(driver, lec_writer, debug):
    #find all sections
    shadow_host = driver.find_element(By.XPATH, '//*[@id="block-ucla-campus-mainpagecontent"]/div[2]/div/div/div/div/ucla-sa-soc-app')
    shadow_root = shadow_host.shadow_root

    #find number of pages
    try:
        pg = shadow_root.find_element(By.CSS_SELECTOR, '[class="jPag-pages"]')
        pgB = pg.find_elements(By.CSS_SELECTOR, '[style="width: 32px;"]')
        pgs = len(pgB)
    except:
        pgs = 1 # if UNO pages

    # loop through each page
    for i in range(pgs):
        print(f"page {i + 1} of {pgs}")
        # get shadow stuff
        shadow_host = driver.find_element(By.XPATH, '//*[@id="block-ucla-campus-mainpagecontent"]/div[2]/div/div/div/div/ucla-sa-soc-app')
        shadow_root = shadow_host.shadow_root

        if pgs > 1:
            # getting current page button :star:
            cpgB = shadow_root.find_element(By.CSS_SELECTOR, '[class="jPag-pages"]').find_elements(By.CSS_SELECTOR, '[style="width: 32px;"]')
            cpgB[i].click()
            #wait for next page to load
            waitTillJqueryComplete(driver, debug)

    
        # 2. Expand all sections on the current page
        try:
            expand_all_button = shadow_root.find_element(By.CSS_SELECTOR, '[id="expandAll"]')
            #JS CLICK!!!
            driver.execute_script("arguments[0].click();", expand_all_button)
        except Exception as e:
            print(f"expand all btn is like nonexistent bruh")
            continue
        
        #wait for expansion
        waitTillJqueryComplete(driver, debug)

        #steal that HTML
        html_content = driver.execute_script("return arguments[0].shadowRoot.innerHTML;", shadow_host) 
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
                    section_list = {}
                    section_list["classId"] = class_id
                    section_list["lec_dis"] = row.select_one('.sectionColumn a').get_text(strip=True, separator=', ')

                    status_raw = row.select_one('.statusColumn').get_text('\n')
                    texts = parseStatus(status_raw)
                    section_list["status"], section_list["enrolled_spots"], section_list["total_spots"] = texts
                    
                    section_list["waitlist_status"] = row.select_one('.waitlistColumn').get_text(strip=True)
                    section_list["days"] = row.select_one('.dayColumn').get_text(strip=True, separator=", ")
                    
                    # Handle multi-line time column
                    section_list["start_time"], section_list["end_time"] = parseTime(row.select_one('div[id*="-days_data"] + p').get_text(separator="\n"))
                    section_list["location"] = row.select_one('.locationColumn').get_text(separator=', ', strip = True)
                    section_list["units"] = row.select_one('.unitsColumn').get_text(strip=True)
                    section_list["instructors"] = row.select_one('.instructorColumn').get_text(separator=', ', strip = True)
                    lec_writer.writerow(section_list)
                except AttributeError:
                    # This happens if a row is missing a column, we can safely skip it
                    continue

#searches for subject, searches for each section, writes it to csv file
def scrapeSubject(subject: str, term, headless: bool):
    # start_time = time.perf_counter()

    #start chrome driver
    chrome_options = Options()
    chrome_options.page_load_strategy = 'normal'
    if headless:
        chrome_options.add_argument("--headless=new")
    try:
        driver = webdriver.Chrome(options=chrome_options)
    except:
        raise Exception("Failed to run webdriver.")
    driver.implicitly_wait(0.5)

    #open up csv file
    section_keys = ["classId", "lec_dis", "status", "total_spots", "enrolled_spots", "waitlist_status", "days", "start_time", "end_time", "location", "units", "instructors"]
    section_file = open("./section_data/" + subject + ".csv", "w", newline='')
    section_writer = csv.DictWriter(section_file, section_keys)
    section_writer.writeheader()

    #search and scrape and write
    if((searchSubject(subject, "(" + subject + ")", term, driver))):
        searchSection(driver, section_writer, subject)
    section_file.close()
    sleep(1)
    driver.quit()
    # end_time = time.perf_counter()
    # elapsed_time = end_time - start_time
    # print(f"Code execution time: {elapsed_time:.4f} seconds")

def scrape_subject_wrapper(job_args):
    """
    This function is picklable. It takes a tuple of arguments
    and unpacks them when calling the actual worker function.
    """
    return scrapeSubject(*job_args)

if __name__ == '__main__':

    multiprocessing.set_start_method('spawn')
    start_time = time.perf_counter()
    subject_list = open("SubjectsList.txt", "r")
    

    # threads = []

    # for i, line in enumerate(subjectList):
    #     if(i < 2):
    #         line = line.strip()
    #         lines = line.split("(")
    #         if (len(lines) > 1):
    #             line = line.split("(")[1][:-1]   
    #         t = scrapeThread(line,"Winter 2026")
    #         t.start()
    #         threads.append(t)

    # for i in threads:
    #     i.join()

    #PROCESS MANAGEMENT STUFF
    #CREATES LIST OF ARGS FOR EXECUTOR
    jobs = []

    for i, line in enumerate(subject_list):
        if(i < 40):
            line = line.strip()
            lines = line.split("(")
            if (len(lines) > 1):
                line = line.split("(")[len(lines) - 1][:-1]   
            arg = (line,"Winter 2026",True)
            jobs.append(arg)

    print("args: ")
    print(jobs)
    print("-" * 50)

    #SETTING UP PROCESS POOL EXECUTOR
    max_workers = 20

    

    #THE PROCESS POOL EXECUTOR
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        print(1)
        iterator = executor.map(scrape_subject_wrapper,jobs)
        results = list(iterator)

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Code execution time: {elapsed_time:.4f} seconds")

    #2 in 10
    #15 in 24
