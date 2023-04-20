import copy
import random
from math import floor

from ..templates.bestiary import Beast
from ..templates.powers import Power
from ..utils import ensure_list, logger
from .deck import Card, Deck
from .player import Player


class Encounter(object):
    """A Deck of Adventures encounter.

    A series of methods for simulating an encounter in Deck of Adventures.

    Attributes:
        gm_deck (Deck): Single deck for GM in encounter
        PCs (list[Player]): List of Players. If initialized with Beast type, will be
            converted to Players
        Enemies (list[Player]): List of Enemies. If initialized with Beast type, will be
            converted to Players
        turn_order (list[Player]): Concatenated list of PCs and Enemies in randomized
            order
        status_list (list[Str]): List of statuses that are simulated.

    """

    def __init__(self, PCs: list[Player | Beast], Enemies: list[Player | Beast]):
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

    def set_csv_logging(self, setting: bool):
        """Turn on CSV logging for all Players in turn_order"""
        for char in self.turn_order:
            char._CSV_LOGGING = setting

    def add_creature(self, creature: Player, side: str = "Enemies"):
        """Add a creature of type Player to the Encounter.

        Args:
            creature (Player): creature to be added
            side (str, optional): Enemies or PCs. Defaults to "Enemies".
        """
        if side.lower() == "enemies":
            self.enemies.append(creature)
        else:
            self.PCs.append(creature)
        self.turn_order = [*self.PCs, *self.enemies]

    def _apply_power(
        self,
        attacker: Player,
        targets: list[Player],
        power: Power = None,
        return_string: bool = False,
        force_result: int = None,  # Force outcome
    ) -> str | None:
        """Perform a Power, attack a target.

        Args:
            attacker (Player): creature performing Power
            targets (list[Player]): List of possible targets
            power (Power, optional): Power to be used. Defaults to None, where nothing
                happens.
            return_string (bool, optional): Return a string describing what happened.
                Defaults to False.
            force_result (int, optional): Override card draw. Defaults to None, where
                attacker/targets draw according to Power for random result.

        Returns:
            str | None: If return_string, returns a string describing results.
        """
        targets = ensure_list(targets)
        if not power:
            return

        result_strings = [f"{attacker.Name} used {power.Name}"]

        for _ in range(ensure_list(power.Targets)[0]):
            target = random.choice(targets)
            if power.Save:
                DR = power.Save.DR or 3 - floor(attacker.Primary_Skill_Mod / 2)
                result = target.save(DR=DR, attrib=power.Save.Type, return_val=True)
                if force_result:
                    result = force_result
                if result < 0:
                    if power.Save.Fail in self.status_list:
                        target._statuses[power.Save.Fail] = (
                            target._statuses.get(power.Save.Fail, 0) + 1
                        )
                        result_strings.append(
                            f"{target.Name} is {power.Save.Fail}: "
                            + f"{target._statuses.get(power.Save.Fail, 0)}"
                        )
                        if power.Save.Fail in self._not_simulated:
                            logger.warning(
                                f"{target.Name} {power.Save.Fail} not simulated"
                            )
                    else:
                        result_strings.append(f"{target.Name} {power.Save.Fail}")
                elif result > 0:
                    result_strings.append(f"{target.Name} resisted {power.Save.Fail}")
                    if power.Save.Succeed:
                        result_strings.append(
                            target.Name + " " + power.Save.Succeed + ". Not simulated"
                        )
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
                    result_strings.append(
                        f"{attacker.Name} wounded {target.Name} by "
                        + f"{wound}: AP {target.AP}/{target.AP_Max}, HP "
                        + f"{target.HP}/{target.HP_Max}"
                    )
            if not return_string:
                logger.info(result_strings)
                result_strings = []

        if return_string:
            return "\n".join(result_strings)

    def _take_turn(self, attacker: Player, targets: list[Player]):
        """Runs the attackers turn on list of possible targets.

        Randomizes if Major or Minor action is taken first before executing all
        components of attacker's turn.

        Args:
            attacker (Player): Player taking the turn.
            targets (list[Player]): List of possible targets.
        """
        actions = ["Major", "Minor"]
        random.shuffle(actions)  # Randomize major vs minor first

        attacker.start_turn()
        for action in actions:
            self._apply_power(attacker, targets, attacker.take_action(action))
        attacker.end_turn()

    def _sim_single_round(self):
        """Simulate a single round in turn order."""
        for char in self.turn_order:
            if char.HP <= 0:
                logger.info(f"{char.Name} is Knocked Out, no turn")
            else:
                self._take_turn(char, self.enemies if char in self.PCs else self.PCs)

    def sim_round(self, n: int = 1):
        """Run n number of rounds of combat in turn order.

        Args:
            n (int, optional): Number of rounds to simulate. Defaults to 1.
        """
        for _ in range(n):
            self._sim_single_round()

    def sim_full_rest(self, participants: list[Player] = None):
        """Simulate a full rest for all participants provided. Default to all.

        Args:
            participants (list[Player], optional): Creatures who should take a full rest.
                Defaults to all in turn order.
        """
        if not participants:
            participants = self.turn_order
        for char in participants:
            char.full_rest()

    def sim_quick_rest(self, participants: list[Player] = None, **kwargs):
        """Simulate a quick rest for all participants provided. Default to all.

        Args:
            participants (list[Player], optional): Creatures who should take a quick rest.
                Defaults to all in turn order.
        """
        if not participants:
            participants = self.turn_order
        for char in self.turn_order:
            char.quick_rest(**kwargs)

    def sim_epic_event(
        self,
        TC: Card = None,
        DR=3,
        participants: list[Player] = None,
        skills: list[str] | str = None,
        successes_needed: int = 1,
        return_string: bool = False,
    ) -> str | None:
        """Simulate an epic event. Players go first, them GM.

        Args:
            TC (Card): target card. Default draw from gm_deck
            DR (int): Draw range.
            participants (list[Player]): list of those involved on a TC. Default all PCs
            skills (list[str] | str): Type of check for each participant in participant
                order. Default 0 mod. If same for all, provide as single string.
                e.g., participants=[PC1, PC2], skill=['STR','Finesse'].
            successes_needed (int): N suited hits before end. Default 1
            return_string (bool): return a string describing the result.
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
        result_string = f"{victor} wins after {draw_count} total cards drawn"

        if return_string:
            return result_string

        logger.info(result_string)
