import copy
import os
import sys
import pytest
import logging
import yaml
from pathlib import Path
from contextlib import nullcontext
from automation.templates.powers import Powers
from automation.templates.bestiary import Bestiary, all_powers, all_items
from automation.templates.items import Items
from automation.simulator.encounter import Encounter
from automation.simulator.deck import Card
from automation.simulator.player import Player
from automation.utils.logger import logger
from automation.utils.logger_csv import draw_log, rest_log

# ---------------------- CONSTANTS ---------------------


def pytest_addoption(parser):
    """
    Permit constants when calling pytest at commandline e.g., pytest --my-verbose False

    Parameters
    ----------
    --my-verbose (bool):  Default True. Pass print statements from Elements.
    --my-teardown (bool): Default True. Delete pipeline on close.
    --my-datadir (str):  Default ./tests/test_data. Relative path of test CSV data.
    """
    parser.addoption(
        "--my-verbose",
        action="store",
        default="True",
        help="Verbose for items: True or False",
        choices=("True", "False"),
    )
    parser.addoption(
        "--my-teardown",
        action="store",
        default="True",
        help="Verbose for items: True or False",
        choices=("True", "False"),
    )
    parser.addoption(
        "--my-datadir",
        action="store",
        default="./tests/test_data/",
        help="Relative path for saving test data",
    )


@pytest.fixture(scope="session")
def setup(request):
    """Take passed commandline variables, set as global"""
    global verbose, _tear_down, verbose_context, test_data_dir

    verbose = str_to_bool(request.config.getoption("--my-verbose"))
    _tear_down = str_to_bool(request.config.getoption("--my-teardown"))
    test_data_dir = request.config.getoption("--my-datadir")
    Path(test_data_dir).mkdir(exist_ok=True)

    if not verbose:
        logger.setLevel(logging.CRITICAL)

    verbose_context = nullcontext() if verbose else QuietStdOut()

    yield verbose_context, _tear_down, test_data_dir


# ------------------ GENERAL FUCNTION ------------------


def str_to_bool(value) -> bool:
    """Return whether the provided string represents true. Otherwise false.
    Args:
        value (any): Any input
    Returns:
        bool (bool): True if value in ("y", "yes", "t", "true", "on", "1")
    """
    # Due to distutils equivalent depreciation in 3.10
    # Adopted from github.com/PostHog/posthog/blob/master/posthog/utils.py
    if not value:
        return False
    return str(value).lower() in ("y", "yes", "t", "true", "on", "1")


class QuietStdOut:
    """If verbose set to false, used to quiet tear_down table.delete prints"""

    def __enter__(self):
        # os.environ["LOG_LEVEL"] = "WARNING"
        logger.setLevel("CRITICAL")
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")

    def __exit__(self, exc_type, exc_val, exc_tb):
        # os.environ["LOG_LEVEL"] = "INFO"
        logger.setLevel("INFO")
        sys.stdout.close()
        sys.stdout = self._original_stdout


# ------------------- FIXTURES -------------------


