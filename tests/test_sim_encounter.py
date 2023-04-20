def test_sim_round(setup, sample_encounter):
    verbose_context, _, _ = setup
    e = sample_encounter
    with verbose_context:
        e.sim_round(1)
        e.PCs[0]._statuses.update({"Knocked Down": 1})
        e.sim_round(10)


def test_quick_rest(setup, sample_encounter):
    verbose_context, _, _ = setup
    e = sample_encounter
    with verbose_context:
        e.sim_round(3)
        e.PCs[0].HP -= 2
        e.PCs[0].AP -= 1
        e.sim_quick_rest()


def test_full_rest(setup, sample_encounter):
    verbose_context, _, _ = setup
    e = sample_encounter
    with verbose_context:
        e.sim_round(3)
        e.sim_full_rest()


def test_add_creature(sample_encounter, sample_bestiary):
    e = sample_encounter
    s2 = sample_bestiary.raw_data["Test Spider Queen"]
    s2.update(dict(Name="E2", id="D"))
    e.add_creature(s2)
    e.add_creature(s2, side="PCs")


def test_apply_status_power(sample_encounter):
    e = sample_encounter
    dc = e.enemies[0].Powers["Test Distracting Call"]

    success_string = e._apply_power(
        attacker=e.enemies[0],
        targets=e.PCs[0],
        power=dc,
        return_string=True,
        force_result=1,
    )
    assert "resisted" in success_string

    fail_string = e._apply_power(
        attacker=e.enemies[0],
        targets=e.PCs[0],
        power=dc,
        return_string=True,
        force_result=-1,
    )
    assert "P1 is Stunned" in fail_string
    assert "Stunned" in e.PCs[0]._statuses


def test_apply_status_no_sim(sample_encounter):
    e = sample_encounter
    success_string = e._apply_power(
        attacker=e.enemies[0],
        targets=e.PCs[0],
        power=e.enemies[0].Powers["Test Destructive Beam"],
        return_string=True,
        force_result=1,
    )
    assert "Not simulated" in success_string


def test_epic_event(setup, sample_encounter):
    verbose_context, _, _ = setup
    with verbose_context:
        e = sample_encounter
        e.sim_epic_event(participants=e.PCs[0], successes_needed=1)
        assert "wins after" in e.sim_epic_event(successes_needed=10, return_string=True)
