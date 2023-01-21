import copy
import random
from typing import List, Union

from ..templates import Beast
from ..utils import ensure_list, logger
from .deck import Deck
from .player import Player


class Encounter(object):
    def __init__(
        self, PCs: List[Union[Player, Beast]], Enemies: List[Union[Player, Beast]]
    ):
        self.gm_deck = Deck(use_TC=False)
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
                            f"{target.Name} is {power.Save.Fail}: "
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
                    if result > 3:
                        target._statuses["Stunned"] = 1
                    logger.info(
                        f"{attacker.Name} wounded {target.Name} by "
                        + f"{wound}: AP {target.AP}/{target.AP_Max}, HP "
                        + f"{target.HP}/{target.HP_Max}"
                    )

    def _take_turn(self, attacker: Player, targets: List[Player]):
        actions = ["Major", "Minor"]
        random.shuffle(actions)  # Randomize major vs minor first

        attacker.start_turn()
        for action in actions:
            self._apply_power(attacker, targets, attacker.take_action(action))
        attacker.end_turn()

    def _sim_single_round(self):
        for char in self.turn_order:
            if char.HP <= 0:
                logger.info(f"{char.Name} is Knocked Out, no turn")
            else:
                self._take_turn(char, self.enemies if char in self.PCs else self.PCs)

    def sim_round(self, n: int = 1):
        for _ in range(n):
            self._sim_single_round()

    def sim_full_rest(self, participants: List[Player] = None):
        if not participants:
            participants = self.turn_order
        for char in participants:
            char.full_rest()

    def sim_quick_rest(self, participants: List[Player] = None, **kwargs):
        if not participants:
            participants = self.turn_order
        for char in self.turn_order:
            char.quick_rest(**kwargs)

    def sim_epic_event(
        self,
        TC=None,
        DR=3,
        participants: List[Player] = None,
        skills: List[str] = None,
        successes_needed=1,
    ):
        """Run epic event. Players go first, them GM.

        Args:
            TC: target card. Default draw from gm_deck
            participants: list of those involved on a TC. Default all PCs
            skill: Type of check for each participant in particpant order. Default 0 mod
                e.g., participants=[PC1, PC2], skill=['STR','Finesse'].
                If same for all, provide as string
            successes_needed: N suited hits before end. Default 1
        """
        if not TC:
            TC = self.gm_deck.draw()
        if not participants:
            participants = copy.copy(self.PCs)
        else:
            participants = ensure_list(participants)
        if not isinstance(skills, list):
            skills = [skills] * len(participants)

        participants.append(self.gm_deck)
        skills.append(None)

        player_successes = 0
        gm_successes = 0
        draw_count = 0

        while player_successes < successes_needed and gm_successes < successes_needed:
            for participant, skill in zip(participants, skills):
                draw_count += 1
                result = participant.check_by_skill(
                    TC=TC, DR=DR, skill=skill, return_val=True
                )
                success = True if result > 2 else False
                if success and participant.Name == "GM":
                    gm_successes += 1
                elif success:
                    player_successes += 1

                if success:
                    logger.info(
                        f"Party {player_successes}, GM {gm_successes} | "
                        + f"{participant.Name} {participant.result_types[result]}"
                    )
        victor = "GM" if gm_successes > player_successes else "Party"
        logger.info(f"{victor} wins after {draw_count} total cards drawn")
