import yaml
from operator import attrgetter
from collections import OrderedDict
from .list_manip import list_to_or

from dataclasses import fields


def my_repr(self):
    nodef_f_vals = (
        (f.name, attrgetter(f.name)(self))
        for f in fields(self)
        if attrgetter(f.name)(self) != f.default and f.repr
    )
    nodef_f_repr = "\n".join(f"{name}={value}" for name, value in nodef_f_vals)
    return f"{self.__class__.__name__}({nodef_f_repr})"


def load_yaml(input_yaml: str):
    """Load the yaml file"""
    with open(input_yaml, encoding="utf8") as f:
        data = yaml.safe_load(f)
    return data


def sort_dict(my_dict, my_list):
    """Sort dict by list of keys. Return OrderedDict"""
    index_map = {v: i for i, v in enumerate(my_list)}
    my_dict_reduced = {k: v for k, v in my_dict.items() if k in my_list}
    return OrderedDict(
        sorted(my_dict_reduced.items(), key=lambda pair: index_map[pair[0]])
    )


def flatten_embedded(input_dict) -> dict:
    """Check vals in input. If dict, make embedded values new keys in output dict

    Novel keys in output dict are {'key_embedded-key': 'embedded_value'}

    Args:
        input_dict (dict): any dict

    Returns:
        output_dict (dict)
    """
    output = {}
    for k, v in input_dict.items():
        if isinstance(v, dict):
            output.update(
                {
                    f"{k}_{embed_k}": list_to_or(embed_v)
                    for embed_k, embed_v in v.items()
                }
            )
        else:
            output.update({k: v})
    return output


def filter_dict_by_key(
    dict_content: dict,
    key_filter: str = "Type",
    key_options: set = None,
) -> dict:
    """Filter an embedded dict by if values of key_filter in listed key_options

    Example:
        my_dict = {"a": {"b": 1}, "c": {"b": 2}, "d": {"b": 3}}
        filter_dict_by_key(dict_content=my_dict,key_filter="b",key_options=[1,2])
        >> {'a': {'b': 1}, 'c': {'b': 2}}

    Args:
        dict_content (dict): Input dict
        key_options (list): Set of items that, when retyped to list must match
            value[list_filter].
        key (str): Optional specification of key. Default "Type"

    Returns:
        dict: filtered dict
    """
    if not key_options:
        return dict_content
    return {
        key: value
        for (key, value) in dict_content.items()
        if value[key_filter] == list(key_options)
    }
