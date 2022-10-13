from __future__ import annotations

from features.shared.item import ItemKey

from typing import Callable, Dict, List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player
    from features.npcs.npc import NPC
    from features.shared.item import Item

# -----------------------------------------------------------------------------
# CONSUMABLE ITEM EFFECT FUNCTIONS
# -----------------------------------------------------------------------------

def use_lesser_health_potion(item: Item, applicator: Player | NPC, targets: List[Player | NPC]) -> str:
    result_str: str = "{0}" + f" used {item.get_full_name()}!\n\n"
    results: List[str] = []
    
    for target in targets:
        target.get_expertise().heal(5)
        results.append("{1}" + f" was healed for 5 HP")

    return result_str + "\n".join(results)


def use_health_potion(item: Item, applicator: Player | NPC, targets: List[Player | NPC]) -> str:
    result_str: str = "{0}" + f" used {item.get_full_name()}!\n\n"
    results: List[str] = []
    
    for target in targets:
        target.get_expertise().heal(25)
        results.append("{1}" + f" was healed for 25 HP")

    return result_str + "\n".join(results)


def use_greater_health_potion(item: Item, applicator: Player | NPC, targets: List[Player | NPC]) -> str:
    result_str: str = "{0}" + f" used {item.get_full_name()}!\n\n"
    results: List[str] = []
    
    for target in targets:
        target.get_expertise().heal(100)
        results.append("{1}" + f" was healed for 100 HP")

    return result_str + "\n".join(results)


def use_lesser_mana_potion(item: Item, applicator: Player | NPC, targets: List[Player | NPC]) -> str:
    result_str: str = "{0}" + f" used {item.get_full_name()}!\n\n"
    results: List[str] = []
    
    for target in targets:
        target.get_expertise().restore_mana(5)
        results.append("{1}" + f" had 5 mana restored")

    return result_str + "\n".join(results)


def use_mana_potion(item: Item, applicator: Player | NPC, targets: List[Player | NPC]) -> str:
    result_str: str = "{0}" + f" used {item.get_full_name()}!\n\n"
    results: List[str] = []
    
    for target in targets:
        target.get_expertise().restore_mana(25)
        results.append("{1}" + f" had 25 mana restored")

    return result_str + "\n".join(results)


def use_greater_mana_potion(item: Item, applicator: Player | NPC, targets: List[Player | NPC]) -> str:
    result_str: str = "{0}" + f" used {item.get_full_name()}!\n\n"
    results: List[str] = []
    
    for target in targets:
        target.get_expertise().restore_mana(100)
        results.append("{1}" + f" had 100 mana restored")

    return result_str + "\n".join(results)

# -----------------------------------------------------------------------------
# MAPPING
# -----------------------------------------------------------------------------

DUELING_CONSUMABLE_ITEM_EFFECTS: Dict[ItemKey, Callable[[Item, Player | NPC, List[Player | NPC]], str]] = {
    ItemKey.LesserHealthPotion: use_lesser_health_potion,
    ItemKey.HealthPotion: use_health_potion,
    ItemKey.GreaterHealthPotion: use_greater_health_potion,
    ItemKey.LesserManaPotion: use_lesser_mana_potion,
    ItemKey.ManaPotion: use_mana_potion,
    ItemKey.GreaterManaPotion: use_greater_mana_potion
}