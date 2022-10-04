from operator import le
from sys import setrecursionlimit
from bs4 import BeautifulSoup, ResultSet, Tag
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat
import json
import time
from Common import *

setrecursionlimit(25000)

if DEBUG:
    PATHS_TO_SCRAPE = ["series"]
else:
    PATHS_TO_SCRAPE = [
        "series",
        "tvshows",
        "asian-series",
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

    season_page = get_website_safe(BASE_URL + f"?p={season_id}")
    soup = BeautifulSoup(season_page.content, "html.parser")

    try:
        all_episodes = soup.find("div", class_="epAll").find_all("a")
    except AttributeError:
        print(
            f"No episodes found for the series {series_title} season {season_number}, skipping it..."
        )
        return {}

    try:
        old_series_dict[series_id]["Seasons"][season_id]["Episodes"]
        if len(all_episodes) == len(old_series_dict[series_id]["Seasons"][season_id]["Episodes"]):
            return {}
        else:
            pass
    except KeyError:
        # Encountered a new series or season of a series_div, scraping it...
        pass

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
        try:
            episode_id = soup.find(
                "span", {"id": "liskSh"}).text.split("=")[-1]
        except AttributeError:
            print(
                f"Episode {episode_number} in season {season_number} in the series with id {series_id} has no id")
            continue

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


def scrape_page(series_divs: list[ResultSet]) -> dict:
    series_dict = {}

    for series_div in series_divs:
        series_image_source = series_div.img.attrs['data-src']
        series_page_source = series_div.find("a")["href"]
        series_title = get_content_title(series_div)

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
            series_image_source, series_id
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

    return series_dict


def scrape_all_series(page_range: tuple) -> dict:
    global old_series_dict, url
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
                splitted_series_divs_list
            )

        for result in results:
            all_series_dict.update(result)

        if DEBUG:
            print(f'Done scraping page {page}')
        else:
            pass

    return all_series_dict


def main():
    global old_series_dict, url

    for path in PATHS_TO_SCRAPE:
        start_time = time.time()

        url = BASE_URL + path
        file_path = f"./output/{path}.json"

        get_cookies()

        with open(file_path, "r") as fp:
            old_series_dict = json.load(fp)

        page_ranges_list = split_into_ranges(8, get_number_of_pages(url))

        if DEBUG:
            print(page_ranges_list)
        else:
            pass

        with ThreadPoolExecutor() as executor:
            results = executor.map(
                scrape_all_series,
                page_ranges_list,
            )

        new_series_dict = {}
        for result in results:
            new_series_dict.update(result)

        combined_series_dict = new_series_dict | old_series_dict

        with open(file_path, "w") as fp:
            json.dump(combined_series_dict, fp, indent=4)

        print(
            f"Done scraping {url} in about {round((time.time() - start_time) / 60)} minute(s)"
        )


if __name__ == "__main__":
    main()
else:
    pass
