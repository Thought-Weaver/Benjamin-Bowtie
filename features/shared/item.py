from __future__ import annotations

import json

from aenum import Enum, skip
from strenum import StrEnum

from types import MappingProxyType
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
    Artifact = "Artifact"


# Using aenum and @skip to create an Enum of StrEnums
# As a result, there can't be any top-level keys
class ClassTag(Enum):
    # Items that can be equipped
    @skip
    class Equipment(StrEnum):
        Equipment = "Equipment"
        Helmet = "Helmet"
        ChestArmor = "Chest_Armor"
        Gloves = "Gloves"
        Boots = "Boots"
        Amulet = "Amulet"
        Ring = "Ring"
        Leggings = "Leggings"
        MainHand = "Main_Hand"
        OffHand = "Off_Hand"

    # Weapon types that can be generated
    @skip
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
    # Fishing Results
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

    # Wishing Well Results
    SunlessSteps = "items/equipment/boots/sunless_steps"
    SunlessHeart = "items/equipment/chest_armor/sunless_heart"
    SunlessGrip = "items/equipment/gloves/sunless_grip"
    SunlessMind = "items/equipment/helmet/sunless_mind"
    SunlessStride = "items/equipment/leggings/sunless_stride"
    SunlessWill = "items/equipment/ring/sunless_will"
    SunlessChains = "items/equipment/amulet/sunless_chains"

# -----------------------------------------------------------------------------
# CLASSES
# -----------------------------------------------------------------------------

class Buffs():
    def __init__(self, con_buff=0, str_buff=0, dex_buff=0, int_buff=0, lck_buff=0, mem_buff=0):
        self.con_buff = con_buff
        self.str_buff = str_buff
        self.dex_buff = dex_buff
        self.int_buff = int_buff
        self.lck_buff = lck_buff
        self.mem_buff = mem_buff

    def __str__(self):
        display_string = ""
        if self.con_buff != 0:
            if self.con_buff > 0:
                display_string += "+"
            display_string += f"{self.con_buff} Constitution\n"
        if self.str_buff != 0:
            if self.str_buff > 0:
                display_string += "+"
            display_string += f"{self.str_buff} Strength\n"
        if self.dex_buff != 0:
            if self.dex_buff > 0:
                display_string += "+"
            display_string += f"{self.dex_buff} Dexterity\n"
        if self.int_buff != 0:
            if self.int_buff > 0:
                display_string += "+"
            display_string += f"{self.int_buff} Intelligence\n"
        if self.lck_buff != 0:
            if self.lck_buff > 0:
                display_string += "+"
            display_string += f"{self.lck_buff} Luck\n"
        if self.mem_buff != 0:
            if self.mem_buff > 0:
                display_string += "+"
            display_string += f"{self.mem_buff} Memory"
        return display_string

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.con_buff = state.get("con_buff", 0)
        self.str_buff = state.get("str_buff", 0)
        self.dex_buff = state.get("dex_buff", 0)
        self.int_buff = state.get("int_buff", 0)
        self.lck_buff = state.get("lck_buff", 0)
        self.mem_buff = state.get("mem_buff", 0)


class ArmorStats():
    def __init__(self, armor_amount=0):
        self._armor_amount = armor_amount

    def get_armor_amount(self):
        return self._armor_amount

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._armor_amount = state.get("armor_amount", 0)


class WeaponStats():
    def __init__(self, min_damage=0, max_damage=0):
        self._min_damage = min_damage
        self._max_damage = max_damage
    
    def get_range_str(self):
        return f"{self._min_damage}-{self._max_damage} damage"

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._min_damage = state.get("min_damage", 0)
        self._max_damage = state.get("max_damage", 0)


