def ul_dict(n):
    return {"upper_lower_int": n}


def test_player_repr(sample_player):
    repr_items = [
        "TC",
        "pc.HP :",
        "Hand     : ",
        "pc.PP :",
        "Deck     :",
        "pc.AP :",
        "Discards :  ",
        "| RestC : 8/8",
    ]
    for item in repr_items:
        assert item in sample_player.__repr__()


def test_statuses(sample_player):
    sample_player._statuses.update({"Entangled": 1, "Knocked Down": 1, "Frozen": 1})
    assert sample_player._apply_upper_lower("check", {}, skill="AGL") == ul_dict(-3)


def test_fatigue(sample_player):
    p = sample_player
    p.full_rest()

    p.modify_fatigue()  # lvl1
    assert sample_player._apply_upper_lower("save", {}) == ul_dict(-1)

    p.modify_fatigue()  # lvl2
    assert sample_player._apply_upper_lower("check", {}) == ul_dict(-1)

    p.modify_fatigue()  # lvl3
    assert sample_player.Speed == sample_player.Speed_Max / 2

    p.modify_fatigue()  # lvl4
    assert p._PP_mult == 2

    p.modify_fatigue()  # lvl5
    assert p._statuses["Knocked Out"] == 1


def test_return_string(sample_card, sample_player):
    assert "with TR" in sample_player.check_by_skill(
        TC=sample_card, DR=3, return_string=True
    )
    assert "with TR" in sample_player.save(DR=3, return_string=True)
    assert "rested" in sample_player.full_rest(return_string=True)
    assert "during Quick" in sample_player.quick_rest(return_string=True)


def test_autoincrement_fatigue(setup, sample_player):
    verbose_context, _, _ = setup
    p = sample_player
    p.full_rest()

    with verbose_context:
        p.discard("all")
        p.check_by_skill()
        p.discard("all")
        p.save()

    assert p._fatigue == 2


def test_no_action(setup, sample_player):
    verbose_context, _, _ = setup
    with verbose_context:
        p = sample_player
        p._statuses = {"Stunned": 1}
        assert not p.take_action(type="Minor")

        p._statuses = {"Burned": 1}
        assert not p.take_action(type="Minor")

        p._statuses = {"Entangled": 1}
        assert not p.take_action()

        p.HP = 0
        assert not p.take_action()
