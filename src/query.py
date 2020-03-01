import re
from enum import Enum

from qwikidata.sparql import return_sparql_query_results


class QueryType(Enum):
    # P276
    LOCATION = 276
    # P36
    CAPITAL = 36
    # P50
    AUTHOR = 50
    # P17
    COUNTRY = 17
    # P170
    CREATOR = 170
    UNKNOWN = 6


def get_types_of(synt_res):
    lemmas = {synt_word["lemma"] for synt_word in synt_res}

    if is_one_of(lemmas, [{"столица"}, {"какой", "город", "центр"}, {"как", "называться", "центр"}]):
        return [QueryType.CAPITAL, QueryType.LOCATION]
    elif is_one_of(lemmas, [{"в", "какой", "страна"}, {"какой", "страна"}, {"какой", "государство"}]):
        return [QueryType.COUNTRY, QueryType.LOCATION]
    elif is_one_of(lemmas, [{"в", "какой", "город"}, {"какой", "город"}]):
        return [QueryType.LOCATION, QueryType.COUNTRY]
    elif is_one_of(lemmas, [{"где"}, {"какой", "принадлежать"}, {"в", "какой"}]):
        return [QueryType.LOCATION, QueryType.COUNTRY]
    elif is_one_of(lemmas, [{"какой", "пролив"}, {"какой", "река"}, {"какой", "остров"}, {"какой", "озеро"}]):
        return [QueryType.LOCATION, QueryType.COUNTRY]

    elif is_one_of(lemmas, [{"создатель"}, {"автор"}, {"кто"}, {"какой", "придумать"}]):
        return [QueryType.AUTHOR, QueryType.CREATOR]

    return [QueryType.UNKNOWN]


def generate_requests(query_types, entities):
    if query_types[0] == QueryType.UNKNOWN:
        return []

    queries = []
    for query_type in query_types:
        where = " . ".join([f"wd:{entity} wdt:P{query_type.value} ?answer" for entity in entities])
        queries.append(f'SELECT ?answer WHERE {"{ " + where + " }"}')

    return queries


def get_request(request):
    if not request:
        return []

    try:
        response = return_sparql_query_results(request)
        results = response["results"]
        values = [result["answer"]["value"] for result in results.get("bindings", {})]
        return [re.findall("Q\\d+", value)[0] for value in values]
    except:
        print("Failed request")
        return []


def is_one_of(lemmas, sets):
    for cur in sets:
        if lemmas.issuperset(cur):
            return True
    return False
