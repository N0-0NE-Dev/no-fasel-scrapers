import re
from Common import *
from bs4 import BeautifulSoup, ResultSet
from typing import Optional, Any
from requests import Response


def main():
    """Scrapes the content on the home page of fasels"""
    get_cookies()
    main_page: Optional[Response] = get_website_safe(
        'https://www.faselhd.club/home3')
    soup: BeautifulSoup = BeautifulSoup(main_page.content, 'html.parser')

    new_content: ResultSet = soup.find_all('div', 'blockMovie')
    new_content += soup.find_all('div', 'epDivHome')

    content_dict: dict[str, list[dict[str, dict[str, str]]]] = {'movies': [], 'asian-series': [],
                                                                'anime': [], 'series': []}
    seen: list[str] = []

    for element in new_content:
        link: str = element.find('a')['href']

        content_page: Optional[Response] = get_website_safe(link)
        soup: BeautifulSoup = BeautifulSoup(
            content_page.content, 'html.parser')

        content_title: str = remove_year(remove_arabic_chars(
            soup.find('div', class_='h3').text.split('-')[0]))

        content_title: str = re.split(r'\s{2,}', content_title)[0]

        if DEBUG:
            print(content_title)
        else:
            pass

        if '%d9%81%d9%8a%d9%84%d9%85' in link:
            content_category: str = 'movies'
        elif 'asian-episodes' in link:
            content_category: str = 'asian-series'
        elif 'anime-episodes' in link:
            content_category: str = 'anime'
        else:
            content_category: str = 'series'

        if DEBUG:
            print(link, content_category)
        else:
            pass

        with open(f'./output/{content_category}.json', 'r') as fp:
            content_file: dict[str, dict[str, Any]] = json.load(fp)

        for key in content_file:
            current_element: dict[str, Any] = content_file[key]
            if (current_element["Title"] == content_title) and (key not in seen):
                seen.append(key)
                content_dict[content_category].append(
                    {key: {"Title": current_element["Title"], "Format": current_element["Format"], "Image Source": current_element["Image Source"]}})
                break
            else:
                continue

    with open('./output/trending-content.json', 'w') as fp:
        json.dump(content_dict, fp, indent=4)


if __name__ == "__main__":
    main()
else:
    pass
