from Common import *
from bs4 import BeautifulSoup

get_cookies()
main_page = get_website_safe('https://www.faselhd.club/home3')
soup = BeautifulSoup(main_page.content, 'html.parser')

new_content = soup.find_all('div', 'blockMovie')
new_content += soup.find_all('div', 'epDivHome')

content_dict = {'movies': [], 'asian-series': [], 'anime': [], 'series': []}
for element in new_content:
    link = element.find('a')['href']

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

    content_page = get_website_safe(link)
    soup = BeautifulSoup(content_page.content, 'html.parser')
    content_id = get_content_id(soup)

    with open(f'./output/{content_category}.json', 'r') as fp:
        content_file = json.load(fp)

    try:
        content = content_file[content_id]
        content_dict[content_category].append(
            {content_id: {"Title": content["Title"], "Format": content["Format"], "Image Source": content["Image Source"]}})
    except KeyError:
        continue

with open('./output/trending-content.json', 'w') as fp:
    json.dump(content_dict, fp)
