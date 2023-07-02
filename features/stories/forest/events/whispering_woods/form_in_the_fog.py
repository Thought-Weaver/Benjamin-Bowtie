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
        
        view: FormInTheFogView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        room_selection_view: ForestRoomSelectionView = ForestRoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class ChaosFromCoinButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Chaos from Coin")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: FormInTheFogView = self.view
        if interaction.user.id == view.get_group_leader().id:
            response = view.chaos_from_coin()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ChaosFromBloodButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Chaos from Blood")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: FormInTheFogView = self.view
        if interaction.user.id == view.get_group_leader().id:
            response = view.chaos_from_blood()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class FormInTheFogView(discord.ui.View):
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

    def chaos_from_coin(self):
        self.clear_items()
        self.add_item(ContinueButton())

        self._dungeon_run.num_mystery_without_treasure = -100

        return Embed(title="Chaos from Coin", description="\"The price is paid,\" it says, snapping its fingers and vanishing. The fog begins to lift, and your party finds itself free to continue their adventure.")

    def chaos_from_blood(self):
        self.clear_items()
        self.add_item(ContinueButton())

        self._dungeon_run.num_mystery_without_shopkeep = -100

        return Embed(title="Chaos from Blood", description="\"The price is paid,\" it says, a scream echoing in the distance as soon as it vanishes. The fog begins to lift, and your party finds itself free to continue their adventure.")

    def get_initial_embed(self):
        return Embed(title="The Form in the Fog", description="Walking further along the path, you find yourselves venturing into a deep fog. You can barely see the details past your own hand, but suddenly from along the path, a shadow steps towards you, its hands outstretched to either side.\n\n\"I would offer you a bargain, travellers,\" it says, \"A choice, if you wish, from coin or blood. Take the former and I shall see the mysteries ahead of you devoid of treasure, but filled with chaotic events, grand battles, and friendly faces. Choose the latter, and I shall exact the price from one who would otherwise furnish you with goods, replacing their position in the mysteries ahead instead with possibilities for treasure, combat, and unknown events.\"")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(ChaosFromBloodButton())
        self.add_item(ChaosFromCoinButton())
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