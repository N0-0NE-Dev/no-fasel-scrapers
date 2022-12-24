import requests
from requests import Response
from requests.exceptions import ConnectionError
from bs4 import BeautifulSoup
from Common import split_into_ranges


def get_website_safe(url: str) -> Response:
    response = None

    while response is None:
        try:
            response = requests.get(url)
        except ConnectionError:
            response = None

    return response


def get_last_page_number(url: str) -> int:
    main_page_source = get_website_safe(url)
    soup = BeautifulSoup(main_page_source.content, "html.parser")
    last_page = int(soup.find_all("a", class_="page-link")[-3].text)

    return last_page


def split_anchor_links(respone: Response) -> list[list[str]]:
    soup = BeautifulSoup(respone.content, "html.parser")
    anchor_tags = soup.find_all("a", class_="icn play")
    links = [tag["href"] for tag in anchor_tags]
    links_ranges = split_into_ranges(6, len(links))

    splitted_links = [links[links_range[0] - 1: links_range[1] - 1]
                      for links_range in links_ranges]

    return splitted_links
