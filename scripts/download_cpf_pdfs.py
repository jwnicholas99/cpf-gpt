import time
import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

DOWNLOAD_DIR = r"PATH/TO/DOWNLOAD/DIR"

service = Service("./chromedriver.exe")
options = Options()
options.add_argument("--window-size=1920,1200")
options.add_experimental_option("prefs", {
  "download.default_directory": DOWNLOAD_DIR,
  "download.prompt_for_download": False,
  "download.directory_upgrade": True,
  "safebrowsing.enabled": True
})

driver = webdriver.Chrome(options=options, service=service)
driver.get("https://sso.agc.gov.sg/Act/CPFA1953?ViewType=Print")
action = ActionChains(driver)

def click_element(element, sleep_time):
    driver.execute_script("arguments[0].scrollIntoView();", element)
    time.sleep(sleep_time)
    action.move_to_element(element).click(element).perform()

def rename_file(newname, folder_of_download):
    filename = max(
        [f for f in os.listdir(folder_of_download)],
        key=lambda xa : os.path.getctime(os.path.join(folder_of_download,xa))
    )
    if '.part' in filename:
        time.sleep(1)
        os.rename(
            os.path.join(folder_of_download, filename), 
            os.path.join(folder_of_download, newname)
        )
    else:
        os.rename(
            os.path.join(folder_of_download, filename),
            os.path.join(folder_of_download,newname)
        )

# Expand all parts
expansions = driver.find_elements(by=By.XPATH, value="//a[@class='displayText']")
for expansion in expansions:
    click_element(expansion, 0.5)

# Find all sections' checkboxes and download
print_pdf = driver.find_element(by=By.XPATH, value="//button[@data-bind='click: onPrintToPdfClick']")
checkboxes = driver.find_elements(by=By.XPATH, value="//input[@class='form-check-input childID']")
for checkbox in checkboxes:
    click_element(checkbox, 1)
    click_element(print_pdf, 1)
    time.sleep(1)
    label = driver.execute_script("return arguments[0].nextElementSibling", checkbox)
    rename_file(f"{label.text}.pdf", "../data")
    time.sleep(2)
    click_element(checkbox, 1)


# Download Schedules
schedule_names = ["Sc1-", "Sc2-", "Sc3-"]
for schedule_name in schedule_names:
    checkbox = driver.find_element(by=By.XPATH, value=f"//input[@value='{schedule_name}']")
    click_element(checkbox, 1)
    click_element(print_pdf, 1)
    time.sleep(3)
    label = driver.execute_script("return arguments[0].nextElementSibling", checkbox)
    rename_file(f"{label.text}.pdf", "../data")
    time.sleep(2)
    click_element(checkbox, 1)
