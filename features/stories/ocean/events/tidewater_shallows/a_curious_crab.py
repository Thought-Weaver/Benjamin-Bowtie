from __future__ import annotations

import discord

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.player import Player
from features.stories.dungeon_run import DungeonRun, RoomSelectionView
from features.stories.ocean.combat.tidewater_shallows.crab_king_duel import CrabKingDuelView

from typing import List

class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: ACuriousCrabView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        room_selection_view: RoomSelectionView = RoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)

class ApproachButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Approach")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: ACuriousCrabView = self.view
        if interaction.user.id == view.get_group_leader().id:
            duel_room = CrabKingDuelView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
            initial_info: Embed = duel_room.get_initial_embed()

            await interaction.response.edit_message(embed=initial_info, view=duel_room, content=None)


class ACuriousCrabView(discord.ui.View):
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
        return Embed(title="A Curious Crab", description=f"Atop a tiny sand dune, it's almost impossible not to notice a little, dancing crab. It seems very excited to see other people in an otherwise empty area of the continental shelf! Nothing other than its motions seem to mark it as unordinary; it has a red carapace, two beady eyes popping up from the top of its head, and little pincers waving about.\n\nYou could get closer, perhaps try to determine what it wants, or you could leave it be.")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(ApproachButton())
        self.add_item(ContinueButton())

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