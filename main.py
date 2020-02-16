import json
import re
import string

import requests
from deeppavlov import configs, build_model
from googlesearch import search

syntactic_model = build_model("ru_syntagrus_joint_parsing")
syntactic_model["main"].to_output_string = False
syntactic_model["main"].output_format = "json"

ner_model = build_model(configs.ner.ner_rus_bert)


def ner(query):
    return ner_model([query])[1][0]


def syntactic(query, ner):
    parsed = syntactic_model([query])[0]

    result = []
    seen = set()
    words = {}

    for i, value in enumerate(ner):
        if i >= len(parsed):
            result.append(words)
            break

        synt_word = parsed[i]

        if synt_word["word"] in {"?", ".", "!"} and synt_word["lemma"] == "PUNCT":
            result.append(words)
            break

        if value.startswith("B-"):
            seen.add(i)
            words[synt_word["id"]] = synt_word["lemma"]
            while synt_word["head"] != "0":
                cur_i = int(synt_word["head"]) - 1
                seen.add(cur_i)
                synt_word = parsed[cur_i]
                if synt_word["upos"] not in {"NOUN", "PROPN", "ADJ"}:
                    break
                words[synt_word["id"]] = (synt_word["lemma"])

        elif value.startswith("I-"):
            seen.add(i)
            words[synt_word["id"]] = synt_word["lemma"]
        elif value == "O" and len(words) != 0:
            result.append(words)
            words = {}

    words = {}
    for i, value in enumerate(ner):
        if i >= len(parsed):
            break

        if i in seen:
            continue

        synt_word = parsed[i]

        if synt_word["upos"] in {"NOUN", "PROPN"}:
            seen.add(i)
            words[synt_word["id"]] = synt_word["lemma"]
            while synt_word["head"] != "0":
                cur_i = int(synt_word["head"]) - 1
                seen.add(cur_i)
                synt_word = parsed[cur_i]
                if synt_word["upos"] not in {"NOUN", "PROPN", "ADJ"}:
                    break
                words[synt_word["id"]] = (synt_word["lemma"])

            result.append(words)
            words = {}

        if synt_word["word"] in {"?", ".", "!"} and synt_word["lemma"] == "PUNCT":
            break

    return [entity for entity in result if len(entity) != 0]


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

    for res in search(query=query, lang="ru", domains=["ru.wikipedia.org"]):
        cur += 1
        page = res[len("https://ru.wikipedia.org/wiki/"):]
        wikidata_id = get_wikidata_ids(page)
        print(query)
        print(wikidata_id)
        if cur >= max_records:
            break


questions = json.loads(open("/home/tanvd/CSC/ONTOLOGY_ITMO/data.json", "r").read())


def main():
    for data in questions:
        question = data["q"]
        print(question)
        entities = syntactic(question, ner(question))
        for entity in entities:
            query = " ".join([word for (_, word) in sorted(entity.items())])
            search_google(query)
        print()


# https://en.wikipedia.org/w/api.php?action=query&prop=pageprops&titles=Kofoworola_Abeni_Pratt&format=json

if __name__ == "__main__":
    main()
