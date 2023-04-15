from dataclasses import dataclass, field, fields
from operator import attrgetter

from ..utils import (
    ensure_list,
    flatten_embedded,
    list_to_or,
    logger,
    make_bullet,
    my_repr,
)
from .powers import Prereq, Save, StatAdjust, list_power_types, load_all_powers
from .yaml_spec import YamlSpec

list_item_types = ["General", "Consumable", "Tool", "Armor", "Weapon", "Shield"]
list_item_rarities = ["Common", "Uncommon", "Rare", "Legendary"]
list_currencies = ["dp", "gp", "sp", "cp"]
all_powers = load_all_powers().as_dict


def load_all_items():
    return Items(input_files=["07_Items.yaml", "07_Items_SAMPLE.yaml"])


class Items(YamlSpec):
    """Set of DofA Items"""

    def __init__(self, input_files="07_Items_SAMPLE.yaml", limit_types: list = None):
        """Initialize. Load file, establish attributes

        Args:
            input_files (str, optional): String to local file or list of strings.
                Defaults to "04_Powers_SAMPLE.yaml".
            limit_types (list, optional): Only output items of provided types.
                Defaults to None, which means all of the following:
                ["General", "Consumable", "Tool", "Armor", "Weapon", "Shield"]
        """
        input_files = ensure_list(ambiguous_item=input_files)
        super().__init__(
            input_files=[file for file in input_files if "item" in file.lower()]
        )
        self._limit_types = limit_types or list_item_types
        self._as_dict = {}
        self._categories = {}
        self._categories_set = set()
        self._csv_fields = set()
        self._type_dict = {k: [] for k in self._limit_types}

    @property
    def as_dict(self) -> dict:
        """Return dict of {Name:Item class}"""
        if not self._as_dict and not self._tried_loading:
            self._build_contents(Item, "Rarity")
        return self._as_dict

    @property
    def categories(self) -> list:
        """Return set of tuples: (categories, subcategories)"""
        return self._build_categories(build_with="Type")

    @property
    def csv_fields(self):
        """Return a list of fields for the CSV output in the desired order"""
        if not self._csv_fields:
            _ = self.categories
        move_front = ["Type", "Name", "Rarity", "Cost"]
        return [
            *move_front,
            *[i for i in sorted(list(self._csv_fields)) if i not in move_front],
        ]


@dataclass(order=True)
class Use:
    """Class representing prerequisites for a given power"""

    Time: str = None
    Effect: int = None
    Duration: str = None
    Limit: str = None
    Power: str = None
    PowerFull: str = field(default=None, repr=False)
    PowerMechanic: str = field(default=None, repr=False)

    def __post_init__(self):
        """After initializing, run checks.

        Checks:
            1. Time is either a valid action or numeric prefix before another word
            2. If Limit is just a number add 'times'
            3. If passed a Power name (with option), set option and retrieve power.
            4. If passed both Power and Effect, log warning. Default to power on print.
        """
        if self.Time:
            dur, measure = self.Time.lower().split(" ")
            if measure == "action" and dur not in map(str.lower, list_power_types):
                logger.warning(f"{dir} not a known action type.")
            elif measure != "action" and not dur.isnumeric():
                logger.warning(f"Expected number for non-action use time: {self.Time}")
        if self.Limit and self.Limit.isnumeric():
            self.Limit += "times"
        if self.Power:
            # Handles multiple powers listed, without choices
            if isinstance(self.Power, list) and not isinstance(self.Power[0], dict):
                self.Power = "Choose the effects of " + list_to_or(self.Power)
                choice = None  # no full power mechanic
            else:
                if isinstance(self.Power, list):  # handles 1 Power: choice
                    power_name, choice = next(iter(self.Power[0].items()))
                else:  # handles 1 Power
                    power_name, choice = self.Power, None

                power_lookup = all_powers.get(power_name, None)

                if not power_lookup:  # If unknown power
                    self.Power = power_name
                    logger.warning(f"Item invokes unknown Power: {power_name}")
                else:
                    self.PowerFull = all_powers[power_name].set_choice(choice)
                    self.Power = self.PowerFull.Name
                    self.PowerMechanic = self.PowerFull._mechanic_for_item
        if self.Effect and self.Power:
            logger.warning(
                f"For items, use effect or power, not both: {self.Effect}, {power_name}"
            )

    @property
    def non_defaults(self):
        """Return non-default items with field.repr==True"""
        return {
            f.name: attrgetter(f.name)(self)
            for f in fields(self)
            if f.repr and (attrgetter(f.name)(self) is not None)
        }

    @property
    def flat(self) -> dict:
        """Return a single dictionary with Use_X as key for each Use field"""
        return flatten_embedded(dict(Use=self.non_defaults))

    @property
    def merged_string(self) -> str:
        """Return a single string representing item, like MergedMechanic for Power"""
        output = f"Up to {self.Limit}, " if self.Limit else ""
        output += f"take {self.Time} to activate. " if self.Time else ""
        output = output.capitalize()
        output += self.PowerMechanic or self.Effect or self.Power
        output += "." if output[-1] != "." else ""
        output += f" Lasts {self.Duration}." if self.Duration else ""
        return output

    def __repr__(self) -> str:
        return my_repr(self)


