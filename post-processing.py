import json


def main() -> None:
    FILE_NAMES = ['movies', 'anime', 'asian-series', 'series', 'tvshows']

    with open('./output/image-indices.json', 'r') as fp:
        image_indices = json.load(fp)

    for index, file in enumerate(FILE_NAMES):
        with open(f'./output/{file}.json', 'r') as fp:
            content = json.load(fp)

        for key in content:
            image_indices[key] = content[key]["Image Source"]

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

        with open(f'./output/{file}.json', 'w') as fp:
            json.dump(content, fp, indent=4)
        
    with open('./output/image-indices.json', 'w') as fp:
        json.dump(image_indices, fp, indent=4)


if __name__ == '__main__':
    main()
else:
    pass
