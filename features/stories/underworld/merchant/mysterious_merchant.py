from __future__ import annotations

import discord
import random

from discord import Embed
from enum import StrEnum
from features.shared.item import LOADED_ITEMS, Item, ItemKey
from features.stories.underworld_room_selection import UnderworldRoomSelectionView
from features.stories.story import Story

from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from bot import BenjaminBowtieBot
    from features.inventory import Inventory
    from features.player import Player
    from features.shared.item import Item
    from features.stories.dungeon_run import DungeonRun

# -----------------------------------------------------------------------------
# NPC VIEW
# -----------------------------------------------------------------------------

class Intent(StrEnum):
    Wares = "Wares"
    Sell = "Sell" # TODO: Implement this


class PrevButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.blurple, label="Next", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: MysteriousMerchantView = self.view
        if interaction.user.id == view.get_group_leader().id:
            response = view.prev_page()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class NextButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.blurple, label="Next", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: MysteriousMerchantView = self.view
        if interaction.user.id == view.get_group_leader().id:
            response = view.next_page()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: MysteriousMerchantView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        for player in view.get_players():
            player.get_dungeon_run().in_rest_area = False

        room_selection_view = UnderworldRoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class EnterWaresButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Browse Wares", row=0)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: MysteriousMerchantView = self.view

        if view.get_group_leader() == interaction.user:
            response = view.enter_wares()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ExitToMainButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.red, label="Back", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: MysteriousMerchantView = self.view

        if view.get_group_leader() == interaction.user:
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
        
        view: MysteriousMerchantView = self.view
        if interaction.user == view.get_group_leader():
            response = view.select_wares_item(self._item_index, self._item)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ConfirmButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.green, label="Confirm", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: MysteriousMerchantView = self.view
        if interaction.user == view.get_group_leader():
            response = view.confirm_using_intent()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class MysteriousMerchantView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run

        self._wares: List[Item] = random.choices(population=[
            # Potions
            LOADED_ITEMS.get_new_item(ItemKey.AtrophyPotion),
            LOADED_ITEMS.get_new_item(ItemKey.CharmPotion),
            LOADED_ITEMS.get_new_item(ItemKey.CleansingPotion),
            LOADED_ITEMS.get_new_item(ItemKey.ConstitutionPotion),
            LOADED_ITEMS.get_new_item(ItemKey.CoralskinPotion),
            LOADED_ITEMS.get_new_item(ItemKey.DexterityPotion),
            LOADED_ITEMS.get_new_item(ItemKey.EnfeeblingPotion),
            LOADED_ITEMS.get_new_item(ItemKey.ExplosivePotion),
            LOADED_ITEMS.get_new_item(ItemKey.FearPotion),
            LOADED_ITEMS.get_new_item(ItemKey.FortitudePotion),
            LOADED_ITEMS.get_new_item(ItemKey.GreaterAtrophyPotion),
            LOADED_ITEMS.get_new_item(ItemKey.GreaterCharmPotion),
            LOADED_ITEMS.get_new_item(ItemKey.GreaterConstitutionPotion),
            LOADED_ITEMS.get_new_item(ItemKey.GreaterDexterityPotion),
            LOADED_ITEMS.get_new_item(ItemKey.GreaterEnfeeblingPotion),
            LOADED_ITEMS.get_new_item(ItemKey.GreaterExplosivePotion),
            LOADED_ITEMS.get_new_item(ItemKey.GreaterFearPotion),
            LOADED_ITEMS.get_new_item(ItemKey.GreaterHealthPotion),
            LOADED_ITEMS.get_new_item(ItemKey.GreaterIntelligencePotion),
            LOADED_ITEMS.get_new_item(ItemKey.GreaterManaPotion),
            LOADED_ITEMS.get_new_item(ItemKey.GreaterPoison),
            LOADED_ITEMS.get_new_item(ItemKey.GreaterPotionOfDeathResist),
            LOADED_ITEMS.get_new_item(ItemKey.GreaterPotionOfDecay),
            LOADED_ITEMS.get_new_item(ItemKey.GreaterSleepingDraught),
            LOADED_ITEMS.get_new_item(ItemKey.GreaterSmokebomb),
            LOADED_ITEMS.get_new_item(ItemKey.GreaterStrengthPotion),
            LOADED_ITEMS.get_new_item(ItemKey.HealthPotion),
            LOADED_ITEMS.get_new_item(ItemKey.IntelligencePotion),
            LOADED_ITEMS.get_new_item(ItemKey.LesserAtrophyPotion),
            LOADED_ITEMS.get_new_item(ItemKey.LesserCharmPotion),
            LOADED_ITEMS.get_new_item(ItemKey.LesserConstitutionPotion),
            LOADED_ITEMS.get_new_item(ItemKey.LesserDexterityPotion),
            LOADED_ITEMS.get_new_item(ItemKey.LesserEnfeeblingPotion),
            LOADED_ITEMS.get_new_item(ItemKey.LesserExplosivePotion),
            LOADED_ITEMS.get_new_item(ItemKey.LesserFearPotion),
            LOADED_ITEMS.get_new_item(ItemKey.LesserHealthPotion),
            LOADED_ITEMS.get_new_item(ItemKey.LesserIntelligencePotion),
            LOADED_ITEMS.get_new_item(ItemKey.LesserManaPotion),
            LOADED_ITEMS.get_new_item(ItemKey.LesserPoison),
            LOADED_ITEMS.get_new_item(ItemKey.LesserPotionOfDeathResist),
            LOADED_ITEMS.get_new_item(ItemKey.LesserPotionOfDecay),
            LOADED_ITEMS.get_new_item(ItemKey.LesserSleepingDraught),
            LOADED_ITEMS.get_new_item(ItemKey.LesserSmokebomb),
            LOADED_ITEMS.get_new_item(ItemKey.LesserStrengthPotion),
            LOADED_ITEMS.get_new_item(ItemKey.LuckPotion),
            LOADED_ITEMS.get_new_item(ItemKey.ManaPotion),
            LOADED_ITEMS.get_new_item(ItemKey.Poison),
            LOADED_ITEMS.get_new_item(ItemKey.PotionOfDeathResist),
            LOADED_ITEMS.get_new_item(ItemKey.PotionOfDecay),
            LOADED_ITEMS.get_new_item(ItemKey.SappingPotion),
            LOADED_ITEMS.get_new_item(ItemKey.SleepingDraught),
            LOADED_ITEMS.get_new_item(ItemKey.Smokebomb),
            LOADED_ITEMS.get_new_item(ItemKey.StrengthPotion),
            LOADED_ITEMS.get_new_item(ItemKey.SuperiorAtrophyPotion),
            LOADED_ITEMS.get_new_item(ItemKey.SuperiorConstitutionPotion),
            LOADED_ITEMS.get_new_item(ItemKey.SuperiorDexterityPotion),
            LOADED_ITEMS.get_new_item(ItemKey.SuperiorExplosivePotion),
            LOADED_ITEMS.get_new_item(ItemKey.SuperiorHealthPotion),
            LOADED_ITEMS.get_new_item(ItemKey.SuperiorIntelligencePotion),
            LOADED_ITEMS.get_new_item(ItemKey.SuperiorManaPotion),
            LOADED_ITEMS.get_new_item(ItemKey.SuperiorPoison),
            LOADED_ITEMS.get_new_item(ItemKey.SuperiorPotionOfDecay),
            LOADED_ITEMS.get_new_item(ItemKey.SuperiorSleepingDraught),
            LOADED_ITEMS.get_new_item(ItemKey.SuperiorSmokebomb),
            LOADED_ITEMS.get_new_item(ItemKey.SuperiorStrengthPotion),

            # Food
            LOADED_ITEMS.get_new_item(ItemKey.Bread),
            LOADED_ITEMS.get_new_item(ItemKey.CookedMinnow),
            LOADED_ITEMS.get_new_item(ItemKey.CookedRoughy),
            LOADED_ITEMS.get_new_item(ItemKey.CrownberryJuice),
            LOADED_ITEMS.get_new_item(ItemKey.ElsberryJuice),
            LOADED_ITEMS.get_new_item(ItemKey.Dumpling),
            LOADED_ITEMS.get_new_item(ItemKey.FishCake),
            LOADED_ITEMS.get_new_item(ItemKey.FlamingCurry),
            LOADED_ITEMS.get_new_item(ItemKey.FriedShrimp),
            LOADED_ITEMS.get_new_item(ItemKey.GoldenApple),
            LOADED_ITEMS.get_new_item(ItemKey.GoldenHoneydrop),
            LOADED_ITEMS.get_new_item(ItemKey.GoldenSalad),
            LOADED_ITEMS.get_new_item(ItemKey.Honey),
            LOADED_ITEMS.get_new_item(ItemKey.MildAle),
            LOADED_ITEMS.get_new_item(ItemKey.MinnowSushi),
            LOADED_ITEMS.get_new_item(ItemKey.MushroomSalad),
            LOADED_ITEMS.get_new_item(ItemKey.MushroomStew),
            LOADED_ITEMS.get_new_item(ItemKey.RoastedPotato),
            LOADED_ITEMS.get_new_item(ItemKey.SeafoodMedley),
            LOADED_ITEMS.get_new_item(ItemKey.SpicyMushroomFlatbread),
            LOADED_ITEMS.get_new_item(ItemKey.SundewDelight),
            LOADED_ITEMS.get_new_item(ItemKey.SweetElsberryWine),
            LOADED_ITEMS.get_new_item(ItemKey.VegetableFritter),
            LOADED_ITEMS.get_new_item(ItemKey.VegetableStew),
        ], k=8)
        self._selected_item: (Item | None) = None
        self._selected_item_index: int = -1

        self._intent: (Intent | None) = None

        self._page = 0
        self._NUM_PER_PAGE = 4

        self._COST_ADJUST = 1 + random.random()

        self.show_initial_buttons()
        
    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_initial_embed(self):
        return Embed(
            title="Mysterious Merchant",
            description=(
                "Covered in a bundle of robes and cloth, two familiar eyes peer out from a gap in the odd attire. The merchant pulls forward a sack from behind them and shakes out various objects.\n\n"
                "\"You touch it, you BUY! (no refunds)\""
            )
        )

    def show_initial_buttons(self):
        self.clear_items()
        self.add_item(EnterWaresButton())
        self.add_item(ContinueButton())

    def get_embed_for_intent(self):
        if self._intent == Intent.Wares:
            return Embed(
                title="Browse Wares",
                description=(
                    "\"I have MANY THINGS!\" they say pointing to all the various things.\n\n"
                )
            )
        return self.get_initial_embed()

    def display_item_info(self):
        player: Player = self._get_player(self._group_leader.id)

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

        # Add 1 to account for low-cost items and avoid free XP/coin exploits
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
        
        player: Player = self._get_player(self._group_leader.id)
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
        self.add_item(ExitToMainButton(min(4, len(page_slots))))

    def _purchase_item(self):
        player: Player = self._get_player(self._group_leader.id)
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

    def confirm_using_intent(self):
        if self._intent == Intent.Wares:
            result = self._purchase_item()

            self._get_wares_page_buttons()

            return result
        return self.get_initial_embed()

    def next_page(self):
        self._page += 1

        self._selected_item = None
        self._selected_item_index = -1

        if self._intent == Intent.Wares:
            self._get_wares_page_buttons()

        return self.get_embed_for_intent()

    def prev_page(self):
        self._page = max(0, self._page - 1)

        self._selected_item = None
        self._selected_item_index = -1

        if self._intent == Intent.Wares:
            self._get_wares_page_buttons()

        return self.get_embed_for_intent()

    def return_to_main_menu(self):
        self._intent = None
        self._page = 0

        self._selected_item = None
        self._selected_item_index = -1

        self.show_initial_buttons()
        return self.get_initial_embed()

    def get_bot(self):
        return self._bot

    def get_users(self):
        return self._users

    def get_players(self):
        return [self._get_player(user.id) for user in self._users]

    def get_database(self):
        return self._database

    def get_guild_id(self):
        return self._guild_id
    
    def get_group_leader(self):
        return self._group_leader
    
    def get_dungeon_run(self):
        return self._dungeon_run
