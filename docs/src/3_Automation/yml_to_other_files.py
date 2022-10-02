"""
Takes yml files as input, can generate a series of other files, including
    Markdown - includes table of contents and links
    CSV      - defaults to tab delimited
    dot      - flow char instruction format
    PNG/SVG  - for rendering flow charts
"""
input_files = ["04_Powers.yml", "05_Vulnerabilities.yml"]  # edit this, permits multiple
writing = ["md", "dot", "png", "csv", "svg"]  #         # list of options
dependencies = ["Skill"]  # "Skill", "Level", "Role"]  # # list of options
add_loners = False  #                                   # Include items without links?
out_delim = "\t"  #                                     # delimiter for csv

import pydot
import logging
from collections import OrderedDict
import csv, yaml, logging, os, pathlib

logging.basicConfig(
    level=os.environ.get(
        "LOG_LEVEL", "info"
    ).upper(),  # debug, info, warning, error, critical
    format="[%(asctime)s][%(funcName)-8s][%(levelname)-8s]: %(message)s",
    datefmt="%H:%M:%S",
)


# ---- Helper ----
# TODO: move to utils script? Make helper class?


def load_source(input_yml="04_Powers.yml"):
    """Load the yaml file"""
    with open(input_yml, encoding="utf8") as f:
        data = yaml.safe_load(f)
    return data


def ensure_list(item):
    return item if isinstance(item, list) else [item]


def list_to_or(entry):
    """Given string or list, return with joined OR"""
    entry = [entry] if not isinstance(entry, list) else entry
    entry = [str(i) for i in entry]
    return " or ".join(entry)


def or_to_list(entry: str):
    """Given string, return list split by OR"""
    return entry.split(" or ")


def sort_dict(my_dict, my_list):
    """Sort dict by list of keys. Return OrderedDict"""
    index_map = {v: i for i, v in enumerate(my_list)}
    return OrderedDict(sorted(my_dict.items(), key=lambda pair: index_map[pair[0]]))


def sort_power(power_dict):
    """Given a power, return OrderedDict in markdown read order"""
    if "Prereq" in power_dict:
        power_dict["Prereq"] = sort_dict(
            power_dict["Prereq"], ["Role", "Level", "Skill", "Power"]
        )
    if "Save" in power_dict:
        power_dict["Save"] = sort_dict(
            power_dict["Save"], ["Trigger", "DR", "Type", "Fail", "Succeed"]
        )

    return sort_dict(
        power_dict,
        [
            "Type",
            "Category",
            "Description",
            "Mechanic",
            "XP",
            "PP",
            "Prereq",
            "Prereq_Role",
            "Prereq_Level",
            "Prereq_Skill",
            "Prereq_Power",
            "To Hit",
            "Damage",
            "Range",
            "AOE",
            "Target",
            "Save",
            "Tags",
        ],
    )


def make_bullet(value, indents=0):
    """Return string with 4 spaces per indent, plus '- '"""
    spaces = indents * "    "
    return f"{spaces}- {value}\n"


