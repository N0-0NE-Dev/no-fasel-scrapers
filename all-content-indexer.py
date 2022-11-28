import json


def main() -> None:
    PATHS = ["anime", "asian-series", "movies", "series", "tvshows"]
    all_content = []

    for path in PATHS:
        with open(f"./output/{path}.json") as file:
            data = json.load(file)

        all_content += [{"key": key,
                        "Title": data[key]["Title"],
                         "Image Source": data[key]["Image Source"],
                         "Category": data[key]["Category"]} for key in data]

    with open("./output/all-content.json", "w") as fp:
        json.dump({"content": all_content}, fp, indent=4)


if __name__ == "__main__":
    main()
else:
    pass
