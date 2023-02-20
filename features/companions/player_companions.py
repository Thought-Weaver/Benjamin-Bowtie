from __future__ import annotations

import discord
import random
import time

from discord.embeds import Embed
from discord.ext import commands
from strenum import StrEnum

from features.mail import Mail
from features.shared.constants import COMPANION_FEEDING_POINTS, COMPANION_NAMING_POINTS, COMPANION_PREFERRED_FOOD_BONUS_POINTS
from features.shared.enums import CompanionKey, CompanionTier
from features.shared.item import LOADED_ITEMS, Item
from features.shared.nextbutton import NextButton
from features.shared.prevbutton import PrevButton

from typing import TYPE_CHECKING, Callable, Dict, List
if TYPE_CHECKING:
    from bot import BenjaminBowtieBot
    from features.companions.companion import Companion
    from features.player import Player

# -----------------------------------------------------------------------------
# MODAL
# -----------------------------------------------------------------------------

class NamingModal(discord.ui.Modal):
    def __init__(self, database: dict, guild_id: int, user: discord.User, companion: Companion | None, view: PlayerCompanionsView, message_id: int):
        companion_name: str = companion.get_name() if companion is not None else "?"

        super().__init__(title=f"Rename {companion_name}")

        self._database = database
        self._guild_id = guild_id
        self._user = user
        self._companion = companion
        self._view = view
        self._message_id = message_id

        self._name_input: discord.ui.TextInput = discord.ui.TextInput(
            label="Name",
            default=companion_name,
            required=True
        )
        self.add_item(self._name_input)

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    async def on_submit(self, interaction: discord.Interaction):
        player: Player = self._view._get_player()

        if self._companion is None:
            embed = Embed(
                title="Companions",
                description=
                f"᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{str(self._companion)}\n\n"
                "Navigate through your companions using the Prev and Next buttons.\n\n"
                f"*Error: No companion is selected!*"
            )

            await self._view.refresh(self._message_id, embed)
            await interaction.response.defer()
            return

        new_name: str = str(self._name_input.value)

        additional_info: str = ""
        if not self._companion.custom_named:
            self._companion.add_companion_points(COMPANION_NAMING_POINTS)
            self._companion.custom_named = True
            additional_info = " and your bond is growing stronger!"

            player.get_stats().companions.bond_points_earned += COMPANION_NAMING_POINTS

        self._companion.set_name(new_name)

        player.get_stats().companions.names_given += 1

        embed = Embed(
            title="Companions",
            description=
            f"᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{str(self._companion)}\n\n"
            "Navigate through your companions using the Prev and Next buttons.\n\n"
            f"*Your companion has been renamed to {new_name}{additional_info}*"
        )

        await self._view.refresh(self._message_id, embed)
        await interaction.response.defer()

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        await interaction.response.send_message("Error: Something has gone terribly wrong.")


# -----------------------------------------------------------------------------
# COMPANIONS CLASS
# -----------------------------------------------------------------------------

class PlayerCompanions():
    def __init__(self, send_mail: Callable[[Mail], None]):
        self.companions: Dict[CompanionKey, Companion] = {}
        self.current_companion: CompanionKey | None = None

        # Used for sending objects to the player when their companion finds
        # them.
        self._send_mail = send_mail

    def tick(self):
        for key in self.companions.keys():
            self.companions[key].fed_this_tick = False

            if self.companions[key].get_tier() == CompanionTier.Best:
                # 5% chance per tick means roughly an item a day
                if random.random() < 0.05:
                    item_key = random.choice(self.companions[key].get_best_tier_items())
                    item = LOADED_ITEMS.get_new_item(item_key)
                    
                    self._send_mail(Mail(self.companions[key].get_name(), item, 0, f"{self.companions[key].get_icon_and_name()} found this and brought it to you!", str(time.time()).split(".")[0], -1))

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.companions = state.get("companions", {})
        self.current_companion = state.get("current_companion", None)

# -----------------------------------------------------------------------------
# COMPANIONS VIEW
# -----------------------------------------------------------------------------