class Powers(object):
    def __init__(self, input_files="04_Powers_SAMPLE.yml", limit_types=None):
        """Initialize"""
        self._data = {}
        self._categories = set()
        input_files = ensure_list(input_files)
        for input_file in input_files:
            self._data.update(load_source(input_file))
        self._template = self._data.pop("Template")
        self._readable_dict = {}
        self._stem = os.path.splitext(os.path.basename(input_files[-1]))[0]
        self._name = self._stem.split("_")[-1]
        self._limit_types = limit_types

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
        power["Category"] = ensure_list(power["Category"])
        power.pop("Save", None)
        return power

    def flatten_embedded(self, input_dict):
        """Given embedded dictionary, concat keys for values"""
        output = {}
        for k, v in input_dict.items():
            if isinstance(v, dict):  # and k != "Save":
                output.update(
                    {
                        f"{k}_{embed_k}": list_to_or(embed_v)  # LATE ADD of list func
                        for embed_k, embed_v in v.items()
                    }
                )
            else:
                output.update({k: v})
        return output

    @property
    def readable_dict(self, limit_types=None):
        """Return readable dict with Mechanics collapsed. Limit by limit_types list"""
        if not limit_types and not self._limit_types:
            limit_types = ["Major", "Minor", "Passive", "Adversary", "House", "Vulny"]
        else:
            limit_types = limit_types or self._limit_types
        if not self._readable_dict:
            self._readable_dict = {
                power: {
                    **self.flatten_embedded(self.merge_mechanics(traits)),
                }
                for (power, traits) in self._data.items()
                if traits["Type"] in limit_types
            }
        return self._readable_dict

    @property
    def categories(self):
        """Return set of tuples: (categories, subcategories)"""
        if not self._categories:
            for v in self._data.values():  # get set of sub/categories for TOC later
                self._categories.add(tuple(ensure_list(v["Category"])))
        return sorted(self._categories)

    def by_category(self, category: list = None):
        if not category:
            return self.readable_dict
        else:
            return {
                k: v
                for k, v in self.readable_dict.items()
                if v["Category"] == list(category)
            }


class Markdown(Powers):
    def __init__(self, input_files="04_Powers_SAMPLE.yml"):
        super().__init__(input_files=input_files)
        self._category_hierarchy = None

    def make_link(self, value, indents=0):
        """For md table of contents, add brackets, parens and remove spaces"""
        no_spaces = value.lower().replace(" ", "-")
        link = f"[{value}](#{no_spaces})"
        return make_bullet(link, indents)

    def make_header(self, value, level=0):
        """Return string with level+1 #"""
        prefix = level * "#"
        return f"\n#{prefix} {value}\n"

    @property
    def category_hierarchy(self):
        if not self._category_hierarchy:
            categories, indents, category_set, prev_cat_tuple = [], [], [], tuple()
            for cat_tuple in self.categories:
                for idx, category in enumerate(cat_tuple):
                    prev_category = (
                        prev_cat_tuple[idx] if idx < len(prev_cat_tuple) else None
                    )
                    if category != prev_category:
                        categories.append(category)
                        indents.append(idx)
                prev_cat_tuple = cat_tuple
                category_set.append(cat_tuple)
            self._category_hierarchy = list(zip(categories, indents, category_set))
        return self._category_hierarchy

    def md_TOC(self):
        """Generate markdown Table of Contents"""
        TOC = "<!-- MarkdownTOC add_links=True -->\n"
        for (category, indent, _) in self.category_hierarchy:
            TOC += self.make_link(category, indent)
        return TOC + "<!-- /MarkdownTOC -->\n"

    def make_entries(self, category_set):
        """Turn each input item into bulleted list with key prefix. Input list of Powers"""
        entries = ""
        for power_name, power in self.by_category(category_set).items():
            power = sort_power(power)
            power = {k: power[k] for k in power if k not in ["Category", "Type"]}
            entries += f"\n**{power_name}**\n\n"
            for k, v in power.items():
                entries += make_bullet(f"{k}: {list_to_or(v)}")
            entries += "\n"
        return entries

    def write(self, output_fp=None, TOC=False):
        """Write markdown"""
        if not output_fp:
            # TODO: Change default out to 1_Mechanics?
            output_fp = "./_Automated_output/" + self._stem + ".md"
        output = (
            "<!-- DEVELOPERS: Please edit corresponding yml in 3_Automation -->\n\n"
        )
        if TOC:
            output += self.md_TOC()
        for (category, indent, category_set) in self.category_hierarchy:
            output += self.make_header(category, indent)
            output += self.make_entries(category_set)
        with open(output_fp, "w", newline="") as f:
            f.write(output)
        logging.info("Wrote md")


