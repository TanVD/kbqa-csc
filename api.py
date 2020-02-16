import re

import requests
from googlesearch import search


def get_wikidata_ids(page):
    url = f"https://ru.wikipedia.org/w/api.php?action=query&prop=pageprops&titles={page}&format=json"
    res = str(requests.get(url).content)
    obj = re.findall("Q\\d+", res)

    if len(obj) != 1:
        print("GOT STRANGE RESULT" + str(res))
        return "NOT FOUND"

    return obj[0]


def search_google(query, max_records=1):
    cur = 1

    for res in search(query=query, lang="ru", domains=["ru.wikipedia.org"], pause=5.0):
        cur += 1
        page = res[len("https://ru.wikipedia.org/wiki/"):]
        wikidata_id = get_wikidata_ids(page)
        print(query)
        print(wikidata_id)
        if cur >= max_records:
            break


def print_search(query, max_records=1):
    print(query)
