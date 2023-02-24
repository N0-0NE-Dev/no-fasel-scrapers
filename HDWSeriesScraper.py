import json
from Common import get_cookies, get_website_safe, hdw_get_last_page_number, hdw_get_image_source, hdw_get_rating, split_into_ranges, DEFAULT_HDW_SELECTOR, HDW_BASE_URL, hdw_get_genres, DEBUG
from bs4 import BeautifulSoup, Tag
from concurrent.futures import ThreadPoolExecutor
from time import perf_counter


def scrape_series(divs: list[Tag]) -> dict:
    series_dict = {}

    for div in divs:
        anchor = div.find("a")
        href = anchor["href"]

        title = anchor["title"]
        series_id = href.split("/")[2]
        series_page_link = HDW_BASE_URL + href

        series_dict[series_id] = {
            "Title": title,
            "Category": "hdwseries",
            "Genres": hdw_get_genres(div),
            "Image Source": hdw_get_image_source(div),
            "Rating": hdw_get_rating(div),
            "Seasons": {}
        }

        series_page = get_website_safe(series_page_link, DEFAULT_HDW_SELECTOR)
        soup = BeautifulSoup(series_page.content, "html.parser")

        seasons = soup.find_all(
            "a", class_="btn btn-secondary btn-bold btn-xxs")

        if len(seasons) == 0:
            episodes_dict = {}
            episodes = soup.find_all("div", class_="content-info")

            for episode in episodes:
                anchor = episode.find("a")
                href = anchor["href"]
                episode_id = href.split("/")[-2]

                try:
                    episode_number = int(href.split("-")[-2])
                except ValueError:
                    episode_number = int(href.split("-")[-1])

                source = HDW_BASE_URL + href

                episodes_dict[episode_id] = {
                    "Episode Number": int(episode_number),
                    "Source": source
                }

            series_dict[series_id]["Seasons"][series_id] = {
                "Season Number": 1,
                "Number Of Episodes": len(episodes),
                "Episodes": episodes_dict
            }
        else:
            for season in seasons:
                episodes_dict = {}
                href = season["href"]
                season_number = href.split("=")[-1]
                season_id = href.split("/")[-2] + season_number
                season_page = get_website_safe(HDW_BASE_URL + href)
                soup = BeautifulSoup(season_page.content, "html.parser")
                episodes = soup.find_all("div", class_="content-info")

                for episode in episodes:
                    anchor = episode.find("a")
                    href = anchor["href"]
                    episode_id = href.split("/")[-2]

                    try:
                        episode_number = int(href.split("-")[-2])
                    except ValueError:
                        episode_number = int(href.split("-")[-1])

                    source = HDW_BASE_URL + href

                    episodes_dict[episode_id] = {
                        "Episode Number": int(episode_number),
                        "Source": source
                    }

                series_dict[series_id]["Seasons"][season_id] = {
                    "Season Number": season_number,
                    "Number Of Episodes": len(episodes),
                    "Episodes": episodes_dict
                }

    return series_dict


def scrape_page_range(page_range: tuple[int, int]) -> dict:
    pages_dict = {}

    for page in range(page_range[0], page_range[1]):
        webpage = get_website_safe(HDW_BASE_URL + f"/tv-shows?page={page}")
        soup = BeautifulSoup(webpage.content, "html.parser")
        series_divs = soup.find_all("div", class_="content-info")

        ranges = split_into_ranges(5, len(series_divs))

        spliitted = [series_divs[series_range[0] - 1: series_range[1] - 1]
                     for series_range in ranges]

        with ThreadPoolExecutor() as executor:
            results = executor.map(scrape_series, spliitted)

        for result in results:
            pages_dict.update(result)

        if DEBUG:
            print(f"Done page {page}")
        else:
            pass

    return pages_dict


def main() -> None:
    master_dict = {}
    get_cookies(HDW_BASE_URL, DEFAULT_HDW_SELECTOR)

    last_page_number = hdw_get_last_page_number(HDW_BASE_URL + "/tv-shows")

    ranges = split_into_ranges(8, last_page_number + 2)

    if DEBUG:
        print(ranges)
    else:
        pass

    with ThreadPoolExecutor() as executor:
        results = executor.map(scrape_page_range, ranges)

    for result in results:
        master_dict.update(result)

    with open("./output/hdwseries.json", "w") as fp:
        json.dump(master_dict, fp, indent=4)


if __name__ == "__main__":
    start_time = perf_counter()
    main()
    end_time = perf_counter()
    print(
        f"Finished scraping all series from hdw in about {round((end_time - start_time) / 60)} minute(s)"
    )
else:
    pass
