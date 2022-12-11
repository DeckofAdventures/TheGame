import os
import csv
import yaml
from collections import OrderedDict
from abc import ABC, abstractmethod
from ..utils.logger import logger


class YamlSpec(ABC):
    """Object for handling yaml spec files: Powers, Bestiary, etc"""

    # TODO: Add properties must be filled in by children? would be ABC/abstract methods

    def __init__(self, input_files) -> None:
        """Takes input files, loads raw data, gets stem and name for saving

        If file not found at input_file relative path, adds ./automation/_input/
        """
        self._raw_data = {}
        self._categories = set()
        self._category_hierarchy = None
        self._content = dict()
        self._fields = None
        self._filepath_default_input = "./automation/_input/"
        self._filepath_default_output = "./automation/_output/"
        self._filepath_mechanics = "./docs/src/1_Mechanics/"
        self._md_TOC = None
        self._dotstring = None
        self._dot_graph = None
        self._dot_loners = []
        self._dot_add_loners = None
        self._dot_dependencies = [
            f"Prereq_{d}" for d in ["Power", "Skill", "Level", "Role"]
        ]

        input_files = self.ensure_list(input_files)
        if len(input_files) > 1:
            self._stem = (
                # When multiple inputs, take prefix before '_', add 'Combined'
                os.path.splitext(os.path.basename(input_files[0]))[0]
                + "_Combined"
            )
        else:
            self._stem = os.path.splitext(os.path.basename(input_files[0]))[0]
        for input_file in input_files:  # If provided mult files, combine
            if not os.path.exists(input_file):
                input_file = self._filepath_default_input + input_file
            logger.debug(f"Loading {input_file}")
            self._raw_data.update(self.load_yaml(input_file))
        self._template = self._raw_data.pop("Template")
        self._name = self._stem.split("_")[-1]

    # ------------------------------- FILEPATH UTILITIES -------------------------------
    @property
    def filepath_default_input(self):
        return self._filepath_default_input

    @property
    def filepath_default_output(self):
        return self._filepath_default_output

    @property
    def filepath_mechanics(self):
        return (
            self._filepath_default_output
            if "SAMPLE" in self._stem
            else self._filepath_mechanics
        )

    # -------------------------------- CORE PROPERTIES ---------------------------------
    @property
    def raw_data(self):
        return self._raw_data

    @abstractmethod
    def content(self):
        pass

    @abstractmethod
    def categories(self):
        pass

    # -------------------------------- GENERAL UTILITIES -------------------------------
    def load_yaml(self, input_yaml: str):
        """Load the yaml file"""
        with open(input_yaml, encoding="utf8") as f:
            data = yaml.safe_load(f)
        return data

    def sort_dict(self, my_dict, my_list):
        """Sort dict by list of keys. Return OrderedDict"""
        index_map = {v: i for i, v in enumerate(my_list)}
        my_dict_reduced = {k: v for k, v in my_dict.items() if k in my_list}
        return OrderedDict(
            sorted(my_dict_reduced.items(), key=lambda pair: index_map[pair[0]])
        )

    def ensure_list(self, ambiguous_item):
        """If input is not a list, return list of input"""
        return ambiguous_item if isinstance(ambiguous_item, list) else [ambiguous_item]

    def list_to_or(self, entry):
        """Given string or list, return items as string joined OR"""
        entry = [entry] if not isinstance(entry, list) else entry
        entry = [str(i) for i in entry]
        return " or ".join(entry)

    def or_to_list(self, entry: str):
        """Given string, return list split by OR"""
        return entry.split(" or ")

    def flatten_embedded(self, input_dict) -> dict:
        """Check vals in input. If dict, make embedded values new keys in output dict

        Novel keys in output dict are {'key_embedded-key': 'embedded_value'}

        Args:
            input_dict (dict): any dict

        Returns:
            output_dict (dict)
        """
        output = {}
        for k, v in input_dict.items():
            if isinstance(v, dict):  # and k != "Save":
                output.update(
                    {
                        f"{k}_{embed_k}": self.list_to_or(
                            embed_v
                        )  # LATE ADD of list func
                        for embed_k, embed_v in v.items()
                    }
                )
            else:
                output.update({k: v})
        return output

    def filter_dict_by_key(
        self,
        dict_content: dict = "None",
        key_filter: str = "Type",
        key_options: set = None,
    ) -> dict:
        """Filter an embedded dict by if values of key_filter in listed key_options

        Example:
            my_dict = {"a": {"b": 1}, "c": {"b": 2}, "d": {"b": 3}}
            filter_dict_by_key(dict_content=my_dict,key_filter="b",key_options=[1,2])
            >> {'a': {'b': 1}, 'c': {'b': 2}}

        Args:
            dict_content (dict): Optional initial dict. Default YamlSpec._raw_data
            key_options (list): Set of items that, when retyped to list must match
                value[list_filter]. TODO: refactor to avoid retyping here, migrate up
            key (str): Optional specification of key. Default "Type"

        Returns:
            dict: filtered dict
        """
        if not dict_content:
            dict_content = self._raw_data
        if not key_options:
            return dict_content
        return {
            key: value
            for (key, value) in dict_content.items()
            if value[key_filter] == list(key_options)
        }

    def by_type(self, type_options: list = None):
        """Returns dict of limited by the type key, if present

        Args:
            type_options (list, optional): list or set of permitted types
                Defaults to None, meaning no filtering or ordering.

        Returns:
            dict: Subset of readable dict
        """
        return self.filter_dict_by_key(
            dict_content=self.content, key_filter="Type", key_options=type_options
        )

    def by_category(self, category: list = None):
        """Returns readable dict of powers limited by category, if present

        Args:
            category (list, optional): Ordered list/set of [category, subcategory].
                Defaults to None, meaning no filtering or ordering.

        Returns:
            dict: Subset of readable dict
        """
        return self.filter_dict_by_key(
            dict_content=self.content, key_filter="Category", key_options=category
        )

    # ------------------------------- MARKDOWN UTILITIES -------------------------------
    @property
    def category_hierarchy(self):
        """Return list of tuples: [(item, indent, (categ, subcat, subsub, etc.))]"""
        if not self._category_hierarchy:
            categories, indents, category_set, prev_category_tuple = [], [], [], tuple()
            for category_tuple in self.categories:
                for idx, category in enumerate(
                    category_tuple
                ):  # indent level, category
                    prev_category = (  # previous category at same heading level
                        prev_category_tuple[idx]
                        if idx < len(prev_category_tuple)
                        else None
                    )
                    if category != prev_category:  # if new, add
                        categories.append(category)
                        indents.append(idx)
                        # subset of tuple relevant to heading level
                        category_set.append(category_tuple[0 : idx + 1])
                prev_category_tuple = category_tuple
            self._category_hierarchy = list(zip(categories, indents, category_set))
        return self._category_hierarchy

    def make_bullet(self, value, indents=0):
        """Return string with 4 spaces per indent, plus `- `"""
        spaces = indents * "    "
        return f"{spaces}- {value}\n"

    def make_link(self, value: str, indents: int = 0) -> str:
        """Make relative within-doc bulleted link for TOC. [name](#no-spaces)

        Args:
            value (str): heading name
            indents (int): indent level for heading

        Returns:
            link (str): markdown formatted indented bullet with relative path for
                table of contents. E.g., `    - [Heading name](#heading-name)`
        """
        no_spaces = value.lower().replace(" ", "-")
        link = f"[{value}](#{no_spaces})"
        return self.make_bullet(link, indents)

    def make_header(self, value: str, level: (int) = 0):
        """Return string with level+1 * `#`

        Args:
            value (str): heading content
            level (int): heading level. e.g., `# Zero`, `## One`
        """
        prefix = level * "#"
        return f"\n#{prefix} {value}\n"

    @property
    def md_TOC(self) -> str:
        """Generate markdown Table of Contents with category_heirarchy"""
        if not self._md_TOC:
            TOC = "<!-- MarkdownTOC add_links=True -->\n"
            for (category, indent, _) in self.category_hierarchy:
                TOC += self.make_link(category, indent)
            self._md_TOC = TOC + "<!-- /MarkdownTOC -->\n"
        return self._md_TOC

    def make_entries(self, category_set: set) -> str:
        """All entries into bulleted lists with key prefixes.

        Args:
            category_set (set): unique set of categories (categ, subcateg)"""
        entries = ""
        for power_name, power in self.by_category(category_set).items():
            power = self.sort_template(power)
            power = {k: power[k] for k in power if k not in ["Category", "Type"]}
            entries += f"\n**{power_name}**\n\n"
            for k, v in power.items():
                entries += self.make_bullet(f"{k}: {self.list_to_or(v)}")
            entries += "\n"
        return entries

    def write_md(self, output_fp: str = None, TOC: bool = False):
        """Write markdown

        Args:
            output_fp (str, optional): relative path for writing output file. Default
                None meaning save to ../docs/src/1_Mechanics/ path with same file name
            TOC (bool, optional): Write table of contents. Default False
        """
        if not output_fp:
            output_fp = self.filepath_mechanics + self._stem + ".md"
        output = "<!-- DEVELOPERS: Please edit corresponding yaml -->\n\n"
        if TOC:
            output += self.md_TOC
        for (category, indent, category_set) in self.category_hierarchy:
            output += self.make_header(category, indent)
            output += self.make_entries(category_set)
        with open(output_fp, "w", newline="") as f:
            f.write(output)
        logger.info(f"Wrote md: {output_fp}")

    # --------------------------------- CSV UTILITIES ----------------------------------

    @property
    def fields(self) -> list:
        """Column names for csv. Excludes 'save', hardcoded

        Returns:
            fields (list): list of column headers for CSV"""
        if not self._fields:
            all_fields = self.sort_template(
                self._template
            )  # get field list from template
            all_fields.pop("Save", None)  # remove Save for CSV
            # Flatten embedded fields
            self._fields = ["Name"] + list(self.flatten_embedded(all_fields).keys())
        return self._fields

    def write_csv(self, output_fp: str = None, delimiter: str = "\t", ext: str = None):
        """Write CSV from YAML, default is tab-delimited

        Args:
            output_fp (str): relative filepath. Default none, which means local
                _output subfolder
            delimeter (str): column delimiter. `\t` for tab or `,` for comma. If other,
                must provide extension in ext
            ext (str): file extension if other than `.csv`, `.tsv`. Must include period
        """
        suffix_dict = {"\t": ".tsv", ",": ".csv"}
        if ext and ext not in [".tsv", ".csv", "tsv", "csv"]:
            suffix_dict.update({delimiter: ext})
        if not output_fp:
            output_fp = (
                self.filepath_default_output + self._stem + suffix_dict[delimiter]
            )
        rows = []
        with open(output_fp, "w", newline="") as f_output:
            csv_output = csv.DictWriter(
                f_output,
                fieldnames=self.fields,
                delimiter=delimiter,
            )
            csv_output.writeheader()
            for k, v in self.content.items():
                if v and any(v.values()):
                    v["Name"] = k
                    rows.append(v)
            csv_output.writerows(rows)
        logger.info(f"Wrote csv: {output_fp}")

    # --------------------------------- DOT UTILITIES ---------------------------------
    @property
    @abstractmethod
    def dot_template(self) -> str:
        """All dot file frontmatter"""
        pass

    def quote(self, s):
        """Return input as quoted string"""
        s = str(s) if not isinstance(s, str) else s
        return '"{}"'.format(s.replace('"', '\\"'))

    def edge_str(self, a: str, b: str = None):
        """Generates a `->` b notation for dot edges

        Args:
            a (str): first node
            b (str, optional): Second node. Optionally with comparison e.g., STR > 2
        """
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
        edges.append(self.edge_str(name))  # Add name to list
        for c in children:  # For each child
            if isinstance(c, str):
                edges.append(self.edge_str(name, c))  # make node->child string as edge
            elif isinstance(c, dict):  # if child is dict
                key = c.keys()[0]  # get first key
                edges.append(self.edge_str(name, key))  # make node->key string
                # get edges recursively with key and value from key
                edges = edges + self.get_edges(key, c[key])
        return edges

    @property
    def loners(self):
        """Loners list, generated by dotstring func. Not implemented"""
        if self._dot_add_loners and not self._dot_loners:
            self.dotstring  # need to run to get all children then add/remove loners
            # TODO: gen list of loners
            logger.WARN("Get loners list not implemented")
        return self._dot_loners

    def get_children(self, power_dict):
        """Return child nodes based on dependency list"""
        if "Prereq_Level" in power_dict.keys():
            power_dict["Prereq_Level"] = f"Level_{power_dict['Prereq_Level']}"
        children = [  # returns embedded lists
            self.or_to_list(v)
            for k, v in power_dict.items()
            if k in self._dot_dependencies
        ]
        return [item for sublist in children for item in sublist]

    @property
    def dotstring(self):
        """Dot file contents"""
        if not self._dotstring:
            edges = []
            for power_name, power in self.content.items():  # for each power
                power_node = self.get_edges(power_name)  # Get `->` notation for power
                children = self.get_children(power)  # Get power children
                if self._dot_add_loners or children:  # If keep loners or has children
                    edges += self.get_edges(power_name, children)  # `->` for children
                    try:  # b/c children, not loner. try to remove from loner list
                        self._dot_loners.remove(power_node)
                    except ValueError:  # if not in loner list, ValueError ok
                        pass
                if not children:  # If no children, is loner
                    self._dot_loners += power_node
            # write list of `->` notations, on new indented lines
            self._dotstring = self.dot_template % ";\n\t".join(edges)
        return self._dotstring

    @property
    def graph(self):
        """Make pydot graph format from dotstring"""
        if not self._dot_graph:
            import pydot

            self._dot_graph = pydot.graph_from_dot_data(self.dotstring)[0]
        return self._dot_graph

    def write_dot(
        self,
        output_fp: str = None,
        add_loners: bool = True,
        dependencies: list = ["Power", "Skill", "Level", "Role"],
    ):
        """Write dot file

        Args:
            output_fp (str, optional): Relative path string.
                Defaults to ./_output/{input_file_name}.dot
            dependencies (list, optional): List of dependencies to include. Defaults
                to ["Power", "Skill", "Level", "Role"]
            add_loners (bool, optional): Include items w/o dependents. Defaults True.
        """
        self._dot_dependencies = [f"Prereq_{dep}" for dep in dependencies]
        self._dot_add_loners = add_loners
        if not output_fp:
            output_fp = self.filepath_default_output + self._stem + ".dot"
        with open(output_fp, "w", newline="") as f_output:
            f_output.write(self.dotstring)
        logger.info(f"Wrote dot: {output_fp}")

    def dot_to_pic(self, output_fp=None, out_format=["png", "svg"]):
        """Write graph as pic. png and/or svg. output_fp is one string, no suffix

        Args:
            output_fp (str): Relative output filepath. Default none, meaning local
                _output/ folder
            out_format (list): List of formats or string. png and/or svg
        """
        if not output_fp:
            output_fp = self.filepath_default_output + self._stem
        out_format = self.ensure_list(out_format)
        if "png" in out_format:
            try:
                self.graph.write_png(output_fp + ".png", prog="dot.exe")
            except FileNotFoundError:
                self.graph.write_png(output_fp + ".png")
            logger.info(f"Wrote png: {output_fp}")
        if "svg" in out_format:
            self.graph.write_svg(output_fp + ".svg")
            logger.info(f"Wrote svg: {output_fp}")
