input_files = ["04_Powers.yml", "05_Vulnerabilities.yml"]  # edit this, permits multiple
writing = ["md"]  # , "dot", "png", "csv", "svg"]  #         # list of options
add_dependencies = ["Skill"]  # "Skill", "Level", "Role"]  # # list of options
add_loners = False  #                                   # Include items without links?
out_delim = "\t"  #                                     # delimiter for csv

import pydot
from collections import OrderedDict
import csv, yaml, logging, os, pathlib
import logging

# logging
logging.basicConfig(
    level=os.environ.get(
        "LOG_LEVEL", "info"
    ).upper(),  # debug, info, warning, error, critical
    format="[%(asctime)s][%(funcName)-8s][%(levelname)-8s]: %(message)s",
    datefmt="%H:%M:%S",
)


class Powers(object):
    def __init__(self, input_files):
        """Initialize"""
        self._data = {}
        input_files = input_files if isinstance(input_files, list) else [input_files]
        for input_file in input_files:
            self._data.update(load_source(input_file))
        self._data.pop("Template")
        self._readable_dict = {}
        self._stem = os.path.splitext(os.path.basename(input_files[-1]))[0]
        self._name = self._stem.split("_")[-1]

    def save_check_to_txt(self, save: dict):
        """Given a Save dict, return a sentence"""
        sentence = save["Trigger"] + ", target(s) make a "
        sentence += "DR " + str(save["DR"]) + " " if "DR" in save else ""
        sentence += list_to_or(save["Type"]) + " Save"
        output = [sentence, "On fail, target(s) " + save["Fail"]]
        output.append(
            "On success, target(s) " + save["Succeed"]
        ) if "Succeed" in save else None
        return ". ".join(output)

    def merge_mechanics(self, power):
        """Given power dict, merge all appropriate items into Mechanic"""
        if isinstance(power["Mechanic"], list):  # when mech are list, indent after 1st
            mech_bullets = power["Mechanic"][0] + "\n"
            for mech_bullet in power["Mechanic"][1:]:
                mech_bullets += make_bullet(mech_bullet)
            power["Mechanic"] = mech_bullets[:-1]  # remove last space
        mechanic = (
            ("For " + list_to_or(power["PP"]) + " PP, " + power["Mechanic"] + ". ")
            if "PP" in power
            else power["Mechanic"]
        )
        if "Save" in power:
            mechanic += self.save_check_to_txt(power["Save"]) + ". "
        power["Mechanic"] = "".join([power["Type"], ". ", mechanic])
        power.pop("Save", None)
        return power

    def flatten_embedded(self, input_dict):
        """Given embedded dictionary, concat keys for values"""
        output = {}
        for k, v in input_dict.items():
            if isinstance(v, dict):  # and k != "Save":
                output.update(
                    {f"{k}_{embed_k}": embed_v for embed_k, embed_v in v.items()}
                )
            else:
                output.update({k: v})
        return output

    def readable_dict(self, limit_types=None):
        """Return readable dict with Mechanics collapsed. Limit by limit_types list"""
        if not limit_types:
            limit_types = ["Major", "Minor", "Passive", "Adversary", "House", "Vulny"]
        if not self._readable_dict:
            self._readable_dict = {
                power: {
                    **self.flatten_embedded(self.merge_mechanics(traits)),
                }
                for (power, traits) in self._data.items()
                if traits["Type"] in limit_types
            }

        return self._readable_dict

    def categories(self):
        """Return set of tuples: (categories, subcategories)"""
        categories = set()  # category: sub pairing
        for v in self._data.values():  # get set of sub/categories for TOC later
            categories.add(tuple(v["Category"]))
        return categories


class Markdown(object):
    def __init__(self, input_files, limit_types=None):
        """Initialize. Input yml."""
        self._data = {}
        self._categories = set()
        input_files = input_files if isinstance(input_files, list) else [input_files]
        for input_file in input_files:
            powers_input = Powers(input_file)
            self._data.update(powers_input.readable_dict())
            self._categories.update(powers_input.categories())
            self._stem = powers_input._stem  # if passing list, default last
            self._name = powers_input._name

    def write(self, output_fp=None, title=None):
        """Write markdown"""
        if not output_fp:
            output_fp = "./_Automated_output/" + self._stem + ".md"
        with open(output_fp, "w", newline="") as f:
            f.write(
                f"""# {self._name}\n
                <!-- DEVELOPERS: Please edit corresponding yaml in 3_Automation -->\n
                """
            )


class Dot(object):
    pass


def main():
    logging.info("Strarted")


# ---- Helper ----


def load_source(input_yml="04_Powers.yml"):
    """Load the yaml file"""
    with open(input_yml, encoding="utf8") as f:
        data = yaml.safe_load(f)
    return data


def list_to_or(entry):
    """Given string or list, return with joined OR"""
    entry = [entry] if not isinstance(entry, list) else entry
    entry = [str(i) for i in entry]
    return " or ".join(entry)


def sort_dict(my_dict, my_list):
    """Sort dict by list of keys. Return OrderedDict"""
    # NOTE: Currently unused. Consider passing ordered do
    index_map = {v: i for i, v in enumerate(my_list)}
    return OrderedDict(sorted(my_dict.items(), key=lambda pair: index_map[pair[0]]))


def make_bullet(value, indents=0):
    """Return string with 4 spaces per indent, plus '- '"""
    spaces = indents * "    "
    return f"{spaces}- {value}\n"
