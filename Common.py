import base64
import sys
from time import sleep
import requests
from bs4 import BeautifulSoup, ResultSet, Tag
from urllib.parse import quote
from typing import Literal, Optional, Any
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from undetected_chromedriver import Chrome
from threading import Lock
from requests.exceptions import ConnectionError, TooManyRedirects, InvalidURL, MissingSchema, ConnectTimeout, ReadTimeout
from requests import Response

DEBUG = False
BASE_URL = "https://www.faselhd.club/"
HEADERS = {
    'authority': 'www.faselhd.club',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
}

cookie_lock: Lock = Lock()
driver: Chrome = uc.Chrome(use_subprocess=True)
driver.minimize_window()
driver.get("https://www.faselhd.club/home3")


def get_cookies() -> None:
    """Gets new cookies to bypass cloudfalre"""
    global cookies_dict

    driver.refresh()

    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located(
            (
                By.CLASS_NAME,
                "logo.ml-3",
            )
        )
    )

    cookies = driver.get_cookies()

    cookies_dict = {cookie["name"]: cookie["value"] for cookie in cookies}

    return


def get_website_safe(webpage_url: str) -> Optional[Response]:
    """Get the webpage at the url provided; automatically gets new cookies when needed, returns None if the page where impossible to reach due to too many redirects"""
    global cookies_dict

    webpage = None
    while webpage is None:
        try:
            webpage = requests.get(
                webpage_url, headers=HEADERS, cookies=cookies_dict)

            if "Cloudflare" in str(webpage.text):
                if not cookie_lock.locked():
                    with cookie_lock:
                        get_cookies()
                else:
                    while cookie_lock.locked():
                        sleep(1)
                webpage = None
            else:
                pass

        except ConnectionError or ReadTimeout:
            if DEBUG:
                print("Fetching website failed, trying again...")
            else:
                pass
            webpage = None
        except TooManyRedirects:
            if DEBUG:
                print(
                    f"Experinced too many redirects when fetching {webpage_url}, skipping it..."
                )
            else:
                pass
            return None

    return webpage


def split_into_ranges(number_of_ranges: int, number_to_be_split: int) -> list[tuple]:
    """Splits the number into (more or less) equal intervals"""
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
    """Removes the Arabic characters from the string provided"""
    encoded_output_string = string.encode("ascii", "ignore")
    decoded_output_string = encoded_output_string.decode()

    return decoded_output_string


def get_number_of_pages(url: str) -> int:
    """Gets the total number of pages of the category"""
    webpage: Optional[Response] = get_website_safe(url)
    soup: BeautifulSoup = BeautifulSoup(webpage.content, "html.parser")

    try:
        last_page_button: Optional[Tag] = soup.find("a", string="»")
        last_page_url: str = last_page_button["href"]
        last_page_number: int = int(last_page_url.split("/")[-1])
    except TypeError:
        if DEBUG:
            print("No last page button found, trying another way...")
        else:
            pass
        pages_list: ResultSet = soup.find_all("li", class_="page-item")
        last_page_number: int = int(pages_list[-1].text)

    return last_page_number


def fix_url(url: str) -> str:
    """Fixes the url by changing the unicode characters back to their original form"""
    url_no_params: str = url.split("?")[0]
    to_replace: Literal = "%3A"
    clean_url: str = quote(url_no_params).replace(to_replace, ":")

    return clean_url


def get_content_format(soup: BeautifulSoup) -> str:
    """Gets the format of the content or returns N/A if no format was found"""
    try:
        content_format: str = (
            soup.find("i", class_="fas fa-play-circle").find_next_sibling().text
        )

        if content_format.isascii():
            return content_format
        else:
            return "N/A"

    except AttributeError:
        return "N/A"


def get_content_id(soup: BeautifulSoup) -> str:
    """Gets the ID of the content"""
    content_id: str = remove_arabic_chars(
        soup.find("i", class_="fas fa-dot-circle")
        .parent.text.replace(":", "")
        .replace("#", "")
    ).strip()

    return content_id


with open("./output/image_indices.json", "r") as fp:
    image_sources: dict[str, str] = json.load(fp)


def save_image(image_url: str, content_id: str) -> str:
    """Uploads the image to imgur and returns its url.
    If the image could not be uploaded it will be saved locally for manual upload.
    If the image origin url could not be reached a default url for a balnk image is returned
    """
    try:
        if content_id in image_sources:
            return image_sources[content_id]

        else:
            image_url: str = fix_url(image_url)
            image: Optional[Response] = get_website_safe(image_url)
            data: dict[str, str] = {
                "image": base64.b64encode(image.content).decode("utf8")}
            headers: dict[str, str] = {
                "Authorization": f"Client-ID {sys.argv[1]}"}

            response: dict[str, Any] = requests.post(
                "https://api.imgur.com/3/image", headers=headers, data=data).json()

            if response["status"] == 200:
                return response["data"]["link"]
            else:
                with open(f"./output/{content_id}.jpg", 'wb') as handler:
                    handler.write(image.content)
                    return "Manual upload required"

    except InvalidURL or MissingSchema:
        return "https://imgpile.com/images/TPDrVl.jpg"

    except ConnectTimeout:
        with open(f"./output/{content_id}.jpg", 'wb') as handler:
            handler.write(image.content)
        return "Manual upload required"


def remove_year(title: str) -> str:
    """Removes the production year from the content title"""
    if title[-4:].isdigit() and len(title) > 4:
        title = title.replace(title[-5:], "")
    else:
        pass

    return title


def get_content_title(soup_result: ResultSet) -> str:
    """Gets the title of the content"""
    title: str = remove_year(remove_arabic_chars(
        soup_result.find("div", class_="h1").text
    ).strip())

    return title
