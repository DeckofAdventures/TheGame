# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.5
#   kernelspec:
#     display_name: doa
#     language: python
#     name: python3
# ---

# ## Simulating encounters
#
# If this is your first time using a notebook, please ensure you have [Python installed](https://www.python.org/downloads/) and you have installed the additional dependencies with the following command: `pip install -r ./automation/requirements.txt`
#
# First, we'll navigate to the repo's root:
#

# +
import os

if os.path.basename(os.getcwd()) != "TheGame":
    os.chdir("..")
# -

# Next, import what you need:
#

import copy
from automation.templates.bestiary import Bestiary
from automation.simulator.deck import Deck
from automation.simulator.encounter import Encounter

# Use the Bestiary to provide dictionaries for each of the combatants. We can use emojis to represent them in the combat output. The Name value will be shown in the log.
#
# Note that files with SAMPLE in the name are designed to workshop ideas and test edge cases, not be included in the game.
#

b = Bestiary(input_files=["06_Bestiary_SAMPLE.yaml", "07_PCs.yaml"]).raw_data
c1 = b["Clubs1"]
c1.update(dict(Name="💀", id="A"))
c2 = copy.copy(b["Clubs1"])
c2.update(dict(Name="👽", id="B"))
s = b["Spider Queen"]
s.update(dict(Name="🎇", id="C"))

# Initialize the encounter. We can see who is involved and resource information by looking at the encounter's `PCs`, `enemies`, or `turn_order` properties.
#
# Note that this may differ from a real encounter because each participant has their own hand and deck. In a true encounter, a GM might manage many characters with the same deck.
#

e = Encounter(PCs=[c1, c2], Enemies=[s])
e.turn_order

# Next, we can simulate a couple rounds of combat. Here, each participant will choose a Power available to them (if sufficient PP) and apply it to an enemy at random. This does not yet cover buffing powers (e.g., Shield, Lend Aid) or mind control status effects (i.e., Charmed, Enthralled).
#

e.sim_round(3)

# We can even simulate epic events.
#

e.sim_epic_event(successes_needed=3)

# Let's see how everyone is doing.
#

e.turn_order

# If you're interested in draining a specific character's resources, we can index them directly and subtract values.
#

spider_queen = e.enemies[0]
spider_queen.HP = 1
spider_queen

# The only thing that can't be set directly is the deck. This has to be managed by either drawing, using a fate card, or shuffling.
#

spider_queen.draw()

spider_queen.exchange_fate()

spider_queen.shuffle(2)
spider_queen

# We can give some or all participants a rest.
#

e.sim_quick_rest(participants=e.PCs)  # If no participants specified, all

e.turn_order

# Or a full rest.
#

e.sim_full_rest()

e.turn_order

# ## Logging
#
# Much of the information we're seeing above in the `[TIME][INFO]` format is as a result of the [logger](https://www.loggly.com/ultimate-guide/python-logging-basics/) that keeps track of this information. We can adjust what we see by adjusting the log level.
#

# +
from automation.utils import logger

logger.setLevel("DEBUG")  # Most information
# logger.setLevel('INFO') # Standard information
# logger.setLevel('WARNING') # Only problems
# logger.setLevel('CRITICAL') # No information
spider_queen.save(DR=3, attrib=["AGL", "STR"], upper_lower="lower", draw_n=2)
e.sim_round()
# -

# For a more detailed record of checks, saves, and rests, turn on CSV logging. This will save logs of who performed which check/save or rest and some associated values.
#

e.set_csv_logging(True)
e.sim_round()
e.sim_quick_rest()

# The following uses system commands rather than Python to look at the output. To use this data more meaningfully, try loading the data with [pandas](https://pythonbasics.org/read-csv-with-pandas/).
#

# !head automation/_output/log_draws.csv

# !head automation/_output/log_rests.csv
