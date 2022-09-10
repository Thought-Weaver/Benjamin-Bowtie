from __future__ import annotations
from io import TextIOWrapper

import discord
import json
import sys

from aenum import Enum, skip
from discord.embeds import Embed
from strenum import StrEnum
from features.shared.nextbutton import NextButton
from features.shared.prevbutton import PrevButton

from types import MappingProxyType
from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from bot import BenjaminBowtieBot
    from features.player import Player


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
            item = Item.load_from_state(item_data)
            return item
        except Exception as e:
            print(f"Error loading item: {e}", file=sys.stderr)
            return None

    @staticmethod
    def load_from_state(item_data: dict):
        return Item(
            item_data.get("key", ""),
            item_data.get("icon", ""),
            item_data.get("name", ""),
            item_data.get("value", 0),
            item_data.get("rarity", Rarity.Unknown),
            item_data.get("class_tags", []),
            item_data.get("state_tags", []),
            item_data.get("count", 1)
        )

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
        self._icon = state.get("_icon", "")
        self._name = state.get("_name", "")
        self._value = state.get("_value", 0)
        self._count = state.get("_count", 0)
        self._rarity = state.get("_rarity", Rarity.Unknown)


# I'm doing it this way because having a dict[ItemKey, Item] would
# mean that using the items in the dict would all point to the same
# reference of the object. That seems extremely risky, even if I copy
# the object every time I use the dict.
# 
# The reason I don't want to use Item.load_from_key every
# time I need a new object is because I/O operations are expensive and
# with multiple potentially happening every second, that could yield
# a lot of errors due to the file being locked.
ITEM_STATES: MappingProxyType[ItemKey, dict] = MappingProxyType({
    # TODO: I'll likely reorganize this later, but these categories
    # are just for my sake and are only referenced in code, so it'll
    # only require some minor refactoring.
    ItemKey.BasicBoots: json.load(open(f"./{ItemKey.BasicBoots}.json", "r")),
    ItemKey.ClumpOfLeaves: json.load(open(f"./{ItemKey.ClumpOfLeaves}.json", "r")),
    ItemKey.Conch: json.load(open(f"./{ItemKey.Conch}.json", "r")),

    ItemKey.Minnow: json.load(open(f"./{ItemKey.Minnow}.json", "r")),
    ItemKey.Roughy: json.load(open(f"./{ItemKey.Roughy}.json", "r")),
    ItemKey.Shrimp: json.load(open(f"./{ItemKey.Shrimp}.json", "r")),

    ItemKey.Oyster: json.load(open(f"./{ItemKey.Oyster}.json", "r")),
    ItemKey.Pufferfish: json.load(open(f"./{ItemKey.Pufferfish}.json", "r")),

    ItemKey.Squid: json.load(open(f"./{ItemKey.Squid}.json", "r")),
    ItemKey.Crab: json.load(open(f"./{ItemKey.Crab}.json", "r")),
    ItemKey.Lobster: json.load(open(f"./{ItemKey.Lobster}.json", "r")),
    ItemKey.Shark: json.load(open(f"./{ItemKey.Shark}.json", "r")),

    ItemKey.Diamond: json.load(open(f"./{ItemKey.Diamond}.json", "r")),
    ItemKey.AncientVase: json.load(open(f"./{ItemKey.AncientVase}.json", "r")),
    ItemKey.MysteriousScroll: json.load(open(f"./{ItemKey.MysteriousScroll}.json", "r")),

    ItemKey.FishMaybe: json.load(open(f"./{ItemKey.FishMaybe}.json", "r")),
})


class Inventory():
    def __init__(self):
        self._inventory_slots: List[Item] = []
        self._coins: int = 0

    def _organize_inventory_slots(self):
        if len(self._inventory_slots) == 0:
            return
        
        item_set: List[Item] = []
        if len(self._inventory_slots) == 1:
            item = self._inventory_slots[0]
            item_set.append(Item(
                item.get_key(),
                item.get_icon(),
                item.get_name(),
                item.get_value(),
                item.get_rarity(),
                item.get_class_tags(),
                item.get_state_tags(),
                0)
            )
        if len(self._inventory_slots) >= 2:
            for item in self._inventory_slots:
                exists = False
                for item_in_set in item_set:
                    if item_in_set == item:
                        exists = True
                        break
                if not exists:
                    item_set.append(Item(
                        item.get_key(),
                        item.get_icon(),
                        item.get_name(),
                        item.get_value(),
                        item.get_rarity(),
                        item.get_class_tags(),
                        item.get_state_tags(),
                        0)
                    )

        new_slots: List[Item] = []
        for item in item_set:
            for other_item in self._inventory_slots:
                if item == other_item:
                    item.add_amount(other_item.get_count())
            if item.get_count() != 0:
                new_slots.append(item)

        self._inventory_slots = sorted(new_slots, key=lambda item: item.get_name())

    def item_exists(self, item: Item):
        for i, inv_item in enumerate(self._inventory_slots):
            if inv_item == item:
                return i
        return -1

    def search_by_name(self, name: str):
        for i, item in enumerate(self._inventory_slots):
            if item.get_name() == name:
                return i
        return -1

    def add_item(self, item: Item):
        if item is None:
            self._organize_inventory_slots()
            return
        self._inventory_slots.append(item)
        self._organize_inventory_slots()

    def remove_item(self, slot_index: int, count=1):
        if count <= 0:
            return None
        if slot_index < len(self._inventory_slots):
            result = self._inventory_slots[slot_index].remove_amount(count)
            if result is not None:
                self._organize_inventory_slots()
                return result
        return None

    def add_coins(self, amount: int):
        self._coins += amount
    
    def remove_coins(self, amount: int):
        if amount > self._coins:
            return None
        self._coins -= amount
        return self._coins

    def get_inventory_slots(self):
        return self._inventory_slots

    def get_coins(self):
        return self._coins

    def get_coins_str(self):
        if self._coins == 1:
            return "1 coin"
        return f"{self._coins} coins"


class InventoryButton(discord.ui.Button):
    def __init__(self, item_index: int, item: Item):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_full_name_and_count()}", row=item_index)
        self._item_index = item_index

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        await interaction.response.defer()


class InventoryView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, user: discord.User):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._user = user
        self._page = 0

        self._NUM_PER_PAGE = 4

        self._get_current_page_buttons()

    def _get_player(self) -> Player:
        return self._database[str(self._guild_id)]["members"][str(self._user.id)]

    def _get_current_page_buttons(self):
        self.clear_items()
        player: Player = self._get_player()
        all_slots = player.get_inventory().get_inventory_slots()

        page_slots = all_slots[self._page * self._NUM_PER_PAGE:min(len(all_slots), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            self.add_item(InventoryButton(i, item))
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(all_slots) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        
    def _get_current_page_info(self):
        player: Player = self._get_player()
        coins_str = player.get_inventory().get_coins_str()
        return Embed(
            title=f"{self._user.display_name}'s Inventory",
            description=f"You have {coins_str}.\n\nNavigate through your items using the Prev and Next buttons."
        )
        
    def next_page(self):
        self._page += 1
        self._get_current_page_buttons()
        return self._get_current_page_info()

    def prev_page(self):
        self._page = max(0, self._page - 1)
        self._get_current_page_buttons()
        return self._get_current_page_info()

    def get_user(self):
        return self._user
