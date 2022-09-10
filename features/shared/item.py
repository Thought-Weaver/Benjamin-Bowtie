from __future__ import annotations
from email.mime import base
from io import TextIOWrapper

import json
import sys

from aenum import Enum, skip
from copy import deepcopy
from strenum import StrEnum

from typing import List

# -----------------------------------------------------------------------------
# ENUMS
# -----------------------------------------------------------------------------

class Rarity(StrEnum):
    Unknown = "Unknown"
    Common = "Common"
    Uncommon = "Uncommon"
    Rare = "Rare"
    Epic = "Epic"
    Legendary = "Legendary"


# Using aenum and @skip to create an Enum of StrEnums
# As a result, there can't be any top-level keys
class ClassTag(Enum):
    # Items that can be equipped
    @skip
    class Equipment(StrEnum):
        Equipment = "Equipment"
        Helmet = "Helmet"
        ChestArmor = "Chest_Armor"
        Boots = "Boots"
        Necklace = "Necklace"
        Ring = "Ring"

        class Weapon(StrEnum):
            Weapon = "Weapon"
            Dagger = "Dagger"
            Sword = "Sword"
            Greatsword = "Greatsword"
            Knuckles = "Knuckles"
            Spear = "Spear"
            Bow = "Bow"
            Staff = "Staff"
            Shield = "Shield"

    # Items that can be stacked and used for certain effects
    @skip
    class Consumable(StrEnum):
        Consumable = "Consumable"
        Potion = "Potion"
        Food = "Food"
        SpellScroll = "Spell_Scroll"

    # Items that can be used as part of crafting consumables
    @skip
    class Ingredient(StrEnum):
        Ingredient = "Ingredient"
        Herb = "Herb"
        RawFish = "Raw_Fish" # Might be good to separate fish from other foods
        RawFood = "Raw_Food" # Like uncooked potatoes, meat, etc.

    @skip
    class Creature(StrEnum):
        Creature = "Creature"
        Fish = "Fish"

    # Items that might might only be good for money.
    @skip
    class Valuable(StrEnum):
        Valuable = "Valuable"
        Gemstone = "Gemstone"

    @skip
    class Readable(StrEnum):
        Readable = "Readable"
        Scroll = "Scroll"

    @skip
    class Misc(StrEnum):
        IsUnique = "Is_Unique"
        NeedsIdentification = "Needs_Identification"
        Junk = "Junk"


class StateTag(Enum):
    pass


class ItemKey(StrEnum):
    AncientVase = "items/valuable/ancient_vase"
    BasicBoots = "items/equipment/boots/basic_boots"
    ClumpOfLeaves = "items/misc/junk/clump_of_leaves"
    Conch = "items/misc/junk/conch"
    Crab = "items/creature/fish/crab"
    Diamond = "items/valuable/gemstone/diamond"
    FishMaybe = "items/creature/fish/fish_maybe"
    Lobster = "items/creature/fish/lobster"
    Minnow = "items/creature/fish/minnow"
    MysteriousScroll = "items/readable/scroll/mysterious_scroll"
    Oyster = "items/creature/fish/oyster"
    Pufferfish = "items/creature/fish/pufferfish"
    Roughy = "items/creature/fish/roughy"
    Shark = "items/creature/fish/shark"
    Shrimp = "items/creature/fish/shrimp"
    Squid = "items/creature/fish/squid"

# -----------------------------------------------------------------------------
# CLASSES
# -----------------------------------------------------------------------------

