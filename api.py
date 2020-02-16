import re

import requests
from googlesearch import search


def get_wikidata_ids(title):
    url = f"https://ru.wikipedia.org/w/api.php?action=query&prop=pageprops&titles={title}&format=json"
    res = str(requests.get(url).content)
    obj = re.findall("Q\\d+", res)

    if len(obj) != 1:
        print("GOT STRANGE RESULT" + str(res))
        return "NOT FOUND"

    return obj[0]


def search_wikipedia(query):
    session = requests.Session()

    url = "https://ru.wikipedia.org/w/api.php"

    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": query
    }

    result = session.get(url=url, params=params)
    data = result.json()

    search = data['query']['search']
    if len(search) == 0:
        return {"Not found"}

    title = search[0]['title']
    id = get_wikidata_ids(title)
    return {id}


def search_google(query, max_records=1):
    cur = 1

    ids = set()

    for res in search(query=query,
                      domains=["ru.wikipedia.org"],
                      num=1,
                      stop=2,
                      pause=2.0,
                      user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36"):
        cur += 1
        page = res[len("https://ru.wikipedia.org/wiki/"):]
        wikidata_id = get_wikidata_ids(page)
        print(query)
        print(wikidata_id)
        ids.add(wikidata_id)
        if cur >= max_records:
            break

    return ids


def print_search(query, max_records=1):
    print(query)