class Intent(StrEnum):
    Companions = "Companions"
    Feed = "Feed"


class CompanionButton(discord.ui.Button):
    def __init__(self, companion: Companion, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{companion.get_name()}", row=row, emoji=companion.get_icon())
        
        self._companion = companion

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: PlayerCompanionsView = self.view
        if interaction.user == view.get_user():
            response = view.select_companion(self._companion)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ChooseButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.green, label=f"Choose", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: PlayerCompanionsView = self.view
        if interaction.user == view.get_user():
            response = view.switch_companion()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class FeedButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.blurple, label=f"Feed", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: PlayerCompanionsView = self.view
        if interaction.user == view.get_user():
            response = view.enter_feed()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class InventoryButton(discord.ui.Button):
    def __init__(self, item_index: int, item: Item, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_name_and_count()}", row=row, emoji=item.get_icon())
        
        self._item_index = item_index
        self._item = item

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: PlayerCompanionsView = self.view
        if interaction.user == view.get_user():
            response = view.select_item(self._item_index, self._item)

            await interaction.response.edit_message(content=None, embed=response, view=view)


class FeedCompanionItemButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.green, label=f"Feed", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: PlayerCompanionsView = self.view
        if interaction.user == view.get_user():
            response = view.feed_companion_item()

            await interaction.response.edit_message(content=None, embed=response, view=view)


class NameCompanionButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.blurple, label=f"Rename", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: PlayerCompanionsView = self.view
        if interaction.user == view.get_user():
            await interaction.response.send_modal(NamingModal(
                view.get_database(),
                view.get_guild_id(),
                view.get_user(),
                view._selected_companion,
                view,
                interaction.message.id)
            )


class ExitButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.red, label=f"Exit", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: PlayerCompanionsView = self.view
        if interaction.user == view.get_user():
            response = view.enter_companions()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class PlayerCompanionsView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, user: discord.User, context: commands.Context):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._user = user
        self._context = context

        self._selected_companion: Companion | None = None
        self._selected_item_index: int = -1
        self._selected_item: Item | None = None

        self._intent = Intent.Companions

        self._page = 0
        self._NUM_PER_PAGE = 4
        
        self._get_companions_page_buttons()

    def _get_player(self) -> Player:
        return self._database[str(self._guild_id)]["members"][str(self._user.id)]

    def send_talismans(self):
        player: Player = self._get_player()
        companions: PlayerCompanions = player.get_companions()

        result_str: str = ""
        for companion_key in companions.companions.keys():
            companion = companions.companions[companion_key]
            if companion.get_tier() == CompanionTier.Best and not companion.talisman_given:
                talisman = LOADED_ITEMS.get_new_item(companion.talisman)
                # This is a tad hacky, but I'd rather not duplicate the function.
                companions._send_mail(Mail(companion.get_name(), talisman, 0, f"{companion.get_icon_and_name()} has given this to you as a symbol of your incredible bond!", str(time.time()).split(".")[0], -1))
                result_str += f"{companion.get_icon_and_name()} has sent a token of your bond to your b!mailbox!\n"
                companion.talisman_given = True
        
        return result_str + "\n\n"

    def get_initial_embed(self):
        talisman_strs = self.send_talismans()

        return Embed(title="Companions", description=f"{talisman_strs}Browse your companions using the next and prev buttons.")

    def _get_companions_page_buttons(self):
        self.clear_items()
        
        player: Player = self._get_player()
        companions: PlayerCompanions = player.get_companions()
        all_slots = list(companions.companions.values())

        page_slots = all_slots[self._page * self._NUM_PER_PAGE:min(len(all_slots), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, companion in enumerate(page_slots):
            self.add_item(CompanionButton(companion, i))

        if self._page != 0:
            self.add_item(PrevButton(min(self._NUM_PER_PAGE, len(page_slots))))
        if len(all_slots) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(self._NUM_PER_PAGE, len(page_slots))))
        
        if self._selected_companion is not None:
            if companions.current_companion != self._selected_companion.get_key():
                self.add_item(ChooseButton(min(self._NUM_PER_PAGE, len(page_slots))))
            self.add_item(FeedButton(min(self._NUM_PER_PAGE, len(page_slots))))
            self.add_item(NameCompanionButton(min(self._NUM_PER_PAGE, len(page_slots))))

    def _display_companion_info(self):
        if self._selected_companion is None:
            self._get_companions_page_buttons()
            
            return Embed(
                title="Companions",
                description=(
                    "Navigate through your companions using the Prev and Next buttons.\n\n"
                    "*Error: Something about that companion changed or it's no longer available.*"
                )
            )

        return Embed(
            title="Companions",
            description=(
                f"᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{str(self._selected_companion)}\n\n"
                "Navigate through your companions using the Prev and Next buttons."
            )
        )

    def enter_companions(self):
        self._intent = Intent.Companions

        self._page = 0
        self._selected_item = None
        self._selected_item_index = -1

        self._get_companions_page_buttons()

        talisman_strs = self.send_talismans()

        return Embed(
            title="Companions",
            description=(
                f"᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{str(self._selected_companion)}\n\n"
                f"{talisman_strs}Navigate through your companions using the Prev and Next buttons."
            )
        )

    def select_companion(self, companion: Companion):
        self._selected_companion = companion

        self._get_companions_page_buttons()
        return self._display_companion_info()

    def switch_companion(self):
        player: Player = self._get_player()
        companions: PlayerCompanions = player.get_companions()

        message: str = ""
        if self._selected_companion is not None:
            companion_key = self._selected_companion.get_key()
            companions.current_companion = companion_key

            self._get_companions_page_buttons()
            message = f"*Switched your companion to {self._selected_companion.get_icon_and_name()}!*"
        else:
            message = f"*Error: There's no companion currently selected!*"

        return Embed(
            title="Companions",
            description=(
                f"᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{str(self._selected_companion)}\n\n"
                "Navigate through your companions using the Prev and Next buttons.\n\n"
                f"{message}"
            )
        )

    def _get_inventory_buttons(self):
        self.clear_items()
        player: Player = self._get_player()
        inventory = player.get_inventory()
        inventory_slots = player.get_inventory().get_inventory_slots()

        if self._selected_companion is not None:
            filtered_indices = inventory.filter_inventory_slots(self._selected_companion.valid_food_categories)
            filtered_items = [inventory_slots[i] for i in filtered_indices]

            page_slots = filtered_items[self._page * self._NUM_PER_PAGE:min(len(filtered_items), (self._page + 1) * self._NUM_PER_PAGE)]
            for i, item in enumerate(page_slots):
                exact_item_index: int = filtered_indices[i + (self._page * self._NUM_PER_PAGE)]
                self.add_item(InventoryButton(exact_item_index, item, i))
            if self._page != 0:
                self.add_item(PrevButton(min(self._NUM_PER_PAGE, len(page_slots))))
            if len(filtered_items) - self._NUM_PER_PAGE * (self._page + 1) > 0:
                self.add_item(NextButton(min(self._NUM_PER_PAGE, len(page_slots))))

            if self._selected_item is not None and self._selected_item_index != -1:
                self.add_item(FeedCompanionItemButton(min(self._NUM_PER_PAGE, len(page_slots))))
            
            self.add_item(ExitButton(min(self._NUM_PER_PAGE, len(page_slots))))

    def enter_feed(self):
        self._intent = Intent.Feed

        self._page = 0

        self._get_inventory_buttons()
        return Embed(
            title="Feed Item",
            description=(
                "Navigate through your items using the Prev and Next buttons."
            )
        )

    def _display_item_info(self):
        player: Player = self._get_player()
        inventory_slots: List[Item] = player.get_inventory().get_inventory_slots()

        if self._selected_item is None or inventory_slots[self._selected_item_index] != self._selected_item:
            self._get_companions_page_buttons()
            
            return Embed(
                title="Feed Item",
                description=(
                    "Navigate through your items using the Prev and Next buttons.\n\n"
                    "*Error: Something about that item changed or it's no longer available.*"
                )
            )

        return Embed(
            title="Feed Item",
            description=(
                f"᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{str(self._selected_item)}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\n"
                "Navigate through your items using the Prev and Next buttons."
            )
        )

    def select_item(self, item_index: int, item: Item):
        self._selected_item_index = item_index
        self._selected_item = item

        self._get_inventory_buttons()
        return self._display_item_info()

    def feed_companion_item(self):
        player: Player = self._get_player()
        inventory = player.get_inventory()
        inventory_slots: List[Item] = inventory.get_inventory_slots()

        if self._selected_item is None or inventory_slots[self._selected_item_index] != self._selected_item or self._selected_companion is None:
            self._get_inventory_buttons()
            
            return Embed(
                title="Feed Item",
                description=(
                    "Navigate through your items using the Prev and Next buttons.\n\n"
                    "*Error: Something about that companion or item changed or they're no longer available.*"
                )
            )

        if self._selected_companion.fed_this_tick:
            self._selected_item = None
            self._selected_item_index = -1

            return Embed(
                title="Feed Item",
                description=(
                    "Navigate through your items using the Prev and Next buttons.\n\n"
                    "*Your companion has already been fed this hour!*"
                )
            )

        removed_item = inventory.remove_item(self._selected_item_index, 1)
        if removed_item is None:
            return Embed(
                title="Feed Item",
                description=(
                    "Navigate through your items using the Prev and Next buttons.\n\n"
                    "*Error: Something about that item changed or it's no longer available.*"
                )
            )

        if self._selected_companion.fed_this_tick:
            return Embed(
                title="Feed Item",
                description=(
                    "Navigate through your items using the Prev and Next buttons.\n\n"
                    "*Your companion has already been fed this hour!*"
                )
            )

        companion_points: int = COMPANION_FEEDING_POINTS
        message: str = f"Your companion eats the {self._selected_item.get_full_name()} and your bond grows stronger."
        if removed_item.get_key() in self._selected_companion.preferred_foods and self._selected_companion.get_tier() == CompanionTier.Good:
            companion_points += COMPANION_PREFERRED_FOOD_BONUS_POINTS
            message += " They love it!"
        self._selected_companion.add_companion_points(companion_points)
        self._selected_companion.fed_this_tick = True

        player.get_stats().companions.bond_points_earned += companion_points
        player.get_stats().companions.items_fed += 1

        self._selected_item = None
        self._selected_item_index = -1

        return Embed(
            title="Feed Item",
            description=(
                "Navigate through your items using the Prev and Next buttons.\n\n"
                f"*{message}*"
            )
        )

    def next_page(self):
        self._page += 1
        if self._intent == Intent.Companions:
            self._selected_companion = None
            self._get_companions_page_buttons()
            return Embed(title="Companions", description="Navigate through your companions using the Prev and Next buttons.")
        elif self._intent == Intent.Feed:
            self._selected_item = None
            self._selected_item_index = -1
            self._get_inventory_buttons()
            return Embed(title="Feed Item", description="Navigate through your items using the Prev and Next buttons.")
        return Embed(title="Unknown")

    def prev_page(self):
        self._page = max(0, self._page - 1)
        if self._intent == Intent.Companions:
            self._selected_companion = None
            self._get_companions_page_buttons()
            return Embed(title="Companions", description="Navigate through your companions using the Prev and Next buttons.")
        elif self._intent == Intent.Feed:
            self._selected_item = None
            self._selected_item_index = -1
            self._get_inventory_buttons()
            return Embed(title="Feed Item", description="Navigate through your items using the Prev and Next buttons.")
        return Embed(title="Unknown")

    async def refresh(self, message_id: int, embed: Embed):
        self._get_companions_page_buttons()
        message: discord.Message = await self._context.fetch_message(message_id)
        await message.edit(view=self, embed=embed)

    def get_bot(self):
        return self._bot

    def get_user(self):
        return self._user

    def get_database(self):
        return self._database

    def get_guild_id(self):
        return self._guild_id

    def get_context(self):
        return self._context
