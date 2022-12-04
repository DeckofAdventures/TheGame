from collections import OrderedDict
from .yaml_spec import YamlSpec


class Bestiary(YamlSpec):
    def __init__(self, input_files="06_Bestiary_SAMPLE.yaml", limit_types: list = None):
        input_files = self.ensure_list(input_files)
        super().__init__(input_files=[file for file in input_files if "Best" in file])
        self._limit_types = limit_types
        self.list_attribs = ["AGL", "CON", "GUT", "INT", "STR", "VIT"]
        self.list_skills = [
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

    def sort_template(self, beast_dict: dict) -> OrderedDict:
        """Given a beast, return OrderedDict in markdown read order"""
        if "Attrib" in beast_dict:
            beast_dict["Attrib"] = self.sort_dict(
                beast_dict["Attrib"], self.list_attribs
            )
        if "Skills" in beast_dict:
            beast_dict["Skills"] = self.sort_dict(
                beast_dict["Skills"],
                self.list_skils,
            )
        if "Phases" in beast_dict:
            beast_dict["Phases"] = self.sort_dict(
                beast_dict["Phases"], ["One", "Two", "Three", "Four", "Five", "Six"]
            )

        return self.sort_dict(
            beast_dict,
            [
                "Type",
                "Level",
                "Threat",
                "HP",
                "AP",
                "AR",
                "PP",
                "Attrib",
                "Skill",
                "Powers",
                "Phases",
                "Description",
            ],
        )

    def set_defaults(self, beast_dict) -> dict:
        """Set zeros as default for AP, Attribs and Skills"""
        top_level_zero_defaults = ["AP"]
        for field in top_level_zero_defaults:
            beast_dict.setdefault(field, 0)
        for field in self.list_attribs:
            beast_dict["Attribs"].setdefault(field, 0)
        for field in self.list_skills:
            beast_dict["Skills"].setdefault(field, 0)

    def merge_features(self, beast_dict):
        pass  # What needs to be flattened?

    @property
    def content(self) -> dict:
        """Return readable dict."""
        if not self._content:
            self._content = {
                power: {
                    **self.flatten_embedded(self.merge_features(traits)),
                }
                for (power, traits) in self._raw_data.items()
            }
        return self.filter_dict_by_key(  # Filter by types specified when init class
            dict_content=self._content, key_filter="Type", key_options=self._limit_types
        )
