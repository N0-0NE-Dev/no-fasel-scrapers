from Common import *
from bs4 import BeautifulSoup
import time


def main():
    """Scrapes the content on the home page of fasel"""
    get_cookies()
    home_page = get_website_safe(
        'https://www.faselhd.club/home3')
    soup = BeautifulSoup(home_page.content, 'html.parser')

    trending_content_divs = soup.find_all('div', 'blockMovie')
    trending_content_divs += soup.find_all('div', 'epDivHome')

    content_dict = {'movies': [], 'asian-series': [],
                    'anime': [], 'series': []}
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

        if DEBUG:
            print(f"{content_title} // {link} // {content_category}\n")
        else:
            pass

        with open(f'./output/{content_category}.json', 'r') as fp:
            content_file = json.load(fp)

        for key in content_file:
            current_title = "".join(content_file[key]["Title"].lower().split())
            clean_content_title = "".join(content_title.lower().split())
            if (current_title == clean_content_title) and (key not in seen):
                seen.append(key)
                content_dict[content_category].append({key: content_file[key]})
                break
            else:
                continue

    with open('./output/trending-content.json', 'w') as fp:
        json.dump(content_dict, fp, indent=4)


if __name__ == "__main__":
    start_time = time.time()
    main()
    print(
        f"Finished scraping the homepage of fasel in about {round((time.time() - start_time) / 60)} minute(s)"
    )
else:
    pass
