import json
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc

driver = uc.Chrome(use_subprocess=True)
driver.maximize_window()
driver.get("https://imgpile.com/login")
sleep(30)

imagesIndex = {}
for page in range(1, 165):
    driver.get(f"https://imgpile.com/_n0_0ne_/?list=images&sort=date_desc&page={page}")

    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located(
            (
                By.CLASS_NAME,
                "replace-svg",
            )
        )
    )

    elements = driver.find_elements(
        By.CLASS_NAME, "text-decoration-none.list-item-desc-title"
    )

    print(len(elements))

    for element in elements:
        imagesIndex[element.text] = (
            element.get_attribute("href").replace("/i/", "/images/") + ".jpg"
        )

    print(f"Finished scraping page {page}")

with open("./output/json/image-index.json", "w") as outputFile:
    json.dump(imagesIndex, outputFile)

driver.quit()

print("Done writing to file")
