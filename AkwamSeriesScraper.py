from bs4 import BeautifulSoup
from Common import split_into_ranges, remove_arabic_chars, DEBUG, upload_image, akwam_get_website_safe, akwam_get_last_page_number, split_anchor_links, akwam_get_genres
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import json
from time import perf_counter

MAIN_PAGE_URL = "https://akwam.to/series?section=0&category=0&rating=0&year=0&language=1&formats=0&quality=0"

with open("./output/arabic-series.json", "r", encoding="utf-8") as fp:
    old_series_dict = json.load(fp)


def scrape_episode(episodes_list: list[str]) -> dict:
    episodes_dict = {}

    for episode_link in episodes_list:
        episode_id = episode_link.split("/")[4]
        episode_select_page = akwam_get_website_safe(episode_link)
        soup = BeautifulSoup(episode_select_page.content, "html.parser")

        try:
            episode_short_link = soup.find(
                "a", class_="link-btn link-show d-flex align-items-center px-3")["href"]
        except TypeError:
            continue

        short_link_page = akwam_get_website_safe(episode_short_link)

        soup = BeautifulSoup(
            short_link_page.content, "html.parser")

        try:
            episode_watch_page_link = soup.find(
                "a", class_="download-link")["href"]
        except TypeError:
            continue

        episode_watch_page = akwam_get_website_safe(episode_watch_page_link)

        soup = BeautifulSoup(
            episode_watch_page.content, "html.parser")

        try:
            episode_number = int(remove_arabic_chars(soup.find(
                "h2", class_="font-size-20 font-weight-bold").find("a").text).split("\n")[0])
        except ArithmeticError:
            continue

        episodes_dict[episode_id] = {
            "Episode Number": episode_number,
            "Source": episode_watch_page_link
        }

    return episodes_dict


def scrape_series(series_list: list[str]) -> dict:
    all_series_dict = {}

    for series in series_list:
        series_id = series.split("/")[-2]
        series_page_source = akwam_get_website_safe(series)
        soup = BeautifulSoup(series_page_source.content, "html.parser")

        series_title = soup.find(
            "h1", "entry-title font-size-28 font-weight-bold text-white mb-0").text.strip()

        image_source = soup.find(
            "div", class_="col-lg-3 col-md-4 text-center mb-5 mb-md-0").find("a")["href"]

        episode_entries = soup.find_all(
            "h2", class_="font-size-18 text-white mb-2")

        episode_links = [entry.find("a")["href"] for entry in episode_entries]

        current_number_of_episodes = len(episode_links)

        try:
            old_number_of_episodes = old_series_dict[series_id]["Number Of Episodes"]

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
            "Genres": akwam_get_genres(soup),
            "Image Source": upload_image(image_source, series_id + "-akwam-series", akwam_get_website_safe),
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
        page_source = akwam_get_website_safe(MAIN_PAGE_URL + f"&page={page}")

        with ThreadPoolExecutor() as executor:
            results = executor.map(
                scrape_series, split_anchor_links(page_source))

        for result in results:
            all_series_dict.update(result)

        if DEBUG:
            print(f"Done scraping page {page}")
        else:
            pass

    return all_series_dict


def main() -> None:
    page_ranges = split_into_ranges(
        8, akwam_get_last_page_number(MAIN_PAGE_URL))

    if DEBUG:
        print(page_ranges)
    else:
        pass

    with ProcessPoolExecutor() as executor:
        results = executor.map(scrape_page_range, page_ranges)

    for result in results:
        old_series_dict.update(result)

    with open("./output/arabic-series.json", "w", encoding="utf-8") as fp:
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
