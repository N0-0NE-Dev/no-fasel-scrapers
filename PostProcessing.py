import json


def main() -> None:
    file_names: list[str] = [
        'anime', 'asian-series', 'movies', 'series', 'tvshows']

    with open('./output/image-indices.json', 'r') as fp:
        image_indices = json.load(fp)

    for file in file_names:
        with open(f'./output/{file}.json', 'r') as fp:
            content = json.load(fp)

        for key in content:
            image_indices[key] = content[key]["Image Source"]

        if file in ['asian-series', 'series', 'tvshows']:
            for key in list(content.keys()):
                if len(content[key]["Seasons"]) == 0:
                    del content[key]
                else:
                    continue

            with open(f'./output/{file}.json', 'w') as fp:
                json.dump(content, fp, indent=4)
        else:
            pass

    with open('./output/image-indices.json', 'w') as fp:
        json.dump(image_indices, fp, indent=4)


if __name__ == '__main__':
    main()
else:
    pass
