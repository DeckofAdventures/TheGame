# Design Document

## Drafting specifics

- The following are not permitted in filenames: `` () {} [] !@#$%^&* ' ` `` and spaces.
- Flavor text that is included in under mechanics always be separable for future
  versions that will apply to different settings. To identify flavor text, use quotes
  within the parent formatting scheme. For example:
   - The Defender Archetype is ...
   - > Defenders of the Realm are renowned for their mighty shields ...
- Specialized terms are listed in the [Glossary](../1_Mechanics/99_Glossary.md) and will
  be capitalized across all documents.
- Terms that are for flavor, not mechanics, are *Italicized*

## Core Design Principles

Deck of Adventures is, first and foremost, designed for **accessibility**, both in ease
of on-boarding and ease of access. Not everyone has specialty dice or the time to study
complex interconnected rules released over a long history. While becoming a Game
Master (GM) may take some time and dedication, a player completely new to tabletop
roleplaying should be able to pick up Deck of Adventures and start playing within an
hour. This means mechanics should be easy to learn, and easy to explain during a first
session. One only needs a standard deck of playing cards.

Second, Deck of Adventures is designed to be **flexible**, across the many types of
stories GMs want to tell. While our mechanics have been workshopped with lore from the
World of Erdania, all core mechanics should be portable to another setting. In other
words, Deck of Adventures is setting-agnostic. No core mechanic should imply a specific
setting (e.g., magical fantasy) and all settings should be playable by ignoring or
reflavoring a subset of optional mechanics (e.g., the Mystic Aura is EMP tech).

Third, participants should be able to quickly and easily engage in **rich storytelling**
with only a standard deck of playing cards. Any component that doesn't contribute to
this end should be revisited. Accessible and flexible doesn't, however, mean sparse. A
first-time player can pick up a pre-made character in minutes, but then optionally
spend much longer planning out how to make a bespoke character that speaks to them,
with creativity fueled by the wide array of choices.

## Design Axioms

Though itterative design, developers have landed on the following as touchstones.

1. **Pip value is contextual.** The number on the card has no inherent value. There's
nothing good or bad about a `2` or a `King`, a `Spade` or a `Club`. The randomized
context determines how good the outcome is.

2. **PP = HP = AP.** During rests, players decide which of these reources to replenish.
Characters may have different maximum, but expending one should feel roughly equivalent
to the others.

3. **Target Cards remain on a character at all times.** Each character is always 
represented by a Target Card. Between combats, the TC remains active on a
character for any other Checks. A new TC is drawn at the start of the next
combat to shuffle the turn order around for each combat.

4. **Target Cards changing often is important.** When Player Dealers are drawing cards
constantly aiming at a specific TC, the likelihood of a success decreases as more cards
that hit are drawn from the deck. Changing TCs to represent each enemy or challenge
keeps the odds of drawing a success balanced over the course of an Adventure.
