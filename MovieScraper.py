from sys import setrecursionlimit
from bs4 import BeautifulSoup, ResultSet
from Common import *
from concurrent.futures import ThreadPoolExecutor
import json
import time

setrecursionlimit(25000)

with open("./output/movies.json") as fp:
    old_movies = json.load(fp)


def scrape_page(movie_divs: list[ResultSet]) -> dict:
    """Scrapes all the movies in the page provided"""
    movies_dict = {}
    for movie_div in movie_divs:
        movie_title = get_content_title(movie_div)

        movie_image_source = movie_div.img.attrs['data-src']
        movie_page_url = movie_div.find("a")["href"]
        movie_page = get_website_safe(movie_page_url)

        if movie_page is not None:
            soup = BeautifulSoup(movie_page.content, "html.parser")
        else:
            continue

        movie_id = get_content_id(soup)

        if movie_id in old_movies:
            continue
        else:
            pass

        try:
            iframeSource = soup.find("iframe")["src"]
        except Exception:
            if DEBUG:
                print(
                    f"No source found for movie {movie_title}, skipping it...")
            else:
                pass
            continue

        movies_dict[movie_id] = {}
        movies_dict[movie_id]["Title"] = movie_title
        movies_dict[movie_id]["Format"] = get_content_format(soup)

        movies_dict[movie_id]["Image Source"] = save_image(
            movie_image_source, movie_id)

        movies_dict[movie_id]["Source"] = iframeSource

    return movies_dict


def scrape_all_movies(page_range: tuple) -> dict:
    """Scrapes all the movies in the page range provided"""
    movies_dict = {}
    for page in range(page_range[0], page_range[1]):

        main_page = get_website_safe(
            BASE_URL + f"all-movies/page/{page}")
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

        if DEBUG:
            print(f'Done scraping page {page}')
        else:
            pass

    return movies_dict


def main() -> None:
    """Scapes all the movies from fasel"""
    get_cookies()

    page_ranges_list = split_into_ranges(
        16,
        get_number_of_pages(BASE_URL + "all-movies"),
    )

    if DEBUG:
        print(page_ranges_list)
    else:
        pass

    with ThreadPoolExecutor() as executor:
        results = executor.map(scrape_all_movies, page_ranges_list)

        for result in results:
            old_movies.update(result)

    with open("./output/movies.json", "w") as fp:
        json.dump(old_movies, fp, indent=4)


if __name__ == "__main__":
    start_time = time.time()
    main()

    print(
        f"Finished scraping all movies from fasel in about {round((time.time() - start_time) / 60)} minute(s)"
    )
else:
    pass
