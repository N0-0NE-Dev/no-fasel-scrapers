import json


def update_indicies():
    file_names = ['anime', 'asian-series', 'movies', 'series', 'tvshows']
    image_indices = {}
    for file in file_names:
        with open(f'./output/json/{file}.json', 'r') as fp:
            content = json.load(fp)

        for key in content:
            image_indices[key] = content[key]["Image Source"]

    with open('./output/json/image-index.json', 'w') as fp:
        json.dump(image_indices, fp)
