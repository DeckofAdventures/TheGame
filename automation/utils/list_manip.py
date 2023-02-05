from collections import Iterable


def ensure_list(ambiguous_item):
    """If input is not a list, return list of input"""
    return ambiguous_item if isinstance(ambiguous_item, list) else [ambiguous_item]


def flatten_list(my_list):
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


def or_to_list(entry: str):
    """Given string, return list split by OR"""
    return entry.split(" or ")
