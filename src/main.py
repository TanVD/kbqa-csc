import json

from src.api import search_wikipedia
from src.entity_extraction import extract_entity
from src.ner_model import ner
from src.query import get_type_of
from src.syntactic_model import syntactic

questions = json.loads(open("data.json", "r").read())


def main():
    results = []

    for data in questions[:100]:
        question = data["question"]
        uid = data["uid"]
        ids = set()
        print(question)
        ner_res = ner(question)
        synt_res = syntactic(ner_res)
        entities = extract_entity(ner_res, synt_res)
        for entity in entities:
            query = " ".join([word for (_, word) in sorted(entity.items())])
            wiki_ids = search_wikipedia(query)
            ids.update([wiki_id for wiki_id in wiki_ids if wiki_id != "NOT FOUND"])

        question_type = get_type_of(synt_res)

        results.append({
            "uid": uid,
            "question": question,
            "entities": list(ids),
            "type": question_type.name
        })

    print(json.dumps(results, ensure_ascii=False))


if __name__ == "__main__":
    main()
