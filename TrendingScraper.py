import re
from Common import *
from bs4 import BeautifulSoup

get_cookies()
main_page = get_website_safe('https://www.faselhd.club/home3')
soup = BeautifulSoup(main_page.content, 'html.parser')

new_content = soup.find_all('div', 'blockMovie')
new_content += soup.find_all('div', 'epDivHome')

content_dict = {'movies': [], 'asian-series': [], 'anime': [], 'series': []}
seen = []

for element in new_content:
    link = element.find('a')['href']

    content_page = get_website_safe(link)
    soup = BeautifulSoup(content_page.content, 'html.parser')

    content_title = remove_year(remove_arabic_chars(
        soup.find('div', class_='h3').text.split('-')[0]).strip())

    content_title = re.split(r'\s{2,}', content_title)[0]

    if DEBUG:
        print(content_title)
    else:
        pass

    if '%d9%81%d9%8a%d9%84%d9%85' in link:
        content_category = 'movies'
    elif 'asian-episodes' in link:
        content_category = 'asian-series'
    elif 'anime-episodes' in link:
        content_category = 'anime'
    else:
        content_category = 'series'

    if DEBUG:
        print(link, content_category)
    else:
        pass

    with open(f'./output/{content_category}.json', 'r') as fp:
        content_file = json.load(fp)

    for key in content_file:
        current_element = content_file[key]
        if (current_element["Title"] == content_title) and (key not in seen):
            seen.append(key)
            content_dict[content_category].append(
                {key: {"Title": current_element["Title"], "Format": current_element["Format"], "Image Source": current_element["Image Source"]}})
            break
        else:
            continue

with open('./output/trending-content.json', 'w') as fp:
    json.dump(content_dict, fp, indent=4)
