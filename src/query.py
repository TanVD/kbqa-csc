from enum import Enum


class QueryType(Enum):
    # P276
    LOCATION = 1
    # P36
    CAPITAL = 2
    # P50
    AUTHOR = 3
    # P17
    COUNTRY = 4
    # P170
    CREATOR = 5
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


def is_one_of(lemmas, sets):
    for cur in sets:
        if lemmas.issuperset(cur):
            return True
    return False
