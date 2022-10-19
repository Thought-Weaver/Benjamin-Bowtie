# -----------------------------------------------------------------------------
# EXPERTISE CONSTANTS
# -----------------------------------------------------------------------------

# Don't want this in the Expertise class to avoid serializing them. Might be
# safer to write a custom __getstate__ instead of leaving these as globals.

BASE_HP = 20
BASE_MANA = 20

CON_HEALTH_SCALE = 0.08
CON_HEALTH_REGEN_SCALE = 0.01
STR_DMG_SCALE = 0.025
DEX_DODGE_SCALE = 0.0025
INT_MANA_SCALE = 0.11
INT_MANA_REGEN_SCALE = 0.01
INT_DMG_SCALE = 0.025
LUCK_CRIT_SCALE = 0.005
LUCK_CRIT_DMG_BOOST = 1.5
DEX_DMG_SCALE = 0.05
