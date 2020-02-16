from deeppavlov import build_model

syntactic_model = build_model("ru_syntagrus_joint_parsing")
syntactic_model["main"].to_output_string = False
syntactic_model["main"].output_format = "json"


def is_noun(word):
    return word["upos"] in {"NOUN", "PROPN"}


def is_noun_modifier(word):
    return word["deprel"] in {"nmod", "appos", "amod", "flat"}


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
                if not is_noun_modifier(synt_word):
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

        if is_noun(synt_word):
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
