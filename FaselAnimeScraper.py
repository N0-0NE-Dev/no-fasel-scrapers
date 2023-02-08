from sys import setrecursionlimit
from time import perf_counter
from bs4 import BeautifulSoup
from googletrans import Translator
from Common import *
from concurrent.futures import ThreadPoolExecutor
import json
from httpx import ReadTimeout

setrecursionlimit(25000)

with open("./output/anime.json", "r") as fp:
    old_animes = json.load(fp)


def clean_anime_title(anime_title: str) -> str:
    """Translate the anime title and remove all unnecessary characters"""
    translation = None
    while translation is None:
        try:
            translation = Translator().translate(
                anime_title, src="ar", dest="en").text
        except ReadTimeout:
            translation = None

    cleaned_anime_title = translation.replace("Anime", "").replace(
        "anime", "").replace("?", "").strip().encode("ascii", "ignore").decode()

    return cleaned_anime_title


def get_iframe_source(episodes: list[str]) -> dict:
    """Gets the video source for each episode"""
    episodes_dict = {}

    for episode in episodes:
        episode_url = episode["href"]
        episode_page = get_website_safe(episode_url)

        if episode_page is not None:
            soup = BeautifulSoup(episode_page.content, "html.parser")
        else:
            continue

        episode_id = get_content_id(soup)

        try:
            iframeSource = soup.find("iframe")["src"]
        except TypeError:
            continue

        episodes_dict[episode_id] = {
            "Episode Number":  int(remove_arabic_chars(episode.text).strip()),
            "Source": iframeSource,
        }

    return episodes_dict


def scrape_episodes(current_number_of_episodes: int, episodes_sources: list[str], start_episode: int = 0) -> dict:
    """Scrapes all the episodes of the anime and their sources"""
    episode_ranges = split_into_ranges(
        8, current_number_of_episodes, start_episode)

    splitted_episodes_list = [
        episodes_sources[episode_range[0] - 1: episode_range[1] - 1]
        for episode_range in episode_ranges
    ]

    with ThreadPoolExecutor() as executor:
        results = executor.map(get_iframe_source, splitted_episodes_list)

    master_dict = {}
    for result in results:
        master_dict.update(result)

    return master_dict


def scrape_anime(page_range: tuple) -> dict:
    """Scrapes all the animes in the page range provided"""
    anime_dict = {}

    for page in range(page_range[0], page_range[1]):
        main_page = get_website_safe(
            FASEL_BASE_URL + f"anime/page/{page}")
        soup = BeautifulSoup(main_page.content, "html.parser")
        anime_divs = soup.find_all(
            "div", class_="col-xl-2 col-lg-2 col-md-3 col-sm-3")

        for anime_div in anime_divs:
            anime_page_source = anime_div.find("a")["href"]

            anime_page = get_website_safe(anime_page_source)
            soup = BeautifulSoup(anime_page.content, "html.parser")

            anime_id = get_content_id(soup)

            if anime_id is None:
                continue
            else:
                pass

            try:
                anime_episodes_list = soup.find(
                    "div", class_="epAll").find_all("a")
            except AttributeError:
                continue

            current_number_of_episodes = len(anime_episodes_list)

            try:
                old_number_of_episodes = old_animes[anime_id]["Number Of Episodes"]
                if current_number_of_episodes == old_number_of_episodes:
                    continue
                else:
                    new_episodes = scrape_episodes(
                        current_number_of_episodes, anime_episodes_list, old_number_of_episodes)

                    old_animes[anime_id]["Number Of Episodes"] += len(
                        new_episodes)

                    old_animes[anime_id]["Episodes"].update(new_episodes)
                    continue
            except KeyError:
                anime_dict[anime_id] = {
                    "Title": clean_anime_title(anime_div.find("div", class_="h1").text),
                    "Category": "anime",
                    "Number Of Episodes": current_number_of_episodes,
                    "Format": get_content_format(soup),
                    "Image Source": upload_image(anime_div.img.attrs['data-src'], anime_id + "-fasel", get_website_safe),
                    "Episodes": scrape_episodes(current_number_of_episodes, anime_episodes_list)
                }

        if DEBUG:
            print(f'Done scraping page {page}')
        else:
            pass

    return anime_dict


def main() -> None:
    """Scrapes all the anime from fasel"""
    get_cookies(FASEL_BASE_URL, (By.CLASS_NAME, "logo.ml-3"))
    page_ranges_list = split_into_ranges(
        8, get_number_of_pages(FASEL_BASE_URL + "anime")
    )

    if DEBUG:
        print(page_ranges_list)
    else:
        pass

    with ThreadPoolExecutor() as executor:
        results = executor.map(scrape_anime, page_ranges_list)

    for result in results:
        old_animes.update(result)

    with open("./output/anime.json", "w") as fp:
        json.dump(old_animes, fp, indent=4)


if __name__ == "__main__":
    start_time = perf_counter()
    main()
    end_time = perf_counter()
    print(
        f"Done scraping all animes from fasel in about {round((end_time - start_time) / 60)} minute(s)"
    )
else:
    pass
