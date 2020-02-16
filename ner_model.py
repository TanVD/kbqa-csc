from deeppavlov import configs, build_model

ner_model = build_model(configs.ner.ner_rus_bert)


def ner(query):
    return [lst[0] for lst in ner_model([query])]
