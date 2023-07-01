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
        
        view: BloodcoralPolypsView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        room_selection_view: RoomSelectionView = RoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class GrabSomeButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Grab Some")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: BloodcoralPolypsView = self.view
        if interaction.user.id == view.get_group_leader().id:
            response = view.grab_some()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class BloodcoralPolypsView(discord.ui.View):
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
        return Embed(title="Floating in the Water", description="In a beam of shimmering sunlight, you all spot tiny, red, floating anemone-like creatures swimming through the water -- there’s a multitude of them all moving slowly between the rocks.\n\nImmediately, you recognize these are bloodcoral polyps and definitely should be avoided. But, if you were quick, you could probably grab some to make health potions without having any latch onto you.")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(GrabSomeButton())
        self.add_item(ContinueButton())

    def grab_some(self):
        self.clear_items()
        self.add_item(ContinueButton())

        result_str: str = ""
        for user in self._users:
            player = self._get_player(user.id)
            if random.random() < 0.2:
                player.get_expertise().damage(30, player.get_dueling(), 0, True)
                result_str += f"{user.display_name} had some bloodcoral polyps attach to them and took 30 damage\n"
            else:
                item = LOADED_ITEMS.get_new_item(ItemKey.BloodcoralPolyp)
                item.add_amount(random.randint(1, 3))
                result_str += f"{user.display_name} successfully got {item.get_count()} bloodcoral polyps\n"

        return Embed(title="Into the Swarm", description=f"You all attempt to grab some bloodcoral polyps:\n\n{result_str}")

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