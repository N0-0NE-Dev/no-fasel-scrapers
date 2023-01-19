from Common import *
from bs4 import BeautifulSoup
from time import perf_counter
import requests
import json

content_dict = {'movies': {}, 'asian-series': {},
                'anime': {}, 'series': {}, "arabic-series": {},
                "arabic-movies": {}}

featured_content_dict = {}


def scrape_akwam() -> None:
    """Scrapes the recent arabic series and movies from akwam"""
    home_page = requests.get("https://akwam.to/one")
    soup = BeautifulSoup(home_page.content, "html.parser")
    anchor_tags = soup.find_all("a", class_="icn play")
    content_links = [tag["href"] for tag in anchor_tags]

    with open("./output/arabic-series.json", "r", encoding="utf-8") as fp:
        arabic_series = json.load(fp)

    with open("./output/arabic-movies.json", "r", encoding="utf-8") as fp:
        arabic_movies = json.load(fp)

    for link in content_links:
        if "series" in link:
            series_id = link.split("/")[-2]

            try:
                content_dict["arabic-series"][series_id] = {"Title": arabic_series[series_id]["Title"],
                                                            "Image Source": arabic_series[series_id]["Image Source"],
                                                            "Category": "arabic-series"}
            except KeyError:
                continue

        elif "movie" in link:
            movie_id = link.split("/")[-2]

            try:
                content_dict["arabic-movies"][movie_id] = {"Title": arabic_movies[movie_id]["Title"],
                                                           "Image Source": arabic_movies[movie_id]["Image Source"],
                                                           "Category": "arabic-movies"}
            except KeyError:
                continue

        else:
            continue


def scrape_fasel() -> None:
    """Scrapes the content on the home page of fasel"""
    get_cookies()
    home_page = get_website_safe(
        'https://www.faselhd.club/home3')
    soup = BeautifulSoup(home_page.content, 'html.parser')

    trending_content_divs = soup.find_all('div', 'blockMovie')
    trending_content_divs += soup.find_all('div', 'epDivHome')

    featured_content = soup.find_all("div", "h1 mb-1")

    seen = []

    for div in trending_content_divs:
        link = div.find('a')['href']
        content_page = get_website_safe(link)
        soup = BeautifulSoup(content_page.content, 'html.parser')

        content_title = remove_year(remove_arabic_chars(soup.find(
            "div", class_="h1 title").text.split('\n')[1].strip()))

        if '%d9%81%d9%8a%d9%84%d9%85' in link:
            content_category = 'movies'
        elif 'asian-episodes' in link:
            content_category = 'asian-series'
        elif 'anime-episodes' in link:
            content_category = 'anime'
        else:
            content_category = 'series'

        with open(f'./output/{content_category}.json', 'r') as fp:
            content_file = json.load(fp)

        for key in content_file:
            current_title = "".join(content_file[key]["Title"].lower().split())
            clean_content_title = "".join(content_title.lower().split())
            if (current_title == clean_content_title) and (key not in seen):
                seen.append(key)
                content_dict[content_category].update(
                    {key: {"Title": content_file[key]["Title"], "Image Source": content_file[key]["Image Source"], "Category": content_category}})
                break
            else:
                continue

    with open("./output/movies.json", "r") as fp:
        movies = json.load(fp)
        for div in featured_content:
            movie_page = get_website_safe(div.find("a")["href"])

            movie_id = get_content_id(BeautifulSoup(
                movie_page.content, "html.parser"))

            featured_content_dict[movie_id] = movies[movie_id]

    with open("./output/featured-content.json", "w") as fp:
        json.dump(featured_content_dict, fp, indent=4)


def main() -> None:
    scrape_fasel()
    scrape_akwam()

    with open("./output/trending-content.json", "w", encoding="utf-8") as fp:
        json.dump(content_dict, fp, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    start_time = perf_counter()
    main()
    end_time = perf_counter()
    print(
        f"Finished scraping the trending content in about {round((end_time - start_time) / 60)} minute(s)"
    )
else:
    pass
