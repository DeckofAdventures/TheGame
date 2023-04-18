from automation.simulator.deck import Card, Deck
import pytest


def test_gen_card(sample_card):
    card = sample_card
    assert card == Card("S", "A")
    assert card - 1 == "K"
    assert isinstance(Card("random"), Card)


def test_card_warns(setup):
    verbose_context, _, _ = setup
    with verbose_context:
        assert isinstance(Card("Not", "Valid"), Card)


def test_gen_deck(setup, sample_card):
    verbose_context, _, _ = setup

    deck = Deck()

    assert isinstance(deck.TC, Card)

    for value in ["TC", "Hand    :  0", "Deck    :  5", "Discards:  0"]:
        assert value in deck.__repr__()

    with verbose_context:
        assert str(Card("SA")) in deck.discard(51, return_string=True)
        _, result = deck._basic_check(TC=sample_card, DR=3)
        assert result == 0  # Expect no result after bleeding deck

    assert "Exchanged Fate Card" in deck.exchange_fate(return_string=True)


def test_autoshuffle_gm_deck():
    deck = Deck(use_TC=False)
    _ = deck.discard(52)
    assert isinstance(deck.draw(), Card)


def test_deck_warns(sample_card):
    with pytest.raises(TypeError) as e:
        _ = Deck().check_by_skill(TC=sample_card, DR=3)
    assert "envoked on a non-GM" in e.value.args[0]


def test_deck_no_fate(setup):
    verbose_context, _, _ = setup

    deck = Deck()
    with verbose_context:
        for _ in range(6):
            _ = deck.exchange_fate()

    assert "No cards available" in deck.exchange_fate(return_string=True)


def test_deck_checks(setup, sample_card):
    verbose_context, _, _ = setup
    deck = Deck()

    with verbose_context:
        result_str, result_int = deck.check(
            TC=sample_card, DR=3, upper_lower="Upper", return_string=True, verbose=True
        )
        assert f"vs {sample_card}" in result_str
        assert isinstance(result_int, int)

        result_str, _ = deck.check(
            TC=sample_card, DR=3, upper_lower_int=-2, return_string=True
        )
        assert "at Lower Hand 3" in result_str
