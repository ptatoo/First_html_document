import csv
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from time import sleep

def parseStatus(text: str):
    texts = text.split("\n")
    texts[2] = texts[1].split(' ')[0]
    texts[1] = texts[1].split(' ')[2]
    return texts

def parseTime(text: str):
    texts = text.split("-")
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
    return output[:-2]

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

    #search for element and click drop down item
    inpt = search_bar.find_element(By.CSS_SELECTOR, '[type="text"]')
    inpt.send_keys(subject)
    drop_down = search_bar.find_element(By.CSS_SELECTOR, '[id="dropdownitems"]')
    drop_down_items = drop_down.find_elements(By.CSS_SELECTOR, '[tabindex="-1"]')
    for drop_down_item in drop_down_items:
        if sub in drop_down_item.text:
            drop_down_item.click()

    #click go button
    go_button = shadow_root.find_element(By.CSS_SELECTOR, '[id="div_btn_go"]')
    go_button.click()

def searchClasses(driver, class_writer, lec_writer):
    #find all classes
    shadow_host = driver.find_element(By.XPATH, '//*[@id="block-ucla-campus-mainpagecontent"]/div[2]/div/div/div/div/ucla-sa-soc-app')
    shadow_root = shadow_host.shadow_root
    while True:
        class_list = shadow_root.find_element(By.CSS_SELECTOR, '[id="resultsTitle"]')
        classes = class_list.find_elements(By.CSS_SELECTOR, '[class="row-fluid class-title"]')
        #scrapes each class
        for cls in classes:
            class_id = cls.get_attribute("id")
            cls.find_element(By.CSS_SELECTOR, '[class="linkLikeButton"]').click()
            rows = cls.find_element(By.CSS_SELECTOR, '[id="' + class_id + '-children"]')
            rows = rows.find_elements(By.CSS_SELECTOR, '[class="row-fluid data_row primary-row class-info class-not-checked"]')
            #each lecture is a row
            for row in rows:
                #open discussion rows
                disExists = False
                try:
                    button = row.find_element(By.CSS_SELECTOR, '[class="transparentButton"]')
                    button.click()
                    disExists = True
                except:
                    pass
                #gather lecture data
                lec_dis = {}
                lec_dis["classId"] = class_id
                lec_dis["lec_dis"] = row.find_element(By.CSS_SELECTOR, '[class="sectionColumn"]').text
                texts = parseStatus(row.find_element(By.CSS_SELECTOR, '[class="statusColumn"]').text)
                lec_dis["status"] = texts[0]
                lec_dis["total_spots"] = texts[1]
                lec_dis["enrolled_spots"] = texts[2]
                lec_dis["waitlist_status"] = row.find_element(By.CSS_SELECTOR, '[class="waitlistColumn"]').text
                lec_dis["days"] = row.find_element(By.CSS_SELECTOR, '[class="dayColumn hide-small beforeCollapseHide"]').get_attribute("innerText").strip()
                timing = row.find_element(By.CSS_SELECTOR, '[class="timeColumn"]').text.split("\n")
                texts = parseTime(timing[-1])
                lec_dis["start_time"] = texts[0]
                lec_dis["end_time"] = texts[1]
                lec_dis["location"] = parseLocation(row.find_element(By.CSS_SELECTOR, '[class="locationColumn hide-small"]').text)
                lec_dis["units"] = row.find_element(By.CSS_SELECTOR, '[class="unitsColumn"]').text
                lec_dis["instructors"] = row.find_element(By.CSS_SELECTOR, '[class="instructorColumn hide-small"]').text
                lec_writer.writerow(lec_dis)
                if disExists:
                    secondaryRows = row.find_elements(By.CSS_SELECTOR, '[class="row-fluid data_row secondary-row class-info class-not-checked"]')
                    for secondaryRow in secondaryRows:
                        lec_dis = {}
                        lec_dis["classId"] = class_id
                        lec_dis["lec_dis"] = secondaryRow.find_element(By.CSS_SELECTOR, '[class="sectionColumn"]').text
                        texts = parseStatus(secondaryRow.find_element(By.CSS_SELECTOR, '[class="statusColumn"]').text)
                        lec_dis["status"] = texts[0]
                        lec_dis["total_spots"] = texts[1]
                        lec_dis["enrolled_spots"] = texts[2]
                        lec_dis["waitlist_status"] = secondaryRow.find_element(By.CSS_SELECTOR, '[class="waitlistColumn"]').text
                        lec_dis["days"] = secondaryRow.find_element(By.CSS_SELECTOR, '[class="dayColumn hide-small beforeCollapseHide"]').get_attribute("innerText").strip()
                        timing = secondaryRow.find_element(By.CSS_SELECTOR, '[class="timeColumn"]').text.split("\n")
                        texts = parseTime(timing[-1])
                        lec_dis["start_time"] = texts[0]
                        lec_dis["end_time"] = texts[1]
                        lec_dis["location"] = parseLocation(secondaryRow.find_element(By.CSS_SELECTOR, '[class="locationColumn hide-small"]').text)
                        lec_dis["units"] = secondaryRow.find_element(By.CSS_SELECTOR, '[class="unitsColumn"]').text
                        lec_dis["instructors"] = secondaryRow.find_element(By.CSS_SELECTOR, '[class="instructorColumn hide-small"]').text
                        lec_writer.writerow(lec_dis)


        break


#start chrome driver
chrome_options = Options()
#chrome_options.add_argument("--headless=new")
try:
    driver = webdriver.Chrome(options=chrome_options)
except:
    raise Exception("Failed to run webdriver.")
driver.implicitly_wait(0.5)

class_keys = ["classId"]
class_file = open("classes.csv", "w", newline='')
class_writer = csv.DictWriter(class_file, class_keys)
class_writer.writeheader()

lec_dis_keys = ["classId", "lec_dis", "status", "total_spots", "enrolled_spots", "waitlist_status", "days", "start_time", "end_time", "location", "units", "instructors"]
lec_dis_file = open("lec_dis.csv", "w", newline='')
lec_writer = csv.DictWriter(lec_dis_file, lec_dis_keys)
lec_writer.writeheader()

searchSubject("math", "(MATH)", "Winter 2026", driver)
searchClasses(driver, class_writer, lec_writer)

class_file.close()
lec_dis_file.close()

sleep(1)
driver.quit()