@pytest.fixture(scope="session")
def yaml_data(setup):
    """For each template, writes test yaml, yeilds class"""

    verbose_context, _tear_down, test_data_dir = setup

    all_data = [
        [  # 0
            test_data_dir + "test_powers.yaml",
            {
                "Test Destructive Beam": {
                    "Type": "Major",
                    "Category": "Magic",
                    "Mechanic": "All creatures within a Line 12 must make an AGL Save",
                    "Description": "Beam description",
                    "XP": 2,
                    "PP": 2,
                    "Prereq": {"Role": "Caster", "Level": 3, "Skill": "Knowledge > 1"},
                    "Damage": 2,
                    "AOE": "Line 12",
                    "Save": {
                        "Trigger": "Once",
                        "Type": "AGL",
                        "Fail": "Blinded",
                        "Succeed": "take 1 damage",
                    },
                },
                "Test Distracting Call": {
                    "Type": "Major",
                    "Category": "Magic",
                    "Mechanic": "All creatures within Aura 6 to make a GUT Save",
                    "Description": "Call description.",
                    "XP": 2,
                    "PP": 2,
                    "Draw": "Upper",
                    "AOE": "Aura 6",
                    "Save": {
                        "Trigger": "Once",
                        "Type": "GUT",
                        "DR": 2,
                        "Fail": "Stunned",
                        "Succeed": "Nonstatus Testing content",
                    },
                },
                "Test Attack, Weapon": {
                    "Name": "Weapon Attack",
                    "Category": ["Combat", "Weapon Attacks"],
                    "Description": "Weapon attack description.",
                    "Mechanic": "You make a check to attack an Enemy",
                    "Type": "Major",
                    "XP": 1,
                },
                "Test Shield": {
                    "Category": ["Combat", "Support"],
                    "Description": "Shield descrip.",
                    "Mechanic": "Add 1 AP to a creature you can see, including yourself"
                    + ". This effect does not stack with other Powers that grant A.",
                    "Type": "Major",
                    "XP": 2,
                    "PP": 1,
                    "Range": 6,
                    "StatAdjust": {"AP": 1},
                    "XP": 1,
                },
                "Test Passsive": {
                    "Name": "Fake passive",
                    "Category": ["Magic", "Fake"],
                    "Description": "Fake description.",
                    "Mechanic": "Anything",
                    "Type": "Passive",
                    "Damage": 1,  # Hit line that skips damage on passives
                    "XP": 1,
                },
                "Test NoType": {
                    "Name": "Fake",
                    "Category": ["Magic", "Fake"],
                    "Description": "Fake description.",
                    "Mechanic": "Anything",
                    "Damage": 1,  # Hit line that skips damage on passives
                    "XP": 1,
                },
                "Test ExcludeType": {
                    "Name": "Fake passive",
                    "Category": ["Magic", "Fake"],
                    "Description": "Fake description.",
                    "Mechanic": "Anything",
                    "Type": "FakeType",
                    "Damage": 1,  # Hit line that skips damage on passives
                    "XP": 1,
                },
            },
        ],
        [  # 1
            test_data_dir + "test_bestiary.yaml",
            {
                "Test Spider Queen": {
                    "Type": "Boss",
                    "HP": 11,
                    "AR": 2,
                    "PP": 6,
                    "Primary_Skill": "Knowledge",
                    "Attribs": {
                        "AGL": -1,
                        "CON": 2,
                        "INT": 2,
                        "GUT": 2,
                        "STR": -1,
                        "VIT": 1,
                    },
                    "Powers": [
                        "Test Attack, Weapon",
                        "Test Distracting Call",
                        "Test Destructive Beam",
                        "Test Shield",
                        {"Favored Terrain": "Webs"},
                    ],
                    "Description": "Spider description.",
                    "Phases": {"One": {"HP": 11, "Allies": ["Grunt"]}},
                },
                "Test Clubs3": {
                    "Type": "PC",
                    "Pronouns": "He/Him",
                    "Role": "Defender",
                    "Level": 2,  # Test throw excess XP warning
                    "Primary_Skill": "Brute",
                    "HP": 8,
                    "AP": 2,
                    "AR": 2,
                    "PP": 10,  # Not used, caught and throws warning
                    "Speed": 6,
                    "Attribs": {
                        "AGL": 1,
                        "STR": 3,  # Test throw stat cap warning
                        "VIT": 1,
                    },
                    "Skills": {"Finesse": 1, "Stealth": 1, "Athletics": 2, "Brute": 2},
                    "Powers": [
                        "Test Attack, Weapon",
                        "Attack, Vengeance",
                        "Attack, Charge",
                        "Momentum",
                        "Momentum Aura",
                        "Shield",
                        "Oath",
                        "Bloodthirsty",
                        "Conceited",  # Test throw excess Vulny warning
                        "Undying",  # Test remove Boss-Only
                        "Fake Power",  # Test throw nonexistent power warning
                    ],
                    "Items": ["Fortified Armor", "Mystic Bulwark", "Fake Item"],
                },
            },
        ],
        [  # 2
            test_data_dir + "test_items.yaml",
            {
                "Mystic Bulwark": {
                    "Type": "Shield",
                    "Rarity": "Rare",
                    "Cost": "1,000 gp",
                    "Use": {
                        "Time": "Unknown Action",  # Hit item action type warning
                        "Limit": "2 times per rest",
                        "Effect": "Test effect",
                        "Power": "Condition Immunity",  # Item power option
                    },
                    "StatAdjust": {"Add": {"AR": -1}, "Replace": {"Craft": -1}},
                },
                "Wand of Flame": {
                    "Type": "Weapon",
                    "Cost": "500 non-currency",
                    "Rarity": "Rare",
                    "Use": {
                        "Time": "One Unknown",  # Hit item non-action numeric enforce
                        "Limit": "3",  # Hit "append 'times'"
                        "Power": [
                            "Attack, Mystic Cone",
                            "Attack, Mystic Aura",
                            "Attack, Mystic",
                            "Fake Power",
                        ],
                    },
                    "StatAdjust": {"Add": {"Craft": 1}, "Replace": {"GUT": 0}},
                    "Damage": 2,
                    "Range": 12,
                    "AOE": "Aura 2",
                    "Prereq": {"Skill": "STR > 0"},
                    "Tags": ["2-handed", "Other Tag"],
                },
            },
        ],
    ]

    for yaml_path, yaml_contents in all_data:
        with open(yaml_path, "w") as yaml_file:
            yaml.dump(yaml_contents, yaml_file)

    yield [yaml_path for yaml_path, _ in all_data]

    if _tear_down:
        with verbose_context:
            for yaml_path, _ in all_data:
                Path(yaml_path).unlink()


