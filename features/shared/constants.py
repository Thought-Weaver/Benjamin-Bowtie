# -----------------------------------------------------------------------------
# EXPERTISE CONSTANTS
# -----------------------------------------------------------------------------

# Don't want this in the Expertise class to avoid serializing them. Might be
# safer to write a custom __getstate__ instead of leaving these as globals.

BASE_HP = 20
BASE_MANA = 20

BASE_CON_HEALTH_SCALE = 0.12
CON_HEALTH_SCALE_ADJUST = 5
CON_HEALTH_SCALE_REDUCTION = 0.01
MIN_CON_HEALTH_SCALE = 0.01

BASE_INT_MANA_SCALE = 0.09
INT_MANA_SCALE_ADJUST = 10
INT_MANA_SCALE_REDUCTION = 0.01
MIN_INT_MANA_SCALE = 0.01

DEX_DODGE_SCALE = 0.004

LUCK_CRIT_SCALE = 0.005
LUCK_CRIT_DMG_BOOST = 1.5

# For attacks and abilities
STR_DMG_SCALE = 0.025
INT_DMG_SCALE = 0.025
DEX_DMG_SCALE = 0.025
LCK_DMG_SCALE = 0.025

BLEED_PERCENT_HP = 0.05
POISONED_PERCENT_HP = 0.05

MAX_GARDEN_SIZE = 4

ARMOR_OVERLEVELED_DEBUFF = 0.15
WEAPON_OVERLEVELED_DEBUFF = 0.15

# -----------------------------------------------------------------------------
# COMPANION CONSTANTS
# -----------------------------------------------------------------------------

BASE_GOOD_TIER_POINTS = 50
BASE_GREAT_TIER_POINTS = 500
BASE_BEST_TIER_POINTS = 1500

COMPANION_NAMING_POINTS = 25
COMPANION_FEEDING_POINTS = 1
COMPANION_PREFERRED_FOOD_BONUS_POINTS = 5
COMPANION_BATTLE_POINTS = 10

# -----------------------------------------------------------------------------
# DUNGEON RUN CONSTANTS
# -----------------------------------------------------------------------------

FOREST_ROOMS = 15
