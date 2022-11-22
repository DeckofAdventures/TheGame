<!-- DEVELOPERS: Please edit corresponding yml -->

# Combat

## Control

**Battlecharged**

- Description: You're always ready for something to go down.
- Mechanic: Passive. When drawing initiative, Draw with Upper Hand.
- XP: 1


**Critical Master**

- Description: When you hit big, you hit BIG. Enemies don't stand a chance against you when you make a critical hit against them.
- Mechanic: Passive. All Critical Success attacks now deal double damage instead of adding +1 damage.
- XP: 1
- Prereq_Level: 3


**Momentum**

- Description: By brute strength, force others to move around the battlefield.
- Mechanic: Passive. As part of your movement, you attempt to move a character who is within 1 space of you.If unwilling, target(s) make a STR or AGL Save. On fail, target(s) be moved to 1 space of attacker's end position.. 
- XP: 1
- Prereq_Role: Defender
- Prereq_Skill: Brute > 0


**Momentum Aura**

- Description: Your strength is supernatural, bending the gravity around you.
- Mechanic: Major. For 1 PP, Your Momentum ability extends to 3 spaces.. If unwilling, target(s) make a STR or AGL Save. On fail, target(s) be moved to 1 space of attacker's end position.. 
- XP: 2
- PP: 1
- Prereq_Role: Defender
- Prereq_Skill: Brute > 1
- Prereq_Power: Momentum
- Target: 6
- Tags: Multi-target


**Find Weakness**

- Description: You can size up an opponent and discover their weaknesses.
- Mechanic: Minor. As a Minor Action, you make a contested Detection check vs. the target's Bluffing. On a Success, you learn one Vulnerability and on Critical Success you learn all Vulnerabilities.
- XP: 1
- Prereq_Level: 2
- Prereq_Skill: Detection > 0
- Tags: Difficulty Prediction


**Pack Tactics**

- Description: When an enemy is outnumbered, you know just how to take advantage.
- Mechanic: Minor. For 1 PP, When an enemy is next to one or more of your allies, you may expend a Minor Action to grant yourself Upper Hand (+1) on your next attack for each ally in their space. If allies or targets move before you attack, this bonus is adjusted accordingly.. 
- XP: 2
- PP: 1
- Prereq_Level: 2
- Tags: Difficulty Prediction


## Mystic Attacks

**Attack, Mystic**

- Description: You've been trained in some form of Magic to Technology and can produce the most basic form with ease. This could be an electrified touch or a blast of energy at range.
- Mechanic: Major. As a Major Action in combat, you can make a check to attack an Enemy. This may be performed while under the effects of another Power.
- XP: 1
- Prereq_Skill: Knowlege > 0 or Craft > 0


**Attack, Mystic Aura**

- Description: You deploy resources to channel your magic all around you.
- Mechanic: Major. For 1 or 2 PP, You perform your Mystic Attack on all characters within 1 or 2 space(s).. 
- XP: 2
- PP: 1 or 2
- Prereq_Role: Caster or Support
- Prereq_Power: Attack, Mystic
- Tags: Multi-target


**Attack, Mystic Amplification**

- Description: You channel your talents into a physical weapon, melding the physical and supernatural.
- Mechanic: Major. For 1 PP, Designate a physical weapon. You may make a Weapon Attack with this weapon using your Primary Skill modifier. This property is lost when you use another Power.. 
- XP: 1
- PP: 1
- Prereq_Role: Martial or Caster
- Prereq_Power: Attack, Mystic


**Attack, Mystic Cone**

- Description: You deploy resources to channel your magic in a wide blast in front of you.
- Mechanic: Major. For 1 PP, Choose one effect when you take this power
- You perform your Mystic Attack on all characters within a cone of 3 spaces in front of you.
- All characters in a 3 space cone in front of you make a Contested Conviction check. On failure, they are Knocked Down. 
- XP: 2
- PP: 1
- Prereq_Role: Caster
- Prereq_Skill: Knowledge > 1 or Craft > 1
- Prereq_Power: Attack, Mystic
- Tags: Multi-target


**Attack, Mystic Confusion**

