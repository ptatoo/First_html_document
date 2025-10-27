from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from time import sleep

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
    sleep(0.5)

    #find search bar shadow DOM
    shadow_content = shadow_root.find_element(By.CSS_SELECTOR, '[id="select_filter_subject"]')
    shadow_root2 = shadow_content.shadow_root
    search_bar = shadow_root2.find_element(By.CSS_SELECTOR, '[id="IweAutocompleteContainer"]')

    #search for element and click drop down item
    input = search_bar.find_element(By.CSS_SELECTOR, '[type="text"]')
    input.send_keys(subject)
    drop_down = search_bar.find_element(By.CSS_SELECTOR, '[id="dropdownitems"]')
    drop_down_items = drop_down.find_elements(By.CSS_SELECTOR, '[tabindex="-1"]')
    for drop_down_item in drop_down_items:
        if sub in drop_down_item.text:
            drop_down_item.click()

    #click go button
    go_button = shadow_root.find_element(By.CSS_SELECTOR, '[id="div_btn_go"]')
    go_button.click()

    #find all classes
    shadow_host = driver.find_element(By.XPATH, '//*[@id="block-ucla-campus-mainpagecontent"]/div[2]/div/div/div/div/ucla-sa-soc-app')
    shadow_root = shadow_host.shadow_root
    while True:
        class_list = shadow_root.find_element(By.CSS_SELECTOR, '[id="resultsTitle"]')
        classes = class_list.find_elements(By.CSS_SELECTOR, '[class="row-fluid class-title"]')
        for cls in classes:
            print(cls.get_attribute("id"))
        break

    sleep(5)

def parseClass():
    print("asdf")

#start chrome driver
chrome_options = Options()
#chrome_options.add_argument("--headless=new")
try:
    driver = webdriver.Chrome(options=chrome_options)
except:
    raise Exception("Failed to run webdriver.")
driver.implicitly_wait(0.5)

searchSubject("math", "(MATH)", "Winter 2026", driver)

sleep(1)
driver.quit()
