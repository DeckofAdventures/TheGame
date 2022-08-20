# Powers

<!-- DEVELOPERS: Please edit corresponding yaml in 3_Automation -->

<!-- MarkdownTOC add_links=True -->
- [Combat](#Combat)
    - [Mystic Attacks](#Mystic-Attacks)
    - [Control](#Control)
    - [Support](#Support)
    - [Weapon Attacks](#Weapon-Attacks)
- [Companion](#Companion)
- [Game Mechanics](#Game-Mechanics)
    - [Adjust Odds](#Adjust-Odds)
    - [Fate Cards](#Fate-Cards)
- [Magic](#Magic)
- [Movement](#Movement)
    - [Stealth](#Stealth)
    - [Speed](#Speed)
- [Roleplay](#Roleplay)
<!-- /MarkdownTOC -->

## Combat

### Mystic Attacks

**Attack, Mystic**

- Description: You've been trained in some form of Magic to Technology and can produce the most basic form with ease. This could be an electrified touch or a blast of energy at range.
- Mechanic: As a Major Action in combat, you can make a check to attack an Enemy. This may be performed while under the effects of another Power.
- Type: Major
    - XP Cost: 1
- Prereq Skill: Knowlege > 0 or Craft > 0
- Tags: None

**Attack, Mystic Aura**

- Description: You deploy resources to channel your magic all around you.
- Mechanic: You perform your Mystic Attack on all characters within 1 or 2 space(s).
- Type: Major
    - XP Cost: 2
    - FP Cost: 1 or 2
- Prereq Power: Attack, Mystic
- Prereq Role: Caster or Support
- Tags: Multi-target

**Attack, Mystic Amplification**

- Description: You channel your talents into a physical weapon, melding the physical and supernatural.
- Mechanic: Designate a physical weapon. You may make a Weapon Attack with this weapon using your Primary Skill modifier. This property is lost when you use another Power.
- Type: Major
    - XP Cost: 1
    - FP Cost: 1
- Prereq Power: Attack, Mystic
- Prereq Role: Martial or Caster
- Tags: None

**Attack, Mystic Cone**

- Description: You deploy resources to channel your magic in a wide blast in front of you.
- Mechanic: Choose one effect when you take this power
- You perform your Mystic Attack on all characters within a cone of 3 spaces in front of you.
- All characters in a 3 space cone in front of you make a Contested Conviction check. On failure, they are Knocked Down
- Type: Major
    - XP Cost: 2
    - FP Cost: 1
- Prereq Power: Attack, Mystic
- Prereq Role: Caster
- Tags: Multi-target

**Attack, Mystic Confusion**

- Description: You channel your abilities to target the psyche of your enemy to leave them incapacitated.
- Mechanic: You draw a Target Card and force 1 or 3 characters to make a Conviction check against your TC. On a failure, those characters are Stunned.
- Type: Major
    - XP Cost: 2
    - FP Cost: 1 or 2
- Prereq Power: Attack, Mystic
- Prereq Role: Support or Caster
- Tags: Multi-target

**Attack, Mystic Entangle**

- Description: You channel your abilities to tie your target in place.
- Mechanic: You draw a Target Card and force 1 or 3 characters to make an Agility check against your TC. On a failure, those characters are Entangled.
- Type: Major
    - XP Cost: 2
    - FP Cost: 1 or 2
- Prereq Power: Attack, Mystic
- Prereq Role: Support or Caster
- Tags: Multi-target

**Attack, Mystic Deprivation**

- Description: You channel your abilities deprive a target of their senses.
- Mechanic: You select the Blinded or Deafened effect, draw a TC, and force 1 or 3 characters to make a Intuition check against your TC. On a failure, target(s) are under the selected effect. Targets who do not use the relevant sense are immune to this Power.
- Type: Major
    - XP Cost: 2
    - FP Cost: 1 or 2
- Prereq Power: Attack, Mystic
- Prereq Role: Support or Caster
- Tags: Multi-target

**Attack, Mystic Dual-Shot**

- Description: You are so adept mystic arts you can start another spell before even finishing the first.
- Mechanic: On your turn, you may take a second Mystic Attack with Lower Hand.
- Type: Minor
    - XP Cost: 3
- Prereq Skill: Finesse > 1
- Prereq Power: Attack, Mystic
- Tags: Multi-target

**Attack, Mystic Dual-Wield Master**

- Description: You are a master of wielding two weapons in combat.
- Mechanic: On your turn, you may take a second Mystic Attack as a Minor Action.
- Type: Minor
    - XP Cost: 1
- Prereq Level: 3
- Prereq Power: Attack, Mystic Dual-Shot
- Tags: Multi-target

### Control

**Battlecharged**

- Description: You're always ready for something to go down.
- Mechanic: When drawing initiative, Draw with Upper Hand.
- Type: Passive
    - XP Cost: 1
- Tags: None

**Critical Master**

- Description: When you hit big, you hit BIG. Enemies don’t stand a chance against you when you make a critical hit against them.
- Mechanic: All Critical Success attacks now deal double damage instead of adding +1 damage.
- Type: Passive
    - XP Cost: 1
- Prereq Level: 3
- Tags: None

**Momentum**

- Description: By brute strength, force others to move around the battlefield.
- Mechanic: As part of your movement, you attempt to move a character who is within 1 space of you. If unwilling, the target makes a Contested Strength or Agility Check to dodge. If the target is willing or fails the check, you may place the target within 1 space of end position.
- Type: Passive
    - XP Cost: 1
- Prereq Role: Defender
- Prereq Skill: Brute > 1
- Tags: None

**Momentum Aura**

- Description: Your strength is supernatural, bending the gravity around you.
- Mechanic: Your Momentum ability extends to 3 spaces, forcing any targeted opponent in that range to make a contested Strength or Agility check.
- Type: Passive
    - XP Cost: 2
    - FP Cost: 1
- Prereq Power: Momentum
- Prereq Role: Defender
- Prereq Skill: Brute > 2
- Tags: Multi-target

**Find Weakness**

- Description: You can size up an opponent and discover their weaknesses.
- Mechanic: As a Minor Action, you make a contested Detection check vs. the target's Bluffing. On a Success, you learn one Vulnerability and on Critical Success you learn all Vulnerabilities.
- Type: Minor
    - XP Cost: 1
- Prereq Level: 2
- Tags: Difficulty Prediction

**Pack Tactics**

- Description: When an enemy is outnumbered, you know just how to take advantage.
- Mechanic: When an enemy is next to one or more of your allies, you may expend a Minor Action to grant yourself Upper Hand (+1) on your next attack for each ally in their space. If allies or targets move before you attack, this bonus is adjusted accordingly.
- Type: Minor
    - XP Cost: 2
    - FP Cost: 1
- Prereq Level: 2
- Tags: Difficulty Prediction

### Support

**Heal**

- Description: Can channel magical energy or medical training to heal others
- Mechanic: Heal yourself or another you can see for 1 or 3 Health Points
- Type: Major
    - XP Cost: 2
    - FP Cost: 1 or 2
- Prereq Role: Support
- Tags: None

**Lend Aid**

- Description: Just a little help from a friend
- Mechanic: As a Minor Action, designate one ally who, on their next draw, will draw with the Upper Hand.
- Type: Minor
    - XP Cost: 1
- Prereq Role: Support
- Tags: None

**Lend Distraction**

- Description: Just an annoyance in the distance
- Mechanic: As a Minor Action, designate a character who, on their next draw, will draw with the Lower Hand.
- Type: Minor
    - XP Cost: 1
- Tags: None

**Lend Mass Distraction**

- Description: You know how to cause a scene.
- Mechanic: Draw a Target Card. 2 or 3 targets make a Conviction check against your TC. On a failure, those characters draw with the Lower Hand on any actions or checks made during their next turn.
- Type: Major
    - XP Cost: 2
    - FP Cost: 1 or 2
- Prereq Level: 2
- Prereq Power: Lend Distraction
- Tags: Multi-target

**Lend Confusion**

- Description: You're such a distracting presence that you bury into the mind of your target, having a sustained effect.
- Mechanic: As a Major Action, select one character to put under the effect of the Lend Distraction Power. At the end of each of their turns this character makes a Contested Conviction Check vs. your Primary Skill to end the effect.
- Type: Major
    - XP Cost: 1
- Prereq Level: 2
- Prereq Power: Lend Distraction
- Prereq Role: Support or Caster
- Tags: None

**Lend Mass Confusion**

- Description: You're such a distracting presence that you bury into the mind of many target, having a sustained effect.
- Mechanic: You draw a TC. 2 or 3 targets make a Conviction check against your TC. On a failure, targets draw with the Lower Hand on any actions made during their turn. At the end of each of their turns, targets may repeat the check to end the effect.
- Type: Major
    - XP Cost: 2
    - FP Cost: 2
- Prereq Level: 3
- Prereq Power: Lend Confusion
- Prereq Role: Support or Caster
- Tags: Multi-target

**Lend/Remove Skill**

- Description: You really know how to target an ability and either support it or get in it's way.
- Mechanic: Designate a character that you would like to Boost or Reduce and choose a Skill (or action that would require a Skill such as Attack). This character draws at Upper or Lower Hand (2 or 3) checks that involve this Skill.
- Type: Major
    - XP Cost: 2
    - FP Cost: 1 or 2
- Prereq Role: Support
- Tags: None

**Lend Readiness**

- Description: Your talents bolster you allies' speed and alertness.
- Mechanic: Select one character. Until the end of the next combat, this character draws their Target Card with the Upper Hand. This effect is maintained even if you use another Power.
- Type: Minor
    - XP Cost: 1
- Prereq Role: Support
- Tags: None

**Lend Vigor**

- Description: Channel energy to do more than help: inspire!
- Mechanic: Designate 1 or 2 character(s) who, on their next turn, can take an additional Major Action without penalty and move 2 additional spaces during their movement.
- Type: Major
    - XP Cost: 2
    - FP Cost: 1 or 2
- Prereq Role: Support or Caster
- Tags: None

**Slow**

- Description: You selectively bend the nature of time
- Mechanic: Select a point in space. You initiate a Primary Skill Contested Check vs. Strength for all creatures within 2 spaces. On a failure, their speed is halved and they are limited to one Major or Minor action per turn. A creature that starts their turn outside of the area is no longer affected. Objects in the area are slowed until the effect ends or they are moved by a creature.
- Type: Major
    - XP Cost: 2
    - FP Cost: 2
- Prereq Level: 3
- Prereq Role: Support or Caster
- Tags: None

**Shield, Others**

- Description: Fortify others by summoning magical armor.
- Mechanic: Add 1 or 2 AP to a creature you can see. This effect does not stack with other Powers, but does stack on top of AP granted by physical items.
- Type: Major
    - XP Cost: 2
    - FP Cost: 1 or 2
- Prereq Role: Support
- Tags: None

**Shield, Self**

- Description: Fortify yourself even further, adjusting your shield or summoning magical armor.
- Mechanic: Add 1 or 2 AP to yourself. This effect is in addition to AP from physical items, but must replace AP from other Powers.
- Type: Major
    - XP Cost: 2
    - FP Cost: 1 or 2
- Prereq Role: Defender
- Tags: None

### Weapon Attacks

**Attack, Weapon**

- Description: You've been trained with basic weaponry, and maybe even taken a liking to a favorite (e.g., hammer or bow). This is your go-to tool on the battlefield.
- Mechanic: As a Major Action in combat, you make a check to attack an Enemy. This may be performed while under the effects of another Power.
- Type: Major
    - XP Cost: 1
- Prereq Skill: Finesse > 0 or Brute > 0
- Tags: None

**Attack, Charge**

- Description: Your weapon training allows you throw your weight into an enemy, heightening your damage.
- Mechanic: You must move 3 spaces before using this Power. You add +1 or 2 to the damage on a successful Weapon Attack. Fate Points are still expended on a miss.
- Type: Major
    - XP Cost: 2
    - FP Cost: 1 or 2
- Prereq Power: Attack, Weapon
- Prereq Role: Defender or Martial
- Tags: None

**Attack, Sweep**

- Description: Your weapon training allows you throw your weight around, potentially knocking targets off balance. Sweep the legs!
- Mechanic: You perform you Weapon Attack on multiple contiguous characters within 1 space. For 2 FP, Targets make a DR 3 Agility check vs. your TC to avoid being Knocked Down.
- Type: Major
    - XP Cost: 2
    - FP Cost: 1 or 2
- Prereq Power: Attack, Weapon
- Prereq Role: Martial or Defender
- Tags: Multi-target

**Attack, Disarm**

- Description: You're so skillful on the battlefield that you know how to target your attacks to focus on the enemy weapon.
- Mechanic: When you spend an Fate Point to disarm, perfom a Weapon Attack. On a hit, the enemy must spend a Major Action picking up that weapon before using it again. This does not apply to Mystic Attacks or additional weapons the enemy may wield.
- Type: Major
    - XP Cost: 2
    - FP Cost: 1
- Prereq Role: Martial or Defender
- Tags: None

**Attack, Vengeance**

- Description: Ever the protector on the field, you leap at the chance to avenge an ally.
- Mechanic: When an ally takes damage in combat, you may take a Weapon Attack against the attacker on your turn with the Upper Hand.
- Type: Major
    - XP Cost: 1
- Prereq Power: Attack, Weapon
- Prereq Role: Defender
- Tags: None

**Attack, Dual-Wield**

- Description: You are adept at wielding two weapons in combat.
- Mechanic: On your turn, you may make a second attack as a Minor Action with Lower Hand.
- Type: Minor
    - XP Cost: 3
- Prereq Power: Attack, Weapon
- Tags: None

**Attack, Dual-Wield Master**

- Description: You are a master of wielding two weapons in combat.
- Mechanic: On your turn, you may make a second attack as a Minor Action. When making this attack, you no longer draw with the Lower Hand.
- Type: Minor
    - XP Cost: 1
- Prereq Level: 3
- Prereq Power: Attack, Dual-Wield
- Tags: None

## Companion

**Creature Connection**

- Description: You have developed a connection with a creature in your setting (e.g., animal, spirit, robot). At the end of a Full Rest you can attune to an animal as a Companion.
- Mechanic: At the end of a Full Rest, you attempt to connect with a creature to take them as a Companion. The GM determines if this attempt was successful and may ask for a relevant Skill check.
- Type: Passive
    - XP Cost: 5
- Prereq Skill: Craft > 1 or Knowledge > 1
- Tags: Companion

**Creature Link**

- Description: You have developed a strong bond with your Companion over time, and can hear its thoughts in your mind.
- Mechanic: Some checks can now be made through your Companion using their Skills and Attributes. The GM determines if a check can reasonably be made through your Companion.
- Type: Passive
    - XP Cost: 2
- Prereq Level: 2
- Prereq Power: Creature Connection
- Tags: Companion

**Creature Mastery**

- Description: Your connection with your chosen creature has deepened, allowing you to increase the creature's power.
- Mechanic: Your Companion gains 1 Health Point and +1 to their Primary Skill modifier.
- Type: Passive
    - XP Cost: 2
- Prereq Level: 2
- Prereq Power: Creature Connection
- Tags: Companion

## Game Mechanics

### Adjust Odds

**Fated Draw**

- Description: Your connection to the Fates is heightened and you feel you can shift the odds in your favor.
- Mechanic: When making a Check, you can draw with the Upper Hand (3).
- Type: Major
    - XP Cost: 2
    - FP Cost: 2
- Prereq Level: 3
- Tags: None

**Lucky**

- Description: Not everything goes your way, but for one reason or another, you seem to avoid the worst.
- Mechanic: On a Suited Miss, you may redraw once. This Power cannot be used multiple times on the same check.
- Type: Passive
    - XP Cost: 1
- Tags: Suited Miss

**Luck Shared**

- Description: You know just how to spread the luck around. When things are going your way, you can share that vibe.
- Mechanic: When you get a Suited Hit, you may use a Minor Action to choose one creature you can see. For their next turn, or the next 6 seconds if out of combat, all draws are made with the Upper Hand.
- Type: Minor
    - XP Cost: 1
- Tags: Suited Hit

**Scrying**

- Description: Your intuition is heightened and you can anticipate moments coming in the near future.
- Mechanic: You can a look at your top 2 cards of your deck and discard up to two of them. You must make a Draw before using this Power again.
- Type: Major
    - XP Cost: 1
    - FP Cost: 1
- Prereq Level: 2
- Tags: Card Viewing

**Scrying, Advanced**

- Description: Your connection to this divine sense has strengthened.
- Mechanic: You can a look at your top 3 cards of your deck and discard up to three of them. You must make a Draw before using this Power again.
- Type: Major
    - XP Cost: 2
    - FP Cost: 2
- Prereq Level: 3
- Prereq Power: Scrying
- Tags: Card Viewing

### Fate Cards

**Aces Wild**

- Description: You have attuned to the wild magic of Aces. When using an Ace as a Fate Card, it grants additional effects depending on the suit.
- Mechanic: Rather than re-drawing using an Ace, you can use Aces as an Action to trigger an effect corresponding to their suit. When you choose this Power (up to twice), select two of the following effects.
- Ace of Clubs: you can play this card to interrupt an enemy’s turn and make a single Major ction - even if you already went that round
- Ace of Diamonds: As a Minor Action, you recover 3 FP OR you and up to three allies each recover 1 FP
- Ace of Hearts: As a Minor Action, you can heal 2 HP for yourself or an ally you can see within 5 squares
- Ace of Spades: As a Minor Action, you can strike an enemy with an automatic hit with a Power of your choosing
- Type: Passive
    - XP Cost: 2
- Prereq Level: 3
- Tags: Fate Cards

## Magic

**Barrier**

- Description: Your skills allow you to deploy temporary impromptu walls
- Mechanic: You create a wall 3 or 5 spaces wide. You may dismiss this wall at any time as a Free Action. This wall is impervious to standard attacks, but may be worn down over time at the GM's discretion.
- Type: Major
    - XP Cost: 2
    - FP Cost: 1 or 2
- Prereq Role: Support or Caster
- Tags: None

**Illusion**

- Description: Your skills let you conjure illusory effects.
- Mechanic: You make an illusory intangible visual (no larger than 1 space) or auditory effect that you've heard before. To determine if it's real, a character makes a Contested Conviction Check. For 2 FP, you can generate both visual and auditory effects, and the check to verify draws with the Lower Hand.
- Type: Major
    - XP Cost: 2
    - FP Cost: 1 or 2
- Prereq Role: Caster
- Tags: None

**Mystic Recovery**

- Description: Be still and meditate to draw energy from deep within you.
- Mechanic: As a Minor Action, recover 1 FP. If you take no other Actions or movement on this turn, recover 3. This may be done up to a number of times equal to your level per Rest.
- Type: Minor
    - XP Cost: 2
- Prereq Role: Support or Caster
- Tags: None

## Movement

### Stealth

**Stealthy Surprise**

- Description: An undetected assailant is particularly deadly.
- Mechanic: You may Hide as a Minor Action.
- Type: Minor
    - XP Cost: 1
- Prereq Skill: Stealth > 1
- Tags: Stealth

**Stealth in the Shadows**

- Description: A creature of the dark, you're especially adept at going unseen.
- Mechanic: When you make a Stealth check in dim light or darkness, you draw with the Upper Hand.
- Type: Passive
    - XP Cost: 1
- Prereq Skill: Stealth > 1
- Tags: Stealth

**Stealth's Call**

- Description: By luck or by magical effect, you know just how to distract those who might catch you lurking.
- Mechanic: You cause an illusory sound to emanate from a point you can see within 10 spaces. You make a Contested Primary Skill Check vs. Detection for any targets within 4 spaces of this point. On failure, they draw Detection Checks at Lower Hand until they leave the area.
- Type: Major
    - XP Cost: 1
    - FP Cost: 1
- Prereq Skill: Stealth > 1
- Tags: Stealth or Multi-target

**Stealth's Blessing**

- Description: You channel a deep energy to go unseen.
- Mechanic: Until your next rest, or use of a Major or Minor Power, your stealth checks are made with Upper Hand. For 2 FP, this effect extends to up to 3 characters. This effect ends for any character who Attacks.
- Type: Major
    - XP Cost: 2
    - FP Cost: 1 or 2
- Prereq Level: 2
- Prereq Skill: Stealth > 2
- Tags: Stealth or Multi-target

### Speed

**Speedy**

- Description: You’re quicker than the rest.
- Mechanic: When you take this Power, your combat speed increases by 2 squares.
- Type: Passive
    - XP Cost: 1
- Tags: Combat

## Roleplay

**Calculating**

- Description: You concentrate and assess the nature of the task at hand to determine how difficult it might be.
- Mechanic: Describe an action you or an ally wishes to take and how you would assess the situation, spending the FP. Depending on your description, the GM may reveal the exact DR or approximate DR (e.g., > 2) of this action before anyone chooses to take it.
- Type: Major
    - XP Cost: 1
    - FP Cost: 1
- Prereq Level: 2
- Prereq Skill: Knowledge > 1 or Investigation > 1
- Tags: Difficulty Prediction

**Cunning**

- Description: You're sharper than the rest when you take your time.
- Mechanic: Choose one Skill other than your Primary Skill. On turns when you only make 1 non-attack action using this Skill, draw with Upper Hand. This power may be taken multiple times for additional Skills.
- Type: Passive
    - XP Cost: 1
- Tags: None

**Focused**

- Description: There's some domain that completely captivates you. When you're invested, you know exactly how to proceed and there's no distracting you. You barely see the outside world.
- Mechanic: Choose one Skill. When engaged in a non-instantaneous task that involves that skill, you draw with the Upper Hand. During this time, you also have the Inattentive Vulnerability and are also unable to perceive the world outside this task. Draw with the Lower Hand for any Skill check made that is not directly related to your current task.
- Type: Passive
    - XP Cost: 0
- Tags: None

**Handy**

- Description: You know how to work with your hands (e.g., machining, lock picking, tailoring).
- Mechanic: Work with your GM to decide a trade with which your character is familiar. When making a check to to perform this craft, draw with the Upper Hand.
- Type: Passive
    - XP Cost: 1
- Prereq Skill: Craft > 1 or Knowledge > 1
- Tags: None

**Keen Eye**

- Description: You’re especially adept at taking in the world around you.
- Mechanic: When you make a Detection check to observe the world around you (visual, auditory or olfactory), draw with the Upper Hand.
- Type: Passive
    - XP Cost: 1
- Tags: None

