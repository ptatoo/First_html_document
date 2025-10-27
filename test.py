from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()

driver.get('http://watir.com/examples/shadow_dom.html')

driver.implicitly_wait(2)

shadow_host = driver.find_element(By.CSS_SELECTOR, '#shadow_host')
shadow_root = shadow_host.shadow_root
shadow_content = shadow_root.find_element(By.CSS_SELECTOR, '#shadow_content')
shadow_root = shadow_root.find_element(By.ID, 'nested_shadow_host')

assert shadow_content.text == 'some text'

driver.quit()