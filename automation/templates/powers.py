from dataclasses import dataclass, field, fields
from operator import attrgetter
from typing import Union

from ..utils import ensure_list, flatten_embedded, list_to_or, make_bullet, my_repr
from .yaml_spec import YamlSpec

list_power_types = [
    "Passive",
    "Vulny",
    "Free",
    "Major",
    "Minor",
    "Adversary",
    "House",
    "Channel",
]


def load_all_powers():
    return Powers(
        input_files=[
            "04_Powers.yaml",
            "04_Powers_SAMPLE.yaml",
            "05_Vulnerabilities.yaml",
        ]
    )


class Powers(YamlSpec):
    """Set of DofA powers

    Attributes:
        content (dict): input powers converted to human-readable mechanics
        categories (set): set of tuples - set((categ, subcat, subsubcat),(categ2))
    """

    def __init__(self, input_files="04_Powers_SAMPLE.yaml", limit_types: list = None):
        """Initialize. Load file, establish attributes

        Args:
            input_files (str, optional): String to local file or list of strings.
                Defaults to "04_Powers_SAMPLE.yaml".
            limit_types (list, optional): Only output items of provided types.
                Defaults to None, which means all of the following:
                ["Major", "Minor", "Passive", "Adversary", "House", "Free", "Vulny"]
        """
        input_files = ensure_list(ambiguous_item=input_files)
        super().__init__(
            input_files=[
                file for file in input_files if "Power" in file or "Vuln" in file
            ]
        )
        self._limit_types = limit_types or list_power_types
        self._as_dict = {}
        self._categories = {}
        self._categories_set = set()
        self._csv_fields = set()

    @property
    def as_dict(self) -> dict:
        """Return dict of {Name:Power class}"""
        if not self._as_dict and not self._tried_loading:
            self._build_contents(Power)
        return self._as_dict

    @property
    def categories(self) -> list:
        """Return set of tuples: (categories, subcategories)"""
        return self._build_categories(build_with="Category")

    @property
    def csv_fields(self):
        """Return a list of fields for the CSV output in the desired order"""
        if not self._csv_fields:
            _ = self.categories
        move_front = ["Type", "Name", "XP", "Mechanic"]
        return [
            *move_front,
            *[i for i in sorted(list(self._csv_fields)) if i not in move_front],
        ]


@dataclass(order=True)
class StatAdjust:
    """Class representing attrib or skill number to add (e.g., Dumb vulny redudces INT)"""

    Stat: str
    Value: int
    add: bool = True

    def __post_init__(self):  # Assumes only one stat is overridden
        if isinstance(self.add, str):
            self.add = self.add.lower() == "add"

    @property
    def text(self) -> str:
        """Return mechanic text of override: Add value to stat"""
        if self.add:
            return f"Add {self.Value} to {self.Stat}"
        return f"Replace {self.Stat} with {self.Value}"

    @property
    def flat(self) -> dict:
        """Return flatted dict {'Prereq_example': value} pairs for csv export"""
        return flatten_embedded(
            {"StatAdjust": {"Stat": self.Stat, "Value": self.Value, "Add": self.add}}
        )


@dataclass(order=True)
class Prereq:
    """Class representing prerequisites for a given power"""

    Role: str = None
    Level: int = None
    Skill: str = None
    Power: str = None

    @property
    def flat(self) -> dict:
        """Return flatted dict {'Prereq_example': value} pairs for csv export"""
        return flatten_embedded(dict(Prereq=self.__dict__))


@dataclass(order=True)
class Save:
    """Class representing a save triggered by a power"""

    Trigger: str = field(repr=False)
    Type: str
    DR: int = None
    Fail: str = field(default=None, repr=False)
    Succeed: str = field(default=None, repr=False)

    @property
    def text(self) -> str:
        """Given a Save dict from a power, return a readable sentence

        Returns:
            save_string (str): readable sentence detailing all features of a save
        """
        sentence = self.Trigger + ", target(s) make a "
        sentence += "DR " + str(self.DR) + " " if self.DR else ""
        sentence += list_to_or(self.Type) + " Save"
        sentence += (
            ""
            if self.DR
            else " with a DR of 3 minus half the Primary Skill of the Attacker"
        )
        output = [sentence, "On fail, target(s) " + self.Fail]
        output.append("On success, target(s) " + self.Succeed) if self.Succeed else None
        return ". ".join(output) + "."

    @property
    def flat(self) -> dict:
        """Return flatted dict {'Save_example': value} pairs for csv export"""
        return flatten_embedded({"Save": {"Type": self.Type, "DR": self.DR}})


