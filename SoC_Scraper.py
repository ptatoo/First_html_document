import csv
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from time import sleep

def parseStatus(text: str):
    texts = text.split("\n")
    if texts[0] == "Open":
        texts[2] = texts[1].split(' ')[0]
        texts[1] = texts[1].split(' ')[2]
        return texts
    else:
        return [texts[0], 0, 0]

def parseTime(text: str):
    texts = text.split("-")
    if len(texts) == 1:
        return ["", ""]
    texts[0] = texts[0][:-2]
    texts[1] = texts[1][:-2]
    return texts

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
    specific_term = term_drop_down.find_element(By.CSS_SELECTOR, '[data-yeartext="Winter 2026"]')
    specific_term.click()

    #find search bar shadow DOM
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
    go_button = shadow_root.find_element(By.CSS_SELECTOR, '[id="div_btn_go"]')
    go_button.click()

#searches for each sectionand writes it to csv file
def searchSection(driver, lec_writer):
    #find all sections
    shadow_host = driver.find_element(By.XPATH, '//*[@id="block-ucla-campus-mainpagecontent"]/div[2]/div/div/div/div/ucla-sa-soc-app')
    shadow_root = shadow_host.shadow_root

    #find number of pages
    try:
        pg = shadow_root.find_element(By.CSS_SELECTOR, '[class="jPag-pages"]')
        pgs = pg.find_elements(By.CSS_SELECTOR, '[style="width: 32px;"]')
    except:
        pgs = [shadow_root]

    for num in pgs:
        if (len(pgs) != 1):
            num.click()
        sleep(0.5)
        class_list = shadow_root.find_element(By.CSS_SELECTOR, '[id="resultsTitle"]')
        classes = class_list.find_elements(By.CSS_SELECTOR, '[class="row-fluid class-title"]')
        #scrapes each class
        for cls in classes:
            class_id = cls.get_attribute("id")
            cls.find_element(By.CSS_SELECTOR, '[class="linkLikeButton"]').click()
            #trys to find the class twice, if not prints an error
            try:
                rows = cls.find_element(By.CSS_SELECTOR, '[id="' + class_id + '-children"]')
            except:
                sleep(0.25)
                try:
                    rows = cls.find_element(By.CSS_SELECTOR, '[id="' + class_id + '-children"]')
                except:
                    print("error: " + class_id)
                    continue
                    
            rows = rows.find_elements(By.CSS_SELECTOR, '[class="row-fluid data_row primary-row class-info class-not-checked"]')
            #each lecture is a row
            for row in rows:
                sections = []
                sections.append(row)
                #open discussion rows and add them to list
                disExists = False
                try:
                    button = row.find_element(By.CSS_SELECTOR, '[class="transparentButton"]')
                    button.click()
                    disExists = True
                except:
                    pass

                if disExists:
                    secondaryRows = row.find_elements(By.CSS_SELECTOR, '[class="row-fluid data_row secondary-row class-info class-not-checked"]')
                    for secondaryRow in secondaryRows:
                        sections.append(secondaryRow)
                        
                #gather lecture and discussiondata
                for section in sections:
                    section_list = {}
                    section_list["classId"] = class_id
                    section_list["lec_dis"] = section.find_element(By.CSS_SELECTOR, '[class="sectionColumn"]').text
                    texts = parseStatus(section.find_element(By.CSS_SELECTOR, '[class="statusColumn"]').text)
                    section_list["status"] = texts[0]
                    section_list["total_spots"] = texts[1]
                    section_list["enrolled_spots"] = texts[2]
                    section_list["waitlist_status"] = section.find_element(By.CSS_SELECTOR, '[class="waitlistColumn"]').text
                    section_list["days"] = section.find_element(By.CSS_SELECTOR, '[class="dayColumn hide-small beforeCollapseHide"]').get_attribute("innerText").strip()
                    timing = section.find_element(By.CSS_SELECTOR, '[class="timeColumn"]').text.split("\n")
                    texts = parseTime(timing[-1])
                    section_list["start_time"] = texts[0]
                    section_list["end_time"] = texts[1]
                    section_list["location"] = parseLocation(section.find_element(By.CSS_SELECTOR, '[class="locationColumn hide-small"]').text)
                    section_list["units"] = section.find_element(By.CSS_SELECTOR, '[class="unitsColumn"]').text
                    section_list["instructors"] = parseInstructor(section.find_element(By.CSS_SELECTOR, '[class="instructorColumn hide-small"]').text)
                    lec_writer.writerow(section_list)

#searches for subject, searches for each section, writes it to csv file
def scrapeSubject(subject: str, term, headless: bool):
    #start chrome driver
    chrome_options = Options()
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
    searchSubject(subject, "(" + subject + ")", term, driver)
    searchSection(driver, section_writer)
    section_file.close()
    sleep(1)
    driver.quit()

# subjectList = open("SubjectsList.txt", "r")
# for line in subjectList:
#     line = line.strip()
#     lines = line.split("(")
#     if (len(lines) > 1):
#         line = line.split("(")[1][:-1]
#     scrapeSubject(line, "Winter 2026")

scrapeSubject("Arabic", "Winter 2026", False)