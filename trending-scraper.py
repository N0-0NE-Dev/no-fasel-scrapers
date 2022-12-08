from common import *
from bs4 import BeautifulSoup
from time import perf_counter
import requests
import json

content_dict = {'movies': {}, 'asian-series': {},
                'anime': {}, 'series': {}, "arabic-series": {}}


def scrape_akwam() -> None:
    """Scrapes the recent arabic series from akwam"""
    home_page = requests.get("https://akwam.to/recent")
    soup = BeautifulSoup(home_page.content, "html.parser")
    series_anchor_tag = soup.find_all("a", class_="icn play")
    series_links = [tag["href"] for tag in series_anchor_tag]

    with open("./output/arabic-series.json", "r", encoding="utf-8") as fp:
        arabic_series_dict = json.load(fp)

    for link in series_links:
        if "series" in link:
            series_id = link.split("/")[4]

            try:
                content_dict['arabic-series'].update(
                    {series_id: {
                        "Title": arabic_series_dict[series_id]["Title"],
                        "Image Source": arabic_series_dict[series_id]["Image Source"],
                        "Category": "arabic-series"}})
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