- Description: You channel your abilities to target the psyche of your enemy to leave them incapacitated.
- Mechanic: Major. For 1 or 2 PP, You draw a Target Card and force 1 or 3 characters to make a Conviction check against your TC. On a failure, those characters are Stunned.. 
- XP: 2
- PP: 1 or 2
- Prereq_Role: Support or Caster
- Prereq_Power: Attack, Mystic
- Tags: Multi-target


**Attack, Mystic Entangle**

- Description: You channel your abilities to tie your target in place.
- Mechanic: Major. For 1 or 2 PP, Selected targets make a Save.. Once, target(s) make a DR 3 AGL Save. On fail, target(s) Entangled. 
- XP: 2
- PP: 1 or 2
- Prereq_Role: Support or Caster
- Prereq_Power: Attack, Mystic
- Target: 1 or 3
- Tags: Multi-target


**Attack, Mystic Deprivation**

- Description: You channel your abilities deprive a target of their senses.
- Mechanic: Major. For 1 or 2 PP, Select the Blinded or Deafened effect.. Once,, target(s) make a DR 3 GUT Save. On fail, target(s) Blinded or Deafened unless immune.. 
- XP: 2
- PP: 1 or 2
- Prereq_Role: Support or Caster
- Prereq_Power: Attack, Mystic
- Target: 1 or 3
- Tags: Multi-target


**Attack, Mystic Dual-Shot**

- Description: You are so adept mystic arts you can start another spell before even finishing the first.
- Mechanic: Minor. On your turn, you may take a second Mystic Attack with Lower Hand.
- XP: 3
- Prereq_Skill: Finesse > 1 or Knowledge > 1 or Craft > 1
- Prereq_Power: Attack, Mystic
- Tags: Multi-target


**Attack, Mystic Dual-Wield Master**

- Description: You are a master of wielding two weapons in combat.
- Mechanic: Minor. On your turn, you may take a second Mystic Attack as a Minor Action.
- XP: 1
- Prereq_Level: 3
- Prereq_Power: Attack, Mystic Dual-Shot
- Tags: Multi-target


## Support

**Heal**

- Description: Can channel magical energy or medical training to heal others
- Mechanic: Major. For 1 or 2 PP, Heal yourself or another you can see for 1 or 3 Health Points. 
- XP: 2
- PP: 1 or 2
- Prereq_Role: Support


**Lend Aid**

- Description: Just a little help from a friend
- Mechanic: Minor. As a Minor Action, designate one ally who, on their next draw, will draw with the Upper Hand.
- XP: 1
- Prereq_Role: Support


**Lend Confusion**

- Description: You're such a distracting presence that you bury into the mind of your target, having a sustained effect.
- Mechanic: Major. Select one character to put under the effect of the Lend Distraction Power. At the end of each of their turns this character makes a Contested Conviction Check vs. your Primary Skill to end the effect.
- XP: 1
- Prereq_Role: Support or Caster
- Prereq_Level: 2
- Prereq_Power: Lend Distraction


**Lend Mass Confusion**

- Description: You're such a distracting presence that you bury into the mind of many target, having a sustained effect.
- Mechanic: Major. For 2 PP, You draw a TC. 2 or 3 targets make a Conviction check against your TC. On a failure, targets draw with the Lower Hand on any actions made during their turn. At the end of each of their turns, targets may repeat the check to end the effect.. 
- XP: 2
- PP: 2
- Prereq_Role: Support or Caster
- Prereq_Level: 3
- Prereq_Power: Lend Confusion
- Tags: Multi-target


**Lend or Remove Skill**

- Description: You really know how to target an ability and either support it or get in it's way.
- Mechanic: Major. For 1 or 2 PP, Designate a character that you would like to Boost or Reduce and choose a Skill (or action that would require a Skill such as Attack). This character draws at Upper or Lower Hand (2 or 3) checks that involve this Skill on their next turn. 
- XP: 2
- PP: 1 or 2
- Prereq_Role: Support


**Lend Readiness**

- Description: Your talents bolster you allies' speed and alertness.
- Mechanic: Minor. Select one character. Until the end of the next combat, this character draws their Target Card with the Upper Hand. This effect is maintained even if you use another Power.
- XP: 1
- Prereq_Role: Support


**Lend Vigor**

- Description: Channel energy to do more than help: inspire!
- Mechanic: Major. For 1 or 2 PP, Designate 1 or 2 character(s) who, on their next turn, can take an additional Major Action without penalty and move 2 additional spaces during their movement.. 
- XP: 2
- PP: 1 or 2
- Prereq_Role: Support or Caster


