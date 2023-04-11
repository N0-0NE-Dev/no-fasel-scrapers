from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ProcessPoolExecutor
from Common import DEBUG, CIMA_NOW_GENRES, get_tmdb_id
from bs4 import BeautifulSoup
from time import perf_counter
import json
import requests
import zipfile
import pathlib

MOVIE_ROUTES = [
    "%D8%A7%D9%81%D9%84%D8%A7%D9%85-%D8%B9%D8%B1%D8%A8%D9%8A%D8%A9",
    "%D8%A7%D9%81%D9%84%D8%A7%D9%85-%D8%A7%D8%AC%D9%86%D8%A8%D9%8A%D8%A9",
    "%D8%A7%D9%81%D9%84%D8%A7%D9%85-%D8%AA%D8%B1%D9%83%D9%8A%D8%A9",
    "%D8%A7%D9%81%D9%84%D8%A7%D9%85-%D9%87%D9%86%D8%AF%D9%8A%D8%A9",
    "%D8%A7%D9%81%D9%84%D8%A7%D9%85-%D8%A7%D9%86%D9%8A%D9%85%D9%8A%D8%B4%D9%86"
]

with open("./output/CimaNowMovies.json", "r", encoding="utf-8") as fp:
    old_movies = json.load(fp)


def scrape_route(route: str) -> dict:
    route_dict = {}

    driver = uc.Chrome(headless=True, use_subprocess=True,
                       driver_executable_path=f"{pathlib.Path().resolve()}/chromedriver", version_main=112)

    driver.get("https://cimanow.cc/category/" + route)

    WebDriverWait(driver, 60).until(EC.presence_of_element_located(
        (By.CLASS_NAME, "owl-head.owl-loaded.owl-drag")))

    last_page = int(driver.find_elements(By.TAG_NAME, "ul")
                    [-1].find_elements(By.TAG_NAME, "li")[-1].get_attribute("innerText"))

    for page in range(1, last_page + 1):
        driver.get(f"https://cimanow.cc/category/{route}/page/{page}")

        soup = BeautifulSoup(driver.page_source, "html.parser")

        content_cards = soup.find("section").find_all("article")

        for card in content_cards:
            href = card.find("a")["href"].split("/")[-2]
            image_source = card.find("img")["src"]

            try:
                raw_genres = card.find_all(
                    "ul")[-1].find_all("li")[-1].find("em").text
            except AttributeError:
                raw_genres = ""

            title = card.find_all(
                "ul")[-1].find_all("li")[-1].text.replace(raw_genres, "").strip()

            genres = [CIMA_NOW_GENRES.get(genre)
                      for genre in raw_genres.split(" ، ")]

            movie_id = str(hash(title))[1:7]

            if movie_id in old_movies:
                continue
            else:
                driver.get("https://cimanow.cc/" + href + "/watching")

                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "tab")))

                anchors = driver.execute_script(
                    "return [...document.getElementById('download').querySelector('li').querySelectorAll('a')]")

                route_dict[movie_id] = {
                    "Title": title,
                    "Image Source": image_source,
                    "Genres": genres,
                    "Sources": [{anchor.get_attribute("innerText").split()[0]: anchor.get_attribute("href")} for anchor in anchors],
                    "Category": "cimanow-movie",
                    "TMDb ID": get_tmdb_id(title, "movies")
                }

        if DEBUG:
            print(f"Done scraping page {page} of {last_page}")
        else:
            pass

    driver.quit()
    return route_dict


def setup() -> None:
    file_name = "chromedriver.zip"

    resp = requests.get(
        "https://chromedriver.storage.googleapis.com/112.0.5615.28/chromedriver_win32.zip")

    with open(file_name, "wb") as handler:
        handler.write(resp._content)

    with zipfile.ZipFile(f"./{file_name}", "r") as ref:
        ref.extractall("./")


def main() -> None:
    setup()

    with ProcessPoolExecutor() as executor:
        results = executor.map(scrape_route, MOVIE_ROUTES)

    for result in results:
        old_movies.update(result)

    with open("./output/CimaNowMovies.json", "w", encoding="utf-8") as fp:
        json.dump(old_movies, fp, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    start_time = perf_counter()
    main()
    end_time = perf_counter()
    print(
        f"Finished scraping all movies from CimaNow in about {round((end_time - start_time) / 60)} minute(s)"
    )
else:
    pass
