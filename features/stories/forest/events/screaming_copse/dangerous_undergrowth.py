from __future__ import annotations

import discord

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.player import Player
from features.shared.statuseffect import DexDebuff
from features.stories.dungeon_run import DungeonRun, RoomSelectionView

from typing import List


class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DangerousUndergrowthView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        room_selection_view: RoomSelectionView = RoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class CrossItButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Cross It")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DangerousUndergrowthView = self.view
        if interaction.user.id == view.get_group_leader().id:
            response = view.cross_it()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ClimbButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Climb")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DangerousUndergrowthView = self.view
        if interaction.user.id == view.get_group_leader().id:
            response = view.climb()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class DangerousUndergrowthView(discord.ui.View):
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
        return Embed(title="Dangerous Undergrowth", description="Along what remains of the path, the dry grass turns to thorny brush spreading out over a large portion of the landscape towards the center of the Screaming Copse.\n\nYou could cross through the painful bramble or possibly climb the dead trees above it, though the latter option would slow your party down for a time:")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(CrossItButton())
        self.add_item(ClimbButton())

    def cross_it(self):
        self.clear_items()
        self.add_item(ContinueButton())

        damage: int = 15
        for user in self._users:
            player = self._get_player(user.id)
            player.get_expertise().damage(damage, player.get_dueling(), 0, True)

        return Embed(title="Cross It", description=f"You all decide to push onwards, bracing the thorns as best you can, but still each take {damage} damage in the process.")

    def climb(self):
        self.clear_items()
        self.add_item(ContinueButton())

        for user in self._users:
            player = self._get_player(user.id)

            debuff = DexDebuff(
                turns_remaining=20,
                value=-15,
                source_str="Dangerous Undergrowth"
            )

            player.get_dueling().status_effects.append(debuff)

        return Embed(title="Climb", description="Rather than risk the damage, you all slowly start to climb the trees and make your way carefully across the cracking, undead branches. The process is laborious and difficult; you all have your Dexterity reduced for the next combat encounter.")

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