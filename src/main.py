import json

from src.api import search_wikipedia
from src.entity_extraction import extract_entity
from src.ner_model import ner
from src.query import get_types_of, QueryType, generate_request, get_request
from src.syntactic_model import syntactic

questions = json.loads(open("data.json", "r").read())


def main():
    results = []

    got = 0
    correct = 0

    for data in questions[:100]:
        question = data["question"]
        print(question)

        uid = data["uid"]
        answer = data.get("answer", [])

        ner_res = ner(question)
        synt_res = syntactic(ner_res)
        entities = extract_entity(ner_res, synt_res)

        ids = set()
        for entity in entities:
            query = " ".join([word for (_, word) in sorted(entity.items())])
            wiki_ids = search_wikipedia(query)
            ids.update([wiki_id for wiki_id in wiki_ids if wiki_id != "NOT FOUND"])

        question_types = get_types_of(synt_res)

        request = generate_request(question_types, ids)

        res = get_request(request)

        if len(res) != 0:
            got += 1

        if set(res) == set(answer) and answer:
            correct += 1

        if set(res) != set(answer) and answer:
            print(f'EXPECTED {json.dumps(answer)}, but got {json.dumps(res)}')

        results.append({
            "uid": uid,
            "question": question,
            "entities": list(ids),
            "type": [question_type.name for question_type in question_types],
            "request": request,
            "result": res
        })

    print(f'TOTAL FOUND {got}')
    print(f'TOTAL CORRECT {correct}')

    print(json.dumps(results, ensure_ascii=False))


if __name__ == "__main__":
    main()
