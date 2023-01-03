from dataclasses import dataclass, field, fields
from operator import attrgetter
from typing import List

from ..utils import ensure_list, logger, make_bullet, make_header, my_repr
from .powers import Powers, list_power_types
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
        self._as_list = []
        self._as_dict = {}

    def _build_contents(self):
        for k, v in self.raw_data.items():
            if v.get("Type", None) in self._limit_types:
                beast = Beast(Name=k, **v)
                self.as_list.append(beast)
                self._as_dict.update({k: beast})

    @property
    def as_list(self):
        if not self._as_list:
            self._build_contents()
        return self._as_list

    @property
    def as_dict(self) -> dict:
        """Return readable dict with Mechanics collapsed."""
        if not self._as_dict:
            self._build_contents()
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

    @property
    def as_tuple(self):
        return (self.AGL, self.CON, self.GUT, self.INT, self.STR, self.VIT)


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

    @property
    def non_defaults(self):
        output = []
        for f in fields(self):
            value = attrgetter(f.name)(self)
            if value != f.default:
                output.append((f.name, value))
        return output


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
        self.Powers_list = [p for p in self.Powers.values()]
        self.Attribs = Attribs(**self.Attribs) if self.Attribs else None
        self.Skills = Skills(**self.Skills) if self.Skills else None
        self.Phases = self.fetch_phases() if self.Phases else None
        self.override_stats()

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
            output.append(Phase(Name=phase, Order=order, **phase_dict))
        return output

    def override_stats(self):
        """Check for any StatOverride powers. Apply overrides"""
        # TODO: Also use this to take attribs and apply them to corresponding skills?
        for power in self.Powers.values():
            override = getattr(power, "StatOverride", None)
            if override:
                attrib_or_skill = (
                    self.Attribs if override.Stat in list_attribs else self.Skills
                )
                setattr(attrib_or_skill, override.Stat, override.Value)

    def _md_stats_table(self):
        top_lvl_stats = (self.HP, self.AP, self.AR, self.PP, self.Speed)
        output = (
            f"### {self.Type}: Level {self.Level}\n\n"
            + "| HP | AP | AR | PP | SPD |\n"
            + "| -- | -- | -- | -- | --- |\n"
            + "| %s  | %s  | %s  | %s  |  %s  |\n\n" % top_lvl_stats
            + "| AGL | CON | GUT | INT | STR | VIT |\n"
            + "| --- | --- | --- | --- | --- | --- |\n"
            + "|  %s  |  %s  |  %s  |  %s  |  %s  |  %s  |\n\n" % self.Attribs.as_tuple
        )
        if self.Skills.non_defaults:
            output += (
                "**Skills**: "
                + ", ".join(["%s %s" % s for s in self.Skills.non_defaults])
                + "\n"
            )
        return output

    def _md_actions(self):
        output = make_header("Powers", 2)
        for power_type in list_power_types:
            # import pdb

            # pdb.set_trace()
            powers_subset = [
                make_bullet(f"**{p.Name}**: {p.Merged_Mechanic}")
                for p in self.Powers_list
                if getattr(p, "Type", "None") == power_type
            ]
            if powers_subset:
                output += make_header(power_type, 3) + "\n" + "".join(powers_subset)
        return output

    def _md_phases(self):
        if not self.Phases:
            return
        output = make_header("Phases", 2)
        for phase in self.Phases:
            output += make_header(f"Phase {phase.Name}", 3) + "\n"
            output += f"Set HP to {phase.HP} and add the following all(y/ies):\n"
            output += "".join([make_bullet(ally) for ally in phase.Allies])
        return output

    @property
    def markdown(self):
        return (
            make_header(self.Name, 1)
            + "\n"
            + self._md_stats_table()
            + self._md_actions()
            + self._md_phases()
        )

    def __repr__(self):
        return my_repr(self)
