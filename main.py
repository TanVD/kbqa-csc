import json

from deeppavlov import build_model

from api import search_google, print_search, search_wikipedia
from ner_model import ner

syntactic_model = build_model("ru_syntagrus_joint_parsing")
syntactic_model["main"].to_output_string = False
syntactic_model["main"].output_format = "json"


def syntactic(ner):
    tokens, ner_tokens = ner
    parsed = syntactic_model([tokens])[0]

    result = []
    seen = set()
    words = {}

    for i, value in enumerate(ner_tokens):
        synt_word = parsed[i]

        if value.startswith("B-"):
            seen.add(i)
            words[synt_word["id"]] = synt_word["lemma"]
            while synt_word["head"] != "0":
                cur_i = int(synt_word["head"]) - 1
                if synt_word["deprel"] not in {"nmod", "appos"}:
                    break
                synt_word = parsed[cur_i]
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

    words = {}

    for i, value in enumerate(ner_tokens):
        if i in seen:
            continue

        synt_word = parsed[i]

        if synt_word["upos"] in {"NOUN", "PROPN"}:
            seen.add(i)
            words[synt_word["id"]] = synt_word["lemma"]
            # Disabled since it provides pretty strange results
            # while synt_word["head"] != "0":
            #     cur_i = int(synt_word["head"]) - 1
            #     if synt_word["deprel"] not in {"nmod", "appos"}:
            #         break
            #     synt_word = parsed[cur_i]
            #     seen.add(cur_i)
            #
            #     words[synt_word["id"]] = (synt_word["lemma"])

            result.append(words)
            words = {}

    if len(words) != 0:
        result.append(words)

    return [entity for entity in result if len(entity) != 0]


questions = json.loads(open("/home/tanvd/CSC/ONTOLOGY_ITMO/data.json", "r").read())


def main():
    total_expected = 0

    total = 0
    total_correct = 0
    total_incorrect = 0
    for data in questions:
        question = data["q"]
        expected_ids = set(data["entities"])
        ids = set()
        print(question)
        entities = syntactic(ner(question))
        for entity in entities:
            query = " ".join([word for (_, word) in sorted(entity.items())])
            id = search_wikipedia(query)
            ids.update(id)

        ids_size = len(ids)
        correct_size = len(ids.intersection(expected_ids))
        incorrect_size = ids_size - correct_size
        total += ids_size
        total_correct += correct_size
        total_incorrect += incorrect_size

        print(f'CORRECT: {correct_size}')
        print(f'INCORRECT: {incorrect_size}')

        print()

    print(f"TOTAL CORRECT {total_correct}")
    print(f"TOTAL INCORRECT {total_incorrect}")


if __name__ == "__main__":
    main()
