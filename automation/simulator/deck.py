# Intial draft adapted from https://github.com/wynand1004/Projects by @TokyoEdtech

import random
from ..utils.logger import logger


class Card(object):
    """Card class

    Example use:
        from automation.simulaiton.deck import Card
        Card("SA") OR Card("S","A")

    Attributes:
        suit (str): one of [D,C,H,S,R,B] for Diamond, Club, Heart, Spade, Red, Black
        val (str): one of [A, K, Q, J, T] for Ace to Ten. Or 2 to 9.
    """

    def __init__(self, suit, val=None):
        if len(suit) == 2:
            self.suit = suit[0].upper()
            self.val = suit[1].upper()
        else:
            self.suit = suit.upper()
            self.val = val.upper()
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

    def range(self, TR: int):
        """Returns list of cards in a TR range"""
        TR = abs(TR)
        return [self + diff for diff in range(-TR, TR)]


class Deck(object):
    """Full deck of cards

    Example use:
        from automation.simulaiton.deck import Deck
        d=Deck()
        d.draw()
        > A♦️
        d.check(TC=Card("S","A"),TR=3)
        > [INFO]: Drew ♦️ 8 vs ♠️ A with TR 3: Miss

    Attributes:
        suits (tuple): all suits in deck
        vals (tuple): all values in deck
        cards (list): source deck
        discards (list): discard pile
        hand (list): jokers and fate cards in hand
    """

    def __init__(self):
        self.cards, self.hand, self.discards = [], [], []
        self._jokers = [Card("B", "Joker"), Card("R", "Joker")]
        self.suits = ("C", "D", "H", "S")
        self.vals = ("A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2")
        # "Start" with all discarded. Shuffle assumes only shuffle from discard to cards
        self.discards.extend([Card(s, v) for s in self.suits for v in self.vals])
        self.hand.extend(self._jokers)
        self.shuffle()

    def __repr__(self):
        """Result of print(Deck)"""
        output = f"Deck: {[c for c in self.cards]}\n"
        output += f"Discards: {[d for d in self.discards]}\n"
        output += f"Hand {[h for h in self.hand]}\n"
        return output

    def shuffle(self, limit=None):
        """Shuffle N from discard to deck

        If limit provided, only shuffle those from discard.
        If no limit, reshuffle all discarded. Add jokers back to hand.
        """
        random.shuffle(self.discards)
        if not limit:
            limit = len(self.discards)
            self.hand = [*set((*self.hand, *self._jokers))]  # Set removes duplicates
        self.cards.extend(self.discards[:limit])
        self.discards = self.discards[limit:]
        random.shuffle(self.cards)

    def draw(self):
        """Draw a card. If any available, return card"""
        if len(self.cards) == 0:
            logger.warning("No cards available in deck. Exhaustion not yet simulated.")
            return
        card = self.cards.pop()
        if card.val == "A":
            self.hand.append(card)
        else:
            self.discards.append(card)
        return card

    def exchange_fate(self):
        """Move fade card from hand. If Ace, add to discard"""
        if len(self.hand) == 0:
            logger.warning("No cards available to exchange")
            return
        card = self.hand.pop()
        if card.val == "A":
            self.discard.append(card)
        logger.info(f"Exchanged Fate Card: {card}")

    def check(self, TC: Card, TR: int, mod: int = 0):
        """Return string corresponding to check 'Hit/Miss/Color/Suit' etc

        Args:
            TC (Card): Target card
            TR: (int): Rarget Target range
            mod (int): TR modifier
        """
        TR = abs(TR) + mod
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
            result += "Hit" if draw.val in TC.range(TR) else "Miss"
        logger.info(f"Drew {draw} vs {TC} with TR {TR}: {result}")
