from collections import OrderedDict
from dataclasses import dataclass, field, fields
from operator import attrgetter
from typing import List

from ..utils import (
    ensure_list,
    flatten_embedded,
    logger,
    make_bullet,
    make_header,
    my_repr,
)
from .powers import list_power_types, load_all_powers
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
list_stats = {list_attribs[n]: list_skills[n * 2 : n * 2 + 2] for n in range(5)}
list_beast_types = ["PC", "Dealer", "NPC", "Boss", "Companion"]
list_boss_phases = ["One", "Two", "Three", "Four", "Five", "Six"]

all_powers = load_all_powers().as_dict


class Bestiary(YamlSpec):
    """Bestiary class - load all or a specific type from yamls

    Example:
        from automation.templates.bestiary import Bestiary, Beast
        Bestiary().as_dict['MyPC'] # Returns Beast object
    """

    # TODO: check stat overrides before printing
    def __init__(self, input_files="06_Bestiary_SAMPLE.yaml", limit_types: list = None):
        input_files = [
            file
            for file in ensure_list(input_files)
            if "best" in file.lower() or "pc" in file.lower()
        ]
        super().__init__(input_files=input_files)
        self._tried_loading = False
        self._limit_types = limit_types or list_beast_types
        self._as_dict = {}
        self._categories = {}
        self._categories_set = set()
        self._csv_fields = set()

    @property
    def as_dict(self) -> dict:
        """Beasts as a dict, callable via string name, value as Beast class"""
        if not self._as_dict and not self._tried_loading:
            self._build_contents(Beast, "Level")
        return self._as_dict

    @property
    def categories(self) -> OrderedDict:
        """Return OrderedDict with {tuple(Type) : [list of beasts]} as key value pairs"""
        return self._build_categories(build_with="Type")

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

    Finesse: int = None
    Stealth: int = None
    Bluffing: int = None
    Performance: int = None
    Knowledge: int = None
    Investigation: int = None
    Detection: int = None
    Craft: int = None
    Athletics: int = None
    Brute: int = None

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
    Allies: List[str] = None

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
    id: str = field(repr=False)
    Name: str = None
    Pronouns: str = None
    Role: str = None
    Level: int = 1
    HP: int = 1
    AP: int = 1
    AR: int = None
    PP: int = 0
    Speed: int = 6
    Primary_Skill: str = None
    Attribs: dict = None
    Skills: dict = None
    Powers: dict = field(default=None, repr=False)
    Phases: list = None
    Items: dict = field(default_factory=dict)
    Description: str = ""

    def __post_init__(self):
        """Generate values not given on initialization"""
        if self.PP != 0:
            logger.warning("Yaml PP is no longer used. Now summed from powers")
        self.sort_index = self.Type
        self.Name = self.Name if self.Name else self.id
        self.Powers, self.PP, self._powers_XP = self.fetch_powers()
        self.Attribs = Attribs(**self.Attribs) if self.Attribs else None
        self.Skills = Skills(**self.Skills) if self.Skills else None
        self.adjust_stats()
        self.Phases = self.fetch_phases() if self.Phases else None
        self.AR = self.AR if self.AR else (3 - (self.Attribs.AGL // 2))  # default
        self.HP_Max = self.HP  # assume providing max when initializing
        self.AP_Max = self.AP
        self.AR_Max = self.AR
        self.PP_Max = self.PP
        self.Speed_Max = self.Speed
        self.RestCards = self.HP
        self.RestCards_Max = self.HP

    def fetch_powers(self) -> dict:
        """Given a list of powers by name, generate a dict {Name: Power class}"""
        output_powers = {}
        powers_pp = 0
        powers_xp = 0
        self.Powers = ensure_list(self.Powers)
        for power in self.Powers:
            if isinstance(power, dict):
                power_name, choice = next(iter(power.items()))
            else:
                power_name, choice = power, None
            this_power = all_powers.get(power_name, None)
            if not this_power:
                logger.warning(f"{self.Name} has a power not in yaml: {power}")
                continue

            output_powers.update({power_name: this_power.set_choice(choice)})
            powers_pp += max(ensure_list(this_power.PP))
            powers_xp += this_power.XP
        return output_powers, powers_pp, powers_xp

    def fetch_phases(self) -> list:
        """Turn phase input into list of phase class items"""
        output = []
        for order, (phase, phase_dict) in enumerate(self.Phases.items()):
            output.append(Phase(Name=phase, Order=order, **phase_dict))
        return output

    def _adjust_stats_via_attribs(self):
        for attrib, skills in list_stats.items():
            for skill in skills:
                if not getattr(self.Skills, skill):
                    logger.debug(
                        f"Set {self.Name} {skill} to {getattr(self.Attribs, attrib)}"
                    )
                    setattr(self.Skills, skill, getattr(self.Attribs, attrib))

    def _adjust_stats_powers_items(self):
        adjs = [getattr(power, "StatAdjusts", []) for power in self.Powers.values()]
        adjs += [getattr(item, "StatAdjusts", []) for item in self.Items.values()]
        adjs = [item for adj in adjs if adj is not None for item in adj]  # Unpack lists

        for adjust in adjs:
            if adjust.Stat in list_attribs:
                adjusted_val = self.Attribs
            elif adjust.Stat in list_skills:
                adjusted_val = self.Skills
            else:
                adjusted_val = self
            current = getattr(adjusted_val, adjust.Stat, 0) if adjust.add else 0
            logger.debug(f"Set {self.Name} {adjust.Stat} to {current} + {adjust.Value}")
            setattr(adjusted_val, adjust.Stat, current + adjust.Value)

    def adjust_stats(self) -> None:
        """Check for any StatAdjust powers. Apply overrides, sum with current value"""
        self._adjust_stats_powers_items()
        self._adjust_stats_via_attribs()

    def check_valid(self):
        pass

    def __repr__(self):
        """Print non-default beast items with repr property and linebreaks"""
        return my_repr(self)

    # ------------------------------- Output functions -------------------------------

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
                for p in self.Powers.values()
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

    def _pc_file_info(self, suffix: str):
        return "./automation/_output/", f"PC_{self.Name}_level_{self.Level}.{suffix}"

    def make_pc_html(self, items: list = None):
        """Save pc html as html file

        Args:
            output_filename (str, optional): Filename, no extension. Always in _output
                folder. Defaults to PC_{Name}_level_{Level}.
            items (list, optional): List of dicts with item name, quantity and info.
                Defaults a set of items store in the _html function.
        """
        output_dir, output_filename = self._pc_file_info("html")
        output_file = output_dir + output_filename
        with open(output_file, "w") as f:
            f.write(self._html(items))
        logger.info(f"Wrote HTML {output_file}")

    def make_pc_img(self, items: list = None):
        """Save pc html as png file

        Args:
            output_filename (str, optional): Filename, no extension. Always in _output
                folder. Defaults to PC_{Name}_level_{Level}.
            items (list, optional): List of dicts with item name, quantity and info.
                Defaults a set of items store in the _html function.
        """
        from html2image import Html2Image

        hti = Html2Image()

        hti.output_path, output_filename = self._pc_file_info(".png")
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
