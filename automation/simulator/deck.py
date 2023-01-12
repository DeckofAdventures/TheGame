# Intial draft adapted from https://github.com/wynand1004/Projects by @TokyoEdtech

import random
from dataclasses import fields
from typing import Union

from ..templates.bestiary import Beast
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

    def range(self, DR: int):
        """Returns list of cards in a TR range"""
        DR = abs(DR)
        return [self + diff for diff in range(-DR, DR + 1)]


class Deck(object):
    """Full deck of cards

    Example use:
        from automation.simulation.deck import Deck
        d=Deck()
        d.draw()
        > ♦️ A
        d.check(TC=Card("S","A"),TR=3)
        > [INFO]: Drew ♦️ 8 vs ♠️ A with TR 3: Miss

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
        self.suits = ("C", "D", "H", "S")
        self.vals = ("A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2")
        # "Start" with all discarded. Shuffle assumes only shuffle from discard to cards
        self.discards.extend([Card(s, v) for s in self.suits for v in self.vals])
        self.hand.extend(self._jokers)
        self._use_TC = use_TC
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
        if self._use_TC:
            self.draw_TC()

    @property
    def TC(self):
        if not self._TC and self._use_TC:
            self.draw_TC
        return self._TC

    def draw_TC(self):
        self._TC = self.draw()

    def draw(self) -> Card:
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

    def discard(self, n):
        """Draw n cards, return none. Discard/hand as normal"""
        for _ in range(n):
            _ = self.draw()

    def exchange_fate(self):
        """Move fate card from hand. If Ace, add to discard"""
        if len(self.hand) == 0:
            logger.warning("No cards available to exchange")
            return
        card = self.hand.pop()
        if card.val == "A":
            self.discards.append(card)
        logger.info(f"Exchanged Fate Card: {card}")

    def _basic_check(self, TC: Card, DR: int) -> Union[None, int]:
        """Return string corresponding to check 'Hit/Miss/Color/Suit' etc

        Args:
            TC (Card): Target card
            TR: (int): Target Range
            mod (int): TR modifier
            return_val (bool): Return the string. Default False.
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
        draw_all: bool = False,
        return_val: bool = False,
        verbose=True,
    ) -> Union[None, int]:
        """Log string corresponding to check 'Hit/Miss/Color/Suit' etc

        Args:
            TC (Card): Target card
            TR: (int): Target Range
            mod (int): TR modifier
            upper_lower (str): 'upper' or 'lower' Hand ('u' or 'l'). Default neither.
            draw_n (int): How many to draw. If upper/lower, default 2. Otherwise 1.
            draw_all (bool): If upper hand, draw all before stopping. Default false.
            return_val (bool): Return the string. Default False.
        """
        DR = abs(DR) + mod  # Apply mod to non-negative TR
        draw_n = abs(draw_n)  # Ensure not negative
        upper_lower = upper_lower[0].upper()

        if upper_lower == "N":
            draw_n = 1
        elif draw_n == 1:  # If upper or lower, make sure is minimum 2
            draw_n = 2

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
        if verbose:
            logger.info(
                f"Drew {draws} vs {TC} with TR {DR}{ul_str}: {self.result_types[result]}"
            )

        if return_val:
            return result


