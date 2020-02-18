import json

from src.api import search_wikipedia
from src.ner_model import ner
from src.syntactic_model import syntactic

questions = json.loads(open("data.json", "r").read())


def main():
    results = []

    total_expected = 0

    total = 0
    total_correct = 0
    total_incorrect = 0
    for data in questions:
        question = data["q"]
        uid = data["uid"]
        expected_ids = set(data["entities"])
        total_expected += len(expected_ids)
        ids = set()
        print(question)
        entities = syntactic(ner(question))
        for entity in entities:
            query = " ".join([word for (_, word) in sorted(entity.items())])
            wiki_ids = search_wikipedia(query)
            ids.update([wiki_id for wiki_id in wiki_ids if wiki_id != "NOT FOUND"])

        ids_size = len(ids)
        correct_size = len(ids.intersection(expected_ids))
        incorrect_size = ids_size - correct_size
        total += ids_size
        total_correct += correct_size
        total_incorrect += incorrect_size

        results.append({
            "uid": uid,
            "entities": list(ids)
        })

        print(f'EXPECTED: {len(expected_ids)}')
        print(f'CORRECT: {correct_size}')
        print(f'INCORRECT: {incorrect_size}')

        print()

    print(f'TOTAL EXPECTED: {total_expected}')

    print(f"TOTAL CORRECT {total_correct}")
    print(f"TOTAL INCORRECT {total_incorrect}")

    print(json.dumps(results))


if __name__ == "__main__":
    main()
