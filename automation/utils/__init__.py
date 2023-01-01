from .logger import logger
from .list_manip import ensure_list, list_to_or, or_to_list
from .dict_manip import sort_dict, flatten_embedded, filter_dict_by_key, load_yaml
from .md_utils import make_bullet, make_link, make_header

__all__ = [
    "logger",
    "ensure_list",
    "list_to_or",
    "or_to_list",
    "make_bullet",
    "make_link",
    "make_header",
    "sort_dict",
    "flatten_embedded",
    "filter_dict_by_key",
    "load_yaml",
    "list_attribs",
    "list_skills",
    "list_power_types",
]

list_attribs = ["AGL", "CON", "GUT", "INT", "STR", "VIT"]
list_skills = [
    "Finesse",
    "Stealth",
    "Bluffing",
    "Performance",
    "Knowledge",
    "Investigation",
    "Detection",
    "Craft",
    "Athletics",
    "Brute",
]
list_power_types = ["Passive", "Vulny", "Major", "Minor", "Adversary", "Free", "House"]
