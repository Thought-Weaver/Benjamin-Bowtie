from __future__ import annotations

import discord

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.player import Player
from features.stories.dungeon_run import DungeonRun
from features.stories.forest_room_selection import ForestRoomSelectionView

from typing import List


class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: UnnamedGraveView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        room_selection_view: ForestRoomSelectionView = ForestRoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class PayRespectsButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Pay Respects")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: UnnamedGraveView = self.view
        if interaction.user.id == view.get_group_leader().id:
            response = view.pay_respects()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class UnnamedGraveView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run
        
        self._display_initial_buttons()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def pay_respects(self):
        self.clear_items()
        self.add_item(ContinueButton())

        self._dungeon_run.num_mystery_without_treasure *= 2
        self._dungeon_run.num_mystery_without_combat = 0

        return Embed(title="Pay Respects", description="You decide to pay your respects to whoever it was that perished here and was marked with the honorific. A wind stirs in the trees and you sense of peaceful repose guide you forward.")

    def get_initial_embed(self):
        return Embed(title="An Unnamed Grave", description="Along the path, you all encounter a grave marked in the traditional way with a bough of veylock wrapped in twine around a tree branch. You could pay respects to the unknown soul if you wished, or you could continue on your way.")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(PayRespectsButton())
        self.add_item(ContinueButton())

    def any_in_duels_currently(self):
        return any(self._get_player(user.id).get_dueling().is_in_combat for user in self._users)

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