class Player(Deck):
    def __init__(self, pc: Beast):
        Deck.__init__(self)
        self.pc = pc
        self._valid_attribs = [f.name for f in fields(self.pc.Attribs)]
        self._valid_mods = self._valid_attribs + [
            f.name for f in fields(self.pc.Skills)
        ]

    def __repr__(self):
        """Result of print(Player)"""
        output = ""
        output += "TC       : %02s | pc.HP : %d/%d\n" % (
            self.TC,
            self.pc.HP,
            self.pc.HP_Max,
        )
        output += "Hand     :  %02d | pc.PP : %d/%d\n" % (
            len(self.hand),
            self.pc.PP,
            self.pc.PP_Max,
        )
        output += "Deck     :  %02d | pc.AP : %d/%d\n" % (
            len(self.cards),
            self.pc.AP,
            self.pc.AP_Max,
        )
        output += "Discards :  %02d | pc.AR : %d\n" % (len(self.discards), self.pc.AR)
        return output

    def check_by_skill(self, TC: Card, DR: int, skill: str, **kwargs):
        """Accepts any Skill or Attrib. Accepts any valid args of Deck.check"""
        assert (
            skill in self._valid_mods
        ), f"Could not find {skill} in {self._valid_mods}"
        mod = getattr(self.pc.Skills, skill, None) or getattr(
            self.pc.Attribs, skill, None
        )
        return self.check(TC, DR, mod=mod, **kwargs)

    def save(self, DR: int = 3, attrib="None", **kwargs):
        """Accepts any Attrib. Accepts any valid args of Deck.check"""
        if attrib != "None":  # Default to mod of 0 when "None"
            assert (
                attrib in self._valid_attribs
            ), f"Could not find {attrib} in {self._valid_attribs}"
        return self.check(
            TC=self.TC, DR=DR, mod=getattr(self.pc.Attribs, attrib, 0), **kwargs
        )

    def full_rest(self, **kwargs):
        self.shuffle()
        for i in ["HP", "PP", "AP", "RestCards"]:
            setattr(self.pc, i, getattr(self.pc, i + "_Max"))

    def quick_rest(self, **kwargs):
        # Never uses Fate cards here
        point_total = 0  # Recover HP/PP
        while self.pc.RestCards > 0 and (
            (self.pc.HP < self.pc.HP_Max) or (self.pc.PP < self.pc.PP_Max)
        ):  # Will always fully recover with available rest cards
            draw = self.save(return_val=True, **kwargs)
            if not draw:
                break
            points = 2 if draw > 0 else 1
            point_total += points
            logger.debug(f"Recovering {points} with cards")
            for _ in range(points):  # Prioritizes 'where am I missing more?'
                attr_diffs = {
                    "HP": abs(self.pc.HP - self.pc.HP_Max),
                    "PP": abs(self.pc.PP - self.pc.PP_Max),
                }
                increment_this = max(attr_diffs, key=attr_diffs.get)
                setattr(self.pc, increment_this, getattr(self.pc, increment_this) + 1)
                logger.debug(
                    f"   1 {increment_this} to {getattr(self.pc,increment_this,'?')}"
                )
            self.pc.RestCards -= 1

        AP_check_mod = max([self.pc.Skills.Knowledge, self.pc.Skills.Craft])
        down_AP = self.pc.AP_Max - self.pc.AP
        while down_AP > 0:
            draw = self.check(
                TC=self.TC,
                DR=max(0, 7 - down_AP),  # of below 7, 0
                mod=AP_check_mod,
                return_val=True,
                **kwargs,
            )
            if not draw:
                break
            elif draw < 0:
                down_AP -= 1  # Try again with recovering one less
            else:
                self.pc.AP += down_AP
                logger.debug(f"Recovering {down_AP} AP to {self.pc.AP}")
                point_total += down_AP
                break

        logger.info(f"Recovered {point_total} HP/PP/AP during Quick Rest")
        self.shuffle(limit=(10 + self.pc.Attribs.VIT * 2))


# class NPC(object):
#     def __init__(self, TC: Card, TR:int, HP: int):
#         self.TC = TC
#         self.TR = TR
#         self.HP = HP # This will need a setter property


# class Encounter(object):
#     def __init__(self):
#         self.enemies = []
#         gmdeck = Deck()

#     def add_enemy(self, name: NPC):
#         self.enemies.append()

#     def attack_enemy(self, player: Player, enemy):
#         result = player.deck.check(enemy.TC,enemy.TR,player.primary_skill_mod)
#         # assigning result needs modification to check above to return val
#         if 'Hit' in result or 'Success' result: enemy.HP -= 1
