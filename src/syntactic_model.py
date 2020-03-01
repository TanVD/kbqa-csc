from deeppavlov import build_model

syntactic_model = build_model("ru_syntagrus_joint_parsing", download=True)
syntactic_model["main"].to_output_string = False
syntactic_model["main"].output_format = "json"


def syntactic(ner):
    tokens, ner_tokens = ner
    parsed = syntactic_model([tokens])[0]

    return parsed
