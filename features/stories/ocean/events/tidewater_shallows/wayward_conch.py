from __future__ import annotations

import discord
import random

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.player import Player
from features.shared.item import LOADED_ITEMS, ItemKey
from features.stories.dungeon_run import DungeonRun, RoomSelectionView

from typing import List


class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: WaywardConchView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        room_selection_view: RoomSelectionView = RoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class TakeConchButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Take Conch")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: WaywardConchView = self.view
        if interaction.user.id == view.get_group_leader().id:
            response = view.take_conch()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ResistButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Resist")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: WaywardConchView = self.view
        if interaction.user.id == view.get_group_leader().id:
            response = view.resist()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class WaywardConchView(discord.ui.View):
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

    def get_initial_embed(self):
        return Embed(title="A Wayward Conch", description="Poking out of the sand in an otherwise empty region of the shallows, you all suddenly come across a shimmering conch. But as you take a closer look, something -- perhaps the almost shifting pattern on its surface -- seems… wrong.\n\nYou could go closer and try to take the conch with you, or you could try to resist its allure and move past deeper into the shallows.")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(TakeConchButton())
        self.add_item(ResistButton())

    def take_conch(self):
        self.clear_items()
        self.add_item(ContinueButton())

        item = LOADED_ITEMS.get_new_item(ItemKey.ConchMaybe)
        player = self._get_player(self._group_leader.id)
        player.get_inventory().add_item(item)

        player.get_dungeon_run().corruption += 2

        return Embed(title="Take It", description=f"You step towards the conch, hearing something almost musical coming from it. The conch wants you to take it. And so you do.\n\n{self._group_leader.display_name} received {item.get_full_name()}")

    def resist(self):
        self.clear_items()
        self.add_item(ContinueButton())

        player = self._get_player(self._group_leader.id)
        resists: bool = random.random() < 0.05 * player.get_dungeon_run().corruption

        if not resists:
            return self.take_conch()
        else:
            return Embed(title="Leave It", description=f"You begin to take a step towards the conch, but think better of it, shaking off whatever mesmerizing effect it was attempting to use on you. Your party continues through the shallows, the conch left behind.")

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