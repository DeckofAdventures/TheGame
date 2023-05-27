from collections import OrderedDict
from dataclasses import dataclass, field, fields
from operator import attrgetter
from typing import List, Tuple

from ..utils import (
    ensure_list,
    flatten_embedded,
    flatten_list,
    logger,
    make_bullet,
    make_header,
    my_repr,
)
from .items import load_all_items
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
list_stats.update(dict(VIT=[]))
list_beast_types = ["PC", "Dealer", "NPC", "Boss", "Companion"]
list_boss_phases = ["One", "Two", "Three", "Four", "Five", "Six"]
xp_progression = dict(  # Value: XP cost
    attrib={-2: -4, -1: -2, 0: 0, 1: 2, 2: 4, 3: 8, 4: 12, 5: 18, 6: 24},
    skills={-2: -2, -1: -1, 0: 0, 1: 1, 2: 2, 3: 4, 4: 6, 5: 9, 6: 12},
)
stat_cap = {1: 2, 2: 2, 3: 3, 4: 3, 5: 3, 6: 4, 7: 4, 8: 5, 9: 5, 10: 6}

all_powers = load_all_powers().as_dict
all_items = load_all_items().as_dict


class Bestiary(YamlSpec):
    """Bestiary class - load all or a specific type from YAMLs

    Example:
        from automation.templates.bestiary import Bestiary, Beast
        Bestiary().as_dict['MyPC'] # Returns Beast object

    Attributes:
        as_dict (dict): dictionary of all beasts loaded
        categories (OrderedDict): tuple of type as key, with list values of individuals
        csv_fields (list): list of fields to be included in csv
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
        if not self._categories:
            self._categories = self._build_categories(build_with="Type")
        return self._categories

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
    """Class to represent a beast's Attributes

    Attributes:
        as_tuple (tuple[int]): set of integers in default order
        flat (dict): uses 'Attrib' as a prefix in {Attrib_AGL: value} dict
    """

    AGL: int = 0
    CON: int = 0
    GUT: int = 0
    INT: int = 0
    STR: int = 0
    VIT: int = 0

    @property
    def as_tuple(self):
        """Just a set of all items as int (0, 1, 2...)"""
        return (self.AGL, self.CON, self.GUT, self.INT, self.STR, self.VIT)

    @property
    def flat(self) -> dict:
        """Return flatted dict {'Attrib_example': value} pairs for csv export"""
        return flatten_embedded(dict(Attrib=self.__dict__))

    def __repr__(self):
        """Print non-default beast items with repr property and linebreaks"""
        return my_repr(self, separator=", ", indent=0)


@dataclass(order=True)
class Skills:
    """Class to represent a beast's Skills

    Attributes:
        as_tuple (tuple[int]): set of integers in default order
        non_defaults (tuple[int]): see above, skip items at 0
        flat (dict): uses 'Skill' as a prefix in {Skill_AGL: value} dict
    """

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
            if value not in [0, None]:
                output.append((f.name, value))
        return output

    @property
    def flat(self) -> dict:
        """Return flatted dict {'Skill_example': value} pairs for csv export"""
        return flatten_embedded(dict(Skill=self.__dict__))

    def __repr__(self):
        """Print non-default beast items with repr property and linebreaks"""
        return my_repr(self, separator=", ", indent=0)


@dataclass(order=True)
class Phase:
    """Class for representing boss phases"""

    # TODO: Should allies be typed as Beast recursively?
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
        self.sort_index = self.Type
        self.Name = self.Name if self.Name else self.id
        self.Powers, self._pow_PP, self._pow_XP, self._vulny_XP = self.fetch_powers()
        self.Items = self.fetch_items() if self.Items else None
        self.Attribs = Attribs(**self.Attribs) if self.Attribs else Attribs()
        self.Skills = Skills(**self.Skills) if self.Skills else Skills()
        self.Phases = self.fetch_phases() if self.Phases else None
        self.AR = self.AR if self.AR else (3 - (self.Attribs.AGL // 2))  # default
        self.RestCards = self.HP
        if self.Type in ["PC"]:
            if self.PP != 0:
                logger.warning(
                    f"{self.Name} has unused PP listed in yaml. Now summed from powers"
                )
            self.PP = self._pow_PP
            self.check_valid()
        self.adjust_stats()
        self.RestCards_Max = self.HP
        self.HP_Max = self.HP  # assume providing max when initializing
        self.AP_Max = self.AP
        self.AR_Max = self.AR
        self.PP_Max = self.PP
        self.Speed_Max = self.Speed
        self.Primary_Skill_Mod = (
            getattr(
                self.Attribs if self.Primary_Skill in list_attribs else self.Skills,
                self.Primary_Skill,
                0,
            )
            if self.Primary_Skill
            else 0
            # Primary skill mod is zero when no primary skill selected so that save DR
            # math still works
        )

    def fetch_powers(self) -> Tuple[dict, int, int, int]:
        """Given a list of powers by name, generate a dict {Name: Power class}

        Returns:
            output_powers (dict): Dictionary of {name: Power class} for this char powers
            powers_pp (int): number of max power points summed across all powers
            powers_xp (int): number of across all powers
            vulny_xp (int): number of xp from vulnerabilities alone
        """
        # TODO: check prereqs in validation
        output_powers = {}
        powers_pp = 0
        powers_xp = 0
        vulny_xp = 0
        self.Powers = ensure_list(self.Powers)
        for listed_power in self.Powers:
            if isinstance(listed_power, dict):
                power_name, choice = next(iter(listed_power.items()))
            else:
                power_name, choice = listed_power, None

            power = all_powers.get(power_name, None)

            if not power:
                logger.warning(f"{self.Name} has a power not in yaml: {power_name}")
                continue
            if self.Type != "Boss" and "Boss-Only" in power.Category:
                logger.warning(f"Removed {self.Name}'s Boss-Only power:{power_name}")
                continue

            output_powers.update({power_name: power.set_choice(choice)})
            powers_pp += max(ensure_list(power.PP))
            xp = ensure_list(power.XP)[-1]
            powers_xp += xp
            if power.Type == "Vulny":
                vulny_xp += xp
        return output_powers, powers_pp, powers_xp, vulny_xp

    def fetch_items(self) -> dict:
        """Return a dict of {item_name: item class} for all items wielded by this char

        Returns:
            dict: set of items as a dictionary
        """
        output_items = {}
        for listed_item in ensure_list(self.Items):
            item = all_items.get(listed_item)
            if not item:
                logger.warning(f"{self.Name} has item not in yaml: {listed_item}")
                continue
            output_items.update({listed_item: item})
        return output_items

    def fetch_phases(self) -> list:
        """Turn phase input into list of phase class items"""
        output = []
        for order, (phase, phase_dict) in enumerate(self.Phases.items()):
            output.append(Phase(Name=phase, Order=order, **phase_dict))
        return output

    def _adjust_skill_via_attribs(self, attribs: list = None):
        """For each attrib passed (if none, all), if skill 0 or None, use attrib value

        Args:
            attribs (list, optional): Set of attribs for which we should adjust skills.
                Defaults to None, which assumes all attribs.
        """
        if not attribs:
            attribs = list_attribs  # All
        for attrib in ensure_list(attribs):
            attrib_val = getattr(self.Attribs, attrib, 0)
            for skill in list_stats[attrib]:
                if not getattr(self.Skills, skill, None):
                    logger.debug(f"{self.Name}:set {skill} to {attrib_val}")
                    setattr(self.Skills, skill, attrib_val)

    def _adjust_stats_powers_items(self):
        """For each power and item, check for StatAdjust fields and modify relevant"""
        adjusts = []
        if self.Powers:
            adjusts.append(
                getattr(power, "StatAdjusts", []) for power in self.Powers.values()
            )
        if self.Items:
            adjusts.append(
                getattr(item, "StatAdjusts", []) for item in self.Items.values()
            )

        for adjust in flatten_list(adjusts):
            if adjust.Stat in list_attribs:
                adjusted_val = self.Attribs
            elif adjust.Stat in list_skills:
                adjusted_val = self.Skills
            else:
                adjusted_val = self
            current = getattr(adjusted_val, adjust.Stat, 0) if adjust.add else 0
            logger.debug(f"Set {self.Name} {adjust.Stat} to {current} + {adjust.Value}")
            setattr(adjusted_val, adjust.Stat, current + adjust.Value)

            if adjust.Stat in list_attribs:
                self._adjust_skill_via_attribs(adjust.Stat)

    def adjust_stats(self) -> None:
        """Check for any StatAdjust powers. Apply overrides, sum with current value"""
        self._adjust_skill_via_attribs()
        self._adjust_stats_powers_items()

    def check_valid(self):
        """Check that this beast is a valid PC. If not, log warnings with flaws"""
        remaining_XP = 6 + (self.Level * 3) - self._pow_XP

        self._adjust_skill_via_attribs()
        max_stat = 0
        for attrib, skills in list_stats.items():
            attrib_val = getattr(self.Attribs, attrib, 0)
            attrib_xp = xp_progression["attrib"][attrib_val]
            max_stat = max(max_stat, attrib_val)
            remaining_XP -= attrib_xp
            for skill in skills:
                skill_val = getattr(self.Skills, skill, 0)
                remaining_XP -= xp_progression["skills"][skill_val - attrib_val]
                max_stat = max(max_stat, skill_val)

        if remaining_XP < 0:
            logger.warning(f"{self.Name} used {abs(remaining_XP)} excess XP")
        if max_stat > stat_cap[self.Level]:
            logger.warning(
                f"{self.Name} has a stat at {max_stat}, above the "
                + f"{stat_cap[self.Level]} cap for level {self.Level}"
            )
        if self._vulny_XP < -4:
            logger.warning(
                f"{self.Name} has {abs(self._vulny_XP)} XP from Vulnys. Limit 4."
                + "\nNote: this check assumes more negative XP value from each Vulny."
            )

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

    def _pc_file_info(self, suffix: str) -> Tuple[str, str]:
        """Return _output relative file path and name for PC file given suffix"""
        return "./automation/_output/", f"PC_{self.Name}_level_{self.Level}.{suffix}"

    def make_pc_html(self, file_path: str = None, items: list = None):
        """Save pc html as html file

        Args:
            file_path (str, optional): Filename, no extension. Always in _output
                folder. Defaults to PC_{Name}_level_{Level}.
            items (list, optional): List of dicts with item name, quantity and info.
                Defaults a set of items store in the _html function.
        """
        output_dir, filename = self._pc_file_info("html")
        output_file = file_path + filename if file_path else output_dir + filename
        with open(output_file, "w") as f:
            f.write(self._html(items))
        logger.info(f"Wrote HTML {output_file}")

    def make_pc_img(
        self,
        file_path: str = None,
        items: list = None,
        browser="google-chrome",
        custom_browser_flags=None,
        dry_run=False,
    ):
        """Save pc html as png file

        Writing out the image with html2image can be a noisy process with multiple
        warning log items from chrome. To quiet these, git clone html2image and pip
        install as editable. Then, add the following as the last line in the command
        list in the relevant browser: '> /dev/null 2>&1'. For chrome.py, L250

        Args:
            file_path (str, optional): Filename, no extension. Always in _output
                folder. Defaults to PC_{Name}_level_{Level}.
            items (list, optional): List of dicts with item name, quantity and info.
                Defaults a set of items store in the _html function.
        """
        from html2image import Html2Image

        hti = Html2Image(
            browser=browser,
            custom_flags=custom_browser_flags,
        )
        output_path, filename = self._pc_file_info("png")
        hti.output_path = file_path or output_path
        hti.size = (950, 1200)
        if not dry_run:
            hti.screenshot(
                html_str=self._html(items),
                save_as=filename,
            )
        logger.info(f"Wrote HTML as image: {hti.output_path}/{filename}")

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
