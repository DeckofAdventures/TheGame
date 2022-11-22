import os
import yaml
from collections import OrderedDict


class YamlSpec(object):
    """Object for handling yaml spec files: Powers, Bestiary, etc"""

    # TODO: Add 'future' properties? must be filled in by child classes

    def __init__(self, input_files, dev: bool = True) -> None:
        self._raw_data = {}
        if isinstance(input_files, list):
            self._stem = (
                os.path.splitext(os.path.basename(input_files))[0].split("_")[0]
                + "Combined"
            )
        else:
            self._stem = os.path.splitext(os.path.basename(input_files[-1]))[0]
        input_files = self.ensure_list(input_files)
        for input_file in input_files:
            self._raw_data.update(self.load_yaml(input_file))
        self._template = self._raw_data.pop("Template")
        self._name = self._stem.split("_")[-1]

    def load_yaml(input_yaml: str = "04_Powers_Sample.yaml"):
        """Load the yaml file"""
        with open(input_yaml, encoding="utf8") as f:
            data = yaml.safe_load(f)
        return data

    def make_bullet(self, value, indents=0):
        """Return string with 4 spaces per indent, plus `- `"""
        spaces = indents * "    "
        return f"{spaces}- {value}\n"

    def sort_dict(self, my_dict, my_list):
        """Sort dict by list of keys. Return OrderedDict"""
        index_map = {v: i for i, v in enumerate(my_list)}
        return OrderedDict(sorted(my_dict.items(), key=lambda pair: index_map[pair[0]]))

    def ensure_list(item: str):
        """If input is not a list, return list of input"""
        return item if isinstance(item, list) else [item]

    def list_to_or(entry):
        """Given string or list, return items as string joined OR"""
        entry = [entry] if not isinstance(entry, list) else entry
        entry = [str(i) for i in entry]
        return " or ".join(entry)

    def or_to_list(entry: str):
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

    def filter_dict_by_type(self, limit_types):
        """NOTE: Functionality will be needed for both powers/beast but currently not
        uesed by Powers"""
        return {
            key: value
            for (key, value) in self._raw_data.items()
            if value["Type"] in limit_types
        }

    @property
    def raw_data(self):
        return self._raw_data
