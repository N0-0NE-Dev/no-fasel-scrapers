import json
from Common import FILE_NAMES
from os import remove, listdir


def main() -> None:
    for file in listdir("./output"):
        if ".jpg" in file or ".webp" in file:
            remove(f"./output/{file}")
        else:
            continue

    with open('./output/image-indices.json', 'r') as fp:
        image_indices = json.load(fp)

    for index, file in enumerate(FILE_NAMES):
        with open(f'./output/{file}.json', 'r', encoding='utf-8') as fp:
            content = json.load(fp)

        for key in content:
            if "arabic" in file:
                image_indices[key + "-akwam" +
                              file.split("-")[-1]] = content[key]["Image Source"]
            else:
                image_indices[key + "-fasel"] = content[key]["Image Source"]

            genres = content[key]["Genres"]

            if type(genres) == list:
                for genre in list(genres):
                    if "%" in genre or genre == "/":
                        genres.remove(genre)
                    else:
                        continue

                content[key]["Genres"] = genres
            else:
                pass

        if index in range(2, 5):
            for key in list(content.keys()):
                if len(content[key]["Seasons"]) == 0:
                    del content[key]
                else:
                    continue

        elif index == 0:
            for key in list(content.keys()):
                if content[key]["Source"] == "":
                    del content[key]
                else:
                    continue

        else:
            pass

        with open(f'./output/{file}.json', 'w', encoding='utf-8') as fp:
            json.dump(content, fp, indent=4, ensure_ascii=False)

    with open('./output/image-indices.json', 'w', encoding='utf-8') as fp:
        json.dump(image_indices, fp, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    main()
else:
    pass
