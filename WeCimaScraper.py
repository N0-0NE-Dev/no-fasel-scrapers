from Common import akwam_get_website_safe, split_into_ranges, remove_arabic_chars, DEBUG
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import json

with open("./output/WeCima.json", "r", encoding="Utf-8") as fp:
    old_series = json.load(fp)


def get_number_of_pages() -> int:
    page = akwam_get_website_safe("https://wecima.tube/download-series/")
    soup = BeautifulSoup(page.content, "html.parser")

    return int(soup.find("ul", "page-numbers").find_all("li")[-2].text)


def scrape_pages(page_range: tuple[int]) -> dict:
    content_dict = {}

    for page_number in range(page_range[0], page_range[1]):
        page = akwam_get_website_safe(
            f"https://wecima.tube/download-series/?page_number={page_number}/")
        soup = BeautifulSoup(page.content, "html.parser")
        divs = soup.find_all("div", class_="GridItem")

        for div in divs:
            div_id = div["cpd"]

            if div_id in old_series:
                continue
            else:
                anchor = div.find("a")

                source = anchor["href"].replace(
                    "https://wecima.tube/series/", "")

                season_number = remove_arabic_chars(anchor["title"])

                title = div.find("strong", class_="hasyear").text.split(
                    "-")[0].strip()

                image_source = div.find(
                    "span", "BG--GridItem")["data-lazy-style"].replace("--image:url(", "").replace(");", "")

                content_dict[div_id] = {
                    "Title": title,
                    "Image Source": image_source,
                    "Season Number": season_number,
                    "Source": source
                }

        if DEBUG:
            print(f"Done page {page_number}")
        else:
            pass

    return content_dict


def main() -> None:
    page_ranges = split_into_ranges(8, get_number_of_pages())

    if DEBUG:
        print(page_ranges)
    else:
        pass

    with ThreadPoolExecutor() as executor:
        results = executor.map(scrape_pages, page_ranges)

    for result in results:
        old_series.update(result)

    with open("./output/WeCima.json", "w", encoding="utf-8") as fp:
        json.dump(old_series, fp, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
else:
    pass
