from Common import *
from bs4 import BeautifulSoup
from time import perf_counter
import requests
import json
from difflib import get_close_matches

content_dict = {'movies': {}, 'asian-series': {},
                'anime': {}, 'series': {}, "arabic-series": {},
                "arabic-movies": {}}

featured_content_dict = {"content": []}


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
    get_cookies(FASEL_BASE_URL, (By.CLASS_NAME, "logo.ml-3"))
    home_page = get_website_safe(FASEL_BASE_URL)
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

                if "Rating" in content_file[key]:
                    rating = content_file[key]["Rating"]
                else:
                    rating = "N/A"

                if "TMDb ID" in content_file[key]:
                    tmdb_id = content_file[key]["TMDb ID"]
                else:
                    tmdb_id = None

                content_dict[content_category].update(
                    {key: {
                        "Title": content_file[key]["Title"],
                        "Image Source": content_file[key]["Image Source"],
                        "Category": content_category,
                        "Genres": content_file[key]["Genres"],
                        "Rating": rating,
                        "TMDb ID": tmdb_id
                    }})

                break
            else:
                continue

    with open("./output/movies.json", "r") as fp:
        movies = json.load(fp)

    for div in featured_content:
        movie_page = get_website_safe(div.find("a")["href"])

        movie_id = get_content_id(BeautifulSoup(
            movie_page.content, "html.parser"))

        if "Genres" in movies[movie_id]:
            genres = movies[movie_id]["Genres"]
        else:
            genres = []

        if "Rating" in movies[movie_id]:
            rating = movies[movie_id]["Rating"]
        else:
            rating = "N/A"

        try:
            featured_content_dict["content"].append({
                "key": movie_id,
                "Title": movies[movie_id]["Title"],
                "Image Source": movies[movie_id]["Image Source"],
                "Category": movies[movie_id]["Category"],
                "Genres": genres,
                "Rating": rating,
                "TMDb ID": movies[movie_id]["TMDb ID"]
            })

        except KeyError:
            continue

    with open("./output/featured-content.json", "w") as fp:
        json.dump(featured_content_dict, fp, indent=4)


def hdw_featured():
    featured = {"content": []}

    with open("./output/featured-content.json", "r") as fp:
        featured_content = json.load(fp)

    with open("./output/hdwmovies.json", "r") as fp:
        movies = json.load(fp)

    names = {movies[key]["Title"]: key for key in movies}

    for movie in featured_content["content"]:
        closest_match = names[get_close_matches(
            movie["Title"], list(names.keys()))[0]]

        if "Genres" in movies[closest_match]:
            genres = movies[closest_match]["Genres"]
        else:
            genres = []

        if "Rating" in movies[closest_match]:
            rating = movies[closest_match]["Rating"]
        else:
            rating = "N/A"

        featured["content"].append({
            "key": closest_match,
            "Title": movies[closest_match]["Title"],
            "Image Source": movies[closest_match]["Image Source"],
            "Category": movies[closest_match]["Category"],
            "Genres": genres,
            "Rating": rating,
            "TMDb ID": movies[closest_match]["TMDb ID"]
        })

        with open("./output/hdw-featured-content.json", "w") as fp:
            json.dump(featured, fp, indent=4)


def hdw_trending():
    trending = {"hdwmovies": {}, "hdwseries": {}}

    with open("./output/trending-content.json", "r", encoding="utf-8") as fp:
        trending_content = json.load(fp)

    trending["arabic-series"] = trending_content["arabic-series"]
    trending["arabic-movies"] = trending_content["arabic-movies"]

    with open("./output/hdwmovies.json", "r") as fp:
        movies = json.load(fp)

    with open("./output/hdwseries.json", "r") as fp:
        series = json.load(fp)

    trending_movie_names = {
        trending_content["movies"][key]["Title"]: key for key in trending_content["movies"]}

    trending_series_names = {
        trending_content["series"][key]["Title"]: key for key in trending_content["series"]}

    movie_names = {movies[key]["Title"]: key for key in movies}

    series_names = {series[key]["Title"]: key for key in series}

    for name in trending_movie_names:
        try:
            matches = get_close_matches(name, movie_names)
            closest_match = movie_names[matches[0]]
        except IndexError:
            continue

        trending["hdwmovies"][closest_match] = {
            "key": closest_match,
            "Title": movies[closest_match]["Title"],
            "Image Source": movies[closest_match]["Image Source"],
            "Category": movies[closest_match]["Category"],
            "Genres": movies[closest_match]["Genres"],
            "Rating": movies[closest_match]["Rating"],
            "TMDb ID": movies[closest_match]["TMDb ID"]
        }

    for name in trending_series_names:
        try:
            matches = get_close_matches(name, series_names)
            closest_match = series_names[matches[0]]
        except IndexError:
            continue

        trending["hdwseries"][closest_match] = {
            "key": closest_match,
            "Title": series[closest_match]["Title"],
            "Image Source": series[closest_match]["Image Source"],
            "Category": series[closest_match]["Category"],
            "Genres": series[closest_match]["Genres"],
            "Rating": series[closest_match]["Rating"],
            "TMDb ID": series[closest_match]["TMDb ID"]
        }

    with open("./output/hdw-trending-content.json", "w", encoding="utf-8") as fp:
        json.dump(trending, fp, indent=4, ensure_ascii=False)


def main() -> None:
    scrape_fasel()
    scrape_akwam()

    with open("./output/trending-content.json", "w", encoding="utf-8") as fp:
        json.dump(content_dict, fp, indent=4, ensure_ascii=False)

    hdw_featured()
    hdw_trending()


if __name__ == "__main__":
    start_time = perf_counter()
    main()
    end_time = perf_counter()
    print(
        f"Finished scraping the trending content in about {round((end_time - start_time) / 60)} minute(s)"
    )
else:
    pass
