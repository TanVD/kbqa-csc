import re


def is_banned(word):
    return word in {"страна", "город", "автор", "писатель"}


def is_proper_noun(word):
    return word["upos"] == "PROPN"


def is_noun(word):
    return word["upos"] == "NOUN"


def is_noun_modifier(word):
    return word["deprel"] in {"nmod", "appos"}


def filter_into(result, ner_tokens, parsed, seen, lambda_filter):
    words = {}
    for i, value in enumerate(ner_tokens):
        if i in seen:
            continue

        synt_word = parsed[i]

        if lambda_filter(synt_word) and not is_banned(synt_word["lemma"]):
            seen.add(i)
            words[synt_word["id"]] = synt_word["lemma"]

            result.append(words)
            words = {}

    if len(words) != 0:
        result.append(words)


def extract_quoted_part(query, result):
    obj = re.findall("\".*?\"", query)
    if obj:
        result.append({1: obj[0].strip('"')})
        return
    obj = re.findall("«.*?»", query)
    if obj:
        result.append({1: obj[0].strip('«').strip('»')})
    return


def extract_entity(query, ner_res, synt_res):
    tokens, ner_tokens = ner_res

    result = []
    seen = set()
    words = {}

    extract_quoted_part(query, result)

    if not result:
        for i, value in enumerate(ner_tokens):
            synt_word = synt_res[i]

            if value.startswith("B-"):
                seen.add(i)
                words[synt_word["id"]] = synt_word["lemma"]
                while synt_word["head"] != "0":
                    cur_i = int(synt_word["head"]) - 1
                    if not is_noun_modifier(synt_word):
                        break
                    synt_word = synt_res[cur_i]
                    seen.add(cur_i)
                    words[synt_word["id"]] = (synt_word["lemma"])
            elif value.startswith("I-"):
                seen.add(i)
                words[synt_word["id"]] = synt_word["lemma"]
            elif value == "O" and len(words) != 0:
                result.append(words)
                words = {}

        if len(words) != 0:
            result.append(words)

    if not result:
        filter_into(result, ner_tokens, synt_res, seen, is_proper_noun)

    if not result:
        filter_into(result, ner_tokens, synt_res, seen, is_noun)

    return [entity for entity in result if len(entity) != 0]
