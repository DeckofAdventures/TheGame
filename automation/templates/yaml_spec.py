import os
import yaml
from collections import OrderedDict
from ..utils.logger import logger


class YamlSpec(object):
    """Object for handling yaml spec files: Powers, Bestiary, etc"""

    # TODO: Add properties must be filled in by children? would be ABC/abstract methods

    def __init__(self, input_files) -> None:
        """Takes input files, loads raw data, gets stem and name for saving

        If file not found at input_file relative path, adds ./automation/_input/
        """
        self._raw_data = {}
        self._categories = set()
        self._content = dict()
        self._filepath_default_input = "./automation/_input/"
        self._filepath_default_output = "./automation/_output/"
        self._filepath_mechanics = "./docs/src/1_Mechanics/"

        input_files = self.ensure_list(input_files)
        if len(input_files) > 1:
            self._stem = (
                # When multiple inputs, take prefix before '_', add 'Combined'
                os.path.splitext(os.path.basename(input_files[0])).split("_")[0]
                + "Combined"
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

    @property
    def filepath_default_input(self):
        return self._filepath_default_input

    @property
    def filepath_default_output(self):
        return self._filepath_default_output

    @property
    def filepath_mechanics(self):
        return self._filepath_mechanics

    def load_yaml(self, input_yaml: str):
        """Load the yaml file"""
        with open(input_yaml, encoding="utf8") as f:
            data = yaml.safe_load(f)
        return data

    def make_bullet(self, value, indents=0):
        """Return string with 4 spaces per indent, plus `- `"""
        # Used in Powers and Markdown classes
        spaces = indents * "    "
        return f"{spaces}- {value}\n"

    def sort_dict(self, my_dict, my_list):
        """Sort dict by list of keys. Return OrderedDict"""
        index_map = {v: i for i, v in enumerate(my_list)}
        return OrderedDict(sorted(my_dict.items(), key=lambda pair: index_map[pair[0]]))

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

    def flatten_embedded(self, input_dict):
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
        key_options: list = None,
    ) -> dict:
        """Filter an embedded dict by if values of key_filter in listed key_options

        Example:
            my_dict = {"a": {"b": 1}, "c": {"b": 2}, "d": {"b": 3}}
            filter_dict_by_key(dict_content=my_dict,key_filter="b",key_options=[1,2])
            >> {'a': {'b': 1}, 'c': {'b': 2}}

        Args:
            dict_content (dict): Optional initial dict. Default YamlSpec._raw_data
            key_options (list): List of options for given [Key]
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
            if value[key_filter] in key_options
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

    @property
    def raw_data(self):
        return self._raw_data
