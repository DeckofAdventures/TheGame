import random
from dataclasses import fields

from ..templates.bestiary import Beast
from ..templates.powers import Power
from ..utils.list_manip import ensure_list
from ..utils.logger import logger
from ..utils.logger_csv import draw_log, rest_log
from .deck import Card, Deck


class Player(Deck, Beast):
    def __init__(self, use_TC=True, **kwargs):
        Deck.__init__(self, use_TC)
        Beast.__init__(self, **kwargs)
        self._valid_attribs = [f.name for f in fields(self.Attribs)] + ["None"]
        self._valid_skills = [f.name for f in fields(self.Skills)] + ["None"]
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
        self._CSV_LOGGING = False

    def __repr__(self):
        """Result of print(Player)"""
        output = self.Name + "\n"
        output += "TC       :%02s | pc.HP : %d/%d\n" % (
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
            0 + kwarg_dict.get("upper_lower_int", 0)
            if kwarg_dict.get("upper_lower_int", 0)
            else 0
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

    def _find_highest_stat(self, options: list) -> int:
        if not isinstance(options, list):
            return options, getattr(self.Attribs, options, 0) or getattr(
                self.Skills, options, 0
            )
        vals = {}
        for option in options:
            vals.update(
                {
                    option: getattr(self.Attribs, option, 0)
                    or getattr(self.Skills, option, 0)
                }
            )
        skill = max(vals, key=vals.get)
        return skill, vals[skill]

    def check_by_skill(self, TC: Card, DR: int, skill: str = None, **kwargs):
        """Accepts any Skill or Attrib. Accepts any valid args of Deck.check"""
        if not skill:
            skill = "None"
        if self._CSV_LOGGING:
            kwargs["return_val"] = True
        skill, mod = self._find_highest_stat(skill)
        new_kwargs = self._apply_upper_lower("check", kwargs, skill=skill)

        # Need to account for return_string for bot and result for checking result
        if new_kwargs.get("return_string"):
            result_string, result = self.check(TC, DR, mod=mod, **new_kwargs)
        else:
            result = self.check(TC, DR, mod=mod, **new_kwargs)

        if result == 0:
            self.modify_fatigue()
            result = self.check_by_skill(TC=TC, DR=DR, skill=skill, **kwargs)
        # NOTE: drawlog doesn't know if had options
        draw_log.info(
            [
                self.id,
                "check",
                result,
                self.result_types.get(result, None),
                DR,
                skill,
                mod,
                kwargs.get("upper_lower", "n"),
                kwargs.get("draw_n", 1),
            ]
        )
        if new_kwargs.get("return_string"):
            return result_string
        return result

    def save(self, DR: int = 3, attrib="None", **kwargs):
        """Accepts any Attrib. Accepts any valid args of Deck.check"""
        if self._CSV_LOGGING:
            kwargs["return_val"] = True

        attrib, mod = self._find_highest_stat(attrib)

        assert (
            attrib in self._valid_attribs
        ), f"Could not find {attrib} in {self._valid_attribs}"
        new_kwargs = self._apply_upper_lower("save", kwargs, skill=attrib)

        # Need to account for return_string for bot and result for checking result
        if new_kwargs.get("return_string"):
            result_string, result = self.check(
                TC=self.TC, DR=DR, mod=getattr(self.Attribs, attrib, 0), **new_kwargs
            )
        else:
            result = self.check(
                TC=self.TC, DR=DR, mod=getattr(self.Attribs, attrib, 0), **new_kwargs
            )

        if result == 0:
            self.modify_fatigue()
            self.save(DR=DR, attrib=attrib, **kwargs)

        # NOTE: drawlog doesn't know if had options
        draw_log.info(
            [
                self.id,
                "save",
                result,
                self.result_types.get(result),
                DR,
                attrib,
                mod,
                kwargs.get("upper_lower", "n"),
                kwargs.get("draw_n", 1),
            ]
        )

        if new_kwargs.get("return_string"):
            return result_string
        if new_kwargs.get("return_val"):
            return result

    def full_rest(self, return_string=False, **_):
        rest_log.info(
            [
                self.id,
                "before",
                "full",
                len(self.discards),
                len(self.hand),
                self.HP,
                self.AP,
                self.PP,
                self.RestCards,
            ]
        )
        self.shuffle()
        for i in ["HP", "PP", "AP", "RestCards", "Speed"]:
            setattr(self, i, getattr(self, i + "_Max"))
        self._statuses = {}
        rest_log.info(
            [
                self.id,
                "after",
                "full",
                len(self.discards),
                len(self.hand),
                self.HP,
                self.AP,
                self.PP,
                self.RestCards,
            ]
        )
        if return_string:
            return f"{self.Name} fully rested."

    def quick_rest(self, return_string=False, **kwargs):
        # Never uses Fate cards here
        rest_log.info(
            [
                self.id,
                "before",
                "quick",
                len(self.discards),
                len(self.hand),
                self.HP,
                self.AP,
                self.PP,
                self.RestCards,
            ]
        )
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
                setattr(self, increment_this, getattr(self, increment_this) + 1)
                logger.debug(
                    f"   1 {increment_this} to {getattr(self,increment_this,'?')}"
                )
            self.RestCards -= 1
        rest_log.info(
            [
                self.id,
                "after",
                "quick",
                len(self.discards),
                len(self.hand),
                self.HP,
                self.AP,
                self.PP,
                self.RestCards,
            ]
        )

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

        result = f"{self.Name} recovered {point_total} HP/PP/AP during Quick Rest"
        logger.info(result)
        self.shuffle(limit=(10 + self.Attribs.VIT * 2))
        if return_string:
            return result

    def wound(self, wound_val, bypass_HP=False):
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
        self._shake_status(["Charmed", "Enthralled"])

    def take_action(self, type="Major") -> Power:
        if self.HP <= 0:
            return
        if self._statuses.get("Stunned") and type == "Minor":
            logger.info(f"{self.Name} stunned, skipping Minor Action.")
            return
        if self._statuses.get("Burned") and type == "Minor":
            self._shake_status(["Burned"])
            return
        if self._statuses.get("Entangled") and type == "Major":
            self._shake_status(["Entangled"])
            return
        options = [
            p
            for p in self.Powers.values()
            if p is not None
            and p.Type == type
            and ensure_list(p.PP)[0] <= self.PP * self._PP_mult
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
        pass  # Intentionally empty for statuses with no consequence

    def _shake_status(self, statuses: list):
        status_dict = {
            "Stunned": {"attrib": "CON", "fail": self._pass, "succeed": self._pass},
            "Poisoned": {"attrib": "VIT", "fail": self.discard, "succeed": self._pass},
            "Frozen": {"attrib": "STR", "fail": self._pass, "succeed": self._pass},
            "Suffocating": {"attrib": "VIT", "fail": self.wound, "succeed": self.wound},
            "Burned": {"attrib": "GUT", "fail": self.wound, "succeed": self._pass},
            "Entangled": {"attrib": "STR", "fail": self._pass, "succeed": self._pass},
        }
        for status in statuses:
            if self._statuses.get(status):
                if self.save(attrib=status_dict[status]["attrib"], return_val=True) > 0:
                    logger.info(f"{self.Name} shakes off {status}")
                    self._statuses[status] = 0
                    status_dict[status]["succeed"](
                        self._statuses[status], bypass_HP=True
                    )
                else:
                    logger.info(f"{self.Name} remains {status}")
                    status_dict[status]["fail"](
                        self._statuses[status] + 1, bypass_HP=True
                    )
            if len(self.cards) == 0:
                self.modify_fatigue(1)