class Item():
    def __init__(self, key: ItemKey, icon: str, name: str, value: int, rarity: Rarity, description: str, flavor_text:str, class_tags: List[str], state_tags: List[str]=[], count=1, level_requirement=0, buffs: Buffs=None, armor_stats: ArmorStats=None, weapon_stats: WeaponStats=None):
        self._key = key
        self._icon = icon
        self._name = name
        self._value = value
        self._rarity = rarity
        self._description = description
        self._flavor_text = flavor_text
        self._class_tags = class_tags
        self._state_tags = state_tags
        self._count = count
        self._level_requirement = level_requirement
        self._buffs = buffs

        self._armor_stats = armor_stats
        self._weapon_stats = weapon_stats

    @staticmethod
    def load_from_state(item_data: dict):
        return Item(
            item_data.get("key", ""),
            item_data.get("icon", ""),
            item_data.get("name", ""),
            item_data.get("value", 0),
            item_data.get("rarity", Rarity.Unknown),
            item_data.get("description", ""),
            item_data.get("flavor_text", ""),
            item_data.get("class_tags", []),
            item_data.get("state_tags", []),
            item_data.get("count", 1),
            item_data.get("level_requirement", 0),
            item_data.get("buffs"),
            item_data.get("armor_stats"),
            item_data.get("weapon_stats")
        )

    def remove_amount(self, amount: int):
        if amount <= self._count:
            result = Item(
                self._key,
                self._icon,
                self._name,
                self._value,
                self._rarity,
                self._description,
                self._flavor_text,
                self._class_tags,
                self._state_tags,
                amount,
                self._level_requirement,
                self._buffs,
                self._armor_stats,
                self._weapon_stats)
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
        if self._count > 1:
            return f"{self._icon} {self._name} ({self._count})"
        return f"{self._icon} {self._name}"

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

    def get_description(self):
        return self._description
    
    def get_flavor_text(self):
        return self._flavor_text

    def get_class_tags(self):
        return self._class_tags

    def get_state_tags(self):
        return self._state_tags

    def get_key(self):
        return self._key

    def get_level_requirement(self):
        return self._level_requirement

    def get_buffs(self):
        return self._buffs

    def get_armor_stats(self):
        return self._armor_stats

    def get_weapon_stats(self):
        return self._weapon_stats

    def __str__(self):
        display_string = f"**{self.get_full_name()}**\n*{self._rarity} Item*\n\n"
        
        if self._armor_stats is not None:
            display_string += f"{self._armor_stats.get_armor_amount()} armor\n"

        if self._weapon_stats is not None:
            display_string += f"{self._weapon_stats.get_range_str()}\n"

        if self._buffs is not None:
            display_string += f"{self._buffs}\n"

        if self._armor_stats is not None or self._weapon_stats is not None or self._buffs is not None:
            display_string += "\n"

        if self._description != "":
            display_string += f"{self._description}\n\n"
        if self._flavor_text != "":
            display_string += f"{self._flavor_text}\n\n"

        if self._count > 1:
            display_string += f"Quantity: *{self._count}*\n"
        
        display_string += f"Value: *{self._value}* each"
        
        return display_string

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
        base_data = LOADED_ITEMS.get_item_state(state["_key"])

        # Always replace these values; the base data overrides them.
        self._key = base_data.get("key", "")
        self._icon = base_data.get("icon", "")
        self._name = base_data.get("name", "")
        self._value = base_data.get("value", 0)
        self._rarity = base_data.get("rarity", Rarity.Unknown)
        self._description = base_data.get("description", "")
        self._flavor_text = base_data.get("flavor_text", "")
        self._level_requirement = base_data.get("level_requirement", 0)
        self._class_tags = base_data.get("class_tags", [])

        armor_data = base_data.get("armor_stats")
        if armor_data is not None:
            self._armor_stats = ArmorStats()
            self._armor_stats.__setstate__(armor_data)
        else:
            self._armor_stats = None
        
        weapon_data = base_data.get("weapon_stats")
        if weapon_data is not None:
            self._weapon_stats = WeaponStats()
            self._weapon_stats.__setstate__(weapon_data)
        else:
            self._weapon_stats = None

        buffs_data = base_data.get("buffs")
        if buffs_data is not None:
            self._buffs = Buffs()
            self._buffs.__setstate__(buffs_data)
        else:
            self._buffs = None

        # These are stateful values and we use what's loaded from the database.
        self._state_tags = state.get("_state_tags", [])
        self._count = state.get("_count", 1)

# I'm doing it this way because having a dict[ItemKey, Item] would
# mean that using the items in the dict would all point to the same
# reference of the object. That seems extremely risky, even if I copy
# the object every time I use the dict.

# The reason I don't want to use Item.load_from_key every
# time I need a new object is because I/O operations are expensive and
# with multiple potentially happening every second, that could yield
# a lot of errors due to the file being locked.
class LoadedItems():
    _states: MappingProxyType[ItemKey, dict] = MappingProxyType({
        item_key.value: json.load(open(f"./features/{item_key.value}.json", "r")) for item_key in ItemKey
    })

    def get_item_state(self, key: ItemKey):
        return self._states[key]

    def get_new_item(self, key: ItemKey):
        return Item.load_from_state(self._states[key])

# -----------------------------------------------------------------------------
# GLOBALS
# -----------------------------------------------------------------------------

LOADED_ITEMS = LoadedItems()
