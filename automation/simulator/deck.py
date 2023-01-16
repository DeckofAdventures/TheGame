# Intial draft adapted from https://github.com/wynand1004/Projects by @TokyoEdtech

import random
from dataclasses import fields
from typing import List, Union

from ..templates import Beast, Power
from ..utils import ensure_list, logger


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
            logger.warning("No cards available in deck.")
            return None
        card = self.cards.pop()
        if card.val == "A":
            self.hand.append(card)
        else:
            self.discards.append(card)
        return card

    def discard(self, n, **_):
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
        upper_lower_int: int = 0,
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
            upper_lower_int (int): Instead of passing upper_lower and draw_n, use
                positive/negative for upper/lower with int of draw_n -1.
                for example, -1 for draw 2 lower
            draw_all (bool): If upper hand, draw all before stopping. Default false.
            return_val (bool): Return the string. Default False.
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
        if verbose:
            logger.info(
                f"Drew {draws} vs {TC} with TR {DR}{ul_str}: {self.result_types[result]}"
            )

        if return_val:
            return result


class Player(Deck, Beast):
    # TODO: STATUS EFFECT SAVES CAN'T CURRENTLY FATIGUE
    # TODO: REFACTOR TO CENTRALIZE STATUS EFFECT SAVES
    def __init__(self, use_TC=True, **kwargs):
        Deck.__init__(self, use_TC)
        Beast.__init__(self, **kwargs)
        self._valid_attribs = [f.name for f in fields(self.Attribs)]
        self._valid_mods = self._valid_attribs + [f.name for f in fields(self.Skills)]
        self._fatigue = 0
        self._PP_mult = 1
        self._statuses = {
            "upper_lower_save": 0,
            "upper_lower_check": 0,
            "upper_lower_next_save": 0,
            "upper_lower_next_check": 0,
            "Entangled": 0,
            "Knocked Down": 0,
            "Knocked Out": 0,
        }
        self._not_simulated = ["Blinded", "Deafened", "Enthralled", "Charmed"]

    def __repr__(self):
        """Result of print(Player)"""
        output = self.Name + "\n"
        output += "TC       : %02s | pc.HP : %d/%d\n" % (
            self.TC,
            self.HP,
            self.HP_Max,
        )
        output += "Hand     :  %02d | pc.PP : %d/%d\n" % (
            len(self.hand),
            self.PP,
            self.PP_Max,
        )
        output += "Deck     :  %02d | pc.AP : %d/%d\n" % (
            len(self.cards),
            self.AP,
            self.AP_Max,
        )
        output += "Discards :  %02d | RestC : %d/%d\n" % (
            len(self.discards),
            self.RestCards,
            self.RestCards_Max,
        )
        return output

    def _apply_upper_lower(self, save_check: str, kwarg_dict: dict, skill="") -> dict:
        all_type = "upper_lower_" + save_check
        next_type = "upper_lower_next_" + save_check
        extra = 0
        if self._statuses.get("Entagled", False) and skill == "AGL":
            extra -= 1
        if self._statuses.get("Knocked Down", False) and skill in ["AGL", "STR"]:
            extra -= 1
        if self._statuses.get("Frozen", False) and type == "skill":
            extra -= 1
        if self._fatigue > 0 and type == "save":
            extra -= 1
        elif self._fatigue > 1:
            extra -= 1
        kwarg_dict["upper_lower_int"] = (
            kwarg_dict.get("upper_lower_int", 0)
            + self._statuses.get(all_type, 0)
            + self._statuses.get(next_type, 0)
            + extra
        )
        self._statuses[next_type] = 0
        return kwarg_dict

    def modify_fatigue(self, change=1):
        self._fatigue += change
        if self._fatigue >= 3 and not self._statuses.get("_fatigue3"):
            self._statuses["_fatigue3"] = True
            self.Speed = self.Speed / 2
        if self._fatigue >= 4 and not self._statuses.get("_fatigue4"):
            self._statuses["_fatigue4"] = True
            self._PP_mult = 2
        if self._fatigue >= 5 and not self._statuses.get("_fatigue5"):
            self._statuses["_fatigue5"] = True
            self._statuses["Knocked Out"] = self._statuses.get("Knocked Out", 0) + 1

    def check_by_skill(self, TC: Card, DR: int, skill: str, **kwargs):
        """Accepts any Skill or Attrib. Accepts any valid args of Deck.check"""
        assert (
            skill in self._valid_mods
        ), f"Could not find {skill} in {self._valid_mods}"
        if isinstance(skill, list):  # if list, use the better skill
            skill_vals = {a: getattr(self.PC.Attribs, a) for a in skill}
            skill = max(skill_vals, key=skill_vals.get)
        mod = getattr(self.Skills, skill, None) or getattr(self.Attribs, skill, None)
        new_kwargs = self._apply_upper_lower("check", kwargs, skill=skill)
        result = self.check(TC, DR, mod=mod, **new_kwargs)
        if result == 0:
            self.modify_fatigue()
            self.check_by_skill(TC=TC, DR=DR, skill=skill, **kwargs)
        return result

    def save(self, DR: int = 3, attrib="None", **kwargs):
        """Accepts any Attrib. Accepts any valid args of Deck.check"""
        if isinstance(attrib, list):  # if list, use the better attrib
            attr_vals = {a: getattr(self.PC.Attribs, a) for a in attrib}
            attrib = max(attr_vals, key=attr_vals.get)
        if attrib != "None":  # Default to mod of 0 when "None"
            assert (
                attrib in self._valid_attribs
            ), f"Could not find {attrib} in {self._valid_attribs}"
        new_kwargs = self._apply_upper_lower("save", kwargs, skill=attrib)
        result = self.check(
            TC=self.TC, DR=DR, mod=getattr(self.Attribs, attrib, 0), **new_kwargs
        )
        if result == 0:
            self.modify_fatigue()
            self.save(DR=DR, attrib=attrib, **kwargs)
            pass
        return result

    def full_rest(self, **_):
        self.shuffle()
        for i in ["HP", "PP", "AP", "RestCards", "Speed"]:
            setattr(self.pc, i, getattr(self.pc, i + "_Max"))
        self._statuses = {}

    def quick_rest(self, **kwargs):
        # Never uses Fate cards here
        point_total = 0  # Recover HP/PP
        while self.RestCards > 0 and (
            (self.HP < self.HP_Max) or (self.PP < self.PP_Max)
        ):  # Will always fully recover with available rest cards
            draw = self.save(return_val=True, **kwargs)
            if not draw:
                break
            points = 2 if draw > 0 else 1
            point_total += points
            logger.debug(f"Recovering {points} with cards")
            for _ in range(points):  # Prioritizes 'where am I missing more?'
                attr_diffs = {
                    "HP": abs(self.HP - self.HP_Max),
                    "PP": abs(self.PP - self.PP_Max),
                }
                increment_this = max(attr_diffs, key=attr_diffs.get)
                setattr(self.pc, increment_this, getattr(self.pc, increment_this) + 1)
                logger.debug(
                    f"   1 {increment_this} to {getattr(self.pc,increment_this,'?')}"
                )
            self.RestCards -= 1

        AP_check_mod = max([self.Skills.Knowledge, self.Skills.Craft])
        down_AP = self.AP_Max - self.AP
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
                self.AP += down_AP
                logger.debug(f"Recovering {down_AP} AP to {self.AP}")
                point_total += down_AP
                break

        logger.info(f"Recovered {point_total} HP/PP/AP during Quick Rest")
        self.shuffle(limit=(10 + self.Attribs.VIT * 2))

    def wound(self, wound_val, bypass_HP=False):
        # Add Charmed Enthralled checks here
        for _ in range(wound_val):
            if self.AP > 0 and not bypass_HP:
                self.AP -= 1
            else:
                self.HP -= 1
        if self.HP <= 0:
            if self._statuses.get("Knocked Out"):
                logger.info(
                    f"{self.Name} attacked again while KO. "
                    + "Epic Event not simulated."
                )
            else:
                self._statuses["Knocked Out"] = 1

    def take_action(self, type="Major") -> Power:
        if self.HP <= 0:
            return
        if self._statuses.get("Stunned") and type == "Minor":
            self.info(f"{self.Name} stunned, skipping Minor Action.")
            return
        if self._statuses.get("Burned") and type == "Minor":
            if self.save(attrib="GUT", return_val=True) > 0:
                self._statuses["Burned"] = 0
                logger.info(f"{self.Name} used Minor Action to stop burning.")
                return
            else:
                self.wound(1, bypass_HP=True)
                return
        if self._statuses.get("Entangled") and type == "Major":
            if self.save(attrib="STR", return_val=True) > 0:
                self._statuses["Entangled"] = 0
                logger.info(f"{self.Name} is no longer stunned.")
            return
        options = [
            p
            for p in self.Powers_list  # ASSUME: Always use lesser PP option
            if p.Type == type and ensure_list(p.PP)[0] <= self.PP * self._PP_mult
        ]
        choice = random.choice(options) if options else None
        if choice:
            logger.info(
                f"{self.Name} used {ensure_list(choice.PP)[0]}/{self.PP} PP "
                + f"with {choice.Name}"
            )
        else:
            logger.info(f"{self.Name} no {type} choices")
        self.PP -= ensure_list(getattr(choice, "PP", 0))[0] * self._PP_mult
        return choice

    def start_turn(self):
        if self._statuses.get("Knocked Down"):
            logger.info(f"{self.Name} gets up")
            self._statuses["Knocked Down"] = 0
        self._shake_status(["Stunned", "Poisoned"])

    def end_turn(self):
        self._shake_status(["Frozen", "Suffocating"])

    def _pass(self, *args, **kwargs):
        pass

    def _shake_status(self, statuses: list):
        status_dict = {
            "Stunned": {"attrib": "CON", "fail": self._pass, "succeed": self._pass},
            "Poisoned": {"attrib": "VIT", "fail": self.discard, "succeed": self._pass},
            "Frozen": {"attrib": "STR", "fail": self._pass, "succeed": self._pass},
            "Suffocating": {"attrib": "VIT", "fail": self.wound, "succeed": self.wound},
        }
        for status in statuses:
            if self._statuses.get(status):
                if self.save(attrib=status_dict[status]["attrib"], return_val=True) > 0:
                    logger.info(f"{self.Name} shakes off {status}")
                    self._statuses[status] = 0
                    status_dict[status]["succeed"](
                        self._statuses[status], bypass_HP=True
                    )
                    logger.info(f"{self.Name} is no longer {status}.")
                else:
                    logger.info(f"{self.Name} remains {status}")
                    status_dict[status]["fail"](
                        self._statuses[status] + 1, bypass_HP=True
                    )
            if len(self.cards) == 0:
                self.modify_fatigue(1)