**Slow**

- Description: You selectively bend the nature of time
- Mechanic: Major. For 2 PP, Select a point in space. You initiate a Primary Skill Contested Check vs. Strength for all creatures within 2 spaces. On a failure, their speed is halved and they are limited to one Major or Minor action per turn. A creature that starts their turn outside of the area is no longer affected. Objects in the area are slowed until the effect ends or they are moved by a creature.. 
- XP: 2
- PP: 2
- Prereq_Role: Support or Caster
- Prereq_Level: 3


**Shield, Others**

- Description: Fortify others by summoning magical armor.
- Mechanic: Major. For 1 or 2 PP, Add 1 or 2 AP to a creature you can see. This effect does not stack with other Powers, but does stack on top of AP granted by physical items.. 
- XP: 2
- PP: 1 or 2
- Prereq_Role: Support


**Shield, Self**

- Description: Fortify yourself even further, adjusting your shield or summoning magical armor.
- Mechanic: Major. For 1 or 2 PP, Add 1 or 2 AP to yourself. This effect is in addition to AP from physical items, but must replace AP from other Powers.. 
- XP: 2
- PP: 1 or 2
- Prereq_Role: Defender


### Distract

**Lend Distraction**

- Description: Just an annoyance in the distance
- Mechanic: Minor. As a Minor Action, designate a character who, on their next draw, will draw with the Lower Hand.
- XP: 1


**Lend Mass Distraction**

- Description: You know how to cause a scene.
- Mechanic: Major. For 1 or 2 PP, Draw a Target Card. 2 or 3 targets make a Conviction check against your TC. On a failure, those characters draw with the Lower Hand on any actions or checks made during their next turn.. 
- XP: 2
- PP: 1 or 2
- Prereq_Level: 2
- Prereq_Power: Lend Distraction
- Tags: Multi-target


## Weapon Attacks

**Attack, Weapon**

- Description: You've been trained with basic weaponry, and maybe even taken a liking to a favorite (e.g., hammer or bow). This is your go-to tool on the battlefield.
- Mechanic: Major. As a Major Action in combat, you make a check to attack an Enemy. This may be performed while under the effects of another Power.
- XP: 1
- Prereq_Skill: Finesse > 0 or Brute > 0


**Attack, Charge**

- Description: Your weapon training allows you throw your weight into an enemy, heightening your damage.
- Mechanic: Major. For 1 or 2 PP, You must move 3 spaces before using this Power. You add +1 or 2 to the damage on a successful Weapon Attack. Power Points are still expended on a miss.. 
- XP: 2
- PP: 1 or 2
- Prereq_Role: Defender or Martial
- Prereq_Power: Attack, Weapon


**Attack, Sweep**

- Description: Your weapon training allows you throw your weight around, potentially knocking targets off balance. Sweep the legs!
- Mechanic: Major. For 1 or 2 PP, You perform you Weapon Attack on multiple contiguous characters within 1 space.. For 2 PP, on a hit, target(s) make a DR 3 AGL Save. On fail, target(s) Knocked Down. 
- XP: 2
- PP: 1 or 2
- Prereq_Role: Martial or Defender
- Prereq_Power: Attack, Weapon
- Tags: Multi-target


**Attack, Disarm**

- Description: You're so skillful on the battlefield that you know how to target your attacks to focus on the enemy weapon.
- Mechanic: Major. For 1 PP, When you spend a Power Point to disarm, perform a Weapon Attack. On a hit, the enemy must spend a Major Action picking up that weapon before using it again. This does not apply to Mystic Attacks or additional weapons the enemy may wield. 
- XP: 2
- PP: 1
- Prereq_Role: Martial or Defender


**Attack, Vengeance**

- Description: Ever the protector on the field, you leap at the chance to avenge an ally.
- Mechanic: Major. When an ally takes damage in combat, you may take a Weapon Attack against the attacker on your next turn with the Upper Hand.
- XP: 1
- Prereq_Role: Defender
- Prereq_Power: Attack, Weapon


**Attack, Dual-Wield**

