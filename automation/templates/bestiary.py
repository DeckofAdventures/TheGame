from collections import OrderedDict
from dataclasses import dataclass, field, fields
from math import floor
from operator import attrgetter
from typing import List

from ..utils import (
    ensure_list,
    flatten_embedded,
    logger,
    make_bullet,
    make_header,
    my_repr,
    sort_dict,
)
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
list_beast_types = ["PC", "Dealer", "NPC", "Boss", "Companion"]
list_boss_phases = ["One", "Two", "Three", "Four", "Five", "Six"]


class Bestiary(YamlSpec):
    """Bestiary class - load all or a specific type from yamls

    Example:
        from automation.templates.bestiary import Bestiary, Beast
        Bestiary().as_dict['MyPC'] # Returns Beast object
    """

    # TODO: check stat overrides before printing
    def __init__(self, input_files="06_Bestiary_SAMPLE.yaml", limit_types: list = None):
        input_files = [file for file in ensure_list(input_files) if "Best" in file]
        super().__init__(input_files=input_files)
        self._tried_loading = False
        self._limit_types = limit_types or list_beast_types
        self._as_list = []
        self._as_dict = {}
        self._categories = {}
        self._categories_set = set()
        self._csv_fields = set()

    def _build_contents(self):
        """Loop over items in the raw dict format. Generate list and dict versions"""
        self._tried_loading = True
        for k, v in self.raw_data.items():
            if v.get("Type", None) in self._limit_types:
                beast = Beast(Name=k, **v)
                self.as_list.append(beast)
                self._as_dict.update({k: beast})

    @property
    def as_list(self):
        """Beasts in a list of the Beast class"""
        if not self._as_list and not self._tried_loading:
            self._build_contents()
        return self._as_list

    @property
    def as_dict(self) -> dict:
        """Beasts as a dict, callable via string name, value as Beast class

        Return readable dict with Mechanics collapsed.

        """
        if not self._as_dict and not self._tried_loading:
            self._build_contents()
        return self._as_dict

    @property
    def categories(self) -> OrderedDict:
        """Return OrderedDict with {tuple(Type) : [list of beasts]} as key value pairs"""
        if not self._categories:
            for b in self.as_list:
                cat_tuple = tuple([b.Type])  # Differs from powers
                self._categories.setdefault(cat_tuple, [])
                self._categories[cat_tuple].append(b.Name)
                self._categories_set.add(cat_tuple)
                self._csv_fields = self._csv_fields.union(list(b.csv_dict.keys()))
        return sort_dict(self._categories, sorted(self._categories_set))

    @property
    def csv_fields(self) -> list:
        """Return a list of fields for the CSV output in the desired order"""
        if not self._csv_fields:
            _ = self.categories
        move_front = [
            "Type",
            "Name",
            "Level",
            "Role",
            "Descriptions",
            "Pronouns",
            "RestCards",
            "Speed",
            "HP",
            "PP",
        ]
        return [
            *move_front,
            *[i for i in sorted(list(self._csv_fields)) if i not in move_front],
        ]


@dataclass(order=True)
class Attribs:
    """Class to represent a beast's Attributes"""

    AGL: int = 0
    CON: int = 0
    GUT: int = 0
    INT: int = 0
    STR: int = 0
    VIT: int = 0

    @property
    def as_tuple(self):
        """Just a set of all items as int (0, 1, 2...)"""
        # TODO: Align match skills equivalent
        return (self.AGL, self.CON, self.GUT, self.INT, self.STR, self.VIT)

    @property
    def flat(self) -> dict:
        """Return flatted dict {'Attrib_example': value} pairs for csv export"""
        return flatten_embedded(dict(Attrib=self.__dict__))

    def __repr__(self):
        """Print non-default beast items with repr property and linebreaks"""
        return my_repr(self, seperator=", ", indent=0)


@dataclass(order=True)
class Skills:
    """Class to represent a beast's Skills"""

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
    def as_tuple(self):
        """List of tuples (Skill, value)"""
        output = []
        for f in fields(self):
            value = attrgetter(f.name)(self)
            output.append((f.name, value))
        return output

    @property
    def non_defaults(self):
        """Return as_tuple above, but only non-default items"""
        output = []
        for f in fields(self):
            value = attrgetter(f.name)(self)
            if value != f.default:
                output.append((f.name, value))
        return output

    @property
    def flat(self) -> dict:
        """Return flatted dict {'Skill_example': value} pairs for csv export"""
        return flatten_embedded(dict(Skill=self.__dict__))

    def __repr__(self):
        """Print non-default beast items with repr property and linebreaks"""
        return my_repr(self, seperator=", ", indent=0)