class Encounter(object):
    def __init__(
        self, PCs: List[Union[Player, Beast]], Enemies: List[Union[Player, Beast]]
    ):
        self.PCs = [p if isinstance(p, Player) else Player(**p) for p in PCs]
        self.enemies = [p if isinstance(p, Player) else Player(**p) for p in Enemies]
        self.turn_order = [*self.PCs, *self.enemies]
        random.shuffle(self.turn_order)
        self.status_list = [
            "Stunned",
            "Entangled",
            "Knocked",
            "Blinded",
            "Deafened",
            "Knocked Out",
            "Knocked Down",
            "Burned",
            "Poisoned",
            "Frozen",
            "Suffocating",
            "Charmed",
            "Enthralled",
        ]
        self._not_simulated = ["Blinded", "Deafened", "Enthralled", "Charmed"]

    def add_enemy(self, name: Player):
        self.enemies.append(name)

    def _apply_power(self, attacker, targets: List[Player], power=None):
        if not power:
            return
        for _ in range(ensure_list(power.Targets)[0]):
            target = random.choice(targets)
            if power.Save:
                result = target.save(
                    DR=power.Save.DR, attrib=power.Save.Type, return_val=True
                )
                if result < 0:
                    if power.Save.Fail in self.status_list:
                        target._statuses[power.Save.Fail] = (
                            target._statuses.get(power.Save.Fail, 0) + 1
                        )
                        logger.info(
                            f"{target.Name} is {power.Save.Fail} 🔥: "
                            + f"{target._statuses.get(power.Save.Fail, 0)}"
                        )
                        if power.Save.Fail in self._not_simulated:
                            logger.warning(
                                f"{target.Name} {power.Save.Fail} not simulated"
                            )
                    else:
                        logger.info(target.Name + " " + power.Save.Fail)
                elif result > 0:
                    logger.info(f"{target.Name} resisted {power.Save.Fail}")
                elif power.Save.Succeed:
                    logger.info(target.Name + power.Save.Succeed + ". Not simulated")
            if power.Damage:
                damage = ensure_list(power.Damage)[0]
                result = attacker.check_by_skill(
                    TC=target.TC,
                    DR=target.AR,
                    skill=attacker.Primary_Skill,
                    upper_lower_int=power.upper_lower_int,
                    return_val=True,
                )
                if result > 0:
                    wound = damage + 1 if result > 3 else damage
                    target.wound(wound)
                    logger.info(
                        f"{attacker.Name} wounded {target.Name} by "
                        + f"{wound}: AP {target.AP}/{target.AP_Max}, HP "
                        + f"{target.HP}/{target.HP_Max}"
                    )

    def _take_turn(self, attacker: Player, targets: List[Player]):
        actions = ["Major", "Minor"]
        random.shuffle(actions)  # Randomize major vs minor first

        attacker.start_turn()
        logger.info(f"{attacker.Name} start turn")
        for action in actions:
            self._apply_power(attacker, targets, attacker.take_action(action))
        attacker.end_turn()

    def sim_round(self):
        for char in self.turn_order:
            if char.HP <= 0:
                logger.info(f"{char.Name} is Knocked Out, no turn")
            else:
                self._take_turn(char, self.enemies if char in self.PCs else self.PCs)
