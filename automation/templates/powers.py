from dataclasses import dataclass, field, fields
from operator import attrgetter
from typing import Union

from ..utils import (  # logger,
    ensure_list,
    flatten_embedded,
    list_to_or,
    make_bullet,
    make_header,
    my_repr,
)
from .yaml_spec import YamlSpec

list_power_types = ["Passive", "Vulny", "Major", "Minor", "Adversary", "Free", "House"]


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
                ["Major", "Minor", "Passive", "Adversary", "House", "Vulny"]

        Attributes:
            _data (dict): raw input data
            _categories (set): all power categories
            _template (dict): Template item from input data
            _content (dict): data restructured to sentences.
            _stem (str): Input file name no extension
            _name (str): Last string of stem when split by `_`
            _limit_types (list): See arg above
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

    @property
    def as_list(self):
        if not self._as_list:
            self._as_list = [
                Power(Name=k, **v)
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
        """Return set of tuples: (categories, subcategories)"""
        if not self._categories:
            for p in self._as_list:  # get set of sub/categories for TOC later
                self._categories.add(tuple(p.Category))
        return sorted(self._categories)


@dataclass(order=True)
class StatOverride:
    as_dict: dict = field(repr=False)
    Stat: str = field(init=False)
    Value: int = field(init=False)

    def __post_init__(self):  # Assumes only one stat is overridden
        self.Stat = list(self.as_dict.keys())[0]
        self.Value = list(self.as_dict.values())[0]

    @property
    def text(self) -> str:
        return f"Set {self.Stat} to {self.Value}"


@dataclass(order=True)
class Prereq:
    Role: str = None
    Level: int = None
    Skill: str = None
    Power: str = None

    @property
    def flat(self) -> dict:
        return flatten_embedded(dict(Prereq=self.__dict__))


@dataclass(order=True)
class Save:
    Trigger: str
    Type: str
    Fail: str
    DR: int = 3
    Succeed: str = None

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
        return ". ".join(output)


@dataclass(order=True)
class Power:
    sort_index: str = field(init=False, repr=False)
    Name: str
    Type: str = field(repr=False)
    Category: Union[str, list] = field(repr=False)
    Description: str = field(default="")
    Mechanic: Union[str, list] = field(default="", repr=False)
    Merged_Mechanic: str = field(init=False)
    XP: int = 1
    PP: int = 0
    Range: int = 6
    AOE: str = None
    Target: int = 1
    Options: str = field(default=None, repr=False)
    Choice: str = field(default=None, repr=False)
    Damage: int = 1
    ToHit: int = 1
    Save: dict = field(default=None, repr=False)
    Prereq: dict = field(default=None, repr=False)
    StatOverride: dict = field(default=None, repr=False)
    Tags: list = None

    def __post_init__(self):
        self.sort_index = self.Type
        self.Category = ensure_list(self.Category)
        self.Save = Save(**self.Save) if self.Save else None
        self.Prereq = Prereq(**self.Prereq) if self.Prereq else None
        self.StatOverride = (
            StatOverride(self.StatOverride) if self.StatOverride else None
        )
        self.Merged_Mechanic = self.merge_mechanic()

    def set_choice(self, choice: str):
        self.Choice = choice
        self.Merged_Mechanic = self.merge_mechanic()
        return self

    def merge_mechanic(self):
        """Given power dict, merge all appropriate items into Mechanic

        Returns:
            power_merged (dict): power with all mechanic items combined.
        """
        if isinstance(self.Mechanic, list):  # when mech are list, indent after 1st
            mech_bullets = self.Mechanic[0] + "\n"
            for mech_bullet in self.Mechanic[1:]:
                mech_bullets += make_bullet(mech_bullet)
            return mech_bullets[:-1]  # remove last space.
        else:  # Listed mechanics do not have PP/Save/StatOverride
            output = []
            if self.Options:
                output.append(self.Choice if self.Choice else self.Options)
            if self.PP != 0:
                output.append("For " + list_to_or(self.PP) + " PP, " + self.Mechanic)
            else:
                output.append(self.Mechanic)
            if self.StatOverride:
                output.append(self.StatOverride.text)
            if self.Save:
                output.append(self.Save.text)
            return ". ".join([self.Type, *output])

    def markdown(self, level=2):
        output = make_header(self.Name, level=level) + "\n"
        for f in fields(self):
            if attrgetter(f.name)(self) != f.default and f.repr:
                output += make_bullet(f"{f.name}: {attrgetter(f.name)(self)}")
        return output

    def __repr__(self):
        return my_repr(self)
