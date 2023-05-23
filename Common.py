from base64 import b64encode
from time import sleep
import requests
from bs4 import BeautifulSoup, ResultSet, Tag
from urllib.parse import quote
from typing import Optional, Callable, Union
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from undetected_chromedriver import Chrome
from threading import Lock
from requests.exceptions import ConnectionError, TooManyRedirects, ReadTimeout, ChunkedEncodingError
from requests import Response
from os import environ
from PIL import Image

DEBUG = False

CIMA_NOW_SELECTOR = (By.CLASS_NAME, "owl-head.owl-loaded.owl-drag")

FILE_NAMES = ["movies", "anime", "asian-series",
              "series", "tvshows", "arabic-series",
              "arabic-movies"]

HDW_FILE_NAMES = ["hdwmovies", "series", "arabic-movies", "arabic-series"]

FASEL_BASE_URL = "https://www.faselhd.vip/"

DEFAULT_HDW_SELECTOR = (By.CLASS_NAME, "top-brand")

AKWAM_GENRES = {
    "87": "Ramadan",
    "30": "Animated",
    "18": "Action",
    "71": "Dubbed",
    "72": "Netflix",
    "20": "Comedy",
    "35": "Thriller",
    "34": "Mystery",
    "33": "Family",
    "88": "Kids",
    "32": "Sports",
    "25": "War",
    "89": "Short",
    "43": "Fantasy",
    "24": "Science Fiction",
    "31": "Musical",
    "29": "Biography",
    "28": "Documentary",
    "27": "Romance",
    "26": "History",
    "23": "Drama",
    "22": "Horror",
    "21": "Crime",
    "19": "Adventure",
    "91": "Western"
}

CIMA_NOW_GENRES = {
    "تشويق": "Suspense",
    "درامي": "Drama",
    "اكشن": "Action",
    "رعب": "Horror",
    "كوميدى": "Comedy",
    "مغامرة": "Adventure",
    "ترفيهي": "Entertainment",
    "غنائي": "Musical",
    "مسابقات": "Competitions",
    "اجتماعي": "Social",
    "جريمة": "Crime",
    "اثارة": "Thriller",
    "رومانسى": "Romance",
    "عائلي": "Family",
    "كوميدي": "Comedy",
    "درامى": "Drama"
}

with open("./output/image-indices.json", "r") as fp:
    IMAGE_SOURCES = json.load(fp)

cookie_lock = Lock()


def get_cookies(url: str, selector: tuple[By, str]) -> None:
    """Gets new cookies to bypass cloudfalre"""
    global cookies_dict, headers

    driver = Chrome(use_subprocess=True, version_main=113)
    driver.minimize_window()
    driver.get(url)

    WebDriverWait(driver, 120).until(EC.presence_of_element_located(selector))

    cookies = driver.get_cookies()

    cookies_dict = {cookie["name"]: cookie["value"] for cookie in cookies}
    headers = {
        "user-agent": driver.execute_script("return window.navigator.userAgent;")
    }

    driver.quit()

    return


def get_website_safe(webpage_url: str, selector: tuple[By, str] = (By.CLASS_NAME, "logo.ml-3")) -> Optional[Response]:
    """Get the webpage at the url provided; automatically gets new cookies when needed, returns None if the page where impossible to reach due to too many redirects"""
    webpage = None
    while webpage is None:
        try:
            webpage = requests.get(
                webpage_url, headers=headers, cookies=cookies_dict)

            if "Cloudflare" in str(webpage.text):
                if not cookie_lock.locked():
                    with cookie_lock:
                        get_cookies(webpage_url, selector)
                else:
                    while cookie_lock.locked():
                        sleep(1)
                webpage = None
            else:
                pass

        except ConnectionError:
            webpage = None

        except ReadTimeout:
            webpage = None

        except ChunkedEncodingError:
            webpage = None

        except TooManyRedirects:
            return None

    return webpage


def split_into_ranges(number_of_ranges: int, range_end: int, range_start: int = 0) -> list[tuple[int, int]]:
    """Splits the number into (more or less) equal intervals"""
    number_to_be_split = range_end - range_start
    number_per_chunk = number_to_be_split // number_of_ranges
    ranges_list = []

    for number in range(number_of_ranges):
        begin = range_start + (number_per_chunk * number)

        if number == number_of_ranges - 1:
            end = range_end
        else:
            end = range_start + (number_per_chunk * (number + 1))

        if (begin + 1, end + 1) in ranges_list or (begin + 1 == end + 1):
            continue
        else:
            ranges_list.append((begin + 1, end + 1))

    return ranges_list


def remove_arabic_chars(string: str) -> str:
    """Removes the Arabic characters from the string provided"""
    return string.encode("ascii", "ignore").decode().strip()


def get_number_of_pages(url: str) -> int:
    """Gets the total number of pages for the category"""
    webpage = get_website_safe(url)
    soup = BeautifulSoup(webpage.content, "html.parser")
    last_page_button = soup.find("a", string="»")

    if last_page_button is not None:
        last_page_url = last_page_button["href"]
        last_page_number = int(last_page_url.split("/")[-1])
    else:
        pages_list = soup.find_all("li", class_="page-item")
        last_page_number = int(pages_list[-1].text)

    return last_page_number


def fix_url(url: str) -> str:
    """Fixes the url by changing the encoded characters back to their original form"""
    return quote(url.split("?")[0]).replace("%3A", ":")


def get_content_format(soup: BeautifulSoup) -> str:
    """Gets the format of the content, returns N/A if no format was found"""
    try:
        content_format = (
            soup.find("i", class_="fas fa-play-circle").find_next_sibling().text
        )

        if content_format.isascii():
            return content_format
        else:
            return "N/A"

    except AttributeError:
        return "N/A"


