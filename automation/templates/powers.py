from dataclasses import dataclass, field, fields
from operator import attrgetter
from typing import Union

from ..utils import (
    ensure_list,
    flatten_embedded,
    list_to_or,
    make_bullet,
    my_repr,
    sort_dict,
)
from .yaml_spec import YamlSpec

list_power_types = ["Passive", "Vulny", "Free", "Major", "Minor", "Adversary", "House"]


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
        self._as_list = []
        self._categories = {}
        self._categories_set = set()
        self._csv_fields = set()
        self._type_dict = {k: [] for k in self._limit_types}

    @property
    def as_list(self):
        """Return list of powers"""
        if not self._as_list:
            self._as_list = [
                Power(Name=k, **v)
                for k, v in self._raw_data.items()
                if v.get("Type", None) in self._limit_types
            ]
        return self._as_list

    @property
    def as_dict(self) -> dict:
        """Return dict of {Name:Power class}"""
        if not self._as_dict:
            self._as_dict = {
                k: Power(Name=k, **v)
                for k, v in self._raw_data.items()
                if v.get("Type", None) in self._limit_types
            }
        return self._as_dict

    @property
    def categories(self) -> list:
        """Return set of tuples: (categories, subcategories)"""
        if not self._categories:
            for p in self.as_list:
                cat_tuple = tuple(p.Category)
                self._categories.setdefault(cat_tuple, [])
                self._categories[cat_tuple].append(p.Name)
                self._categories_set.add(cat_tuple)
                self._csv_fields = self._csv_fields.union(list(p.csv_dict.keys()))
        return sort_dict(self._categories, sorted(self._categories_set))

    @property
    def type_dict(self) -> dict:
        """Cache of powers by type {Major: [a, b]}"""
        if not any(self._type_dict.values()):
            for p in self.as_list:
                self._type_dict[p.Type].append(p.Name)
        return self._type_dict

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
class StatOverride:
    """Class representing attrib or skill number to add (e.g., Dumb vulny redudces INT)"""

    as_dict: dict = field(repr=False)
    Stat: str = field(init=False)
    Value: int = field(init=False)

    def __post_init__(self):  # Assumes only one stat is overridden
        self.Stat = list(self.as_dict.keys())[0]
        self.Value = list(self.as_dict.values())[0]

    @property
    def text(self) -> str:
        """Return mechanic text of override: Add value to stat"""
        return f"Add {self.Value} to {self.Stat}"

    @property
    def flat(self) -> dict:
        """Return flatted dict {'Prereq_example': value} pairs for csv export"""
        return flatten_embedded(
            {"StatOverride": {"Stat": self.Stat, "Value": self.Value}}
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
    DR: int = 3
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
    Description: str = field(default="")
    Mechanic: Union[str, list] = field(default="")
    Mechanic_raw: str = field(init=False, repr=False)
    XP: int = ""
    PP: int = field(default=0, repr=False)
    Range: int = 6
    AOE: str = None
    Target: int = 1
    Options: str = field(default=None, repr=False)
    Choice: str = field(default=None, repr=False)
    Damage: int = 1
    ToHit: int = 1
    Save: dict = field(default=None, repr=False)
    Prereq: dict = field(default=None)
    StatOverride: dict = field(default=None, repr=False)
    Tags: list = None

    def __post_init__(self):
        """Generate values not given on initialization"""
        self.sort_index = self.Type
        self.Category = ensure_list(self.Category)
        self.Save = Save(**self.Save) if self.Save else None
        self.Prereq = Prereq(**self.Prereq) if self.Prereq else None
        self.StatOverride = (
            StatOverride(self.StatOverride) if self.StatOverride else None
        )
        self.Mechanic_raw = self.Mechanic
        self.Mechanic = self.merge_mechanic()

    def set_choice(self, choice: str):
        """Given a choice among options, revise merged mechanic property"""
        self.Choice = choice
        self.Mechanic = self.merge_mechanic()
        return self

    def merge_mechanic(self) -> str:
        """Given power dict, merge all appropriate items into Mechanic

        Assumes Listed mechanics do not have PP/Save/StatOverride

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
            if self.StatOverride:
                output.append(self.StatOverride.text)
            if self.Save:
                output.append(self.Save.text)
            return ". ".join([self.Type, *output])

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
            "StatOverride",
            "Save",
            "Prereq",
            "Description",
        ]
        output = {k: v for k, v in self.__dict__.items() if k not in removed}
        for attrib in [self.StatOverride, self.Save, self.Prereq]:
            if attrib:
                output.update({**attrib.flat})
        return output

    def __repr__(self):
        """Print non-default power items with repr property and linebreaks"""
        return my_repr(self)
