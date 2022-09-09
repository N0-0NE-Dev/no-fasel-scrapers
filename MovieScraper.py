from sys import setrecursionlimit
from bs4 import BeautifulSoup, ResultSet
from Common import *
from concurrent.futures import ThreadPoolExecutor
import json
import time

setrecursionlimit(25000)

with open("./output/json/movies.json") as fp:
    old_movies = json.load(fp)


def scrape_page(movie_divs: list[ResultSet]) -> dict:
    movies_dict = {}
    for movie_div in movie_divs:
        movie_title = remove_year_from_title(remove_arabic_chars(
            movie_div.find("div", class_="h1").text
        ).strip())

        movie_image_source = movie_div.img.attrs['data-src']
        movie_page_url = movie_div.find("a")["href"]
        movie_page = get_website_safe(movie_page_url)

        soup = BeautifulSoup(movie_page.content, "html.parser")

        movie_id = get_content_id(soup)

        if movie_id in old_movies:
            continue
        else:
            pass

        try:
            iframeSource = soup.find("iframe")["src"]
        except Exception:
            print(f"No source found for movie {movie_title}, skipping it...")
            continue

        movies_dict[movie_id] = {}
        movies_dict[movie_id]["Title"] = movie_title
        movies_dict[movie_id]["Format"] = get_content_format(soup)

        movies_dict[movie_id]["Image Source"] = save_image(
            movie_image_source, movie_id)

        movies_dict[movie_id]["Source"] = iframeSource

    return movies_dict


def scrape_all_movies(page_range: tuple) -> dict:
    movies_dict = {}
    for page in range(page_range[0], page_range[1]):

        main_page = get_website_safe(
            f"https://www.faselhd.club/all-movies/page/{page}")
        soup = BeautifulSoup(main_page.content, "html.parser")

        movie_divs = soup.find_all(
            "div", class_="col-xl-2 col-lg-2 col-md-3 col-sm-3")

        movie_divs_ranges = split_into_ranges(6, len(movie_divs))
        splitted_movie_divs_list = [
            movie_divs[movie_divs_range[0] - 1: movie_divs_range[1] - 1]
            for movie_divs_range in movie_divs_ranges
        ]

        with ThreadPoolExecutor() as executor:
            results = executor.map(scrape_page, splitted_movie_divs_list)

        for result in results:
            movies_dict.update(result)

    return movies_dict


def main() -> None:
    get_cookies()

    page_ranges_list = split_into_ranges(
        16,
        get_number_of_pages("https://www.faselhd.club/all-movies"),
    )

    print(page_ranges_list)

    with ThreadPoolExecutor() as executor:
        results = executor.map(scrape_all_movies, page_ranges_list)

        for result in results:
            old_movies.update(result)

    with open("./output/json/movies.json", "w") as fp:
        json.dump(old_movies, fp)


if __name__ == "__main__":
    start_time = time.time()
    main()

    print(
        f"Finished scraping all movies from fasel in about {round((time.time() - start_time) / 60)} minute(s)"
    )
else:
    pass