def get_content_id(soup: BeautifulSoup) -> Optional[str]:
    """Gets the ID of the content"""
    try:
        return remove_arabic_chars(
            soup.find("i", class_="fas fa-dot-circle")
            .parent.text.replace(":", "")
            .replace("#", "")
        )
    except AttributeError:
        return None


def upload_image(image_url: str, content_id: str, get_image: Callable[[str], Response]) -> str:
    if DEBUG:
        print(content_id)
    else:
        pass

    if content_id in IMAGE_SOURCES:
        return IMAGE_SOURCES[content_id]
    else:
        pass

    if image_url == "":
        return "https://imgpile.com/images/TPDrVl.jpg"
    else:
        pass

    image = get_image(image_url)
    image_path = f"./output/{content_id}"

    if ".webp" in image_url:
        with open(image_path + ".webp", "wb") as handler:
            handler.write(image.content)

        jpg_image = Image.open(image_path + ".webp").convert("RGB")
        jpg_image.save(image_path + ".jpg", "jpeg")

        with open(image_path + ".jpg", "rb") as fp:
            base64_image = fp.read()
    else:
        base64_image = b64encode(image.content).decode("utf8")

    headers = {"Authorization": f"Client-ID {environ.get('IMGUR_CLIENT_ID')}"}
    data = {"image": base64_image}

    try:
        return requests.post("https://api.imgur.com/3/image", headers=headers, data=data).json()["data"]["link"]
    except Exception:
        return "https://imgpile.com/images/TPDrVl.jpg"


def remove_year(title: str) -> str:
    """Removes the production year from the content title"""
    if title[-4:].isdigit() and len(title) > 4:
        title = title.replace(title[-5:], "")
    else:
        pass

    return title


def get_content_title(soup_result: ResultSet) -> str:
    """Gets the title of the content"""
    title = remove_year(remove_arabic_chars(
        soup_result.find("div", class_="h1").text
    ))
    return title


def get_genres(soup: BeautifulSoup) -> Union[list[str], str]:
    try:
        genre_tags = soup.find(
            "i", class_="far fa-folders").find_next_siblings("a")

        genres = [tag["href"].split("/")[-1].capitalize()
                  for tag in genre_tags]
    except AttributeError:
        genres = []

    return genres


def akwam_get_website_safe(url: str) -> Response:
    response = None

    while response is None:
        try:
            response = requests.get(url)
        except ConnectionError:
            response = None
        except ChunkedEncodingError:
            response = None

    return response


def akwam_get_last_page_number(url: str) -> int:
    main_page_source = akwam_get_website_safe(url)
    soup = BeautifulSoup(main_page_source.content, "html.parser")
    last_page = int(soup.find_all("a", class_="page-link")[-3].text)

    return last_page


def split_anchor_links(respone: Response) -> list[list[str]]:
    soup = BeautifulSoup(respone.content, "html.parser")
    anchor_tags = soup.find_all("a", class_="icn play")
    links = [tag["href"] for tag in anchor_tags]
    links_ranges = split_into_ranges(6, len(links))

    splitted_links = [links[links_range[0] - 1: links_range[1] - 1]
                      for links_range in links_ranges]

    return splitted_links


def akwam_get_genres(soup: BeautifulSoup) -> Union[list[str], str]:
    genre_tags = soup.find_all("a", class_="badge badge-pill badge-light ml-2")

    try:
        genre_ids = [tag["href"].split("=")[-1] for tag in genre_tags]
    except TypeError:
        return []

    genres = [AKWAM_GENRES[key] for key in genre_ids]

    return genres


def hdw_get_last_page_number(url: str, selector: tuple[By, str] = DEFAULT_HDW_SELECTOR) -> int:
    webpage = get_website_safe(url, selector)
    soup = BeautifulSoup(webpage.content, "html.parser")

    return int(soup.find_all("a", class_="page-link")[-2].text)


def hdw_get_image_source(div: Tag) -> str:
    return div.find_previous_sibling("a").find("img")["src"]


def hdw_get_rating(div: Tag) -> Optional[str]:
    try:
        rating = div.find_previous_sibling("a").find(
            "span", class_="float-left yellow").text.replace(",", ".").strip()
    except AttributeError:
        rating = None

    return rating


def hdw_get_genres(div: Tag) -> list[str]:
    return list(map(lambda genre: genre.strip(), div.find("span", class_="content-views").text.split(", ")))


def clean_iframe_source(iframe_source: str) -> str:
    try:
        return iframe_source.split("=")[2].replace("&img", "")
    except IndexError:
        return ""


def get_tmdb_id(title: str, genre: str) -> Optional[str]:
    params = {
        "query": title,
        "api_key": environ.get("TMDB_API_KEY")
    }

    if genre == "movies":
        request_url = "https://api.themoviedb.org/3/search/movie"
    else:
        request_url = "https://api.themoviedb.org/3/search/tv"

    resp = requests.get(request_url, params=params)

    try:
        tmdb_id = resp.json().get("results")[0].get("id")
    except IndexError:
        tmdb_id = None

    return tmdb_id


def cima_now_get_last_page(soup: BeautifulSoup):
    return int(soup.find_all("ul")[-1].find_all("li")[-1].text)


def cima_now_get_sources(soup: BeautifulSoup):
    anchors = soup.find("ul", {"id": "download"}).find("li").find_all("a")
    return [{anchor.text.split()[0]: anchor["href"]} for anchor in anchors]
