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

# ## Handling custom classes
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

from automation.templates.powers import Powers
from automation.templates.bestiary import Bestiary

# ### Loading Powers
#
# We can load lists of Powers from one or more sources. A Power is defined by a `yaml` file through various features. For example:
#
# ```yaml
# Attack, Mystic Aura:
#   Category:
#     - Combat
#     - Mystic Attacks
#   Description: You deploy resources to channel magic all around you.
#   Mechanic: Perform Mystic Attack on all characters within 1-2 space(s)
#   Type: Major
#   XP: 2
#   PP: [1, 2]
#   Prereq:
#     Power: Attack, Mystic
#     Role:
#       - Caster
#       - Support
# ```
#
# We can load all Powers from one or more files with the `Powers` class. This includes Vulnerabilities. The files with SAMPLE in the name are designed to workshop ideas and test edge cases, not be included in the game.
#

all_powers = Powers(input_files=["04_Powers.yaml", "05_Vulnerabilities.yaml"])

# This class offers a number of options, including looking at categories, writing the set to markdown or csv, and looking at individual items.
#

# all_powers.categories
# all_powers.write_md()
all_powers.as_dict["Attack, Mystic Aura"]

# ### Loading Bestiary
#
# More powerfully, however, Powers support the Bestiary, which includes the set of PCs, NPCs and Bosses one might use in an [Encounter](./Encounters.ipynb). We can similarly load Beasts from `yaml` files with predefined structure. For example:
#
# ```yaml
# Grunt:
#   Type: NPC
#   HP: 2
#   AR: 3
#   PP: 0
#   Attribs:
#     AGL: 1
#     INT: -1
#   Powers:
#     - Attack, Weapon
#   Level: 1
#   Description: A low level soldier.
# ```
#
# For more information about required or default values, please inspect the `Beast` class.
#

bestiary = Bestiary(input_files="06_Bestiary.yaml")

# This class has similar capabilities as the `Powers` class for saving output as well as looking at individual cases.
#

bestiary.as_dict["Mystic, Caster"]

caster = bestiary.as_dict["Mystic, Caster"]
caster

# These classes are really useful, however, when we add them to an [Encounter](./Encounters.ipynb).
#

# ## Writing files
#
# To write out each of the various file types (markdown, csv, image), we can simply call the `yaml_to_other` function.
#
# Note that png output refers to character sheets, which are currently only available for PCs.
#

# +
from automation.templates.main import yaml_to_other

yaml_to_other(
    input_files=["04_Powers.yaml", "05_Vulnerabilities.yaml", "06_Bestiary.yaml"],
    writing=["md", "csv", "png"],
    out_delim="\t",  # CSV delimiter - "," is also available
)
# -
