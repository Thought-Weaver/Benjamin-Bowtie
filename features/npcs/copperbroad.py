from __future__ import annotations
from uuid import uuid4

import discord

from discord import Embed
from strenum import StrEnum
from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Expertise, ExpertiseClass
from features.house.house import House
from features.house.recipe import LOADED_RECIPES, RecipeKey
from features.npcs.npc import NPC, NPCDuelingPersonas, NPCRoles
from features.shared.ability import ATidySumII, BoundToGetLuckyIII, CursedCoinsI, HookII, SeaSprayV
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, Item, ItemKey
from features.shared.nextbutton import NextButton
from features.shared.prevbutton import PrevButton
from features.stats import Stats

from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from bot import BenjaminBowtieBot
    from features.house.recipe import Recipe
    from features.inventory import Inventory
    from features.player import Player

# -----------------------------------------------------------------------------
# NPC VIEW
# -----------------------------------------------------------------------------

class Intent(StrEnum):
    Wares = "Wares"
    Recipes = "Recipes"


class EnterWaresButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="Browse Wares", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: ChefView = self.view

        if view.get_user() == interaction.user:
            response = view.enter_wares()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class EnterRecipesButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="Browse Recipes", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: ChefView = self.view

        if view.get_user() == interaction.user:
            response = view.enter_recipes()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ExitButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.red, label="Back", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: ChefView = self.view

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
        
        view: ChefView = self.view
        if interaction.user == view.get_user():
            response = view.select_wares_item(self._item_index, self._item)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class RecipesDisplayButton(discord.ui.Button):
    def __init__(self, recipe: Recipe, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{recipe.name}", row=row, emoji=recipe.icon)
        
        self._recipe = recipe

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: ChefView = self.view
        if interaction.user == view.get_user():
            response = view.select_recipe(self._recipe)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ConfirmButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.green, label="Confirm", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: ChefView = self.view
        if interaction.user == view.get_user():
            response = view.confirm_using_intent()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ChefView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, user: discord.User):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._user = user

        self._chef: ChefView = database[str(guild_id)]["npcs"][NPCRoles.Chef]

        self._wares: List[Item] = [
            LOADED_ITEMS.get_new_item(ItemKey.AppleCider),
            LOADED_ITEMS.get_new_item(ItemKey.Bread),
            LOADED_ITEMS.get_new_item(ItemKey.CookedMinnow),
            LOADED_ITEMS.get_new_item(ItemKey.CookedRoughy),
            LOADED_ITEMS.get_new_item(ItemKey.Dumpling),
            LOADED_ITEMS.get_new_item(ItemKey.FishCake),
            LOADED_ITEMS.get_new_item(ItemKey.FriedShrimp),
            LOADED_ITEMS.get_new_item(ItemKey.MildAle),
            LOADED_ITEMS.get_new_item(ItemKey.MinnowSushi),
            LOADED_ITEMS.get_new_item(ItemKey.MushroomSalad),
            LOADED_ITEMS.get_new_item(ItemKey.MushroomStew),
            LOADED_ITEMS.get_new_item(ItemKey.RoughySushi),
            LOADED_ITEMS.get_new_item(ItemKey.VegetableFritter),
            LOADED_ITEMS.get_new_item(ItemKey.VegetableStew),

            LOADED_ITEMS.get_new_item(ItemKey.AllumCutting),
            LOADED_ITEMS.get_new_item(ItemKey.AppleSeed),
            LOADED_ITEMS.get_new_item(ItemKey.AshberrySeed),
            LOADED_ITEMS.get_new_item(ItemKey.AzureberrySeed),
            LOADED_ITEMS.get_new_item(ItemKey.CrownberrySeed),
            LOADED_ITEMS.get_new_item(ItemKey.DragonPepperSeed),
            LOADED_ITEMS.get_new_item(ItemKey.ElsberrySeed),
            LOADED_ITEMS.get_new_item(ItemKey.GrovemelonSeed),
            LOADED_ITEMS.get_new_item(ItemKey.HoneyfruitSeed),
            LOADED_ITEMS.get_new_item(ItemKey.PlumpinSeed),
            LOADED_ITEMS.get_new_item(ItemKey.PotatoCutting),
            LOADED_ITEMS.get_new_item(ItemKey.SpearLeekCutting),
            LOADED_ITEMS.get_new_item(ItemKey.SunfruitSeed),
            LOADED_ITEMS.get_new_item(ItemKey.SweetrootCutting)
        ]
        self._selected_item: (Item | None) = None
        self._selected_item_index: int = -1

        self._recipes: List[Recipe] = [
            LOADED_RECIPES.get_new_recipe(RecipeKey.Bread),
            LOADED_RECIPES.get_new_recipe(RecipeKey.CookedMinnow),
            LOADED_RECIPES.get_new_recipe(RecipeKey.CookedRoughy),
            LOADED_RECIPES.get_new_recipe(RecipeKey.Dumpling),
            LOADED_RECIPES.get_new_recipe(RecipeKey.FishCakeWithMinnow),
            LOADED_RECIPES.get_new_recipe(RecipeKey.FishCakeWithRoughy),
            LOADED_RECIPES.get_new_recipe(RecipeKey.FriedShrimp),
            LOADED_RECIPES.get_new_recipe(RecipeKey.MushroomSalad),
            LOADED_RECIPES.get_new_recipe(RecipeKey.MushroomStew),
            LOADED_RECIPES.get_new_recipe(RecipeKey.VegetableFritter)
        ]
        self._selected_recipe: (Recipe | None) = None

        self._intent: (Intent | None) = None

        self._page = 0
        self._NUM_PER_PAGE = 4

        self._COST_ADJUST = 1.5 # 50% price increase from base when purchasing items

        self.show_initial_buttons()
        
    def _get_player(self) -> Player:
        return self._database[str(self._guild_id)]["members"][str(self._user.id)]

    def get_initial_embed(self):
        return Embed(
            title="Crown & Anchor Tavern",
            description=(
                "The warm glow of the large, wooden tavern near the center of the village is always an inviting presence. In the evenings, people gather for knucklebones, good conversation with friends, and excellent food. "
                "In the kitchen behind the bar of the Crown & Anchor Tavern, a tall, wide-chested man with an apron stands masterfully combining ingredients in a trusty pan over the fire.\n\n"
                "Copperbroad, the tavern's cook, greets you with a smile and a nod, \"'Ere ta learn some of me recipes, eh? Or perhaps jus' ta grab a bite ta eat?\""
            )
        )

    def show_initial_buttons(self):
        self.clear_items()
        self.add_item(EnterWaresButton(0))
        self.add_item(EnterRecipesButton(1))

    def get_embed_for_intent(self):
        player: Player = self._get_player()
        if self._intent == Intent.Wares:
            return Embed(
                title="Browse Wares",
                description=(
                    "\"Take a look at what I got! Plenty o' food and drink ta go around.\"\n\n"
                    f"You have {player.get_inventory().get_coins_str()}."
                )
            )
        if self._intent == Intent.Recipes:
            return Embed(
                title="Browse Recipes",
                description=(
                    "\"I got a secret o' two I can share with ye.\"\n\n"
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

    def display_recipe_info(self):
        player: Player = self._get_player()
        if self._selected_recipe is None:
            self._get_recipes_page_buttons()
            
            return Embed(
                title="Browse Recipes",
                description=(
                    f"You have {player.get_inventory().get_coins_str()}.\n\n"
                    "Navigate through available recipes using the Prev and Next buttons.\n\n"
                    "*Error: Something about that recipe changed or it's no longer available.*"
                )
            )

        actual_cost: int = int(self._selected_recipe.value * self._COST_ADJUST) + 1
        actual_cost_str: str = f"{actual_cost} coin" if actual_cost == 1 else f"{actual_cost} coins"
        return Embed(
            title="Browse Recipes",
            description=(
                f"You have {player.get_inventory().get_coins_str()}.\n\n"
                f"᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{self._selected_recipe.get_name_and_icon()}\n\n**Price: {actual_cost_str}**\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\n"
                "Navigate through available recipes using the Prev and Next buttons."
            )
        )

    def select_recipe(self, recipe: Recipe):
        self._selected_recipe = recipe

        self._get_recipes_page_buttons()
        return self.display_recipe_info()

    def _get_recipes_page_buttons(self):
        self.clear_items()
        
        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        house: House = player.get_house()
        all_slots = list(filter(lambda r: r not in house.crafting_recipes, self._recipes))

        page_slots = all_slots[self._page * self._NUM_PER_PAGE:min(len(all_slots), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, recipe in enumerate(page_slots):
            self.add_item(RecipesDisplayButton(recipe, i))
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(all_slots) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        
        if self._selected_recipe is not None:
            actual_value: int = int(self._selected_recipe.value * self._COST_ADJUST) + 1
            if inventory.get_coins() >= actual_value:
                self.add_item(ConfirmButton(min(4, len(page_slots))))
        self.add_item(ExitButton(min(4, len(page_slots))))

    def _purchase_recipe(self):
        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        house: House = player.get_house()
        if self._selected_recipe is not None:
            actual_value: int = int(self._selected_recipe.value * self._COST_ADJUST) + 1
            if inventory.get_coins() >= actual_value:
                inventory.remove_coins(actual_value)
                house.crafting_recipes.append(LOADED_RECIPES.get_new_recipe(self._selected_recipe.key))
                self._get_recipes_page_buttons()

                return Embed(
                    title="Browse Recipes",
                    description=(
                        f"You have {inventory.get_coins_str()}.\n\n"
                        "Navigate through available recipes using the Prev and Next buttons.\n\n"
                        f"*You purchased {self._selected_recipe.get_name_and_icon()}!*"
                    )
                )
            else:
                self._get_recipes_page_buttons()

                return Embed(
                    title="Browse Recipes",
                    description=(
                        f"You have {inventory.get_coins_str()}.\n\n"
                        "Navigate through available recipes using the Prev and Next buttons.\n\n"
                        f"*Error: You don't have enough coins to buy that!*"
                    )
                )

        self._get_recipes_page_buttons()
        return Embed(
            title="Browse Recipes",
            description=(
                f"You have {inventory.get_coins_str()}.\n\n"
                "Navigate through available recipes using the Prev and Next buttons.\n\n"
                "*Error: Something about that recipe changed or it's no longer available.*"
            )
        )

    def enter_recipes(self):
        self._intent = Intent.Recipes
        self._get_recipes_page_buttons()
        return self.get_embed_for_intent()

    def confirm_using_intent(self):
        if self._intent == Intent.Wares:
            result = self._purchase_item()

            self._get_wares_page_buttons()

            return result
        if self._intent == Intent.Recipes:
            result = self._purchase_recipe()

            self._selected_recipe = None
            self._get_recipes_page_buttons()

            return result
        
        return self.get_initial_embed()

    def next_page(self):
        self._page += 1

        self._selected_item = None
        self._selected_item_index = -1
        self._selected_recipe = None

        if self._intent == Intent.Wares:
            self._get_wares_page_buttons()
        if self._intent == Intent.Recipes:
            self._get_recipes_page_buttons()

        return self.get_embed_for_intent()

    def prev_page(self):
        self._page = max(0, self._page - 1)

        self._selected_item = None
        self._selected_item_index = -1
        self._selected_recipe = None

        if self._intent == Intent.Wares:
            self._get_wares_page_buttons()
        if self._intent == Intent.Recipes:
            self._get_recipes_page_buttons()

        return self.get_embed_for_intent()

    def return_to_main_menu(self):
        self._intent = None
        self._page = 0

        self._selected_item = None
        self._selected_item_index = -1
        self._selected_recipe = None

        self.show_initial_buttons()
        return self.get_initial_embed()

    def get_user(self):
        return self._user

# -----------------------------------------------------------------------------
# NPC CLASS
# -----------------------------------------------------------------------------

class Chef(NPC):
    def __init__(self):
        super().__init__("Copperbroad", NPCRoles.Chef, NPCDuelingPersonas.Mage, {})

        self._setup_npc_params()

    def _setup_inventory(self):
        if self._inventory is None:
            self._inventory = Inventory()
        
        dumplings = LOADED_ITEMS.get_new_item(ItemKey.Dumpling)
        dumplings.add_amount(4)

        items_to_add = [dumplings]

        self._inventory.add_coins(500)
        for item in items_to_add:
            self._inventory.add_item(item)

    def _setup_xp(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._expertise.add_xp_to_class(3500, ExpertiseClass.Fisher, self._equipment) # Level 10
        self._expertise.add_xp_to_class(1750, ExpertiseClass.Merchant, self._equipment) # Level 10
        self._expertise.add_xp_to_class(750, ExpertiseClass.Guardian, self._equipment) # Level 5
        self._expertise.add_xp_to_class(600, ExpertiseClass.Alchemist, self._equipment) # Level 5

        self._expertise.points_to_spend = 0
        
        self._expertise.constitution = 10
        self._expertise.intelligence = 5
        self._expertise.dexterity = 0
        self._expertise.strength = 5
        self._expertise.luck = 5
        self._expertise.memory = 5

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.Helmet, LOADED_ITEMS.get_new_item(ItemKey.IronHelmet))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.Gloves, LOADED_ITEMS.get_new_item(ItemKey.IronGauntlets))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.ChestArmor, LOADED_ITEMS.get_new_item(ItemKey.IronCuirass))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.CopperbroadsFryingPan))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.Leggings, LOADED_ITEMS.get_new_item(ItemKey.IronLeggings))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.Boots, LOADED_ITEMS.get_new_item(ItemKey.IronGreaves))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [
            SeaSprayV(), HookII(), BoundToGetLuckyIII(),
            ATidySumII(), CursedCoinsI()
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
        self._name = "Copperbroad"
        self._role = NPCRoles.Chef
        self._dueling_persona = NPCDuelingPersonas.Mage
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
