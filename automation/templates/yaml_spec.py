import csv
import os
from abc import ABC, abstractmethod

from ..utils import (
    ensure_list,
    filter_dict_by_key,
    load_yaml,
    logger,
    make_bullet,
    make_header,
    make_link,
)


class YamlSpec(ABC):
    """Object for handling yaml spec files: Powers, Bestiary, etc"""

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

        input_files = ensure_list(input_files)
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
            self._raw_data.update(load_yaml(input_file))
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
    def as_dict(self):
        pass

    @abstractmethod
    def as_list(self):
        pass

    @abstractmethod
    def categories(self):
        pass

    def by_type(self, type_options: list = None):
        """Returns dict of limited by the type key, if present

        Args:
            type_options (list, optional): list or set of permitted types
                Defaults to None, meaning no filtering or ordering.

        Returns:
            dict: Subset of readable dict
        """
        return filter_dict_by_key(
            dict_content=self.as_dict, key_filter="Type", key_options=type_options
        )

    def by_category(self, category: list = None):
        """Returns readable dict of powers limited by category, if present

        Args:
            category (list, optional): Ordered list/set of [category, subcategory].
                Defaults to None, meaning no filtering or ordering.

        Returns:
            dict: Subset of readable dict
        """
        return filter_dict_by_key(
            dict_content=self.as_dict, key_filter="Category", key_options=category
        )

    # ------------------------------- MARKDOWN UTILITIES -------------------------------
    @property
    def category_hierarchy(self):
        """Return list of tuples: [(item, indent, (categ, subcat, subsub, etc.))]"""
        if not self._category_hierarchy:
            categories, indents, category_set, prev_category_tuple = [], [], [], tuple()
            for category_tuple in self.categories:
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
            for (category, indent, _) in self.category_hierarchy:
                TOC += make_link(category, indent)
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
                entries += make_bullet(f"{k}: {self.list_to_or(v)}")
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
            output += make_header(category, indent)
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
            for k, v in self.as_dict.items():
                if v and any(v.values()):
                    v["Name"] = k
                    rows.append(v)
            csv_output.writerows(rows)
        logger.info(f"Wrote csv: {output_fp}")
