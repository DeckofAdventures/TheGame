from dataclasses import dataclass, field, fields
from operator import attrgetter

from ..utils import ensure_list, flatten_embedded, list_to_or, make_bullet, my_repr
from .powers import Prereq, Save, StatAdjust
from .yaml_spec import YamlSpec

list_item_types = ["General", "Consumable", "Tool", "Armor", "Weapon", "Shield"]
list_item_rarities = ["Common", "Uncommon", "Rare", "Legendary"]


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

    @property
    def flat(self) -> dict:
        """Return flatted dict {'Prereq_example': value} pairs for csv export"""
        return flatten_embedded(dict(Prereq=self.__dict__))


@dataclass(order=True)
class Item:
    """Class representing an item"""

    sort_index: str = field(init=False, repr=False)
    id: str
    Name: str
    Type: str = field(default="General")
    Rarity: str = field(default="Common")
    Description: str = field(default="")
    Use: dict = field(default=None, repr=False)
    Range: int = 6
    AOE: str = None
    Damage: int = 1
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
        self.Prereq = Prereq(**self.Use) if self.Use else None
        self.StatAdjust = (
            [StatAdjust(s) for s in ensure_list(self.StatAdjust)]
            if self.StatAdjust
            else None
        )

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
            "StatAdjust",
            "Save",
            "Prereq",
            "Description",
        ]
        output = {k: v for k, v in self.__dict__.items() if k not in removed}
        for attrib in [self.StatAdjust, self.Save, self.Prereq]:
            if attrib:
                output.update({**attrib.flat})
        return output

    def __repr__(self):
        """Print non-default power items with repr property and linebreaks"""
        return my_repr(self)