@dataclass(order=True)
class Phase:
    """Class for representing boss phases"""

    # TODO: Should allies be typed as Beast? Recursive?
    Name: str
    Order: int = field(repr=False)
    HP: int = 1
    Allies: List[str] = field(default=None)

    def __repr__(self):
        """Print non-default beast items with repr property and linebreaks"""
        return my_repr(self, indent=1)


@dataclass(order=True)
class Beast:
    """Class for representing all creatures (e.g., PCs, bosses, etc.)"""

    # TODO:
    #  - Add validator to confirm valid PC
    #  - Accept list of items, the values of which may impact other stats

    sort_index: str = field(init=False, repr=False)
    Type: str
    Name: str = None  # Must be unique. Do we need a diff unique ID? Name+Level?
    Pronouns: str = None
    Role: str = None
    Level: int = 1
    HP: int = 1
    AP: int = 1
    AR: int = field(default=None)
    PP: int = 0  # TODO: migrate to post-init, sum PP from all available powers
    Speed: int = 6
    Primary_Skill: str = field(default=None)
    Attribs: dict = field(default=None)
    Skills: dict = field(default=None)
    Powers: dict = field(default=None, repr=False)
    Powers_list: list = field(default_factory=list, repr=False)
    Phases: list = field(default=None)
    Description: str = ""

    def __post_init__(self):
        """Generate values not given on initialization"""
        self.sort_index = self.Type
        self.Powers = self.fetch_powers()
        self.Powers_list = [p for p in self.Powers.values()]
        self.Attribs = Attribs(**self.Attribs) if self.Attribs else None
        self.Skills = Skills(**self.Skills) if self.Skills else None
        self.Phases = self.fetch_phases() if self.Phases else None
        self.AR = self.AR if self.AR else (3 - floor(self.Attribs.AGL / 2))  # default
        self.HP_Max = self.HP  # assume providing max when initializing
        self.AP_Max = self.AP
        self.AR_Max = self.AR
        self.PP_Max = self.PP
        self.Speed_Max = self.Speed
        self.RestCards = self.HP
        self.RestCards_Max = self.HP

        self.override_stats()

    def fetch_powers(self) -> dict:
        """Given a list of powers by name, generate a dict {Name: Power class}"""
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

    def fetch_phases(self) -> list:
        """Turn phase input into list of phase class items"""
        output = []
        for order, (phase, phase_dict) in enumerate(self.Phases.items()):
            output.append(Phase(Name=phase, Order=order, **phase_dict))
        return output

    def override_stats(self) -> None:
        """Check for any StatOverride powers. Apply overrides, sum with current value"""
        # TODO: Also use this to take attribs and apply them to corresponding skills?
        for power in self.Powers.values():
            override = getattr(power, "StatOverride", None)
            if override:
                attrib_or_skill = (
                    self.Attribs if override.Stat in list_attribs else self.Skills
                )
                setattr(
                    attrib_or_skill,
                    override.Stat,
                    attrgetter(override.Stat)(attrib_or_skill) + override.Value,
                )

    def _md_stats_table(self) -> str:
        """Generate string for stats table included in markdown bestiary"""
        top_lvl_stats = (self.HP, self.AP, self.AR, self.PP, self.Speed)
        output = (
            f"### {self.Type}: Level {self.Level}\n\n"
            + "| HP | AP | AR | PP | SPD |\n"
            + "| -- | -- | -- | -- | --- |\n"
            + "| %s  | %s  | %s  | %s  |  %s  |\n\n" % top_lvl_stats
            + "| AGL | CON | GUT | INT | STR | VIT |\n"
            + "| --- | --- | --- | --- | --- | --- |\n"
            + "|  %s  |  %s  |  %s  |  %s  |  %s  |  %s  |\n" % self.Attribs.as_tuple
        )
        if self.Skills:
            if self.Skills.non_defaults:
                output += (
                    "\n**Skills**: "
                    + ", ".join(["%s %s" % s for s in self.Skills.non_defaults])
                    + "\n"
                )
        return output

    def _md_actions(self) -> str:
        """Generate markdown list of powers separated by type"""
        output = make_header("Powers", 2)
        for power_type in list_power_types:
            powers_subset = [
                make_bullet(f"**{p.Name}**: {p.Mechanic}")
                for p in self.Powers_list
                if getattr(p, "Type", "None") == power_type
            ]
            if powers_subset:
                output += make_header(power_type, 3) + "\n" + "".join(powers_subset)
        return output

    def _md_phases(self) -> str:
        """Generate markdown string for phases"""
        if not self.Phases:
            return ""
        output = make_header("Phases", 2)
        for phase in self.Phases:
            output += make_header(f"Phase {phase.Name}", 3) + "\n"
            output += f"Set HP to {phase.HP} and add the following all(y/ies):\n\n"
            output += "".join([make_bullet(ally) for ally in phase.Allies])
        return output

    @property
    def markdown(self) -> str:
        """Concatenate info relevant to markdown export"""
        return (
            make_header(self.Name, 1)
            + "\n"
            + self._md_stats_table()
            + self._md_actions()
            + self._md_phases()
        )

    @property
    def _pc_sheet_stats(self) -> tuple:
        """Generate top-level stats for PC sheet"""
        # TODO: Modify so it aligns with how markdown takes top_level_stats
        # Why separate AR for the PC sheet but not the markdown?
        return [
            ("HP", self.HP, self.HP_Max),
            ("AP", self.AP, self.AP_Max),
            ("PP", self.PP, self.PP_Max),
            ("Speed", self.Speed, self.Speed_Max),
            ("Rest Cards", self.RestCards, self.RestCards_Max),
        ]

    def _html(self, items=None):
        """Generate html from jinja template representing PC"""
        import jinja2  # intentional lazy import

        assert self.Type in ["PC", "Dealer"], "Can only make html for PCs"

        default_items = (
            self.Items
            if self.Items
            else [
                {"name": "Armor", "quantity": "1", "info": "Chain Mail. AR 2."},
                {"name": "Shield", "quantity": "1", "info": "Heavy Shield. 2 AP."},
                {"name": "Shortsword", "quantity": "1", "info": "1 damage. 1 handed."},
                {"name": "Maul", "quantity": "1", "info": "2 damage. 2 handed."},
            ]
        )

        return (
            jinja2.Environment(loader=jinja2.FileSystemLoader("./automation/_input/"))
            .get_template("PC_template.html")
            .render(pc=self, items=items if items else default_items)
        )

    def make_pc_html(self, output_filename: str = None, items: list = None):
        """Save pc html as html file

        Args:
            output_filename (str, optional): Filename, no extension. Always in _output
                folder. Defaults to PC_{Name}_level_{Level}.
            items (list, optional): List of dicts with item name, quantity and info.
                Defaults a set of items store in the _html function.
        """
        if not output_filename:
            output_filename = f"PC_{self.Name}_level_{self.Level}"
        output_file = "./automation/_output/" + output_filename + ".html"
        with open(output_file, "w") as f:
            f.write(self._html(items))
        logger.info(f"Wrote HTML {output_file}")

    def make_pc_img(self, output_filename: str = None, items: list = None):
        """Save pc html as png file

        Args:
            output_filename (str, optional): Filename, no extension. Always in _output
                folder. Defaults to PC_{Name}_level_{Level}.
            items (list, optional): List of dicts with item name, quantity and info.
                Defaults a set of items store in the _html function.
        """
        from html2image import Html2Image

        if not output_filename:  # TODO: remove repetition with make_pc_html function
            output_filename = f"PC_{self.Name}_level_{self.Level}"
        output_filename += ".png"
        hti = Html2Image()
        hti.output_path = "./automation/_output/"
        hti.size = (950, 1200)
        hti.screenshot(
            html_str=self._html(items),
            save_as=output_filename,
        )
        logger.info(f"Wrote HTML as image: {output_filename}")

    @property
    def csv_dict(self) -> dict:
        """Set of information to be added as a row in the output csv"""
        removed = [
            "sort_index",
            "Powers",
            "Powers_list",
            "Attribs",
            "Skills",
            "Phases",
            "_html",
        ]
        output = {k: v for k, v in self.__dict__.items() if k not in removed}
        for attrib in [self.Attribs, self.Skills]:
            if attrib:
                output.update({**attrib.flat})
        return output

    def __repr__(self):
        """Print non-default beast items with repr property and linebreaks"""
        return my_repr(self)
