import requests
from requests import Response
from requests.exceptions import ConnectionError
from bs4 import BeautifulSoup
from Common import split_into_ranges
from typing import Union


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


def get_genres(soup: BeautifulSoup) -> Union[list[str], str]:
    genres_dict = {
        "87": "Ramadan",
        "30": "Animated",
        "18": "Action",
        "71": "Dubbed",
        "72": "Netflix",
        "20": "Comedy",
        "35": "Thriller",
        "34": "Mystery",
        "33": "Family",
        "88": "Kids",
        "32": "Sports",
        "25": "War",
        "89": "Short",
        "43": "Fantasy",
        "24": "Science Fiction",
        "31": "Musical",
        "29": "Biography",
        "28": "Documentary",
        "27": "Romance",
        "26": "History",
        "23": "Drama",
        "22": "Horror",
        "21": "Crime",
        "19": "Adventure",
        "91": "Western"
    }

    genre_tags = soup.find_all("a", class_="badge badge-pill badge-light ml-2")

    try:
        genre_ids = [tag["href"].split("=")[-1] for tag in genre_tags]
    except TypeError:
        return "N/A"

    genres = [genres_dict[key] for key in genre_ids]

    return genres
