from sys import setrecursionlimit
from bs4 import BeautifulSoup, ResultSet, Tag
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat
import json
import time
from Common import *

setrecursionlimit(25000)

urls_to_scrape = [
    "https://www.faselhd.club/series",
    "https://www.faselhd.club/tvshows",
    "https://www.faselhd.club/asian-series",
]


def scrape_season(
    season: Tag,
    series_title: str,
    series_id: str
) -> dict:
    global old_series_dict
    season_dict = {}
    season_id = season.find("div")["data-href"]

    season_number = int(remove_arabic_chars(
        season.find("div", class_="title").text
    ).lstrip())

    season_page = get_website_safe(f"https://www.faselhd.club/?p={season_id}")
    soup = BeautifulSoup(season_page.content, "html.parser")

    try:
        all_episodes = soup.find("div", class_="epAll").find_all("a")
    except AttributeError:
        print(
            f"No episodes found for the series {series_title} season {season_number}, skipping it..."
        )
        return {}

    try:
        if len(all_episodes) == len(
            old_series_dict[series_id]["Seasons"][season_id]["Episodes"]
        ):
            return {}
        else:
            pass
    except KeyError:
        pass
        # Encountered a new series or season of a series_div, scraping it...

    season_dict[season_id] = {}
    season_dict[season_id]["Season Number"] = season_number
    season_dict[season_id]["Episodes"] = {}

    for episode_number, episode in enumerate(all_episodes, start=1):
        episode_source = episode["href"]
        episode_page = get_website_safe(episode_source)

        if episode_page is None:
            continue
        else:
            pass

        soup = BeautifulSoup(episode_page.content, "html.parser")
        episode_id = soup.find("span", {"id": "liskSh"}).text.split("=")[-1]

        try:
            iframe_source = soup.find("iframe")["src"]
        except TypeError:
            print("No source found for this one cheif, skipping it...")
            continue

        season_dict[season_id]["Episodes"][episode_id] = {}
        season_dict[season_id]["Episodes"][episode_id][
            "Episode Number"
        ] = episode_number

        season_dict[season_id]["Episodes"][episode_id]["Source"] = iframe_source

    return season_dict


def scrape_page(series_divs: list[ResultSet], url: str) -> dict:
    series_dict = {}

    for series_div in series_divs:
        series_image_source = series_div.img.attrs['data-src']
        # try:
        #     series_image_source = series_div.find("div", class_="imgdiv-class").find("img")[
        #         "data-src"
        #     ]
        # except AttributeError:
        #     series_image_source = series_div.img.attrs['data-src']
        #     print(series_image_source)
        #     # series_image_source = ""

        series_page_source = series_div.find("a")["href"]
        series_title = remove_year_from_title(remove_arabic_chars(
            series_div.find("div", class_="h1").text
        ).strip())

        series_page = get_website_safe(series_page_source)
        soup = BeautifulSoup(series_page.content, "html.parser")

        try:
            series_id = get_content_id(soup)
        except AttributeError:
            print(
                f"The series {series_title} either has no ID or is blank, skipping it..."
            )
            return {}

        series_dict[series_id] = {}
        series_dict[series_id]["Title"] = series_title
        series_dict[series_id]["Format"] = get_content_format(soup)

        series_dict[series_id]["Image Source"] = save_image(
            series_image_source, f"./output/new-images/{url.split('/')[-1]}", series_id
        )

        series_dict[series_id]["Seasons"] = {}

        season_divs = soup.find_all("div", class_="col-xl-2 col-lg-3 col-md-6")

        with ThreadPoolExecutor() as executor:
            seasons_dicts = executor.map(
                scrape_season,
                season_divs,
                repeat(series_title),
                repeat(series_id)
            )

        for season_dict in seasons_dicts:
            series_dict[series_id]["Seasons"].update(season_dict)

        if len(series_dict[series_id]["Seasons"]) == 0:
            # print("Encountered a totally empty series, deleting it...")
            del series_dict[series_id]
        else:
            pass

    return series_dict


def scrape_all_series(url: str, page_range: tuple) -> dict:
    global old_series_dict
    all_series_dict = {}

    for page in range(page_range[0], page_range[1]):
        main_page = get_website_safe(f"{url}/page/{page}")
        soup = BeautifulSoup(main_page.content, "html.parser")
        series_divs = soup.find_all(
            "div", class_="col-xl-2 col-lg-2 col-md-3 col-sm-3")

        series_divs_ranges = split_into_ranges(6, len(series_divs))
        splitted_series_divs_list = [
            series_divs[series_divs_range[0] - 1: series_divs_range[1] - 1]
            for series_divs_range in series_divs_ranges
        ]

        with ThreadPoolExecutor() as executor:
            results = executor.map(
                scrape_page,
                splitted_series_divs_list,
                repeat(url)
            )

        for result in results:
            all_series_dict.update(result)

        print(f"Page {page} in {url.split('/')[-1]} is done")

    return all_series_dict


def main():
    for url in urls_to_scrape:
        start_time = time.time()

        global old_series_dict
        file_path = f"./output/json/{url.split('/')[-1]}.json"
        get_cookies()

        with open(file_path, "r") as fp:
            old_series_dict = json.load(fp)

        page_ranges_list = split_into_ranges(8, get_number_of_pages(url))
        print(page_ranges_list)

        with ThreadPoolExecutor() as executor:
            results = executor.map(
                scrape_all_series,
                repeat(url),
                page_ranges_list,
            )

        for result in results:
            old_series_dict.update(result)

        with open(file_path, "w") as fp:
            json.dump(old_series_dict, fp)

        print(
            f"Done scraping {url} in about {round((time.time() - start_time) / 60)} minute(s)"
        )


if __name__ == "__main__":
    main()
else:
    pass
