from collections import OrderedDict
from .yaml_spec import YamlSpec
from ..utils.logger import logger


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
list_beast_types = ["PC", "NPC", "Boss"]  # TODO: ADD


class Bestiary(YamlSpec):
    # TODO: check stat overrides before printing
    def __init__(self, input_files="06_Bestiary_SAMPLE.yaml", limit_types: list = None):
        input_files = [file for file in self.ensure_list(input_files) if "Best" in file]
        super().__init__(input_files=input_files)
        self._limit_types = limit_types or list_beast_types

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
        beast_dict.setdefault("AP", 0)
        beast_dict.setdefault("Speed", 6)
        for field in self.list_attribs:
            beast_dict["Attribs"].setdefault(field, 0)
        if beast_dict["Type"] == "Dealer":
            for field in self.list_skills:  # Should pull from attrib
                beast_dict["Skills"].setdefault(field, 0)
        return beast_dict

    def stats_to_table(self, beast_dict):
        beast_dict = self.set_defaults(beast_dict)
        top_lvl_stats = tuple(
            beast_dict[stat] for stat in ["HP", "AP", "AR", "PP", "Speed"]
        )
        attrib_stats = tuple(beast_dict["Attribs"][stat] for stat in self.list_attribs)
        table_structure = (
            f"### {beast_dict['Type']}: Level {beast_dict['Level']}\n\n"
            + "| HP | AP | AR | PP | SPD |\n"
            + "| -- | -- | -- | -- | --- |\n"
            + "| %s  | %s  | %s  | %s  |  %s  |\n\n" % top_lvl_stats
            + "| AGL | CON | GUT | INT | STR | VIT |\n"
            + "| --- | --- | --- | --- | --- | --- |\n"
            + "|  %s  |  %s  |  %s  |  %s  |  %s  |  %s  | \n\n" % attrib_stats
        )
        if beast_dict.get("Skills"):
            skills_has = beast_dict["Skills"].keys()
            skill_string = " %s, ".join(skills_has) + " %s"
            skill_stats = tuple(beast_dict["Skills"][stat] for stat in skills_has)
            table_structure += "**Skills**: " + skill_string % skill_stats + "\n\n"
        return table_structure

    def run_stat_overrides(self, beast_dict):
        pass
        if "Stat Overrides" not in beast_dict:
            return beast_dict
        list_stats = beast_dict["Stat Overrides"]

    @property
    def categories(self):
        """Return set of Types for organizing output"""
        return set(
            beast_type
            for beast_type in ["Dealer", "Boss", "NPC", "Companion"]
            if beast_type not in self._limit_types
        )

    @property
    def content(self) -> dict:
        """Return readable dict."""
        raise NotImplementedError
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

    @property
    def dot_template(self) -> str:
        """All dot file frontmatter"""
        logger.warning("Dot template not yet implented for Bestiary")
        return ""