- Description: You are adept at wielding two weapons in combat.
- Mechanic: Minor. On your turn, you may make a second attack as a Minor Action with Lower Hand.
- XP: 3
- Prereq_Skill: Finesse > 1 or Brute > 1
- Prereq_Power: Attack, Weapon


**Attack, Dual-Wield Master**

- Description: You are a master of wielding two weapons in combat.
- Mechanic: Minor. On your turn, you may make a second attack as a Minor Action. When making this attack, you no longer draw with the Lower Hand.
- XP: 1
- Prereq_Level: 3
- Prereq_Power: Attack, Dual-Wield


# Companion

**Creature Connection**

- Description: You have developed a connection with a creature in your setting (e.g., animal, spirit, robot). At the end of a Full Rest you can attune to an animal as a Companion.
- Mechanic: Passive. At the end of a Full Rest, you attempt to connect with a creature to take them as a Companion. The GM determines if this attempt was successful and may ask for a relevant Skill check.
- XP: 5
- Prereq_Skill: Craft > 0 or Knowledge > 0
- Tags: Companion


**Creature Link**

- Description: You have developed a strong bond with your Companion over time, and can hear its thoughts in your mind.
- Mechanic: Passive. Some checks can now be made through your Companion using their Skills and Attributes. The GM determines if a check can reasonably be made through your Companion.
- XP: 2
- Prereq_Level: 2
- Prereq_Power: Creature Connection
- Tags: Companion


**Creature Mastery**

- Description: Your connection with your chosen creature has deepened, allowing you to increase the creature's power.
- Mechanic: Passive. Your Companion gains 1 Health Point and +1 to their Primary Skill modifier.
- XP: 2
- Prereq_Level: 2
- Prereq_Power: Creature Connection
- Tags: Companion


# Game Mechanics

## Adjust Odds

**Fated Draw**

- Description: Your connection to the Fates is heightened and you feel you can shift the odds in your favor.
- Mechanic: Major. For 2 PP, When making a Check, you can draw with the Upper Hand (3).. 
- XP: 2
- PP: 2
- Prereq_Level: 3


**Lucky**

- Description: Not everything goes your way, but for one reason or another, you seem to avoid the worst.
- Mechanic: Passive. On a Suited Miss, you may redraw once. This Power cannot be used multiple times on the same check.
- XP: 1
- Tags: Suited Miss


**Luck Shared**

- Description: You know just how to spread the luck around. When things are going your way, you can share that vibe.
- Mechanic: Minor. When you get a Suited Hit, you may use a Minor Action to choose one creature you can see. Until the end of their next turn, or for the next 6 seconds if out of combat, all draws are made with the Upper Hand.
- XP: 1
- Tags: Suited Hit


**Scrying**

- Description: Your intuition is heightened and you can anticipate moments coming in the near future.
- Mechanic: Major. For 1 PP, You can a look at your top 2 cards of your deck and discard up to two of them. You must make a Draw before using this Power again.. 
- XP: 1
- PP: 1
- Prereq_Level: 2
- Tags: Card Viewing


**Scrying, Advanced**

- Description: Your connection to this divine sense has strengthened.
- Mechanic: Major. For 2 PP, You can a look at your top 3 cards of your deck and discard up to three of them. You must make a Draw before using this Power again.. 
- XP: 2
- PP: 2
- Prereq_Level: 3
- Prereq_Power: Scrying
- Tags: Card Viewing


## Fate Cards

**Aces Wild**

- Description: You have attuned to the wild magic of Aces. When using an Ace as a Fate Card, it grants additional effects depending on the suit.
- Mechanic: Passive. Rather than re-drawing using an Ace, you can use Aces as an Action to trigger an effect corresponding to their suit. When you choose this Power (up to twice), select two of the following effects.
- Ace of Clubs: you can play this card to interrupt an enemy's turn and make a single Major ction - even if you already went that round
- Ace of Diamonds: As a Minor Action, you recover 3 PP OR you and up to three allies each recover 1 PP
- Ace of Hearts: As a Minor Action, you can heal 2 HP for yourself or an ally you can see within 5 squares
- Ace of Spades: As a Minor Action, you can strike an enemy with an automatic hit with a Power of your choosing
- XP: 2
- Prereq_Level: 3
- Tags: Fate Cards


# Magic

**Barrier**

