import json
from Common import FILE_NAMES


def main() -> None:
    all_content = []

    for name in FILE_NAMES:
        with open(f"./output/{name}.json", "r", encoding="utf-8") as file:
            data = json.load(file)

        for key in data:
            if "Rating" in data[key]:
                rating = data[key]["Rating"]
            else:
                rating = "N/A"

            all_content += [{"key": key,
                            "Title": data[key]["Title"],
                             "Image Source": data[key]["Image Source"],
                             "Category": data[key]["Category"],
                             "Genres": data[key]["Genres"],
                             "Rating": rating
                             }]

    with open("./output/all-content.json", "w", encoding="utf-8") as fp:
        json.dump({"content": all_content}, fp, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
else:
    pass
