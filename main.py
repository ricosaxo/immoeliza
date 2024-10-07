from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

service = Service(executable_path=r"C:\Users\Rik\Desktop\immoeliza\chromedriver.exe")
driver = webdriver.Chrome(service=service)

try:
    driver.get("https://immoweb.be")

    # Wait for the shadow host element to be present
    shadow_host = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#usercentrics-root"))  
    )

    # Access the shadow root
    shadow_root = driver.execute_script('return arguments[0].shadowRoot', shadow_host)

    # Wait for the 'uc-accept-all-button' inside the shadow DOM to be present
    accept_button = WebDriverWait(driver, 10).until(
        lambda d: shadow_root.find_element(By.CSS_SELECTOR, "button[data-testid='uc-accept-all-button']")
    )

    # Click the button
    accept_button.click()

    # Optionally wait for the button to be clicked and further actions
    WebDriverWait(driver, 10).until(EC.staleness_of(accept_button))

    # Now wait for the search box submit button to be present and click it
    search_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'searchBoxSubmitButton'))
    )
    search_button.click()

    # Additional wait if necessary (optional)
    time.sleep(15)

finally:
    driver.quit()