- Description: Your skills allow you to deploy temporary impromptu walls
- Mechanic: Major. For 1 or 2 PP, You create a wall 3 or 5 spaces wide. You may dismiss this wall at any time as a Free Action. This wall is impervious to standard attacks, but may be worn down over time at the GM's discretion.. 
- XP: 2
- PP: 1 or 2
- Prereq_Role: Support or Caster


**Illusion**

- Description: Your skills let you conjure illusory effects.
- Mechanic: Major. For 1 or 2 PP, You make an illusory intangible visual (no larger than 1 space) or auditory effect that you've heard before. To determine if it's real, a character makes a Contested Conviction Check. For 2 PP, you can generate both visual and auditory effects, and the check to verify draws with the Lower Hand.. 
- XP: 2
- PP: 1 or 2
- Prereq_Role: Caster
- Prereq_Skill: Knowledge > 0


# Movement

## Speed

**Speedy**

- Description: You're quicker than the rest.
- Mechanic: Passive. When you take this Power, your combat speed increases by 2 squares.
- XP: 1
- Tags: Combat


## Stealth

**Stealthy Surprise**

- Description: An undetected assailant is particularly deadly.
- Mechanic: Minor. You attempt to hide from nearby creatures.
- XP: 1
- Prereq_Skill: Stealth > 1
- Tags: Stealth


**Stealth in the Shadows**

- Description: A creature of the dark, you're especially adept at going unseen.
- Mechanic: Passive. When you make a Stealth check in dim light or darkness, you draw with the Upper Hand.
- XP: 1
- Prereq_Skill: Stealth > 1
- Tags: Stealth


**Stealth's Call**

- Description: By luck or by magical effect, you know just how to distract those who might catch you lurking.
- Mechanic: Major. For 1 PP, You cause an illusory sound to emanate from a point you can see within 10 spaces. You make a Contested Primary Skill Check vs. Detection for any targets within 4 spaces of this point. On failure, they draw Detection Checks at Lower Hand until they leave the area.. 
- XP: 1
- PP: 1
- Prereq_Skill: Stealth > 1
- Tags: Stealth or Multi-target


**Stealth's Blessing**

- Description: You channel a deep energy to go unseen.
- Mechanic: Major. For 1 or 2 PP, Until your next rest, or use of a Major or Minor Power, your stealth checks are made with Upper Hand. For 2 PP, this effect extends to up to 3 characters. This effect ends for any character who Attacks.. 
- XP: 2
- PP: 1 or 2
- Prereq_Skill: Stealth > 2
- Tags: Stealth or Multi-target


# Roleplay

**Calculating**

- Description: You concentrate and assess the nature of the task at hand to determine how difficult it might be.
- Mechanic: Major. For 1 PP, Describe an action you or an ally wishes to take and how you would assess the situation, spending the PP. Depending on your description, the GM may reveal the exact DR or approximate DR (e.g., > 2) of this action before anyone chooses to take it.. 
- XP: 1
- PP: 1
- Prereq_Level: 2
- Prereq_Skill: Knowledge > 1 or Investigation > 1
- Tags: Difficulty Prediction


**Cunning**

- Description: You're sharper than the rest when you take your time.
- Mechanic: Passive. Choose one Skill other than your Primary Skill. On turns when you only make 1 non-attack action using this Skill, draw with Upper Hand. This power may be taken multiple times for additional Skills.
- XP: 1


**Focused**

- Description: There's some domain that completely captivates you. When you're invested, you know exactly how to proceed and there's no distracting you. You barely see the outside world.
- Mechanic: Passive. Choose one Skill. When engaged in a non-instantaneous task that involves that skill, you draw with the Upper Hand. During this time, you also have the Inattentive Vulnerability and are also unable to perceive the world outside this task. Draw with the Lower Hand for any Skill check made that is not directly related to your current task.
- XP: 0


**Handy**

- Description: You know how to work with your hands (e.g., machining, lock picking, tailoring).
- Mechanic: Passive. Work with your GM to decide a trade with which your character is familiar. When making a check to to perform this craft, draw with the Upper Hand.
- XP: 1
- Prereq_Skill: Craft > 1 or Knowledge > 1


**Keen Eye**

- Description: You're especially adept at taking in the world around you.
- Mechanic: Passive. When you make a Detection check to observe the world around you (visual, auditory or olfactory), draw with the Upper Hand.
- XP: 1

