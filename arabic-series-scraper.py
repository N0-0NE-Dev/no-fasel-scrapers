import requests
from bs4 import BeautifulSoup
from common import split_into_ranges, remove_arabic_chars, DEBUG
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import json
from requests import Response
from requests.exceptions import ConnectionError
from time import perf_counter

MAIN_PAGE_URL = "https://akwam.to/series?section=0&category=0&rating=0&year=0&language=1&formats=0&quality=0"

with open("./output/arabic-series.json", "r") as fp:
    old_series_dict = json.load(fp)


def get_website_safe(url: str) -> Response:
    response = None

    while response is None:
        try:
            response = requests.get(url)
        except ConnectionError:
            response = None

    return response


def save_image(image_url: str, series_id: str) -> str:
    image = get_website_safe(image_url)

    with open(f"./output/images/arabic-series/{series_id}.jpg", "wb") as fp:
        fp.write(image.content)

    return "Saved"


def scrape_episode(episodes_list: list[str]) -> dict:
    episodes_dict = {}

    for episode_link in episodes_list:
        episode_id = episode_link.split("/")[4]
        episode_select_page = get_website_safe(episode_link)
        soup = BeautifulSoup(episode_select_page.content, "html.parser")

        try:
            episode_short_link = soup.find(
                "a", class_="link-btn link-show d-flex align-items-center px-3")["href"]
        except TypeError:
            continue

        short_link_page = get_website_safe(episode_short_link)

        soup = BeautifulSoup(
            short_link_page.content, "html.parser")

        episode_watch_page_link = soup.find(
            "a", class_="download-link")["href"]

        episode_watch_page = get_website_safe(episode_watch_page_link)

        soup = BeautifulSoup(
            episode_watch_page.content, "html.parser")

        episode_number = remove_arabic_chars(soup.find(
            "h2", class_="font-size-20 font-weight-bold").find("a").text).split("\n")[0]

        episode_source = soup.find("source")["src"]

        episodes_dict[episode_id] = {
            "Episode Number": episode_number,
            "Source": episode_source
        }

    return episodes_dict


def scrape_series(series_list: list[str]) -> dict:
    all_series_dict = {}

    for series in series_list:
        series_id = series.split("/")[-2]
        series_page_source = get_website_safe(series)
        soup = BeautifulSoup(series_page_source.content, "html.parser")

        series_title = soup.find(
            "h1", "entry-title font-size-28 font-weight-bold text-white mb-0").text

        if "House of Cards" in series:
            continue
        else:
            pass

        image_source = soup.find(
            "div", class_="col-lg-3 col-md-4 text-center mb-5 mb-md-0").find("a")["href"]

        episode_entries = soup.find_all(
            "h2", class_="font-size-18 text-white mb-2")

        episode_links = [entry.find("a")["href"] for entry in episode_entries]

        current_number_of_episodes = len(episode_links)

        try:
            old_number_of_episodes = int(
                old_series_dict[series_id]["Number Of Episodes"])

            if current_number_of_episodes == old_number_of_episodes:
                continue
            else:
                pass

        except KeyError:
            pass

        episodes_links_ranges = split_into_ranges(4, len(episode_links))

        splitted_episodes_list = [episode_links[episodes_links_range[0] - 1: episodes_links_range[1] - 1]
                                  for episodes_links_range in episodes_links_ranges]

        all_series_dict[series_id] = {
            "Title": series_title,
            "Category": "arabic-series",
            "Number Of Episodes": current_number_of_episodes,
            "Format": "WEB-DL",
            "Image Source": save_image(image_source, series_id),
            "Episodes": {}
        }

        with ThreadPoolExecutor() as executor:
            results = executor.map(scrape_episode, splitted_episodes_list)

        for result in results:
            all_series_dict[series_id]["Episodes"].update(result)

        all_series_dict[series_id]["Number Of Episodes"] = len(
            all_series_dict[series_id]["Episodes"].keys())

    return all_series_dict


def scrape_page_range(page_range: tuple[int]) -> dict:
    all_series_dict = {}

    for page in range(page_range[0], page_range[1]):
        page_source = get_website_safe(MAIN_PAGE_URL + f"&page={page}")
        soup = BeautifulSoup(page_source.content, "html.parser")
        series_anchor_tags = soup.find_all("a", class_="icn play")
        series_links = [tag["href"] for tag in series_anchor_tags]
        series_links_ranges = split_into_ranges(6, len(series_links))

        splitted_series_links = [series_links[series_links_range[0] - 1: series_links_range[1] - 1]
                                 for series_links_range in series_links_ranges]

        with ThreadPoolExecutor() as executor:
            results = executor.map(scrape_series, splitted_series_links)

        for result in results:
            all_series_dict.update(result)

        if DEBUG:
            print(f"Done scraping page {page}")
        else:
            pass

    return all_series_dict


def main() -> None:
    main_page_source = get_website_safe(MAIN_PAGE_URL)
    soup = BeautifulSoup(main_page_source.content, "html.parser")
    page_buttons = soup.find_all("a", class_="page-link")
    last_page_button = page_buttons[-3]
    last_page_number = int(last_page_button.text)
    page_ranges = split_into_ranges(10, last_page_number)

    if DEBUG:
        print(page_ranges)
    else:
        pass

    with ProcessPoolExecutor() as executor:
        results = executor.map(scrape_page_range, page_ranges)

    for result in results:
        old_series_dict.update(result)

    with open("test.json", "w", encoding="utf-8") as fp:
        json.dump(old_series_dict, fp, indent=4, ensure_ascii=False)

    return


if __name__ == "__main__":
    start_time = perf_counter()
    main()
    end_time = perf_counter()
    print(
        f"Done scraping all arabic-series from akwam in about {round((end_time - start_time) / 60)} minute(s)"
    )
else:
    pass
