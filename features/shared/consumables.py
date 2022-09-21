
from typing import Callable, Dict

from features.shared.item import ItemKey

# -----------------------------------------------------------------------------
# MAPPING
# -----------------------------------------------------------------------------

CONSUMABLE_ITEM_EFFECTS: Dict[ItemKey, Callable[[int, int], int]] = {}

# -----------------------------------------------------------------------------
# CONSUMABLE ITEM EFFECT FUNCTIONS
# -----------------------------------------------------------------------------