class Csv(Powers):
    def __init__(self, input_files="04_Powers_SAMPLE.yml"):
        super().__init__(input_files=input_files)
        self._fields = None

    @property
    def fields(self):
        """Which fields to write"""
        if not self._fields:
            all_fields = sort_power(self._template)
            all_fields.pop("Save", None)  # remove Save for CSV
            self._fields = ["Name"] + list(self.flatten_embedded(all_fields).keys())
        return self._fields

    def write(self, output_fp=None, delimiter="\t"):
        """Write CSV from YAML, default is tab-delimited"""
        suffix_dict = {"\t": ".tsv", ",": ".csv"}
        if not output_fp:
            output_fp = "./_Automated_output/" + self._stem + suffix_dict[delimiter]
        rows = []
        with open(output_fp, "w", newline="") as f_output:
            csv_output = csv.DictWriter(
                f_output,
                fieldnames=self.fields,
                delimiter=delimiter,
            )
            csv_output.writeheader()
            for k, v in self.readable_dict.items():
                if v and any(v.values()):
                    v["Name"] = k
                    rows.append(v)
            csv_output.writerows(rows)
        logging.info("Wrote csv")


class Dot(Powers):
    def __init__(
        self,
        input_files="04_Powers_SAMPLE.yml",
        dependencies: list = None,
        add_loners=True,
    ):
        super().__init__(input_files=input_files)
        if not dependencies:
            self._dependencies = [
                f"Prereq_{dep}" for dep in ["Power", "Skill", "Level", "Role"]
            ]
        else:
            self._dependencies = [f"Prereq_{dep}" for dep in dependencies]
        self._template = None
        self._add_loners = add_loners
        self._dotstring = None
        self._graph = None
        self._loners = []

    def quote(self, s):
        """Return quoted string"""
        s = str(s) if not isinstance(s, str) else s
        return '"{}"'.format(s.replace('"', '\\"'))

    def edge_str(self, a, b=None):
        """Generates a `->` b notation for dot edges"""
        comparators = ["<", ">", "≤", "≥"]
        if b is not None:
            label = ""
            if any(comp in b for comp in comparators):
                b, comparison = b.split(" ", 1)
                label = f' [label="{comparison}"]'
            return f"{self.quote(b)} -> {self.quote(a)}{label}"
        else:
            return f"{self.quote(a)}"

    def get_edges(self, name, children=[]):
        """Generate full set of child->node given children"""
        edges = []
        edges.append(self.edge_str(name))
        for c in children:
            if isinstance(c, str):
                edges.append(self.edge_str(name, c))
            elif isinstance(c, dict):
                key = c.keys()[0]
                edges.append(self.edge_str(name, key))
                edges = edges + self.get_edges(key, c[key])
        return edges

    @property
    def loners(self):
        """Loners list, generated by dotstring func"""
        if self._add_loners and not self._loners:
            self.dotstring  # need to run to get all children then add/remove loners
            # TODO: gen list of loners
        return self._loners

    @property
    def template(self):
        if not self._template:
            gen_powers = True if "powers" in self._stem.lower() else False

            dot_frontmatter = (
                """digraph {concentrate=true; splines=curved; compound=true;\n"""
            )
            dot_subgraph_role = (
                "\n/* Roles */\n"
                "\tCaster [shape=box style=filled];\n"
                "\tSupport [shape=box style=filled];\n"
                "\tMartial [shape=box style=filled];\n"
                "\tDefender [shape=box style=filled];\n"
            )
            dot_subgraph_skill = (
                "/* Skill */\n"
                '\tsubgraph cluster_stats { label="Stats/Attributes"\n'
                '\t\tsubgraph cluster_agility{label="Agility" {Finesse Stealth} };\n'
                '\t\tsubgraph cluster_Conviction{label="Conviction" {Bluffing Performance} };\n'
                '\t\tsubgraph cluster_Intuition{label="Intuition" {Detection Craft} };\n'
                '\t\tsubgraph cluster_Intelligence{label="Intelligence"'
                "{Knowledge Investigation} };\n"
                '\t\tsubgraph cluster_Strength{label="Strength"  {Athletics Brute} };\n'
                '\t\tsubgraph cluster_Vitality{label="Vitality" {Vitality [style = invis]} };'
                "\n\t}\n\n"
            )
            dot_subgraph_level = (
                "/* Level */\n"
                '\tsubgraph cluster_levels { label="Levels";\n'
                "\tLevel_1 [shape=box style=filled];\n"
                "\tLevel_2 [shape=box style=filled];\n"
                "\tLevel_3 [shape=box style=filled];\n"
                "\tLevel_4 [shape=box style=filled];}\n\n"
            )
            dot_subgraph_loners = (
                "/* Loners */\n"
                '\tsubgraph cluster_levels {label="No Prerequisites";\n\t%s}\n'
            )
            if gen_powers:
                if "Prereq_Role" in self._dependencies:
                    dot_frontmatter += dot_subgraph_role
                if "Prereq_Skill" in self._dependencies:
                    dot_frontmatter += dot_subgraph_skill
                if "Prereq_Level" in self._dependencies:
                    dot_frontmatter += dot_subgraph_level
            if add_loners:
                dot_frontmatter += dot_subgraph_loners % ";\n\t".join(self.loners)
            return dot_frontmatter + "\n/* Linked */\n\t" + "%s\n}"
        return self._template

    def get_children(self, power_dict):
        """Return child nodes based on dependency list"""
        if "Prereq_Level" in power_dict.keys():
            power_dict["Prereq_Level"] = f"Level_{power_dict['Prereq_Level']}"
        children = [  # returns embedded lists
            or_to_list(v) for k, v in power_dict.items() if k in self._dependencies
        ]
        return [item for sublist in children for item in sublist]

    @property
    def dotstring(self):
        """Write dot file"""
        if not self._dotstring:
            edges = []
            for power_name, power in self.readable_dict.items():
                power_node = self.get_edges(power_name)
                children = self.get_children(power)
                if self._add_loners or children:
                    edges += self.get_edges(power_name, children)
                    try:
                        self._loners.remove(power_node)
                    except ValueError:
                        pass
                if not children:
                    self._loners += power_node
            self._dotstring = self.template % ";\n\t".join(edges)
        return self._dotstring

    @property
    def graph(self):
        if not self._graph:
            self._graph = pydot.graph_from_dot_data(self.dotstring)[0]
        return self._graph

    def write(self, output_fp=None):
        """Write dot file"""
        if not output_fp:
            output_fp = "./_Automated_output/" + self._stem + ".dot"
        with open(output_fp, "w", newline="") as f_output:
            f_output.write(self.dotstring)
        logging.info("Wrote dot")

    def to_pic(self, output_fp=None, out_format=["png", "svg"]):
        """Write graph as pic. png and/or svg. output_fp is one string, no suffix"""
        if not output_fp:
            output_fp = "./_Automated_output/" + self._stem
        out_format = ensure_list(out_format)
        if "png" in out_format:
            try:
                self.graph.write_png(output_fp + ".png", prog="dot.exe")
            except FileNotFoundError:
                self.graph.write_png(output_fp + ".png")
            logging.info("Wrote png")
        if "svg" in out_format:
            self.graph.write_svg(output_fp + ".svg")
            logging.info("Wrote svg")


def main(
    input_files=input_files,
    writing=writing,
    dependencies=dependencies,
    add_loners=add_loners,
    out_delim=out_delim,
):
    for f in input_files:
        logging.info(f"Started {f}")
        if "md" in writing:
            Markdown(f).write()
        if "csv" in writing:
            Csv(f).write(delimiter=out_delim)
        if any(img_out in writing for img_out in ["dot", "png", "svg"]):
            dot = Dot(f, dependencies=dependencies, add_loners=add_loners)
            if "dot" in writing:
                dot.write()
            dot.to_pic(out_format=[i for i in writing if i in ["png", "svg"]])


if __name__ == "__main__":
    main()
