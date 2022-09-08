from time import sleep
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from typing import Optional
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from threading import Lock


cookie_lock = Lock()
driver = uc.Chrome(use_subprocess=True)
driver.minimize_window()
driver.get("https://www.faselhd.club/home3")


def get_cookies() -> None:
    global driver, cookie_lock

    driver.refresh()

    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located(
            (
                By.CLASS_NAME,
                "logo.ml-3",
            )
        )
    )

    cookies = driver.get_cookies()

    cookie_dict = {cookie["name"]: cookie["value"] for cookie in cookies}

    with open("./main/config/cookies.json", "w") as fp:
        json.dump(cookie_dict, fp)

    return


def load_cookies() -> dict:
    with open("./main/config/cookies.json", "r") as fp:
        cookies = json.load(fp)

    return cookies


def get_website_safe(webpage_url: str) -> Optional[requests.Response]:
    global cookie_lock
    cookies = load_cookies()
    with open("main\config\headers.json", "r") as fp:
        headers = json.load(fp)

    webpage = None
    while webpage is None:
        try:
            webpage = requests.get(webpage_url, headers=headers, cookies=cookies)

            if "Cloudflare" in str(webpage.text):
                print("We are detected, getting new cookies...")

                if not cookie_lock.locked():
                    with cookie_lock:
                        get_cookies()
                else:
                    while cookie_lock.locked():
                        sleep(1)
                    print("Done sleeping")

                cookies = load_cookies()
                webpage = None
            else:
                pass

        except requests.exceptions.ConnectionError:
            print("Fetching website failed, trying again...")
            webpage = None
        except requests.exceptions.TooManyRedirects:
            print(
                f"Experinced too many redirects when fetching {webpage_url}, skipping it..."
            )
            return None

    return webpage


def split_into_ranges(number_of_ranges: int, number_to_be_split: int) -> list[tuple]:
    pages_per_chunk = number_to_be_split // number_of_ranges
    ranges_list = []
    for _ in range(number_of_ranges):
        start_page = pages_per_chunk * _

        if _ == number_of_ranges - 1:
            end_page = number_to_be_split
        else:
            end_page = pages_per_chunk * (_ + 1)

        if (
            start_page + 1,
            end_page + 1,
        ) in ranges_list or start_page + 1 == end_page + 1:
            continue
        else:
            ranges_list.append((start_page + 1, end_page + 1))

    return ranges_list


def remove_arabic_chars(string: str) -> str:
    encoded_output_string = string.encode("ascii", "ignore")
    decoded_output_string = encoded_output_string.decode()

    return decoded_output_string


def get_number_of_pages(url: str) -> int:
    webpage = get_website_safe(url)
    soup = BeautifulSoup(webpage.content, "html.parser")

    try:
        last_page_button = soup.find("a", string="»")
        last_page_url = last_page_button["href"]
        last_page_number = int(last_page_url.split("/")[-1])
    except TypeError:
        print("No last page button found, trying another way...")
        pagesList = soup.find_all("li", class_="page-item")
        last_page_number = int(pagesList[-1].text)

    return last_page_number


def fix_url(url: str) -> str:
    url_no_params = url.split("?")[0]
    to_replace = "%3A"
    clean_url = quote(url_no_params).replace(to_replace, ":")

    return clean_url


def get_content_format(soup: BeautifulSoup) -> str:
    try:
        content_format = (
            soup.find("i", class_="fas fa-play-circle").find_next_sibling().text
        )

        if content_format.isascii():
            pass
        else:
            raise AttributeError

    except AttributeError:
        content_format = "N/A"

    return content_format


def get_content_id(soup: BeautifulSoup) -> str:
    content_id = remove_arabic_chars(
        soup.find("i", class_="fas fa-dot-circle")
        .parent.text.replace(":", "")
        .replace("#", "")
    ).strip()

    return content_id


with open("./output/json/image-index.json", "r") as fp:
    image_sources = json.load(fp)


def save_image(url: str, dir_path: str, content_id: str) -> str:
    try:
        if content_id in image_sources:
            return image_sources[content_id]

        else:
            url = fix_url(url)
            imagePage = get_website_safe(url)
            with open(f"{dir_path}/{content_id}.jpg", "wb") as fp:
                fp.write(imagePage.content)

            return "New Image Please Upload"

    except requests.exceptions.InvalidURL or requests.exceptions.MissingSchema:
        return "https://imgpile.com/images/TPDrVl.jpg"
