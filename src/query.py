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


def get_type_of(synt_res):
    lemmas = {synt_word["lemma"] for synt_word in synt_res}
    if is_one_of(lemmas, [{"где"}, {"какой", "принадлежит"}]):
        return QueryType.LOCATION
    elif is_one_of(lemmas, [{"столица"}, {"какой", "город"}]):
        return QueryType.CAPITAL
    elif is_one_of(lemmas, [{"страна", "какой"}]):
        return QueryType.COUNTRY
    elif is_one_of(lemmas, [{"создатель"}, {"кто", "создать"}]):
        return QueryType.CREATOR
    elif is_one_of(lemmas, [{"автор"}, {"кто", "придумать"}, {"какой", "придумать"}, {"кто", "написать"}]):
        return QueryType.AUTHOR

    return QueryType.UNKNOWN


def generate_request(query_type, entities):
    if query_type == QueryType.UNKNOWN:
        return ""

    where = " . ".join([f"wd:{entity} wdt:P{query_type.value} ?answer" for entity in entities])
    return f'SELECT ?answer WHERE {"{ " + where + " }"}'


def get_request(request):
    if not request:
        return ""

    response = return_sparql_query_results(request)
    results = response["results"]
    values = [result["answer"]["value"] for result in results.get("bindings", {})]
    return [re.findall("Q\\d+", value)[0] for value in values]


def is_one_of(lemmas, sets):
    for cur in sets:
        if lemmas.issuperset(cur):
            return True
    return False
