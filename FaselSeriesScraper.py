from sys import setrecursionlimit
from bs4 import BeautifulSoup, ResultSet, Tag
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat
import json
from time import perf_counter
from Common import *

setrecursionlimit(25000)

PATHS_TO_SCRAPE = [
    "series",
    "tvshows",
    "asian-series",
]


def scrape_episodes(episode_list: ResultSet, last_episode_number: int = 0) -> dict:
    episodes_dict = {}
    for index, episode in enumerate(episode_list, start=1):
        episode_page = get_website_safe(episode["href"])

        if episode_page is None:
            continue
        else:
            soup = BeautifulSoup(episode_page.content, "html.parser")

        try:
            episode_id = soup.find(
                "span", {"id": "liskSh"}).text.split("=")[-1]

            iframe_source = soup.find("iframe")["src"]

        except AttributeError:
            continue

        except TypeError:
            continue

        episodes_dict[episode_id] = {
            "Episode Number": last_episode_number + index,
            "Source": clean_iframe_source(iframe_source),
        }

    return episodes_dict


def scrape_season(season: Tag, series_id: str) -> dict:
    """Gets the sources of all the episodes in the season provided"""
    global old_series_dict

    try:
        season_id = season.find("div")["data-href"]
    except KeyError:
        return {}

    season_number = int(remove_arabic_chars(
        season.find("div", class_="title").text).lstrip())

    season_page = get_website_safe(FASEL_BASE_URL + f"?p={season_id}")
    soup = BeautifulSoup(season_page.content, "html.parser")

    try:
        all_season_episodes = soup.find("div", class_="epAll").find_all("a")
    except AttributeError:
        return {}

    current_number_of_episodes = len(all_season_episodes)

    try:
        old_number_of_episodes = old_series_dict[series_id]["Seasons"][season_id]["Number Of Episodes"]

        if current_number_of_episodes == old_number_of_episodes:
            return {}

        else:
            raw_new_episodes = all_season_episodes[old_number_of_episodes:]

            old_series_dict[series_id]["Seasons"][season_id]["Number Of Episodes"] += len(
                raw_new_episodes)

            new_episodes = scrape_episodes(
                raw_new_episodes, old_number_of_episodes)

            old_series_dict[series_id]["Seasons"][season_id]["Episodes"].update(
                new_episodes)

            return {}

    except KeyError:
        season_dict = {
            season_id:
            {
                "Season Number": season_number,
                "Number Of Episodes": current_number_of_episodes,
                "Episodes": scrape_episodes(all_season_episodes)
            }
        }

        return season_dict


def scrape_page(series_divs: list[ResultSet], path: str) -> dict:
    """Scrapes all the series in the page provided"""
    series_dict = {}

    for series_div in series_divs:
        series_page = get_website_safe(series_div.find("a")["href"])
        soup = BeautifulSoup(series_page.content, "html.parser")

        series_id = get_content_id(soup)

        if series_id is None:
            return {}
        else:
            pass

        series_dict[series_id] = {
            "Title": get_content_title(series_div),
            "Category": path,
            "Format": get_content_format(soup),
            "Genres": get_genres(soup),
            "Number Of Episodes": 0,
            "Image Source": upload_image(series_div.img.attrs['data-src'], series_id + "-fasel", get_website_safe),
            "Seasons": {}
        }

        season_divs = soup.find_all("div", class_="col-xl-2 col-lg-3 col-md-6")

        with ThreadPoolExecutor() as executor:
            seasons_dicts = executor.map(
                scrape_season,
                season_divs,
                repeat(series_id)
            )

        total_number_of_episodes = 0
        for season_dict in seasons_dicts:
            series_dict[series_id]["Seasons"].update(season_dict)

            for season_key in season_dict:
                total_number_of_episodes += season_dict[season_key]["Number Of Episodes"]

        series_dict[series_id]["Number Of Episodes"] = total_number_of_episodes

    return series_dict


def scrape_all_series(page_range: tuple, path: str) -> dict:
    """Scrapes all the series in the page range provided"""
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
                splitted_series_divs_list,
                repeat(path)
            )

        for result in results:
            all_series_dict.update(result)

        if DEBUG:
            print(f'Done scraping page {page}')
        else:
            pass

    return all_series_dict


def main() -> None:
    """Scrapes all the series, tv shows and asian series from fasel"""
    global old_series_dict, url

    for path in PATHS_TO_SCRAPE:
        start_time = perf_counter()

        url = FASEL_BASE_URL + path
        file_path = f"./output/{path}.json"

        get_cookies(FASEL_BASE_URL, (By.CLASS_NAME, "logo.ml-3"))

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
                repeat(path)
            )

        new_series_dict = {}
        for result in results:
            new_series_dict.update(result)

        combined_series_dict = new_series_dict | old_series_dict

        with open(file_path, "w") as fp:
            json.dump(combined_series_dict, fp, indent=4)

        end_time = perf_counter()

        print(
            f"Finished scraping  all {path} from fasel in about {round((end_time - start_time) / 60)} minute(s)"
        )


if __name__ == "__main__":
    main()
else:
    pass
