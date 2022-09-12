from sys import setrecursionlimit
import time
from bs4 import BeautifulSoup
from googletrans import Translator
from Common import *
from concurrent.futures import ThreadPoolExecutor
import json
from httpcore._exceptions import ConnectTimeout

setrecursionlimit(25000)

with open("./output/anime.json", "r") as fp:
    old_animes = json.load(fp)


def get_iframe_source(episodes: list[str]) -> dict:
    episodes_dict = {}

    for episode in episodes:
        episode_url = episode["href"]
        episode_number = int(remove_arabic_chars(episode.text).strip())
        episode_page = get_website_safe(episode_url)

        try:
            soup = BeautifulSoup(episode_page.content, "html.parser")
        except AttributeError:
            print(
                f"Experinced too many redirects when fetching {episode_url}, skipping it..."
            )
            continue

        episode_id = get_content_id(soup)

        try:
            iframeSource = soup.find("iframe")["src"]
        except TypeError:
            print(
                f"The episode on page {episode_url} has no source, skipping it...")
            continue

        episodes_dict[episode_id] = {}
        episodes_dict[episode_id]["Episode Number"] = episode_number
        episodes_dict[episode_id]["Episode Source"] = iframeSource

    return episodes_dict


def clean_anime_title(anime_title: str) -> str:
    translator = Translator()

    translation = None
    while translation == None:
        try:
            translation = translator.translate(
                anime_title, src="ar", dest="en").text
        except ConnectTimeout:
            print("Failed to translate anime title, trying again...")
            translation = None

    cleaned_anime_title = translation.replace(
        "Anime", "").replace("?", "").strip()

    cleaned_anime_title = cleaned_anime_title.encode(
        "ascii", "ignore").decode()

    return cleaned_anime_title


def scrapeEpisodes(number_of_episodes: int, episodes_sources: list[str]) -> dict:
    episode_ranges = split_into_ranges(8, number_of_episodes)

    splitted_episodes_list = [
        episodes_sources[episode_range[0] - 1: episode_range[1] - 1]
        for episode_range in episode_ranges
    ]

    master_dict = {}
    with ThreadPoolExecutor() as executor:
        results = executor.map(get_iframe_source, splitted_episodes_list)
        for result in results:
            master_dict.update(result)

    return master_dict


def scrape_anime(page_range: tuple) -> dict:
    global old_animes
    anime_dict = {}

    for page in range(page_range[0], page_range[1]):
        main_page = get_website_safe(
            BASE_URL + f"anime/page/{page}")
        soup = BeautifulSoup(main_page.content, "html.parser")
        anime_divs = soup.find_all(
            "div", class_="col-xl-2 col-lg-2 col-md-3 col-sm-3")

        for anime_div in anime_divs:
            anime_title = anime_div.find("div", class_="h1").text
            anime_image_source = anime_div.img.attrs['data-src']
            anime_page_source = anime_div.find("a")["href"]

            anime_page = get_website_safe(anime_page_source)
            soup = BeautifulSoup(anime_page.content, "html.parser")

            anime_id = get_content_id(soup)

            try:
                anime_episodes_list = soup.find(
                    "div", class_="epAll").find_all("a")
            except AttributeError:
                print(
                    f"The anime on page {anime_page_source} has no episodes, skipping it..."
                )
                continue

            number_of_episodes = len(anime_episodes_list)

            try:
                if number_of_episodes == len(old_animes[anime_id]["Episodes"]):
                    continue
                else:
                    pass
            except KeyError:
                # Anime does not exist
                pass

            cleaned_anime_title = clean_anime_title(anime_title)

            anime_dict[anime_id] = {}
            anime_dict[anime_id]["Title"] = cleaned_anime_title
            anime_dict[anime_id]["Format"] = get_content_format(soup)

            anime_dict[anime_id]["Image Source"] = save_image(
                anime_image_source, anime_id
            )

            anime_dict[anime_id]["Episodes"] = scrapeEpisodes(
                number_of_episodes, anime_episodes_list
            )

        if DEBUG:
            print(f'Done scraping page {page}')
        else:
            pass

    return anime_dict


def main():
    global old_animes
    get_cookies()
    page_ranges_list = split_into_ranges(
        8, get_number_of_pages(BASE_URL + "anime")
    )

    print(page_ranges_list)

    with ThreadPoolExecutor() as executor:
        results = executor.map(scrape_anime, page_ranges_list)
        for result in results:
            old_animes.update(result)

    with open("./output/anime.json", "w") as fp:
        json.dump(old_animes, fp)


if __name__ == "__main__":
    start_time = time.time()
    main()

    print(
        f"Done scraping all animes from fasel in about {round((time.time() - start_time) / 60)} minute(s)"
    )
else:
    pass