@dataclass(order=True)
class Power:
    """Class representing a Power"""

    sort_index: str = field(init=False, repr=False)
    Name: str
    Type: str = field(repr=False)
    Category: Union[str, list] = field(repr=False)
    id: str = field(default="", repr=False)
    Description: str = field(default="")
    Mechanic: Union[str, list] = field(default="")
    Mechanic_raw: str = field(init=False, repr=False)
    XP: int = 0
    PP: int = field(default=0, repr=False)
    Range: int = 6
    AOE: str = None
    Targets: int = 1
    Draw: str = "None"
    Options: str = field(default=None, repr=False)
    Choice: str = field(default=None, repr=False)
    Damage: int = field(default=1, repr=True)
    ToHit: int = 1
    Save: dict = field(default=None, repr=False)
    Prereq: dict = field(default=None)
    StatAdjust: dict = field(default=None, repr=False)
    Tags: list = None

    def __post_init__(self):
        """Generate values not given on initialization"""
        self.sort_index = self.Type
        self.Category = ensure_list(self.Category)
        self.Save = Save(**self.Save) if self.Save else None
        self.Prereq = Prereq(**self.Prereq) if self.Prereq else None
        self.Damage = 0 if self.Type in ["Vulny", "Passive"] else self.Damage
        self.StatAdjusts = (
            self._compose_adjust(self.StatAdjust) if self.StatAdjust else None
        )
        self.Mechanic_raw = self.Mechanic
        self.Mechanic = self.merge_mechanic()
        self.upper_lower_int = self._get_upper_lower_int()

    def set_choice(self, choice: str = None):
        """Given a choice among options, revise merged mechanic property"""
        if not choice:
            return self

        self.Choice = choice
        self.Mechanic = self.merge_mechanic()
        return self

    def _get_upper_lower_int(self):
        upper_lower = self.Draw.upper()[0]
        return 2 if upper_lower == "U" else -2 if upper_lower == "L" else 0

    def _compose_adjust(self, stat_adjust_items):
        output = []
        for k, v in stat_adjust_items.items():
            if k.lower() in ["add", "replace"]:
                output += [StatAdjust(Stat=s, Value=val, add=k) for s, val in v.items()]
            else:
                output.append(StatAdjust(Stat=k, Value=v, add=True))
        return output

    def merge_mechanic(self) -> str:
        """Given power dict, merge all appropriate items into Mechanic

        Assumes Listed mechanics do not have PP/Save/StatAdjust

        Returns:
            power_merged (dict): power with all mechanic items combined.
        """
        if isinstance(self.Mechanic_raw, list):  # when mech are list, indent after 1st
            mech_bullets = self.Type + ". " + self.Mechanic_raw[0] + "\n"
            for mech_bullet in self.Mechanic_raw[1:]:
                mech_bullets += make_bullet(mech_bullet, 1)
            return mech_bullets[:-1]  # remove last space.
        else:
            output = []
            if self.Options:
                output.append(self.Choice if self.Choice else self.Options)
            if self.PP != 0:
                output.append(
                    "For " + list_to_or(self.PP) + " PP, " + self.Mechanic_raw
                )
            elif self.Mechanic_raw:
                output.append(self.Mechanic_raw)
            if self.StatAdjust:
                output += [adjust.text for adjust in self.StatAdjusts]
            if self.Save:
                output.append(self.Save.text)
            return ". ".join([self.Type, *output])

    @property
    def _mechanic_for_item(self) -> str:
        choice = self.Choice + ". " if self.Choice else ""
        return choice + self.Mechanic_raw

    @property
    def markdown(self) -> str:
        """Concatenate info relevant to markdown export"""
        output = f"\n**{self.Name}**\n\n"
        for f in fields(self):
            if attrgetter(f.name)(self) != f.default and f.name != "Name" and f.repr:
                if f.name == "Prereq":
                    for key, value in self.Prereq.flat.items():
                        title = key.replace("_", " ")
                        output += make_bullet(f"{title}: {value}")
                elif f.name == "Damage" and self.Type in ["Vulny", "Passive"]:
                    continue
                else:
                    output += make_bullet(
                        f"{f.name}: {list_to_or(attrgetter(f.name)(self))}"
                    )
        return output

    @property
    def csv_dict(self) -> dict:
        """Set of information to be added as a row in the output csv"""
        removed = [
            "sort_index",
            "Mechanic_raw",
            "Options",
            "Choice",
            "StatAdjust",
            "Save",
            "Prereq",
            "Description",
        ]
        output = {k: v for k, v in self.__dict__.items() if k not in removed}
        for attrib in [self.StatAdjusts, self.Save, self.Prereq]:
            for a in ensure_list(attrib):
                if a:
                    output.update({**a.flat})
        return output

    def __repr__(self):
        """Print non-default power items with repr property and linebreaks"""
        return my_repr(self)
