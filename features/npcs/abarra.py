from __future__ import annotations
from uuid import uuid4

import discord

from discord import Embed
from enum import StrEnum
from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Expertise, ExpertiseClass
from features.house.house import House
from features.house.recipe import LOADED_RECIPES, Recipe, RecipeKey
from features.npcs.npc import NPC, NPCDuelingPersonas, NPCRoles
from features.shared.ability import BoundToGetLuckyIII, CounterstrikeIII, EvadeIII, HeavySlamII, PiercingStrikeIII, PressTheAdvantageI, ScarArmorII, SecondWindIII, WhirlwindIII
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, Item, ItemKey
from features.shared.nextbutton import NextButton
from features.shared.prevbutton import PrevButton
from features.stats import Stats

from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from bot import BenjaminBowtieBot
    from features.inventory import Inventory
    from features.player import Player

# -----------------------------------------------------------------------------
# NPC VIEW
# -----------------------------------------------------------------------------

class Intent(StrEnum):
    Wares = "Wares"
    Patterns = "Patterns"


class EnterWaresButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Browse Wares", row=0)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: BlacksmithView = self.view

        if view.get_user() == interaction.user:
            response = view.enter_wares()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class EnterPatternsButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Browse Patterns", row=1)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: BlacksmithView = self.view

        if view.get_user() == interaction.user:
            response = view.enter_patterns()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ExitButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.red, label="Back", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: BlacksmithView = self.view

        if view.get_user() == interaction.user:
            response = view.return_to_main_menu()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class WaresDisplayButton(discord.ui.Button):
    def __init__(self, item_index: int, item: Item, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_name_and_count()}", row=row, emoji=item.get_icon())
        
        self._item_index = item_index
        self._item = item

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: BlacksmithView = self.view
        if interaction.user == view.get_user():
            response = view.select_wares_item(self._item_index, self._item)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class PatternsDisplayButton(discord.ui.Button):
    def __init__(self, pattern: Recipe, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{pattern.name}", row=row, emoji=pattern.icon)
        
        self._pattern = pattern

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: BlacksmithView = self.view
        if interaction.user == view.get_user():
            response = view.select_pattern(self._pattern)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ConfirmButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.green, label="Confirm", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: BlacksmithView = self.view
        if interaction.user == view.get_user():
            response = view.confirm_using_intent()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class BlacksmithView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, user: discord.User):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._user = user

        self._blacksmith: BlacksmithView = database[str(guild_id)]["npcs"][NPCRoles.Blacksmith]
        self._wares: List[Item] = [
            LOADED_ITEMS.get_new_item(ItemKey.IronDagger),
            LOADED_ITEMS.get_new_item(ItemKey.IronSword),
            LOADED_ITEMS.get_new_item(ItemKey.IronOre),
            LOADED_ITEMS.get_new_item(ItemKey.CopperOre),
            LOADED_ITEMS.get_new_item(ItemKey.Mothsilk),
            LOADED_ITEMS.get_new_item(ItemKey.Spidersilk),
            LOADED_ITEMS.get_new_item(ItemKey.Whetstone),
            LOADED_ITEMS.get_new_item(ItemKey.JewelersKit)
        ]
        self._selected_item: (Item | None) = None
        self._selected_item_index: int = -1

        self._patterns: List[Recipe] = [
            LOADED_RECIPES.get_new_recipe(RecipeKey.IronIngot),
            LOADED_RECIPES.get_new_recipe(RecipeKey.CopperIngot),
            LOADED_RECIPES.get_new_recipe(RecipeKey.MothsilkBolt),
            LOADED_RECIPES.get_new_recipe(RecipeKey.SpidersilkBolt),
            LOADED_RECIPES.get_new_recipe(RecipeKey.IronDagger),
            LOADED_RECIPES.get_new_recipe(RecipeKey.IronGreatsword),
            LOADED_RECIPES.get_new_recipe(RecipeKey.IronKnuckles),
            LOADED_RECIPES.get_new_recipe(RecipeKey.IronSpear),
            LOADED_RECIPES.get_new_recipe(RecipeKey.LithewoodStaff),
            LOADED_RECIPES.get_new_recipe(RecipeKey.WrathbarkStaff),
            LOADED_RECIPES.get_new_recipe(RecipeKey.IronSword),
            LOADED_RECIPES.get_new_recipe(RecipeKey.CopperRing),
            LOADED_RECIPES.get_new_recipe(RecipeKey.CopperNecklace),
            LOADED_RECIPES.get_new_recipe(RecipeKey.LeatherHelmet),
            LOADED_RECIPES.get_new_recipe(RecipeKey.LeatherJerkin),
            LOADED_RECIPES.get_new_recipe(RecipeKey.LeatherGloves),
            LOADED_RECIPES.get_new_recipe(RecipeKey.LeatherLeggings),
            LOADED_RECIPES.get_new_recipe(RecipeKey.LeatherBoots),
            LOADED_RECIPES.get_new_recipe(RecipeKey.IronHelmet),
            LOADED_RECIPES.get_new_recipe(RecipeKey.IronCuirass),
            LOADED_RECIPES.get_new_recipe(RecipeKey.IronGauntlets),
            LOADED_RECIPES.get_new_recipe(RecipeKey.IronLeggings),
            LOADED_RECIPES.get_new_recipe(RecipeKey.IronGreaves),
            LOADED_RECIPES.get_new_recipe(RecipeKey.WoodenBuckler)
        ]
        self._selected_pattern: (Recipe | None) = None

        self._intent: (Intent | None) = None

        self._page = 0
        self._NUM_PER_PAGE = 4

        self._COST_ADJUST = 1.5 # 50% price increase from base when purchasing items

        self.show_initial_buttons()
        
    def _get_player(self) -> Player:
        return self._database[str(self._guild_id)]["members"][str(self._user.id)]

    def get_initial_embed(self):
        return Embed(
            title="Abarra's Smithy",
            description=(
                "Nearby the village market stands an unassuming hut, the home of one Abarra, the local blacksmith. Outside at his forge, you can hear him hammering away at the metal, honing his craft.\n\n"
                "The heat increases drastically as you approach, and all around you can see scattered the various pieces (plenty of horseshoes you note) he's been making.\n\n"
                "He pauses his work for a moment to look at you, \"Hm? Hm.\" Then he nods with his head towards a small selection of inventory items that he's been crafting for hopeful adventurers such as yourself."
            )
        )

    def show_initial_buttons(self):
        self.clear_items()
        self.add_item(EnterWaresButton())
        self.add_item(EnterPatternsButton())

    def get_embed_for_intent(self):
        player: Player = self._get_player()
        if self._intent == Intent.Wares:
            return Embed(
                title="Browse Wares",
                description=(
                    "\"Hm.\" He nods to the various pieces of armor and weapons.\n\n"
                    f"You have {player.get_inventory().get_coins_str()}."
                )
            )
        return self.get_initial_embed()

    def display_item_info(self):
        player: Player = self._get_player()
        if self._selected_item is None or not (0 <= self._selected_item_index < len(self._wares) and self._wares[self._selected_item_index] == self._selected_item):
            self._get_wares_page_buttons()
            
            return Embed(
                title="Browse Wares",
                description=(
                    f"You have {player.get_inventory().get_coins_str()}.\n\n"
                    "Navigate through available wares using the Prev and Next buttons.\n\n"
                    "*Error: Something about that item changed or it's no longer available.*"
                )
            )

        actual_cost: int = int(self._selected_item.get_value() * self._COST_ADJUST) + 1
        actual_cost_str: str = f"{actual_cost} coin" if actual_cost == 1 else f"{actual_cost} coins"
        return Embed(
            title="Browse Wares",
            description=(
                f"You have {player.get_inventory().get_coins_str()}.\n\n"
                f"᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{self._selected_item}\n\n**Price: {actual_cost_str}**\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\n"
                "Navigate through available wares using the Prev and Next buttons."
            )
        )

    def select_wares_item(self, index: int, item: Item):
        self._selected_item = item
        self._selected_item_index = index

        self._get_wares_page_buttons()
        return self.display_item_info()

    def _get_wares_page_buttons(self):
        self.clear_items()
        
        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        all_slots = self._wares

        page_slots = all_slots[self._page * self._NUM_PER_PAGE:min(len(all_slots), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            self.add_item(WaresDisplayButton(i + (self._page * self._NUM_PER_PAGE), item, i))
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(all_slots) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        
        if self._selected_item is not None:
            actual_value: int = int(self._selected_item.get_value() * self._COST_ADJUST) + 1
            if inventory.get_coins() >= actual_value:
                self.add_item(ConfirmButton(min(4, len(page_slots))))
        self.add_item(ExitButton(min(4, len(page_slots))))

    def _purchase_item(self):
        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        if self._selected_item is not None and self._wares[self._selected_item_index] == self._selected_item:
            actual_value: int = int(self._selected_item.get_value() * self._COST_ADJUST) + 1
            if inventory.get_coins() >= actual_value:
                inventory.remove_coins(actual_value)
                inventory.add_item(LOADED_ITEMS.get_new_item(self._selected_item.get_key()))
                self._get_wares_page_buttons()

                return Embed(
                    title="Browse Wares",
                    description=(
                        f"You have {inventory.get_coins_str()}.\n\n"
                        "Navigate through available wares using the Prev and Next buttons.\n\n"
                        f"*You purchased 1 {self._selected_item.get_full_name()}!*"
                    )
                )
            else:
                self._get_wares_page_buttons()

                return Embed(
                    title="Browse Wares",
                    description=(
                        f"You have {inventory.get_coins_str()}.\n\n"
                        "Navigate through available wares using the Prev and Next buttons.\n\n"
                        f"*Error: You don't have enough coins to buy that!*"
                    )
                )

        self._get_wares_page_buttons()
        return Embed(
            title="Browse Wares",
            description=(
                f"You have {inventory.get_coins_str()}.\n\n"
                "Navigate through available wares using the Prev and Next buttons.\n\n"
                "*Error: Something about that item changed or it's no longer available.*"
            )
        )

    def enter_wares(self):
        self._intent = Intent.Wares
        self._get_wares_page_buttons()
        return self.get_embed_for_intent()

    def display_pattern_info(self):
        player: Player = self._get_player()
        if self._selected_pattern is None:
            self._get_patterns_page_buttons()
            
            return Embed(
                title="Browse Patterns",
                description=(
                    f"You have {player.get_inventory().get_coins_str()}.\n\n"
                    "Navigate through available recipes using the Prev and Next buttons.\n\n"
                    "*Error: Something about that recipe changed or it's no longer available.*"
                )
            )

        actual_cost: int = int(self._selected_pattern.value * self._COST_ADJUST) + 1
        actual_cost_str: str = f"{actual_cost} coin" if actual_cost == 1 else f"{actual_cost} coins"
        return Embed(
            title="Browse Patterns",
            description=(
                f"You have {player.get_inventory().get_coins_str()}.\n\n"
                f"᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{self._selected_pattern.get_name_and_icon()}\n\n**Price: {actual_cost_str}**\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\n"
                "Navigate through available recipes using the Prev and Next buttons."
            )
        )

    def select_pattern(self, pattern: Recipe):
        self._selected_pattern = pattern

        self._get_patterns_page_buttons()
        return self.display_pattern_info()

    def _get_patterns_page_buttons(self):
        self.clear_items()
        
        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        house: House = player.get_house()
        all_slots = list(filter(lambda r: r not in house.crafting_recipes, self._patterns))

        page_slots = all_slots[self._page * self._NUM_PER_PAGE:min(len(all_slots), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, pattern in enumerate(page_slots):
            self.add_item(PatternsDisplayButton(pattern, i))
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(all_slots) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        
        if self._selected_pattern is not None:
            actual_value: int = int(self._selected_pattern.value * self._COST_ADJUST) + 1
            if inventory.get_coins() >= actual_value:
                self.add_item(ConfirmButton(min(4, len(page_slots))))
        self.add_item(ExitButton(min(4, len(page_slots))))

    def _purchase_pattern(self):
        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        house: House = player.get_house()
        if self._selected_pattern is not None:
            actual_value: int = int(self._selected_pattern.value * self._COST_ADJUST) + 1
            if inventory.get_coins() >= actual_value:
                inventory.remove_coins(actual_value)
                house.crafting_recipes.append(LOADED_RECIPES.get_new_recipe(self._selected_pattern.key))
                self._get_patterns_page_buttons()

                return Embed(
                    title="Browse Patterns",
                    description=(
                        f"You have {inventory.get_coins_str()}.\n\n"
                        "Navigate through available recipes using the Prev and Next buttons.\n\n"
                        f"*You purchased {self._selected_pattern.get_name_and_icon()}!*"
                    )
                )
            else:
                self._get_patterns_page_buttons()

                return Embed(
                    title="Browse Patterns",
                    description=(
                        f"You have {inventory.get_coins_str()}.\n\n"
                        "Navigate through available recipes using the Prev and Next buttons.\n\n"
                        f"*Error: You don't have enough coins to buy that!*"
                    )
                )

        self._get_patterns_page_buttons()
        return Embed(
            title="Browse Patterns",
            description=(
                f"You have {inventory.get_coins_str()}.\n\n"
                "Navigate through available recipes using the Prev and Next buttons.\n\n"
                "*Error: Something about that recipe changed or it's no longer available.*"
            )
        )

    def enter_patterns(self):
        self._intent = Intent.Patterns
        self._get_patterns_page_buttons()
        return self.get_embed_for_intent()

    def confirm_using_intent(self):
        if self._intent == Intent.Wares:
            result = self._purchase_item()

            self._get_wares_page_buttons()

            return result
        if self._intent == Intent.Patterns:
            result = self._purchase_pattern()

            self._selected_pattern = None
            self._get_patterns_page_buttons()

            return result
        return self.get_initial_embed()

    def next_page(self):
        self._page += 1

        self._selected_item = None
        self._selected_item_index = -1
        self._selected_pattern = None

        if self._intent == Intent.Wares:
            self._get_wares_page_buttons()
        if self._intent == Intent.Patterns:
            self._get_patterns_page_buttons()

        return self.get_embed_for_intent()

    def prev_page(self):
        self._page = max(0, self._page - 1)

        self._selected_item = None
        self._selected_item_index = -1
        self._selected_pattern = None

        if self._intent == Intent.Wares:
            self._get_wares_page_buttons()
        if self._intent == Intent.Patterns:
            self._get_patterns_page_buttons()

        return self.get_embed_for_intent()

    def return_to_main_menu(self):
        self._intent = None
        self._page = 0

        self._selected_item = None
        self._selected_item_index = -1
        self._selected_pattern = None

        self.show_initial_buttons()
        return self.get_initial_embed()

    def get_user(self):
        return self._user

# -----------------------------------------------------------------------------
# NPC CLASS
# -----------------------------------------------------------------------------

class Blacksmith(NPC):
    def __init__(self):
        super().__init__("Abarra", NPCRoles.Blacksmith, NPCDuelingPersonas.Bruiser, {})

        self._setup_npc_params()
            
    def _setup_inventory(self):
        if self._inventory is None:
            self._inventory = Inventory()
        
        items_to_add = []

        self._inventory.add_coins(150)
        for item in items_to_add:
            self._inventory.add_item(item)

    def _setup_xp(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._expertise.add_xp_to_class(1000, ExpertiseClass.Fisher, self._equipment) # Level 5
        self._expertise.add_xp_to_class(3976, ExpertiseClass.Merchant, self._equipment) # Level 15
        self._expertise.add_xp_to_class(7000, ExpertiseClass.Guardian, self._equipment) # Level 25
        
        self._expertise.points_to_spend = 0
        
        self._expertise.constitution = 20
        self._expertise.intelligence = 0
        self._expertise.dexterity = 0
        self._expertise.strength = 16
        self._expertise.luck = 0
        self._expertise.memory = 9

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.Helmet, LOADED_ITEMS.get_new_item(ItemKey.IronHelmet))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.Gloves, LOADED_ITEMS.get_new_item(ItemKey.IronGauntlets))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.ChestArmor, LOADED_ITEMS.get_new_item(ItemKey.IronCuirass))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.AbarrasGreatsword))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.Leggings, LOADED_ITEMS.get_new_item(ItemKey.IronLeggings))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.Boots, LOADED_ITEMS.get_new_item(ItemKey.IronGreaves))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [
            WhirlwindIII(), SecondWindIII(), PiercingStrikeIII(),
            ScarArmorII(), CounterstrikeIII(), PressTheAdvantageI(),
            EvadeIII(), HeavySlamII(), BoundToGetLuckyIII()
        ]
    
    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Abarra"
        self._role = NPCRoles.Blacksmith
        self._dueling_persona = NPCDuelingPersonas.Bruiser
        self._dueling_rewards = {}
        
        self._inventory: Inventory | None = state.get("_inventory")
        if self._inventory is None:
            self._inventory = Inventory()
            self._setup_inventory()

        self._equipment: Equipment | None = state.get("_equipment")
        if self._equipment is None:
            self._equipment = Equipment()
            self._setup_equipment()

        self._expertise: Expertise | None = state.get("_expertise")
        if self._expertise is None:
            self._expertise = Expertise()
            self._setup_xp()

        self._dueling: Dueling | None = state.get("_dueling")
        if self._dueling is None:
            self._dueling = Dueling()
            self._setup_abilities()

        self._stats: Stats | None = state.get("_stats")
        if self._stats is None:
            self._stats = Stats()
