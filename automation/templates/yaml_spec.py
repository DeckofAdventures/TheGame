import csv
import os
from abc import ABC, abstractmethod
from collections import OrderedDict

from ..utils import ensure_list, load_yaml, logger, make_header, make_link, sort_dict


class YamlSpec(ABC):
    """Object for handling yaml spec files: Powers, Bestiary, etc"""

    def __init__(self, input_files) -> None:
        """Takes input files, loads raw data, gets stem and name for saving

        If file not found at input_file relative path, adds ./automation/_input/
        """
        self._md_TOC = ""
        self._raw_data = {}
        self._categories = set()
        self._category_hierarchy = None
        self._content = dict()
        self._fields = None
        self._default_root = os.getenv("THEGAME_ROOT") or "./automation/"
        self._filepath_default_input = self._default_root + "_input/"
        self._filepath_default_output = self._default_root + "_output/"
        self._filepath_mechanics = "./docs/src/1_Mechanics/"
        self._tried_loading = False
        self._limit_types = []
        self._as_dict = {}
        self._type_dict = {}  # Declaring on build_contents

        input_files = ensure_list(input_files)
        if not input_files:
            logger.critical(
                "YamlSpec recieved empty file list. Check that file naame contains"
                + " relevant keywords like 'power', 'vuln', 'best', 'pc', or 'item'"
            )
        elif len(input_files) > 1:
            self._stem = (
                # When multiple inputs, take prefix before '_', add 'Combined'
                os.path.splitext(os.path.basename(input_files[0]))[0]
                + "_Combined"
            )
        elif len(input_files) == 1:
            self._stem = os.path.splitext(os.path.basename(input_files[0]))[0]

        self._filepath_output = (
            self._filepath_default_output
            if "SAMPLE" in self._stem or "test" in self._stem
            else self._filepath_mechanics
        )

        for input_file in input_files:  # If provided mult files, combine
            if not os.path.exists(input_file):
                input_file = self._filepath_default_input + input_file
            logger.debug(f"Loading {input_file}")
            self._raw_data.update(load_yaml(input_file))
        self._template = self._raw_data.pop("Template", None)
        self._name = self._stem.split("_")[-1]

    # ------------------------------- FILEPATH UTILITIES -------------------------------
    @property
    def filepath_default_input(self):
        return self._filepath_default_input

    @property
    def filepath_default_output(self):
        return self._filepath_default_output

    @property
    def filepath_output(self):
        return self._filepath_output

    @filepath_output.setter  # Allows setting new output fp
    def filepath_output(self, filepath_output: str):
        # TODO: add path verification here
        self._filepath_output = filepath_output

    # -------------------------------- CORE PROPERTIES ---------------------------------
    def _build_contents(self, this_data_class, id_component="", **kwargs):
        """Loop over items in the raw dict format. Generate list and dict versions"""
        self._type_dict = {k: [] for k in self._limit_types}
        self._tried_loading = True
        for k, v in self.raw_data.items():
            type = v.get("Type", None)
            if not type:
                logger.warning(f"YAML item missing Type: {k}")
            elif type in self._limit_types:
                id = v["Name"] + str(v.get(id_component)) if v.get("Name") else k
                _ = v.setdefault("Name", k)
                self._as_dict.update({k: this_data_class(id=id, **v, **kwargs)})
                self._type_dict[type].append(k)  # Build type dict
            elif type not in self._limit_types:
                logger.debug(f"Skipping YAML item due to excluded Type: {k}")

    def _build_categories(self, build_with="Type") -> OrderedDict:
        """Return OrderedDict with {tuple(Type) : [list of beasts]} as key value pairs"""
        if not self._categories:
            for k, v in self.as_dict.items():
                cat_tuple = tuple(ensure_list(getattr(v, build_with)))
                self._categories.setdefault(cat_tuple, [])
                self._categories[cat_tuple].append(k)  # Changed v.Name -> k
                self._categories_set.add(cat_tuple)
                self._csv_fields = self._csv_fields.union(list(v.csv_dict.keys()))
                self._categories = sort_dict(
                    self._categories, sorted(self._categories_set)
                )
        return self._categories

    @property
    def raw_data(self):
        return self._raw_data

    @abstractmethod
    def as_dict(self):
        pass

    @abstractmethod
    def categories(self) -> dict:
        """{(hierarchy tuple): [List of names]} dict"""
        pass

    @property
    def type_dict(self) -> dict:
        """Cache of items by type e.g. {Major: [a, b]}"""
        if not self._tried_loading:
            self._build_contents
        return self._type_dict

    # ------------------------------- MARKDOWN UTILITIES -------------------------------
    @property
    def category_hierarchy(self):
        """Return list of tuples: [(item, indent, (categ, subcat, subsub, etc.))]"""
        if not self._category_hierarchy:
            categories, indents, category_set, prev_category_tuple = [], [], [], tuple()
            for category_tuple in self.categories.keys():
                for idx, category in enumerate(category_tuple):  # indent lvl, category
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

    @property
    def md_TOC(self) -> str:
        """Generate markdown Table of Contents with category_heirarchy"""
        if not self._md_TOC:
            TOC = "<!-- MarkdownTOC add_links=True -->\n"
            for category, indent, _ in self.category_hierarchy:
                TOC += make_link(category, indent)
            self._md_TOC = TOC + "<!-- /MarkdownTOC -->\n"
        return self._md_TOC

    def make_entries(self, category_set: set) -> str:
        """All entries into bulleted lists with key prefixes.

        Args:
            category_set (set): unique set of categories (categ, subcateg)"""
        entries = ""
        for item_name in self.categories.get(category_set, []):
            entries += self.as_dict[item_name].markdown
        return entries

    def write_md(self, output_fp: str = None, TOC: bool = False):
        """Write markdown

        Args:
            output_fp (str, optional): relative path for writing output file. Default
                None meaning save to ../docs/src/1_Mechanics/ path with same file name
            TOC (bool, optional): Write table of contents. Default False
        """
        if not output_fp:
            output_fp = self.filepath_output + self._stem + ".md"
        output = (
            "<!-- markdownlint-disable MD013 MD024 -->\n"
            + "<!-- DEVELOPERS: Please edit corresponding yaml -->\n"
        )
        if TOC:
            output += self.md_TOC
        for category, indent, category_set in self.category_hierarchy:
            output += make_header(category, indent)
            output += self.make_entries(category_set)
        with open(output_fp, "w", newline="") as f:
            f.write(output)
        logger.info(f"Wrote md: {output_fp}")

    # --------------------------------- CSV UTILITIES ----------------------------------

    @abstractmethod
    def csv_fields(self) -> list:
        """Column names for csv

        Returns:
            fields (list): list of column headers for CSV"""
        pass

    def write_csv(self, output_fp: str = None, delimiter: str = "\t"):
        """Write CSV from YAML, default is tab-delimited

        Args:
            output_fp (str): relative filepath. Default none, which means local
                _output subfolder
            delimeter (str): column delimiter. `\t` for tab or `,` for comma. If other,
                must provide extension in ext
            ext (str): file extension if other than `.csv`, `.tsv`. Must include period
        """
        suffix_dict = {"\t": ".tsv", ",": ".csv"}
        if not output_fp:
            output_fp = self.filepath_output + self._stem + suffix_dict[delimiter]
        rows = []
        with open(output_fp, "w", newline="") as f_output:
            csv_output = csv.DictWriter(
                f_output,
                fieldnames=self.csv_fields,
                delimiter=delimiter,
            )
            csv_output.writeheader()
            for i in self.as_dict.values():
                rows.append(i.csv_dict)
            csv_output.writerows(rows)
        logger.info(f"Wrote csv: {output_fp}")
