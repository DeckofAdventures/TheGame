# Initial draft adapted from https://github.com/wynand1004/Projects by @TokyoEdtech

import random

from ..utils import logger

all_suits = ("C", "D", "H", "S")
all_vals = ("A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2")


class Card(object):
    """Card class

    Example use:
        ```python
        from automation.simulation.deck import Card
        Card("SA") == Card("S","A")
        > True
        ```

    Attributes:
        suit (str): one of [D,C,H,S,R,B] for Diamond, Club, Heart, Spade, Red, Black
        val (str): one of [A, K, Q, J, T] for Ace to Ten. Or 2 to 9.
        val_number (int): integer corresponding to above value
        color (str): either R or B for red or black
    """

    def __init__(self, suit, val=" "):
        if len(suit) == 2:
            self.suit = suit[0].upper()
            self.val = suit[1].upper()
        elif val.lower() == "joker":
            self.suit = suit[0].upper()
            self.val = "Joker"
        else:
            self.suit = suit[0].upper()
            self.val = val[0].upper()

        if self.val != "Joker" and (
            self.suit not in all_suits or self.val not in all_vals
        ):
            if suit.lower() != "random":
                logger.warning(f"Couldn't make card value from input: {suit}, {val}")
            self.suit = random.choice(all_suits)
            self.val = random.choice(all_vals)

        self._val_to_num = {  # A:1, 2:2, ... T:10
            "A": 1,
            "2": 2,
            "3": 3,
            "4": 4,
            "5": 5,
            "6": 6,
            "7": 7,
            "8": 8,
            "9": 9,
            "T": 10,
            "J": 11,
            "Q": 12,
            "K": 0,
            "Joker": "Joker",
        }
        self._num_to_val = {v: k for k, v in self._val_to_num.items()}

    @property
    def suit_symbol(self):
        """Symbol for each suit, including red and black for jokers"""
        return {
            "D": "♦️",
            "C": "♠️",
            "H": "♥️",
            "S": "♠️",
            "R": "🟥",  # Red joker
            "B": "⬛",  # Black joker
        }[self.suit]

    @property
    def val_number(self):
        """Integer value for number, to permit calculations"""
        return self._val_to_num[self.val]

    @property
    def color(self):
        """R or B"""
        return "B" if self.suit in ["C", "S", "B"] else "R"

    def __repr__(self):
        """Result of print(card)"""
        return f"{self.suit_symbol} {self.val}"

    def __add__(self, x: int):
        """Result of card + integer. Loops around"""
        assert self.val != "Joker", "Cannot add/subtract Joker"
        return self._num_to_val[(self.val_number + x) % 13]

    def __sub__(self, x: int):
        """Result of card - integer. Loops around"""
        assert self.val != "Joker", "Cannot add/subtract Joker"
        return self._num_to_val[(self.val_number - x) % 13]

    def __eq__(self, x):
        """Returns true if two cards are the same"""
        return (self.suit == x.suit) & (self.val == x.val)

    def __hash__(self):
        """Returns unique value to represent card"""
        return hash((self.suit, self.val))

    def range(self, DR: int):
        """Returns list of cards in a DR"""
        DR = abs(DR)
        return [self + diff for diff in range(-DR, DR + 1)]