@pytest.fixture(scope="session")
def sample_powers(yaml_data):
    """Any specific fixtures"""
    powers, _, _ = yaml_data

    p = Powers(powers)
    p.filepath_output = test_data_dir

    global supplemental_powers

    yield p


@pytest.fixture(scope="session")
def sample_items(yaml_data):
    """Any specific fixtures"""
    _, _, items = yaml_data

    i = Items(items)
    i.filepath_output = test_data_dir
    yield i


@pytest.fixture(scope="session")
def sample_bestiary(setup, yaml_data, sample_powers, sample_items):
    verbose_context, _, _ = setup
    _, bestiary, _ = yaml_data

    all_powers.update(sample_powers.as_dict)
    all_items.update(sample_items.as_dict)

    with verbose_context:
        b = Bestiary(bestiary)
    b.filepath_output = test_data_dir

    yield b


@pytest.fixture(scope="session")
def sample_beast(setup, sample_bestiary):
    verbose_context, _, _ = setup
    with verbose_context:
        b = sample_bestiary.as_dict
    yield b["Test Clubs3"], b["Test Spider Queen"]


@pytest.fixture(scope="module")
def sample_player(setup, sample_bestiary):
    verbose_context, _, _ = setup
    with verbose_context:
        b = sample_bestiary.raw_data["Test Clubs3"]
        b.update({"id": "P1"})
        p = Player(**b)

    yield p


@pytest.fixture(scope="module")
def sample_encounter(setup, sample_bestiary):
    """Any specific fixtures"""
    verbose_context, _, test_data_dir = setup

    draw_log.filename = test_data_dir + "log_draws.csv"
    rest_log.filename = test_data_dir + "log_rests.csv"

    b = copy.copy(sample_bestiary.raw_data)
    c1 = b["Test Clubs3"]
    c1.update(dict(Name="P1", id="A"))
    c2 = copy.copy(c1)
    c2.update(dict(Name="P2", id="B"))
    s = b["Test Spider Queen"]
    s.update(dict(Name="E1", id="C"))

    with verbose_context:
        e = Encounter(PCs=[c1, c2], Enemies=[s])
    e.set_csv_logging(True)

    yield e


@pytest.fixture()
def write_mds(setup, sample_powers, sample_bestiary, sample_items):
    verbose_context, _tear_down, _ = setup
    list_classes = [sample_powers, sample_bestiary, sample_items]

    for my_class in list_classes:
        with verbose_context:
            my_class.write_md(TOC=True)

    yield True

    if _tear_down:
        with verbose_context:
            for my_class in list_classes:
                Path(my_class.filepath_output + my_class._stem + ".md").unlink()


@pytest.fixture()
def write_csvs(setup, sample_powers, sample_bestiary, sample_items):
    verbose_context, _tear_down, _ = setup
    list_classes = [sample_powers, sample_bestiary, sample_items]

    for my_class in list_classes:
        with verbose_context:
            my_class.write_csv()

    yield True

    if _tear_down:
        with verbose_context:
            for my_class in list_classes:
                Path(my_class.filepath_output + my_class._stem + ".tsv").unlink()


@pytest.fixture()
def split_pdf(setup):
    verbose_context, _, test_data_dir = setup

    with verbose_context:
        from automation.pdf.split_premades import split_pdf

        file_paths = split_pdf(
            dry_run=True, out_folder=Path(test_data_dir), return_paths=True
        )

    yield file_paths


@pytest.fixture(scope="session")
def sample_card():
    yield Card("SA")
