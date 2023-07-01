from __future__ import annotations

import discord
import random

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.player import Player
from features.stories.dungeon_run import DungeonRun, RoomSelectionView

from typing import List


class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: TheHookView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        room_selection_view: RoomSelectionView = RoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class TouchItButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Touch It")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: TheHookView = self.view
        if interaction.user.id == view.get_group_leader().id:
            response = view.touch_it()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class TheHookView(discord.ui.View):
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
        return Embed(title="The Hook", description="A shadow suddenly comes over your party and as you look upwards, you see a shifting, dark shape and something descending closer and closer towards you all. As it approaches the ocean floor, you instantly recognize the shape -- even if the size comes as a surprise:\n\nIt’s an enormous iron hook, as though it should be attached to the fishing rod of a colossus. After a few moments, hovering about 50 feet above the sand and coral, it stops. You feel oddly compelled to reach out and touch it.")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(TouchItButton())
        self.add_item(ContinueButton())

    def touch_it(self):
        self.clear_items()
        self.add_item(ContinueButton())

        for user in self._users:
            player = self._get_player(user.id)
            player.get_dungeon_run().corruption += 2

        rooms_to_move = random.randint(1, 3)
        direction = -1 if random.random() < 0.5 else 1
        self._dungeon_run.rooms_until_boss = max(0, self._dungeon_run.rooms_until_boss + (direction * rooms_to_move))

        return Embed(title="Where Do They Go", description=f"There's a powerful force emanating from the hook that draws you closer towards it -- but just as you're about to touch it, the world begins to spin and warp as though being projected against a glass sphere. When it finally stops, your party realizes they're not where they were previously, though further back or forward along the path is difficult to say. The hook is nowhere to be seen.")

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