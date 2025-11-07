
import csv
import time
import re

#SELENIUM DRIVERS
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#beautiful soup
from bs4 import BeautifulSoup

#you ALSO NEED LXML DUUUUDE




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

class UCLAScraper:
    BASE_URL = "https://sa.ucla.edu/ro/public/soc"
    def __init__(self, term: str, headless: bool):
        self.term = term
        self.headless = headless
        self.driver = None
        self.lec_writer = None

    #so it can be used with with
    def __enter__(self):
        chrome_options = Options()
        chrome_options.page_load_strategy = 'none'
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


    def waitTillJqueryComplete(self, debug = "debug", timeout=15):
        try:
            wait = WebDriverWait(self.driver,timeout=timeout)
            wait.until(lambda d: d.execute_script("return (typeof jQuery !== 'undefined') && (jQuery.active === 0)"))
        except:
            print(f"ERRRRr: {debug}")
            return False

    def isJqueryComplete(self, timeout=15):
        try:
            return self.driver.execute_script("return (typeof jQuery !== 'undefined') && (jQuery.active === 0)")
        except:
            return False

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

    def scrape_HTML(self):
        # get shadow stuff
            shadow_host = self.driver.find_element(By.XPATH, '//*[@id="block-ucla-campus-mainpagecontent"]/div[2]/div/div/div/div/ucla-sa-soc-app')

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
                        self.lec_writer.writerow(section_list)
                    except AttributeError:
                        # This happens if a row is missing a column, we can safely skip it
                        continue
    
    def click_on_page(self, pg):
        shadow_host = self.driver.find_element(By.XPATH, '//*[@id="block-ucla-campus-mainpagecontent"]/div[2]/div/div/div/div/ucla-sa-soc-app')
        shadow_root = shadow_host.shadow_root

        cpgB = shadow_root.find_element(By.CSS_SELECTOR, '[class="jPag-pages"]').find_elements(By.CSS_SELECTOR, '[style="width: 32px;"]')
        cpgB[pg].click()

    def expand_page(self):
        try:
            shadow_host = self.driver.find_element(By.XPATH, '//*[@id="block-ucla-campus-mainpagecontent"]/div[2]/div/div/div/div/ucla-sa-soc-app')
            shadow_root = shadow_host.shadow_root
            expand_all_button = shadow_root.find_element(By.CSS_SELECTOR, '[id="expandAll"]')
            #JS CLICK!!!
            self.driver.execute_script("arguments[0].click();", expand_all_button)
        except Exception as e:
            print(e)
    
    def waitTillPageInteractive(self, timeout = 8):
        wait = WebDriverWait(self.driver, timeout=timeout)
        wait.until(
        lambda d: d.execute_script("return document.readyState") in ["interactive", "complete"]
        )

    #searches for each section and writes it to csv file
    def scrape_all(self, subject):    
        
        start = time.perf_counter()

        url = self.get_url(subject)
        self.driver.get(url)

        #gets shadow stuff
        self.waitTillPageInteractive()
        
        shadow_host = self.driver.find_element(By.XPATH, '//*[@id="block-ucla-campus-mainpagecontent"]/div[2]/div/div/div/div/ucla-sa-soc-app')
        shadow_root = shadow_host.shadow_root

        #find number of pages
        try:
            pg = shadow_root.find_element(By.CSS_SELECTOR, '[class="jPag-pages"]')
            pgB = pg.find_elements(By.CSS_SELECTOR, '[style="width: 32px;"]')
            pgs = len(pgB)
        except:
            pgs = 1 # if UNO pages

        handles = self.driver.window_handles

        #opens x number of tabs corresponding to pages and stores their window handles in a list (in order to how their opeed so that the one that has the most time  too load is accessed first)
        for i in range(pgs-1):
            self.driver.execute_script(f"window.open('{url}');")
            new_handles = set(self.driver.window_handles)
            new_window_handle = (new_handles - set(handles)).pop() # Get the single new handle
            handles.append(new_window_handle)

        #opens 1 additional tab so that driver doesn't quit when all tabs close
        self.driver.execute_script(f"window.open('about:blank');")
        
        #prepping stupid ass logic
        unloaded_tabs = handles
        unpaged_tabs = []
        paged_tabs = []
        expanded_loading_tabs = []
        expanded_loaded_tabs = []
        
        page = 0

        #stupid ass logic
        while unloaded_tabs or unpaged_tabs or paged_tabs or expanded_loading_tabs or expanded_loaded_tabs:
            try:
                #TS in weird ass order for optimization
                print(unloaded_tabs)
                print(unpaged_tabs)
                print(paged_tabs)
                print(expanded_loading_tabs)
                print(expanded_loaded_tabs)

                
                #ts bottle necks the most cuz it always immidately continuously loads, breaks bc of it too
                for handle in unloaded_tabs:
                    self.driver.switch_to.window(handle)
                    if(self.driver.execute_script("return document.readyState") == "complete"):
                        unpaged_tabs.append(handle)
                        unloaded_tabs.remove(handle)
                        
                #ts bottlenecks in loading if its tnot fully loaded, but less imprtant bottle neck compared to the o ther two, but still breaks cuz prio first one
                for handle in paged_tabs:
                    self.driver.switch_to.window(handle)
                    if(self.isJqueryComplete()):
                        self.expand_page()
                        expanded_loading_tabs.append(handle)
                        paged_tabs.remove(handle)

                #TS not break in order bc it should be prioritized as it done'st bottle neck on loading
                for handle in unpaged_tabs:
                    self.driver.switch_to.window(handle)

                    self.click_on_page(page)
                    page+=1

                    paged_tabs.append(handle)
                    unpaged_tabs.remove(handle)
                
                #oospie
                for handle in expanded_loading_tabs:
                    self.driver.switch_to.window(handle)
                    if(self.isJqueryComplete()):
                        expanded_loaded_tabs.append(handle)
                        expanded_loading_tabs.remove(handle)
                        
                #ts bottle necks second most bc loading in expanded data takes time, breaks bc of it too
                for handle in expanded_loaded_tabs: 
                    self.driver.switch_to.window(handle)
                    self.scrape_HTML()
                    expanded_loaded_tabs.remove(handle)
                    self.driver.close()
                
                
                
            except Exception as e: 
                if(e):
                    print(e)   
                pass
        
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
            self.lec_writer = csv.DictWriter(section_file, section_keys)
            self.lec_writer.writeheader()

            #scrape
            self.scrape_all(subject)

            start = time.perf_counter()

            self.driver.implicitly_wait(0.5)
            section_file.close()

            end = time.perf_counter()
            print("TT close driver and sec file: " + f"{end-start}")
        endF = time.perf_counter()
        print("total time: " + f"{endF-startF}")