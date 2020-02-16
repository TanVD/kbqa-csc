import json

from api import search_wikipedia
from ner_model import ner
from syntactic_model import syntactic

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