class Item():
    def __init__(self, key: ItemKey, icon: str, name: str, value: int, rarity: Rarity, class_tags: List[ClassTag], state_tags: List[StateTag]=[], count=1):
        self._key = key
        self._icon = icon
        self._name = name
        self._value = value
        self._rarity = rarity
        self._class_tags = class_tags
        self._state_tags = state_tags
        self._count = count

    @staticmethod
    def load_from_key(key: ItemKey):
        try:
            file: TextIOWrapper = open(f"./{key}.json", "r")
            item_data: dict = json.load(file)
            item = Item(
                item_data.get("key", ""),
                item_data.get("icon", ""),
                item_data.get("name", ""),
                item_data.get("value", 0),
                item_data.get("rarity", Rarity.Unknown),
                item_data.get("class_tags", []),
                item_data.get("state_tags", []),
                item_data.get("count", 1)
            )
            return item
        except Exception as e:
            print(f"Error loading item: {e}", file=sys.stderr)
            return None

    def remove_amount(self, amount: int):
        if amount <= self._count:
            result = Item(
                self._key,
                self._icon,
                self._name,
                self._value,
                self._rarity,
                self._class_tags,
                self._state_tags,
                amount)
            self._count -= amount
            return result
        return None

    def add_amount(self, amount: int):
        self._count += amount

    def get_name(self):
        return self._name

    def get_full_name(self):
        return f"{self._icon} {self._name}"

    def get_full_name_and_count(self):
        return f"{self._icon} {self._name} ({self._count})"

    def get_value(self):
        return self._value

    def get_value_str(self):
        if self._value == 1:
            return "1 coin"
        return f"{self._value} coins"

    def get_count(self):
        return self._count

    def get_icon(self):
        return self._icon

    def get_rarity(self):
        return self._rarity

    def get_class_tags(self):
        return self._class_tags

    def get_state_tags(self):
        return self._state_tags

    def get_key(self):
        return self._key

    def __str__(self):
        return f"**{self.get_full_name()}**\n*{self.get_rarity()} Item*\n\n" \
            f"Count: *{self.get_count()}*\n" \
            f"Value: *{self.get_value()}* each"

    def __eq__(self, obj):
        if not isinstance(obj, Item):
            return False
        
        if ClassTag.Misc.IsUnique in self.get_state_tags() or \
            ClassTag.Misc.IsUnique in obj.get_state_tags():
            return False

        return self._key == obj.get_key() and \
               self._state_tags == obj.get_state_tags()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        state_key = state.get("_key", "")
        if state_key != "":
            base_item: Item = LOADED_ITEMS.get_new_item(state_key)
            self._key = base_item.get_key()
            self._icon = base_item.get_icon()
            self._name = base_item.get_name()
            self._value = base_item.get_value()
            self._rarity = base_item.get_rarity()
            self._class_tags = base_item.get_class_tags()
        else:
            self._key = state.get("_key", "")
            self._icon = state.get("_icon", "")
            self._name = state.get("_name", "")
            self._value = state.get("_value", 0)
            self._rarity = state.get("_rarity", Rarity.Unknown)
            self._class_tags = state.get("_class_tags", [])

        self._state_tags = state.get("_state_tags", [])
        self._count = state.get("_count", 0)


# Using a class that loads the item instead of a global dict with
# state dicts makes more sense since I imagine I'll soon be subtyping
# Item to make additional classes (Armor, Weapon, etc.). With a dict like
# this, I'd have to specify multiple times in the code what class to init.
# My only concern is deepcopy failing.

# I'm doing it this way because having a dict[ItemKey, Item] would
# mean that using the items in the dict would all point to the same
# reference of the object. That seems extremely risky, even if I copy
# the object every time I use the dict.

# The reason I don't want to use Item.load_from_key every
# time I need a new object is because I/O operations are expensive and
# with multiple potentially happening every second, that could yield
# a lot of errors due to the file being locked.
class LoadedItems():
    _items: dict[ItemKey, Item] = {
        ItemKey.BasicBoots: Item.load_from_key(ItemKey.BasicBoots),
        ItemKey.ClumpOfLeaves: Item.load_from_key(ItemKey.ClumpOfLeaves),
        ItemKey.Conch: Item.load_from_key(ItemKey.Conch),

        ItemKey.Minnow: Item.load_from_key(ItemKey.Minnow),
        ItemKey.Roughy: Item.load_from_key(ItemKey.Roughy),
        ItemKey.Shrimp: Item.load_from_key(ItemKey.Shrimp),

        ItemKey.Oyster: Item.load_from_key(ItemKey.Oyster),
        ItemKey.Pufferfish: Item.load_from_key(ItemKey.Pufferfish),

        ItemKey.Squid: Item.load_from_key(ItemKey.Squid),
        ItemKey.Crab: Item.load_from_key(ItemKey.Crab),
        ItemKey.Lobster: Item.load_from_key(ItemKey.Lobster),
        ItemKey.Shark: Item.load_from_key(ItemKey.Shark),

        ItemKey.Diamond: Item.load_from_key(ItemKey.Diamond),
        ItemKey.AncientVase: Item.load_from_key(ItemKey.AncientVase),
        ItemKey.MysteriousScroll: Item.load_from_key(ItemKey.MysteriousScroll),

        ItemKey.FishMaybe: Item.load_from_key(ItemKey.FishMaybe),
    }

    def get_new_item(self, key: ItemKey):
        return deepcopy(self._items[key])

# -----------------------------------------------------------------------------
# GLOBALS
# -----------------------------------------------------------------------------

LOADED_ITEMS = LoadedItems()
