from typing import Generator, Iterable


def ensure_list(ambiguous_item):
    """If input is not a list, return list of input"""
    return ambiguous_item if isinstance(ambiguous_item, list) else [ambiguous_item]


def flatten_list(my_list) -> Generator:
    """For a list containing embedded lists, generate 1d list with no 'None' vals"""
    for item in my_list:
        if not item:
            continue
        if isinstance(item, Iterable) and not isinstance(item, str):
            for x in flatten_list(item):
                yield x
        else:
            yield item


def list_to_or(entry):
    """Given string or list, return items as string joined OR"""
    entry = [entry] if not isinstance(entry, list) else entry
    entry = [str(i) for i in entry]
    return " or ".join(entry)
