from __future__ import annotations
from uuid import uuid4

import discord
import re

from discord import Embed
from discord.ext import tasks
from strenum import StrEnum
from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Attribute, Expertise, ExpertiseClass
from features.house.recipe import LOADED_RECIPES, Recipe, RecipeKey
from features.npcs.npc import NPC, NPCDuelingPersonas, NPCRoles
from features.shared.ability import BoundToGetLuckyIII, ContractManaToBloodIII, ContractWealthForPowerIII, EmpowermentI, IncenseIII, ParalyzingFumesI, PreparePotionsIII, QuickAccessI, RegenerationIII, SecondWindI, SilkspeakingI, ThunderingTorrentIII, VitalityTransferIII
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, Item, ItemKey
from features.shared.nextbutton import NextButton
from features.shared.prevbutton import PrevButton
from random import choice

from typing import TYPE_CHECKING, List

from features.stats import Stats
if TYPE_CHECKING:
    from bot import BenjaminBowtieBot
    from features.house.house import House
    from features.inventory import Inventory
    from features.player import Player

# -----------------------------------------------------------------------------
# MODALS
# -----------------------------------------------------------------------------

class PurchaseModal(discord.ui.Modal):
    def __init__(self, database: dict, guild_id: int, user: discord.User, item: Item, view: YennaView, message_id: int):
        super().__init__(title=f"Purchase {item.get_full_name()}")

        self._database = database
        self._guild_id = guild_id
        self._user = user
        self._item = item
        self._view = view
        self._message_id = message_id

        # TODO: Small problem: I don't have a way of displaying the total cost to the user
        # since there's no callback on the text input value changing.
        self._count_input: discord.ui.TextInput = discord.ui.TextInput(
            label="Quantity",
            default="1",
            required=True
        )
        self.add_item(self._count_input)

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    async def on_submit(self, interaction: discord.Interaction):
        pass

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        await interaction.response.send_message("Error: Something has gone terribly wrong.")

# -----------------------------------------------------------------------------
# NPC VIEW
# -----------------------------------------------------------------------------

class Intent(StrEnum):
    Wares = "Wares"
    Identify = "Identify"
    Tarot = "Tarot"
    Recipes = "Recipes"


class EnterWaresButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Browse Wares", row=0)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: YennaView = self.view

        if view.get_user() == interaction.user:
            response = view.enter_wares()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class EnterRecipesButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Browse Recipes", row=1)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: YennaView = self.view

        if view.get_user() == interaction.user:
            response = view.enter_recipes()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class EnterIdentifyButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Identify Items", row=2)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: YennaView = self.view

        if view.get_user() == interaction.user:
            response = view.enter_identify()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class EnterTarotButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Tarot Reading", row=3)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: YennaView = self.view

        if view.get_user() == interaction.user:
            response = view.enter_tarot()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ExitButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.red, label="Back", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: YennaView = self.view

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
        
        view: YennaView = self.view
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
        
        view: YennaView = self.view
        if interaction.user == view.get_user():
            response = view.select_recipe(self._recipe)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class IdentifyDisplayButton(discord.ui.Button):
    def __init__(self, item_index: int, item: Item, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_name_and_count()}", row=row, emoji=item.get_icon())
        
        self._item_index = item_index
        self._item = item

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: YennaView = self.view
        if interaction.user == view.get_user():
            response = view.select_identify_item(self._item_index, self._item)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ConfirmButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.green, label="Confirm", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: YennaView = self.view
        if interaction.user == view.get_user():
            response = view.confirm_using_intent()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class YennaView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, user: discord.User):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._user = user

        self._yenna: Yenna = database[str(guild_id)]["npcs"][NPCRoles.FortuneTeller]
        self._wares: List[Item] = [
            # Potions
            LOADED_ITEMS.get_new_item(ItemKey.CrystalVial),
            LOADED_ITEMS.get_new_item(ItemKey.LesserHealthPotion),
            LOADED_ITEMS.get_new_item(ItemKey.HealthPotion),
            LOADED_ITEMS.get_new_item(ItemKey.GreaterHealthPotion),
            LOADED_ITEMS.get_new_item(ItemKey.LesserManaPotion),
            LOADED_ITEMS.get_new_item(ItemKey.ManaPotion),
            LOADED_ITEMS.get_new_item(ItemKey.GreaterManaPotion),

            # Herbs
            LOADED_ITEMS.get_new_item(ItemKey.AntlerCoral),
            LOADED_ITEMS.get_new_item(ItemKey.Asptongue),
            LOADED_ITEMS.get_new_item(ItemKey.Seaclover),
            LOADED_ITEMS.get_new_item(ItemKey.Shellplate),
            LOADED_ITEMS.get_new_item(ItemKey.Stranglekelp),

            # Seeds
            LOADED_ITEMS.get_new_item(ItemKey.AsptongueSeed),
            LOADED_ITEMS.get_new_item(ItemKey.MeddlespreadSpores),
            LOADED_ITEMS.get_new_item(ItemKey.SeacloverSeed),
            LOADED_ITEMS.get_new_item(ItemKey.SnowdewSeed),
            LOADED_ITEMS.get_new_item(ItemKey.SungrainSeed),

            # Soils
            LOADED_ITEMS.get_new_item(ItemKey.Ash),
            LOADED_ITEMS.get_new_item(ItemKey.Clay),
            LOADED_ITEMS.get_new_item(ItemKey.Compost),
            LOADED_ITEMS.get_new_item(ItemKey.Dirt),
            LOADED_ITEMS.get_new_item(ItemKey.Loam),
            LOADED_ITEMS.get_new_item(ItemKey.Pebbles)
        ]
        self._selected_item: (Item | None) = None
        self._selected_item_index: int = -1

        self._recipes: List[Recipe] = [
            LOADED_RECIPES.get_new_recipe(RecipeKey.CrystalVialWithFlawlessQuartz),
            LOADED_RECIPES.get_new_recipe(RecipeKey.CrystalVialWithQuartz),
            LOADED_RECIPES.get_new_recipe(RecipeKey.LesserConstitutionPotion),
            LOADED_RECIPES.get_new_recipe(RecipeKey.LesserStrengthPotion),
            LOADED_RECIPES.get_new_recipe(RecipeKey.LesserDexterityPotion),
            LOADED_RECIPES.get_new_recipe(RecipeKey.LesserIntelligencePotion),
            LOADED_RECIPES.get_new_recipe(RecipeKey.LesserHealthPotion),
            LOADED_RECIPES.get_new_recipe(RecipeKey.LesserManaPotion),
            LOADED_RECIPES.get_new_recipe(RecipeKey.LesserPoison)
        ]
        self._selected_recipe: (Recipe | None) = None

        self._intent: (Intent | None) = None

        self._page = 0
        self._NUM_PER_PAGE = 4

        self._COST_ADJUST = 1.5 # 50% price increase from base when purchasing items
        self._IDENTIFY_COST = 50 # Fixed at 50 coins for now
        self._TAROT_COST = 500 # Fixed at 500 coins for now

        self.show_initial_buttons()
        
    def _get_player(self) -> Player:
        return self._database[str(self._guild_id)]["members"][str(self._user.id)]

    def get_initial_embed(self):
        return Embed(
            title="Madame Yenna's Tent",
            description=(
                "In the bustling village market stands an unusual tent, covered in a patterned red, gold, and purple fabric. "
                "Stepping inside, the daylight suddenly disperses and shadow engulfs you. Your eyes adjust to the dim interior, oddly larger than it appeared from the outside.\n\n"
                "A flickering light passes across the shadows cast by the setup in front of you: Dark wooden chairs, one near you and another on the opposite side of a rectangular table hewn of the same wood. "
                "The table has white wax candles on either side, illuminating tarot cards, potions, herbs, and various occult implements that belong to the figure hidden in the shadows beyond the table's edge.\n\n"
                "\"Matters of fate and destiny are often complex,\" she says, moving closer to the light, though you remain unable to see the upper half of her face. \"What can I do to aid your journey?\""
            )
        )

    def show_initial_buttons(self):
        self.clear_items()

        self.add_item(EnterWaresButton())
        self.add_item(EnterRecipesButton())
        self.add_item(EnterIdentifyButton())
        self.add_item(EnterTarotButton())

    def get_embed_for_intent(self):
        player: Player = self._get_player()
        if self._intent == Intent.Wares:
            return Embed(
                title="Browse Wares",
                description=(
                    "\"Looking to procure something for what lies ahead? I have herbs, potions, and scrolls -- all of which I'm willing to part with for a reasonable fee.\"\n\n"
                    f"You have {player.get_inventory().get_coins_str()}."
                )
            )
        if self._intent == Intent.Identify:
            return Embed(
                title="Identify Item",
                description=(
                    "\"The mysteries of this world can often be a challenge to unravel. Let's see the truth hidden within.\"\n\n"
                    f"You have {player.get_inventory().get_coins_str()}."
                )
            )
        if self._intent == Intent.Tarot:
            return Embed(
                title="Tarot Reading",
                description=(
                    "\"You wish to see what the cards reveal? Come, sit. Let us look into the past, the present, and the future.\"\n\n"
                    f"This will cost **{self._TAROT_COST} coins**. You have {player.get_inventory().get_coins_str()}.\n\n"
                    "*Note: This will RESET your attribute points, allowing you to reallocate them.*"
                )
            )
        if self._intent == Intent.Recipes:
            return Embed(
                title="Browse Recipes",
                description=(
                    "\"There are some things I can teach you, yes. I suspect you'd prefer it to creating an explosion in your alchemy chamber.\"\n\n"
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

    def display_identify_info(self):
        player: Player = self._get_player()
        all_slots: List[Item] = player.get_inventory().get_inventory_slots()
        if self._selected_item is None or not (0 <= self._selected_item_index < len(all_slots) and all_slots[self._selected_item_index] == self._selected_item):
            self._get_identify_page_buttons()
            return Embed(
                title="Identify Item",
                description=(
                    f"You have {player.get_inventory().get_coins_str()}.\n\n"
                    "Navigate through your items using the Prev and Next buttons.\n\n"
                    "*Error: Something about that item changed or it's no longer available.*"
                )
            )

        return Embed(
            title="Identify Item",
            description=(
                f"You have {player.get_inventory().get_coins_str()}.\n\n"
                f"᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n**{self._selected_item.get_full_name()}**\n*{self._selected_item.get_rarity()} Item*\n\nIdentification Cost: {self._IDENTIFY_COST}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\n"
                "Navigate through your items using the Prev and Next buttons."
            )
        )

    def select_identify_item(self, index: int, item: Item):
        self._selected_item = item
        self._selected_item_index = index

        self._get_identify_page_buttons()
        return self.display_identify_info()

    def _get_identify_page_buttons(self):
        self.clear_items()
        player: Player = self._get_player()
        inventory = player.get_inventory()
        inventory_slots = inventory.get_inventory_slots()

        filtered_indices = inventory.filter_inventory_slots([ClassTag.Misc.NeedsIdentification])
        filtered_items = [inventory_slots[i] for i in filtered_indices]

        page_slots = filtered_items[self._page * self._NUM_PER_PAGE:min(len(filtered_items), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            exact_item_index: int = filtered_indices[i + (self._page * self._NUM_PER_PAGE)]
            self.add_item(IdentifyDisplayButton(exact_item_index, item, i))
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(filtered_items) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        if self._selected_item is not None:
            self.add_item(ConfirmButton(min(4, len(page_slots))))
        self.add_item(ExitButton(min(4, len(page_slots))))

    def _identify_item(self):
        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        all_slots: List[Item] = inventory.get_inventory_slots()
        if self._selected_item is None or all_slots[self._selected_item_index] != self._selected_item:
            return Embed(
                title="Identify Item",
                description=(
                    f"You have {inventory.get_coins_str()}.\n\n"
                    "Navigate through your items using the Prev and Next buttons.\n\n"
                    "*Error: Something about that item changed or it's no longer available.*"
                )
            )

        if inventory.get_coins() < self._IDENTIFY_COST:
            return Embed(
                title="Identify Item",
                description=(
                    f"You have {inventory.get_coins_str()}.\n\n"
                    "Navigate through your items using the Prev and Next buttons.\n\n"
                    f"*You don't have the coins needed ({self._IDENTIFY_COST}) to identify this item.*" 
                )
            )

        if ClassTag.Equipment.Equipment in self._selected_item.get_class_tags():
            # TODO: Implement this when random items based on rarity happens
            # inventory.remove_coins(self._IDENTIFY_COST)
            # inventory.remove_item(self._selected_item_index)
            # Then add a new item randomly generated based on the selected item's rarity
            pass
        
        if self._selected_item.get_key() == ItemKey.MysteriousScroll:
            return self._yenna.identify_scroll(player, self._selected_item_index, self._user.display_name, self._IDENTIFY_COST)

        if self._selected_item.get_key() == ItemKey.FishMaybe:
            return self._yenna.identify_fish_maybe(player, self._selected_item_index, self._IDENTIFY_COST)

        return Embed(
            title="Identify Item",
            description=(
                f"You have {inventory.get_coins_str()}.\n\n"
                "Navigate through your items using the Prev and Next buttons.\n\n"
                "\"Strange... I can't make sense of this item at all. Perhaps let's try a different one.\""
            )
        )

    def enter_identify(self):
        self._intent = Intent.Identify
        self._get_identify_page_buttons()
        return self.get_embed_for_intent()

    def _tarot_reading(self):
        self.clear_items()
        self.add_item(ExitButton(0))

        attrs = self._get_player().get_expertise().get_all_attributes()

        description = (
            "*The flicker of the candlelight dances across Yenna's hands as she shuffles the cards. She asks you to split the deck, then again, merging the pieces as you see fit. She lets you shuffle for a time, then takes the cards back and spreads them in a fan before you. You choose three.*\n\n"
            "\"Let us begin with the past...\"\n\n"
            "*She flips over the first card: It's an image of a blank figure, wrapped in shadow like cloth, no features visible beyond a vaguely humanoid body. Behind them are a series of desaturated lights of various colors that blend into a fog.*\n\n"
            "\"The Stranger. When you arrived here in town, you were unknown and without direction. You've come from beyond with a destiny your own to create. The possibilities were endless and you chose...\"\n\n"
        )

        max_val = max([attrs.constitution, attrs.dexterity, attrs.intelligence, attrs.luck, attrs.memory, attrs.strength])
        best_attr = None
        if attrs.constitution == max_val:
            description += (
                "*She flips over the next card: It's an image of a castle on a hill, powerful shields depicted on the tapestries that drape over its walls. The sky is clear and the hill itself is a hale and hearty green.*\n\n"
                "\"The Fortress. You're seldom one to take risks and your endurance is a point of pride. Though you're a tough contender, beware the dangers of poison and curses which may easily sap that away.  Your role is best served as a protector for the moment, though what you choose is entirely up to you.\"\n\n"
            )
            best_attr = Attribute.Constitution
        if attrs.dexterity == max_val:
            description += (
                "*She flips over the next card. It's an image of two people: One a person in a hooded cloak with daggers gleaming at their side, the other a dashing rapier-wielder in a fine doublet -- the latter bears an uncanny resemblance to Galos. They're back to back, almost as though two sides of the same coin.*\n\n"
                "\"The Dancers. You're elegant and quick, there's no doubt about that; those who try to stop you will find themselves suddenly facing nothing at all. Despite this, you can't keep running forever. There will come a time when you have to hit back: Prepare for that day.\"\n\n"
            )
            best_attr = Attribute.Dexterity
        if attrs.intelligence == max_val:
            description += (
                "*She flips over the next card: It's an painterly image of the stars with blue and white swirling gases, but in the center is an amorphous gap leading only to darkness. You could almost swear there's something inside that void.*\n\n"
                "\"The Eternal. You have a hunger for knowledge and power -- not to mention an affinity for the arcane. These are useful traits that will aid you in life, but be careful about how far you go. There are some things better left unknown and some things not worth reaching for.\"\n\n"
            )
            best_attr = Attribute.Intelligence
        if attrs.luck == max_val:
            description += (
                "*She flips over the next card: It's an image of a golden coin flipping through the air, a visage of chaos on one side and a vision of a paradise on the other. The card itself shines and glimmers in a mesmerizing way.*\n\n"
                "\"The Chance. Often regarded as a symbol of wealth, it's true meaning relates to fortune and destiny. Most people would look at what happens in your life and call you lucky, but it'd be more accurate to say that things just tend to happen to you. Be careful, for good and bad are relative concepts -- you may find chance to be your downfall, not your uprising.\"\n\n"
            )
            best_attr = Attribute.Luck
        if attrs.memory == max_val:
            description += (
                "*She flips over the next card: It's an image of a winding forest path leading forward into golden light which you can't see past. The trees bend into arches like a tunnel around the grass and dirt, strangely comforting and mysterious. An obscured figure with their back towards you walks down the path towards the light.*\n\n"
                "\"The Voyager. Very rarely in my long life have I ever seen this card pulled. You want to do it all and explore the potential within, but you don't neglect understanding what it means. Without that, you'll find your experiences superficial and ultimately meaningless.\"\n\n"
            )
            best_attr = Attribute.Memory
        if attrs.strength == max_val:
            description += (
                "*She flips over the next card: It's an image of a beautiful, brown horse galloping over a vast field. Its rippling muscles are clearly visible -- painted with careful detail -- and it seems to be in peak fitness.*\n\n"
                "\"The Stallion. Your strength is your greatest attribute, both in body and willpower. I wouldn't doubt you train often and endeavor to become a powerful guardian. Be warned, however: Without the right tools by your side, all that brawn will fail you.\"\n\n"
            )
            best_attr = Attribute.Strength

        possibilities = []
        for i in range(5):
            if best_attr == Attribute.Intelligence and i == 1:
                continue
            if best_attr == Attribute.Luck and i == 2:
                continue
            if best_attr == Attribute.Strength and i == 3:
                continue
            if best_attr == Attribute.Constitution and i == 4:
                continue
            possibilities.append(i)
        final_result = choice(possibilities)

        if final_result == 0:
            description += (
                "*She flips over the final card: It's an image of a person whose right hand is falling apart, as though being turned into sand and dust. Their left hand, however, is sprouting vines and flowers, turning green up the arm. The background appears to be a desert in midday, the sand around them identical to that which they're slowing becoming.*\n\n"
                "\"Death. It is an inevitable thing. But fear not, for this doesn't mean all roads lead towards destruction. Death can mean a new beginning, a chance to try something different. Endings surround us and though we often fight against them, some carry powerful meanings and lessons worth listening to.\"\n\n"
            )
        if final_result == 1:
            description += (
                "*She flips over the final card: It's an image of a vast body of blue water with the sun setting on the horizon. You can see the end of a shimmering, white sand beach in the foreground with footsteps leading towards the water, but no sign of the figure who made them.*\n\n"
                "\"The Endless. There are many possible futures that await you, and this card is merely a suggestion: There is much to learn out there in the world, including great powers which could aid your journey. Mana, in particular, is something worth exploring and understanding deeply.\"\n\n"
            )
        if final_result == 2:
            description += (
                "*She flips over the final card: It's an image of a golden coin flipping through the air, a visage of chaos on one side and a vision of a paradise on the other. The card itself shines and glimmers in a mesmerizing way.*\n\n"
                "\"The Chance. Often regarded as a symbol of wealth, it's true meaning relates to fortune and destiny. Consider looking out for what could improve your opportunities in life and invest in what will guarantee you a better future.\n\n\""
            )
        if final_result == 3:
            description += (
                "*She flips over the final card: It's an image of a beautiful, brown horse galloping over a vast field. Its rippling muscles are clearly visible -- painted with careful detail -- and it seems to be in peak fitness.*\n\n"
                "\"The Stallion. You may consider improving your strength in the future and becoming a powerful guardian. Don't underestimate a strong hand in combat and how a well-placed blow could change the course of a fight.\"\n\n"
            )
        if final_result == 4:
            description += (
                "*She flips over the final card: It's an image of an old man sitting in front of a bonfire, surrounded by mushrooms of various types and colors. The background seems to be a deep forest in the middle of the night -- the main source of light seems to be the flames before him.*\n\n"
                "\"The Sage. For the many options that you may yet choose, there is a benefit to remembering where you've been and studying the wisdom of those who have ventured out into the world before you. This is often regarded as the card of the alchemists, though I'm perhaps a bit biased to suggest you learn some alchemy yourself.\"\n\n"
            )

        description += "\"Remember that the choices are yours to make. What I have shown you here is merely a look into the past, present, and one possible future.\"\n\n*Your attribute points have been reset and you can now spend them again.*"

        if self._get_player().get_inventory().get_coins() >= self._TAROT_COST:
            self._get_player().get_expertise().reset_points()
            self._get_player().get_dueling().abilities = []
            self._get_player().get_inventory().remove_coins(self._TAROT_COST)

        return Embed(
            title="Tarot Reading",
            description=description
        )

    def enter_tarot(self):
        self.clear_items()
        self._intent = Intent.Tarot
        if self._get_player().get_inventory().get_coins() >= self._TAROT_COST:
            self.add_item(ConfirmButton(0))
        self.add_item(ExitButton(0))
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
        if self._intent == Intent.Identify:
            result = self._identify_item()

            self._selected_item = None
            self._selected_item_index = -1
            self._get_identify_page_buttons()

            return result
        if self._intent == Intent.Tarot:
            return self._tarot_reading()
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
        if self._intent == Intent.Identify:
            self._get_identify_page_buttons()
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
        if self._intent == Intent.Identify:
            self._get_identify_page_buttons()
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

class Yenna(NPC):
    def __init__(self):
        super().__init__("Yenna", NPCRoles.FortuneTeller, NPCDuelingPersonas.Healer, {})

        self._setup_npc_params()

    def identify_scroll(self, player: Player, selected_item_index: int, display_name: str, identify_cost: int):
        inventory = player.get_inventory()

        word_set = set(self._scroll_text.lower().replace(".", "").replace(",", "").replace("?", "").replace("!", "").split(" "))
        found_words = set(self._words_identified)
        words_remaining = word_set - found_words
        
        if len(words_remaining) == 0:
            inventory.add_coins(40)
            inventory.remove_item(selected_item_index)
            return Embed(
                title="A Mysterious Scroll",
                description=(
                    "\"Ah, another one of these scrolls. It looks like there's nothing more I can glean from the text. The final message is:\"\n\n"
                    f"{self._scroll_text}\n\n"
                    "\"However, allow me to offer compensation at least for trusting the scroll to me.\"\n\n"
                    "*You pay nothing for this identification and instead receive 40 coins.*"
                )
            )
        
        random_word: str = choice(list(words_remaining))
        self._words_identified.append(random_word)
        found_words.add(random_word)
        words_remaining = word_set - found_words
        
        result_text = self._scroll_text
        for word in words_remaining:
            # Replace both the lowercase and the capitalized forms of the word
            result_text = re.sub(r"\b%s\b" % word, "▮" * len(word), result_text)
            result_text = re.sub(r"\b%s\b" % word.capitalize(), "▮" * len(word), result_text)

        last_to_identify_str = ""
        if display_name == self._last_to_identify_scroll:
            last_to_identify_str = f"\"Another one, {display_name}? You have a propensity for acquiring unusual items it seems. With time and effort, I anticipate we'll decipher all there is to know here.\""
        else:
            last_to_identify_str = f"\"Another one? {self._last_to_identify_scroll} also brought me one before... With time and effort, I anticipate we'll decipher all there is to know here.\"" if self._last_to_identify_scroll != "" else ""
        
        inventory.remove_coins(identify_cost)
        inventory.remove_item(selected_item_index)
        self._last_to_identify_scroll = display_name

        return Embed(
            title="A Mysterious Scroll",
            description=(
                f"{last_to_identify_str}\n\n"
                "*Reaching out past the firelight, Yenna takes the scroll from your hands and unrolls it onto the table.*\n\n"
                "\"This scroll is degrading -- not from being previously submerged in water, but perhaps due to its exposure to air? The parchment is some kind of pulped kelp, dyed made to look like the off-white coloration I'd typically expect in a scroll of this design. "
                "There are words written here, but they're more like a failed attempt to write the Common tongue with some borrowed elements from other languages and more still I don't recognize. I might be able to make some sense of them...\"\n\n"
                "*Yenna pours over the scroll for hours, comparing to her books and other texts in an effort to understand it. Eventually, the parchment begins to fully fall apart in the warm light.*\n\n"
                f"Here's what I have for you (identified the word *{random_word}*):\n\n"
                f"{result_text}"
            )
        )

    def identify_fish_maybe(self, player: Player, selected_item_index: int, identify_cost: int):
        inventory = player.get_inventory()

        inventory.remove_coins(identify_cost)
        inventory.remove_item(selected_item_index)

        result = Embed()
        result_num: int = int(self._num_fish_maybe_identified / self._NUM_FISH_PER_RESULT)

        if self._num_fish_maybe_identified / self._NUM_FISH_PER_RESULT > 4:
            inventory.add_coins(identify_cost + 25)
            return Embed(title="A Fish?",
                description=(
                    "\"Thank you for bringing another of these to me. I'll take care of it. Please, take these in return.\"\n\n"
                    "*You pay nothing for this identification and instead receive 25 coins.*"
                )
            )

        if self._num_fish_maybe_identified % self._NUM_FISH_PER_RESULT == 0:
            if result_num == 0:
                result = Embed(title="A Fish?",
                    description=(
                        "*Yenna stares for a moment at what you've procured from your pack, cocking her head ever so slightly.*\n\n"
                        "\"A fish? If you want to know its nature, seek out Quinan's mother, not me.\"\n\n"
                        "*But again she looks at it -- or perhaps tries to -- for something seems... wrong. She goes silent for a moment, then reaches out a hand.*\n\n"
                        "\"Acquire me some more and I'll see what alchemy can reveal about their nature.\""
                    )
                )
            if result_num == 1:
                result = Embed(title="A Fish?",
                    description=(
                        "\"This should be enough to try a few different alchemical tests. I've prepared some potions that should help identify the properties of these fish.\"\n\n"
                        "*She procures a few implements, some vials, and liquids of various hues and viscosities from her supplies. As she deposits them one by one onto different parts of the fish, but no smoke, color changes, flashes of fire, or otherwise appear before you.*\n\n"
                        "\"At least one of those should have produced some reaction... It's as though they're ordinary, but I can't let this feeling of unease pass. I'm going to need more of these fish, if you can find them.\""
                    )
                )
            if result_num == 2:
                result = Embed(title="A Fish?",
                    description=(
                        "\"I've acquired some rare herbs that should reveal any magical nature to these creatures. They might be able to channel mana, weaving some kind of ward against those who would try to eat them.\"\n\n"
                        "*She laughs at her own joke, though nervously. You can tell she doesn't believe her own words.*\n\n"
                        "*In the dim light, she lays the fish before her and lights a bowl of incense. She places the fish into a bath of salt water, the scent mingling with the burning manabloom. With care, she adds two vials of liquid to the bath, each clear and unfamiliar to you.*\n\n"
                        "*At first, nothing happens. There's stillness, but for a moment you could swear you saw one of the fish... move. Wriggle. Then stillness again. Then out of the corner of your eye: A mouth gaping? Closing and opening? It couldn't be alive.*\n\n"
                        "*Yenna takes a separated, green and yellow liquid that looks like golden oil atop a shallow sea from her bag, then adds it to the bath.*\n\n"
                        "\"What-- get back!\"\n\n"
                        "*Her exclamation rings out as the tub suddenly explodes with blood and a black liquid that overflows and covers the table. It drips to the floor, thick and oozing more and more from the tub. Yenna raises her hands and a web of light descends on it. With some resistance, the terrifying effect slows and begins to die down.*\n\n"
                        "\"This is no fish. And certainly no power of mana. Bring me more of them and we'll try a different approach.\""
                    )
                )
            if result_num == 3:
                result = Embed(title="A Fish?",
                    description=(
                        "\"Thus far we have tried alchemy in its many forms, but for a deeper look at what these creatures are, I'll need to channel mana.\"\n\n"
                        "*With a snap of her fingers, she starts a fire under some kind of alembic. She waves a hand over the fish and, with delicate precision, she plucks off a scale from the fish binding it with some unseen power, then another, then another --*\n\n"
                        "*And it shrieks, a shattering noise inside your very mind, not of pain but something else. How could it feel any pain? It's been dead since you caught it. From her sudden withdrawal, you can tell Yenna felt the same outburst.*\n\n"
                        "*There's silence. For now, Yenna stops. Carefully, she begins to approach and places it into a jar to keep it contained.*\n\n"
                        "\"There is one last thing I can do. I dread to, for what it might mean, but bring me a fresh set of these creatures and we will settle this matter.\""
                    )
                )
            if result_num == 4:
                result = Embed(title="A Fish?",
                    description=(
                        "\"I've grown greatly concerned about what may lurk beneath the waters. At first, I thought it some mutation or rare creature previously unknown, but these...\"\n\n"
                        "*She begins to move her hands over the fish in the beginnings of a powerful ritual. The candlelight flickers in and out, shadows growing longer, shapes and figures seeming to dance in the fading glow.*\n\n"
                        "*Yenna dashes a flash of powder into a pot containing the last of the flames, only for it to erupt brightly with an overpowering scent of starpepper and charred wood.*\n\n"
                        "*In that moment, the light reduced to a mere ember, you can glimpse something. Almost in the reflection of its scales. Eyes. Far too many eyes. And something else… Like the fish was stitched together on the inside. Like tendrils should be wriggling out from every part of its body. Like there's another version of this thing, something hidden away, beneath.*\n\n"
                        "\"There are things in this world that we all agreed would be better kept secret. Dealt with on our own, so that no one would spend every waking moment in fear. I believe now that some such force is at play here, in the depths, though it's unlike any I've encountered before. Descend. Descend into the dark ocean and find the source. This is what you must do if we're to cease the machinations of this eldritch thing. We'll speak on this more later.\""
                    )
                )
        else:           
            result = Embed(title="A Fish?",
                description=(
                    "\"Thank you for bringing another of these to me. Any others you can find would be appreciated.\"\n\n"
                    f"*{self._NUM_FISH_PER_RESULT - (self._num_fish_maybe_identified % self._NUM_FISH_PER_RESULT)} Fish? needed*"
                )
            )

        self._num_fish_maybe_identified += 1
        return result

    def _setup_inventory(self):
        if self._inventory is None:
            self._inventory = Inventory()

        health_potions = LOADED_ITEMS.get_new_item(ItemKey.HealthPotion)
        health_potions.add_amount(2)
        sapping_potions = LOADED_ITEMS.get_new_item(ItemKey.SappingPotion)
        sapping_potions.add_amount(1)

        items_to_add = [health_potions, sapping_potions]

        self._inventory.add_coins(5000)
        for item in items_to_add:
            self._inventory.add_item(item)

    def _setup_xp(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._expertise.add_xp_to_class(96600, ExpertiseClass.Merchant, self._equipment) # Level 20
        self._expertise.add_xp_to_class(1600, ExpertiseClass.Guardian, self._equipment) # Level 5
        self._expertise.add_xp_to_class(22000, ExpertiseClass.Alchemist, self._equipment) # Level 30

        self._expertise.points_to_spend = 0
        
        self._expertise.constitution = 15
        self._expertise.intelligence = 30
        self._expertise.dexterity = 10
        self._expertise.strength = 3
        self._expertise.luck = 10
        self._expertise.memory = 12

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.Helmet, LOADED_ITEMS.get_new_item(ItemKey.MothsilkCowl))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.Gloves, LOADED_ITEMS.get_new_item(ItemKey.MothsilkGloves))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.Ring, LOADED_ITEMS.get_new_item(ItemKey.BandOfGreaterRestoration))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.ChestArmor, LOADED_ITEMS.get_new_item(ItemKey.RobeOfTheEyelessSeer))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.YennasStaff))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.OffHand, LOADED_ITEMS.get_new_item(ItemKey.DeckOfFate))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.Boots, LOADED_ITEMS.get_new_item(ItemKey.MothsilkBoots))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()

        # TODO: Also add fate-bending abilities
        self._dueling.abilities = [
            BoundToGetLuckyIII(), SecondWindI(), SilkspeakingI(),
            ParalyzingFumesI(), RegenerationIII(), ThunderingTorrentIII(),
            PreparePotionsIII(), EmpowermentI(),
            IncenseIII(), ContractManaToBloodIII(), ContractWealthForPowerIII()
        ]

    def _setup_story_variables(self, state: dict):
        self._scroll_text: str = "You walk on chains with your eyes. Push the fingers through the surface into the void. The trees are talking now. Through a maze you are rewarded in chaos. They are in the dreaming, in the wanting, in the knowing. Beware the red hexagons. It is the world in the mirror of ocean's make. How do you walk? Repeat it. The name of the sound. We build it until nothing remains. Don't you want these waves to drag you away? Come hither to us, Fisher King. You can almost hear us now. Your throne is waiting."
        self._words_identified: List[str] = state.get("_words_identified", [])
        self._last_to_identify_scroll: str = state.get("_last_to_identify_scroll", "")
        self._num_fish_maybe_identified: int = state.get("_num_fish_maybe_identified", 0)
        self._NUM_FISH_PER_RESULT: int = 5 # Theoretically this could scale with the number of active players

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()
        self._setup_story_variables(state={})

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Yenna"
        self._role = NPCRoles.FortuneTeller
        self._dueling_persona = NPCDuelingPersonas.Healer
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
        
        self._setup_story_variables(state)
