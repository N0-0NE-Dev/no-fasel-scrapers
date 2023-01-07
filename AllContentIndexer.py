import json
from Common import FILE_NAMES


def main() -> None:
    all_content = []

    for name in FILE_NAMES:
        with open(f"./output/{name}.json", "r", encoding="utf-8") as file:
            data = json.load(file)

        all_content += [{"key": key,
                        "Title": data[key]["Title"],
                         "Image Source": data[key]["Image Source"],
                         "Category": data[key]["Category"]} for key in data]

    with open("./output/all-content.json", "w", encoding="utf-8") as fp:
        json.dump({"content": all_content}, fp, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
else:
    pass
