from automation.templates.bestiary import Bestiary
from automation.templates.items import Items
from automation.templates.powers import Powers

# TODO: Add isinstance assertions of dataclass subfields


def test_powers(sample_powers):
    assert isinstance(sample_powers, Powers)
    assert len(sample_powers.as_dict) == 5
    assert len(sample_powers.categories) == 4
    assert len(sample_powers.csv_fields) == 24


def test_bestiary(sample_bestiary):
    assert isinstance(sample_bestiary, Bestiary)
    assert len(sample_bestiary.as_dict) == 2
    assert len(sample_bestiary.categories) == 2
    assert len(sample_bestiary.csv_fields) == 42


def test_items(sample_items):
    assert isinstance(sample_items, Items)
    assert len(sample_items.as_dict) == 2
    assert len(sample_items.categories) == 2
    assert len(sample_items.csv_fields) == 14


def test_beast_attribs(sample_beast):
    assert "AGL=1" in sample_beast[0].Attribs.__repr__()


def test_beast_skills(sample_beast):
    skills = sample_beast[0].Skills
    assert ("Finesse", 1) == skills.as_tuple[0]
    assert "Finesse=1" in skills.__repr__()


def test_beast_repr(sample_beast):
    assert "Add -1 to AR." in sample_beast[0].__repr__()


def test_beast_phase_repr(sample_beast):
    assert "Grunt" in sample_beast[1].__repr__()


def test_beast_img(setup, sample_beast):
    verbose_context, _, test_data_dir = setup
    b, _ = sample_beast
    with verbose_context:
        b.make_pc_html(file_path=test_data_dir)  # TODO: Check actual output
        b.make_pc_img(file_path=test_data_dir, dry_run=True)


def test_item_cost(sample_items):
    assert "1,000 gp" == sample_items.as_dict["Mystic Bulwark"].Cost.flat["Cost_raw"]


def test_power_choice(sample_powers):
    assert (
        "On fail, target(s) Blinded."
        in sample_powers.as_dict["Test Destructive Beam"].__repr__()
    )


def test_spec_properties(sample_powers):
    assert "_input" in sample_powers.filepath_default_input
    assert "_output" in sample_powers.filepath_default_output
    assert len(sample_powers.type_dict["Major"]) == 4
