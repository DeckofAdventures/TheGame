from dataclasses import dataclass, field
from typing import List

from ..utils import ensure_list, logger, my_repr
from .powers import Power, Powers
from .yaml_spec import YamlSpec

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
list_beast_types = ["PC", "NPC", "Boss", "Companion"]
list_boss_phases = ["One", "Two", "Three", "Four", "Five", "Six"]


class Bestiary(YamlSpec):
    # TODO: check stat overrides before printing
    def __init__(self, input_files="06_Bestiary_SAMPLE.yaml", limit_types: list = None):
        input_files = [file for file in ensure_list(input_files) if "Best" in file]
        super().__init__(input_files=input_files)
        self._limit_types = limit_types or list_beast_types
        self._as_dict = {}
        self._as_list = []

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

    @property
    def as_list(self):
        if not self._as_list:
            self._as_list = [
                Beast(Name=k, **v)
                for k, v in self._raw_data.items()
                if v.get("Type", None) in self._limit_types
            ]
        return self._as_list

    @property
    def as_dict(self) -> dict:
        """Return readable dict with Mechanics collapsed."""
        if not self._as_dict:
            self._as_dict = {
                k: Power(Name=k, **v)
                for k, v in self._raw_data.items()
                if v.get("Type", None) in self._limit_types
            }
        return self._as_dict

    @property
    def categories(self):
        """Return set of Types for organizing output"""
        return set(self._limit_types)


@dataclass(order=True)
class Attribs:
    AGL: int = 0
    CON: int = 0
    GUT: int = 0
    INT: int = 0
    STR: int = 0
    VIT: int = 0


@dataclass(order=True)
class Skills:
    Finesse: int = 0
    Stealth: int = 0
    Bluffing: int = 0
    Performance: int = 0
    Knowledge: int = 0
    Investigation: int = 0
    Detection: int = 0
    Craft: int = 0
    Athletics: int = 0
    Brute: int = 0


@dataclass(order=True)
class Phase:
    Name: str
    Order: int = field(repr=False)
    HP: int = 1
    Allies: List[str] = field(default=None)  # Should this be typed as Beast? Recursive?


@dataclass(order=True)
class Beast:
    sort_index: str = field(init=False, repr=False)
    Name: str
    Type: str
    Level: int = 1
    HP: int = 1
    AP: int = 1
    AR: int = 1
    PP: int = 1
    Speed: int = 6
    Attribs: dict = field(default=None)
    Skills: dict = field(default=None)
    Powers: dict = field(default=None, repr=False)
    Powers_list: list = field(default_factory=list)
    Phases: list = field(default=None)
    Description: str = ""

    def __post_init__(self):
        self.sort_index = self.Type
        self.Powers = self.fetch_powers()
        self.Powers_list = [p for p in self.Powers]
        self.Attribs = Attribs(**self.Attribs) if self.Attribs else None
        self.Skills = Skills(**self.Skills) if self.Skills else None
        self.Phases = self.fetch_phases() if self.Phases else None

    def fetch_powers(self):
        output = {}
        all_powers = Powers(
            input_files=[
                "04_Powers.yaml",
                "04_Powers_SAMPLE.yaml",
                "05_Vulnerabilities.yaml",
            ]
        ).as_dict
        self.Powers = ensure_list(self.Powers)
        for power in self.Powers:
            if isinstance(power, dict):
                power_name = list(power.keys())[0]
                this_power = all_powers.get(power_name, None)
                output.update(
                    {power_name: this_power.set_choice(list(power.values())[0])}
                )
            else:
                this_power = all_powers.get(power, None)
                output.update({power: this_power})
            if not this_power:
                logger.warning(f"{self.Name} has a power not in yaml: {power}")
        return output

    def fetch_phases(self):
        output = []
        for order, (phase, phase_dict) in enumerate(self.Phases.items()):
            # import pdb

            # pdb.set_trace()
            output.append(Phase(Name=phase, Order=order, **phase_dict))
        return output

    def override_stats(self):
        pass  # check if any listed powers have overrides, then do so

    def __repr__(self):
        return my_repr(self)
