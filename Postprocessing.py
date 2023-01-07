import json
from Common import FILE_NAMES
import hashlib


def main() -> None:
    hashes_dict = {}

    with open('./output/image-indices.json', 'r') as fp:
        image_indices = json.load(fp)

    for index, file in enumerate(FILE_NAMES):
        with open(f'./output/{file}.json', 'r', encoding='utf-8') as fp:
            content = json.load(fp)

            hashes_dict[file] = hashlib.md5(
                json.dumps(content).encode("utf-8")).hexdigest()

        for key in content:
            if "arabic" in file:
                image_indices[key + "-akwam" +
                              file.split("-")[-1]] = content[key]["Image Source"]
            else:
                image_indices[key + "-fasel"] = content[key]["Image Source"]

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

    with open("./output/hashes.json", "w") as fp:
        json.dump(hashes_dict, fp, indent=4)


if __name__ == '__main__':
    main()
else:
    pass
