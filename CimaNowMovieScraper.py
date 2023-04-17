from selenium.webdriver.common.by import By
from concurrent.futures import ThreadPoolExecutor
from Common import DEBUG, CIMA_NOW_GENRES, get_tmdb_id, get_website_safe, get_cookies, CIMA_NOW_SELECTOR, cima_now_get_sources, cima_now_get_last_page
from bs4 import BeautifulSoup
from time import perf_counter
import json

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

    resp = get_website_safe(
        "https://cimanow.cc/category/" + route, CIMA_NOW_SELECTOR)

    soup = BeautifulSoup(resp.content, "html.parser")

    last_page = cima_now_get_last_page(soup)

    for page in range(1, last_page + 1):
        resp = get_website_safe(
            f"https://cimanow.cc/category/{route}/page/{page}", CIMA_NOW_SELECTOR)

        soup = BeautifulSoup(resp.content, "html.parser")

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
                resp = get_website_safe(
                    "https://cimanow.cc/" + href + "/watching", CIMA_NOW_SELECTOR)

                soup = BeautifulSoup(resp.content, "html.parser")

                route_dict[movie_id] = {
                    "Title": title,
                    "Image Source": image_source,
                    "Genres": genres,
                    "Sources": cima_now_get_sources(soup),
                    "Category": "cimanow-movie",
                    "TMDb ID": get_tmdb_id(title, "movies")
                }

        if DEBUG:
            print(f"Done scraping page {page} of {last_page}")
        else:
            pass

    return route_dict


def main() -> None:
    get_cookies("https://cimanow.cc/", (By.CLASS_NAME, "logo"))

    with ThreadPoolExecutor() as executor:
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