@dataclass(order=True)
class Cost:
    """Item cost split by number and currency. Useful for csv comparisons"""

    raw: str = field(repr=False)
    Value: int = field(init=False)
    Denomination: str = field(init=False)

    def __post_init__(self):
        """Check that currency is in list of valid currencies (e.g., gp, cp)"""
        self.Value, self.Denomination = self.raw.split(" ")
        if self.Denomination not in list_currencies:
            logger.warning(f"Unexpected currency type: {self.Denomination}")

    @property
    def flat(self) -> dict:
        """Return single dictionary with {Cost_Value: Value, Cost_Denom: denom}"""
        return flatten_embedded(dict(Cost=self.__dict__))

    def __repr__(self) -> str:
        """When printing, just use raw form e.g. 2 gp"""
        return self.raw


@dataclass(order=True)
class Item:
    """Class representing an item"""

    sort_index: str = field(init=False, repr=False)
    id: str = field(repr=False)
    Name: str
    Type: str = field(default="General", repr=False)
    Cost: str = None
    Rarity: str = field(default="Common")
    Description: str = field(default="")
    Use: dict = field(default=None)
    Range: int = 6
    AOE: str = None
    Damage: int = 0
    Save: dict = field(default=None, repr=False)
    Prereq: dict = field(default=None)
    StatAdjust: dict = field(default=None, repr=False)
    Tags: list = None

    def __post_init__(self):
        """Generate values not given on initialization"""
        self.sort_index = self.Type
        self.Save = Save(**self.Save) if self.Save else None
        self.Prereq = Prereq(**self.Prereq) if self.Prereq else None
        self.Use = Use(**self.Use) if self.Use else None
        self.StatAdjusts = (
            self._compose_adjust(self.StatAdjust) if self.StatAdjust else None
        )
        self.Cost = Cost(self.Cost) if self.Cost else None
        if self.StatAdjusts and not self.Description:
            self.Description = ". ".join([s.text for s in self.StatAdjusts]) + "."

    def _compose_adjust(self, stat_adjust_items) -> list:
        """Compose list of StatAdjust class objects, respecting Add vs. Replace"""
        output = []
        for k, v in stat_adjust_items.items():
            if k.lower() in ["add", "replace"]:
                output += [StatAdjust(Stat=s, Value=val, add=k) for s, val in v.items()]
            else:
                output.append(StatAdjust(Stat=k, Value=v, add=True))
        return output

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
                elif f.name == "Cost":
                    output += make_bullet(f"Cost: {self.Cost.raw}")
                elif f.name == "Use":
                    output += make_bullet(f"Use: {self.Use.merged_string}")
                elif f.name == "Tags":
                    output += make_bullet(f"Tags: {', '.join(ensure_list(self.Tags))}")
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
            "StatAdjust",
            "StatAdjusts",
            "Prereq",
            "Description",
            "id",
            "Use",
        ]
        output = {k: v for k, v in self.__dict__.items() if k not in removed}
        for attrib in [self.Prereq, self.Use]:
            for a in ensure_list(attrib):
                if a:
                    output.update({**a.flat})
        return output

    def __repr__(self):
        """Print non-default items with repr property and linebreaks"""
        return my_repr(self)