class Deck(object):
    """Full deck of cards

    Example use:
        ```python
        from automation.simulation.deck import Deck
        d=Deck()
        d.draw()
        > ♦️ A
        d.check(TC=Card("S","A"),DR=3)
        > [INFO]: Drew ♦️ 8 vs ♠️ A with DR 3: Miss
        ```

    Attributes:
        suits (tuple): all suits in deck
        vals (tuple): all values in deck
        cards (list): source deck
        discards (list): discard pile
        hand (list): jokers and fate cards in hand
    """

    def __init__(self, use_TC=True):
        self.cards, self.hand, self.discards = [], [], []
        self._jokers = [Card("B", "Joker"), Card("R", "Joker")]
        # "Start" with all discarded. Shuffle assumes only shuffle from discard to cards
        self.discards.extend([Card(s, v) for s in all_suits for v in all_vals])
        self.hand.extend(self._jokers)
        self._use_TC = use_TC
        self.Name = "GM" if not self._use_TC else "Deck"
        self._TC = None
        self.shuffle()
        self.result_types = {
            "Critical Success": 5,
            "Major Success": 4,
            "Suited Hit": 3,
            "Color Hit": 2,
            "Hit": 1,
            "No result": 0,
            "Suited Miss": -1,
            "Color Miss": -2,
            "Miss": -3,
        }
        self.result_types.update(dict([reversed(i) for i in self.result_types.items()]))

    def __repr__(self):
        """Result of print(Deck)"""
        output = ""
        output += f"TC      : {self.TC}\n"
        output += f"Hand    :  {len(self.hand):02d}\n"
        output += f"Deck    :  {len(self.cards):02d}\n"
        output += f"Discards:  {len(self.discards):02d}\n"
        return output

    def shuffle(self, limit: int = None):
        """Shuffle N from discard to deck

        If limit provided, only shuffle those from discard. If no limit, reshuffle all
        discarded. Add jokers back to hand.

        Args:
            limit (int, optional): Number of cards to shuffle back into deck. Defaults
                to None.
        """
        random.shuffle(self.discards)
        if not limit:
            limit = len(self.discards)
            self.hand = [*set((*self.hand, *self._jokers))]  # Set removes duplicates
        self.cards.extend(self.discards[:limit])
        self.discards = self.discards[limit:]
        random.shuffle(self.cards)
        if self._use_TC:
            self.draw_TC()

    @property
    def TC(self) -> Card:
        """Target card

        Returns:
            Card: Current Target Card from deck. Not applicable to GM decks.
        """
        if not self._TC and self._use_TC:
            self.draw_TC
        return self._TC

    def draw_TC(self):
        """Draw a new target card"""
        self._TC = self.draw()

    def draw(self) -> Card | None:
        """Draw a card, if available. Otherwise returns None.

        Returns:
            Card: _description_
        """
        """Draw a card. If any available, return card"""
        if len(self.cards) == 0 and self._use_TC:
            logger.warning("No cards available in deck.")
            return None
        elif len(self.cards) == 0 and not self._use_TC:
            self.shuffle()  # for GMs, just shuffle
        card = self.cards.pop()
        if card.val == "A":
            self.hand.append(card)
        else:
            self.discards.append(card)
        return card

    def check_by_skill(self, **kwargs):
        if self._use_TC:
            raise TypeError("check_by_skill method invoked on a non-GM deck")
        kwargs.pop("skill", None)
        return self.check(**kwargs)

    def discard(self, n: int, return_string=False, **_) -> str | None:
        """Draw n cards, return none. Discard/hand as normal

        Args:
            n (int): Number of cards to discard. If "all", uses discards all remaining.
            return_string (bool, optional): Return a string reflecting result. Defaults
                to False.

        Returns:
            str | None: If return_string, report "Drew X"
        """ """"""
        if n == "all":
            n = len(self.cards)

        draws = []
        for _ in range(n):
            draws.append(self.draw())

        if return_string:
            return f"Drew {draws}"

    def exchange_fate(self, return_string=False) -> str | None:
        """Move fate card from hand. If Ace, add to discard

        Args:
            return_string (bool, optional): Default to False"""
        if len(self.hand) == 0:
            result = "No cards available to exchange"
        else:
            card = self.hand.pop()
            if card.val == "A":
                self.discards.append(card)
            result = f"Exchanged Fate Card: {card}"

        if return_string:
            return result

        logger.info(result)

    def _basic_check(self, TC: Card, DR: int) -> None | int:
        """Return string corresponding to check 'Hit/Miss/Color/Suit' etc

        Args:
            TC (Card): Target card
            DR: (int): Difficulty Range
            mod (int): DR modifier
        """
        DR = abs(DR)
        draw = self.draw()
        result = ""
        if draw is None:
            result += "No result"
        elif draw == TC:
            result += "Critical Success"
        elif draw.val == TC.val:
            result += "Major Success"
        else:
            if draw.suit == TC.suit:
                result += "Suited "
            elif draw.color == TC.color:
                result += "Color "
            result += "Hit" if draw.val in TC.range(DR) else "Miss"
        return (draw, self.result_types[result])  # Return (draw, int)

    def check(
        self,
        TC: Card,
        DR: int,
        mod: int = 0,
        upper_lower: str = "none",
        draw_n: int = 1,
        upper_lower_int: int = 0,
        draw_all: bool = False,
        return_val: bool = False,
        return_string: bool = False,
        verbose=True,
    ) -> tuple[int, str] | str:
        """Log string corresponding to check 'Hit/Miss/Color/Suit' etc

        Args:
            TC (Card): Target card
            DR: (int): Difficulty Range
            mod (int): DR modifier
            upper_lower (str): 'upper' or 'lower' Hand ('u' or 'l'). Default neither.
            draw_n (int): How many to draw. If upper/lower, default 2. Otherwise 1.
            upper_lower_int (int): Instead of passing upper_lower and draw_n, use
                positive/negative for upper/lower with int of draw_n -1.
                for example, -1 for draw 2 lower
            draw_all (bool): If upper hand, draw all before stopping. Default false.
            return_val (bool): Return the integer of the result. Default False.
            return_string (bool): Return the string describing what happened. Default
                False.
            verbose (bool): Log the result string as a debug item

        Returns:
            tuple | str: If return_string, returns a tuple containing the result as a
                string, followed by the result value. If return_val, only integer result.
        """

        DR = max(0, abs(DR) + mod)  # Apply mod to non-negative TR
        if upper_lower_int:
            upper_lower = (
                "U" if upper_lower_int > 0 else "L" if upper_lower_int < 0 else "N"
            )
            draw_n = 1 if upper_lower == "N" else abs(upper_lower_int) + 1
        else:
            upper_lower = upper_lower[0].upper()
            draw_n = 1 if upper_lower == "N" else 2 if abs(draw_n) == 1 else abs(draw_n)

        results = []
        draws = []

        for _ in range(draw_n):
            draw, this_result = self._basic_check(TC, DR)
            draws.append(draw)
            results.append(this_result)
            if results[-1] > 0 and not draw_all and upper_lower == "U":
                break  # If success (>0) and not draw-all with upper, stop drawing

        ul_str = ""
        if upper_lower == "U":
            ul_str = f" at Upper Hand {draw_n}"
        elif upper_lower == "L":
            ul_str = f" at Lower Hand {draw_n}"

        result = max(results) if upper_lower == "U" else min(results)
        result_string = (
            f"Drew {draws} vs {TC} with DR {DR}{ul_str}: {self.result_types[result]}"
        )

        if verbose:
            logger.debug(result_string)

        if return_string:
            return result_string, result
        elif return_val:
            return result
