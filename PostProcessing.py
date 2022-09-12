import json


def main():
    file_names = ['anime', 'asian-series', 'movies', 'series', 'tvshows']

    with open('./output/image_indices.json', 'r') as fp:
        image_indices = json.load(fp)

    for file in file_names:
        with open(f'./output/{file}.json', 'r') as fp:
            content = json.load(fp)

        for key in content:
            image_indices[key] = content[key]["Image Source"]

        if file == 'series':
            for key in list(content.keys()):
                if len(content[key]["Seasons"]) == 0:
                    del content[key]
                else:
                    continue

            with open('./output/series.json', 'w') as fp:
                json.dump(content, fp)

    with open('./output/image_indices.json', 'w') as fp:
        json.dump(image_indices, fp)


if __name__ == '__main__':
    main()
else:
    pass
