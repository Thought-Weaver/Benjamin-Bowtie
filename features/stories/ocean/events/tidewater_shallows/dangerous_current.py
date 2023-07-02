from __future__ import annotations

import discord

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.player import Player
from features.stories.dungeon_run import DungeonRun
from features.stories.ocean_room_selection import OceanRoomSelectionView

from typing import List


class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DangerousCurrentView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        room_selection_view: OceanRoomSelectionView = OceanRoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class EnterCurrentButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Enter Current")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DangerousCurrentView = self.view
        if interaction.user.id == view.get_group_leader().id:
            response = view.enter_current()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class DangerousCurrentView(discord.ui.View):
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
        return Embed(title="Dangerous Current", description="Though most of the ocean in this region has been calm, something catches your attention: It's almost as though a wind is rushing through the water, dragging bits of kelp and fish unlucky enough to be caught in it further across the ocean floor.\n\nBut, dangerous though it seems, this could be to your advantage: Were you to take this current, you'd almost certainly suffer some damage, but you'd be much closer to your goal.")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(EnterCurrentButton())
        self.add_item(ContinueButton())

    def enter_current(self):
        self.clear_items()
        self.add_item(ContinueButton())

        damage_str: str = ""
        for user in self._users:
            player = self._get_player(user.id)
            damage: int = int(player.get_expertise().max_hp * 0.2)

            player.get_expertise().damage(damage, player.get_dueling(), 0, True)

            damage_str += f"{user.display_name} took {damage} damage\n\n"

        self._dungeon_run.rooms_until_boss = max(0, self._dungeon_run.rooms_until_boss - 3)

        return Embed(title="Into the Current", description=f"You all enter the raging current and, in an instant, are dragged along through the water -- the undersea landscape flying by as your body is tossed around. Just as you're certain the tumbling will cause you to go unconscious, it begins to slow and you're deposited somewhere further along in the shallows.\n\n{damage_str}")

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