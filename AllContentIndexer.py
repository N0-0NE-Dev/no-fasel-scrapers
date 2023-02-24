import json
from Common import FILE_NAMES, HDW_FILE_NAMES


def main() -> None:
    file_name_lists = [FILE_NAMES, HDW_FILE_NAMES]

    for index, name_list in enumerate(file_name_lists):
        all_content = []

        for name in name_list:
            with open(f"./output/{name}.json", "r", encoding="utf-8") as file:
                data = json.load(file)

            for key in data:
                if "Rating" in data[key]:
                    rating = data[key]["Rating"]
                else:
                    rating = "N/A"

                if "Genres" in data[key]:
                    genres = data[key]["Genres"]
                else:
                    genres = []

                all_content += [{"key": key,
                                "Title": data[key]["Title"],
                                 "Image Source": data[key]["Image Source"],
                                 "Category": data[key]["Category"],
                                 "Genres": genres,
                                 "Rating": rating
                                 }]

            if index == 0:
                output_file = "all-content"
            else:
                output_file = "hdw-all-content"

            with open(f"./output/{output_file}.json", "w", encoding="utf-8") as fp:
                json.dump({"content": all_content}, fp,
                          indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
else:
    pass
