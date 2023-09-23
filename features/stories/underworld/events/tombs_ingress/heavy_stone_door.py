from __future__ import annotations

import discord
import random

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.stories.underworld.treasure.hidden_room_treasure import HiddenRoomTreasureRoomView
from features.stories.underworld_room_selection import UnderworldRoomSelectionView
from features.player import Player
from features.shared.nextbutton import NextButton
from features.shared.prevbutton import PrevButton
from features.stories.dungeon_run import DungeonRun
from enum import StrEnum

from typing import List

class Intent(StrEnum):
    Choose = "Choose"


class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: HeavyStoneDoorView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        room_selection_view = UnderworldRoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class EnterChooseButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Choose")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: HeavyStoneDoorView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the duel.")
            return

        if view.get_group_leader().id == interaction.user.id:
            response = view.enter_choose()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class SelectPlayerButton(discord.ui.Button):
    def __init__(self, user_id: int, name: str, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=name, row=row)
        
        self._user_id = user_id
        self._name = name

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: HeavyStoneDoorView = self.view
        if view.get_group_leader().id == interaction.user.id:
            response = view.select(self._user_id, self._name)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ConfirmButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.green, label="Confirm", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: HeavyStoneDoorView = self.view
        selected_id: int | None = view._selected_id
        if view.get_group_leader().id == interaction.user.id and selected_id is not None:
            response = view.confirm()
            if response is None:
                await interaction.response.edit_message(content=None, embed=view.get_initial_embed(), view=view)
            else:
                if response == True:
                    treasure_room = HiddenRoomTreasureRoomView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
                    await interaction.response.edit_message(content=None, embed=treasure_room.get_initial_embed(), view=treasure_room)
                else:
                    result = view.get_embed_for_failure()
                    await interaction.response.edit_message(content=None, embed=result, view=view)


class ExitButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.red, label="Exit", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: HeavyStoneDoorView = self.view
        if view.get_group_leader() == interaction.user:
            embed = view.exit_to_main_menu()
            await interaction.response.edit_message(content=None, embed=embed, view=view)


class HeavyStoneDoorView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run

        self._intent: Intent | None = None
        self._selected_id: int | None = None

        self._page = 0
        self._NUM_PER_PAGE = 4

        self._CHANCE_PER_STR_TO_SUCCEED = 0.01

        self._display_initial_buttons()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_initial_embed(self):
        return Embed(title="A Heavy Door", description="Moving through the streets of this ancient city, you pass by a particularly large and ornate door. It looks to be a single slab of stone and though you give it a push to see what's inside, it doesn't budge in the slightest. Perhaps the strongest among you could attempt this by pushing themselves?")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(EnterChooseButton())
        self.add_item(ContinueButton())

    def any_in_duels_currently(self):
        return any(self._get_player(user.id).get_dueling().is_in_combat for user in self._users)

    def enter_choose(self):
        self._intent = Intent.Choose
        self._get_buttons()
        return self.get_embed_for_intent()

    def _get_buttons(self):
        self.clear_items()

        page_slots = self._users[self._page * self._NUM_PER_PAGE:min(len(self._users), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, user in enumerate(page_slots):
            self.add_item(SelectPlayerButton(user.id, user.display_name, i))
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(self._users) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        if self._selected_id is not None:
            self.add_item(ConfirmButton(min(4, len(page_slots))))
        self.add_item(ExitButton(min(4, len(page_slots))))

    def select(self, user_id: int, name: str):
        self._selected_id = user_id

        self._get_buttons()

        player: Player = self._get_player(user_id)
        chance_success: int = int(100 * self._CHANCE_PER_STR_TO_SUCCEED * player.get_combined_attributes().strength)

        return Embed(title="Choose a Player", description=f"You are currently selecting {name} to open the door. They have a {chance_success}% chance of success.\n\nNavigate through your party using the Prev and Next buttons.")

    def confirm(self):
        if self._selected_id is not None:
            player: Player = self._get_player(self._selected_id)
            chance_success: float = 100 * self._CHANCE_PER_STR_TO_SUCCEED * player.get_combined_attributes().strength
            return random.random() < chance_success
        else:
            self._display_initial_buttons()
            return None

    def get_embed_for_intent(self, error: str=""):
        if self._intent == Intent.Choose:
            return Embed(
                title="Choose a Player",
                description=(
                    "Choose a player from your party.\n\nNavigate through your party using the Prev and Next buttons."
                    f"{error}"
                )
            )
        return self.get_initial_embed()

    def get_embed_for_failure(self):
        self.clear_items()
        self.add_item(ContinueButton())
        
        return Embed(title="Not An Inch", description="Despite your best efforts, the door remains steadfast, unwilling to budge and let you explore whatever may be inside.")

    def next_page(self):
        self._page += 1

        if self._intent == Intent.Choose:
            self._selected_id = None
            self._get_buttons()

        return self.get_embed_for_intent()

    def prev_page(self):
        self._page = max(0, self._page - 1)

        if self._intent == Intent.Choose:
            self._selected_id = None
            self._get_buttons()

        return self.get_embed_for_intent()

    def exit_to_main_menu(self):
        self._intent = None
        self._display_initial_buttons()
        return self.get_initial_embed()

    def get_bot(self):
        return self._bot

    def get_users(self):
        return self._users

    def get_database(self):
        return self._database

    def get_guild_id(self):
        return self._guild_id

    def get_group_leader(self):
        return self._group_leader

    def get_dungeon_run(self):
        return self._dungeon_run
    
    def get_players(self):
        return [self._get_player(user.id) for user in self._users]
