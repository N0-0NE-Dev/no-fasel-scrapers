import json
from Common import get_website_safe, get_cookies, split_into_ranges, DEBUG, hdw_get_last_page_number, hdw_get_image_source, hdw_get_rating, hdw_get_genres
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from concurrent.futures import ThreadPoolExecutor
from time import perf_counter

with open("./output/hdwmovies.json", "r", encoding="utf-8") as fp:
    old_moivies = json.load(fp)


def scrape_page_range(page_range: tuple[int]) -> dict:
    movies_dict = {}

    for page in range(page_range[0], page_range[1]):
        webpage = get_website_safe(
            f"https://www.hdwatched.xyz/movies?page={page}")

        soup = BeautifulSoup(webpage.content, "html.parser")

        divs = soup.find_all("div", class_="content-info")

        for div in divs:
            anchor = div.find("a")
            href = anchor["href"]

            movie_id = href.split("/")[-2]

            if movie_id in old_moivies:
                continue
            else:
                pass

            source = "https://www.hdwatched.xyz/free" + href
            title = anchor.find("span").text

            movies_dict[movie_id] = {
                "Title": title,
                "Category": "hdwmovies",
                "Image Source": hdw_get_image_source(div),
                "Genres": hdw_get_genres(div),
                "Source": source,
                "Rating": hdw_get_rating(div),
            }

        if DEBUG:
            print(f"Done page {page}")
        else:
            pass

    return movies_dict


def main() -> None:
    get_cookies("https://www.hdwatched.xyz", (By.CLASS_NAME, "top-brand"))

    last_page_number = hdw_get_last_page_number(
        "https://www.hdwatched.xyz/movies")

    ranges = split_into_ranges(8, last_page_number + 2)

    if DEBUG:
        print(ranges)
    else:
        pass

    with ThreadPoolExecutor() as executor:
        results = executor.map(scrape_page_range, ranges)

    for result in results:
        old_moivies.update(result)

    with open("./output/hdwmovies.json", "w", encoding="utf-8") as fp:
        json.dump(old_moivies, fp, indent=4, ensure_ascii=False)

    return


if __name__ == "__main__":
    start_time = perf_counter()
    main()
    end_time = perf_counter()
    print(
        f"Finished scraping all movies from hdw in about {round((end_time - start_time) / 60)} minute(s)"
    )
else:
    pass
