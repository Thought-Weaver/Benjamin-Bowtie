from __future__ import annotations

import discord

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.player import Player
from features.shared.constants import POISONED_PERCENT_HP
from features.shared.statuseffect import DexDebuff, Poisoned
from features.stories.dungeon_run import DungeonRun, RoomSelectionView

from typing import List


class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: StagnantWaterView = self.view

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
        
        view: StagnantWaterView = self.view
        if interaction.user.id == view.get_group_leader().id:
            response = view.cross_it()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class GoAroundButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Go Around")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: StagnantWaterView = self.view
        if interaction.user.id == view.get_group_leader().id:
            response = view.go_around()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class StagnantWaterView(discord.ui.View):
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
        return Embed(title="Stagnant Water", description="Here the dead grass gives way to muck and mire; before you all is a large marshland from which you can clearly see protruding bones. You could go around it, though that'd make the journey longer, or you could try wading through the bog and risk infection.")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(CrossItButton())
        self.add_item(GoAroundButton())

    def cross_it(self):
        self.clear_items()
        self.add_item(ContinueButton())

        for user in self._users:
            player = self._get_player(user.id)

            debuff = Poisoned(
                turns_remaining=5,
                value=POISONED_PERCENT_HP,
                source_str="Stagnant Water"
            )

            player.get_dueling().status_effects.append(debuff)
        
        return Embed(title="Cross It", description=f"Though you count yourselves lucky nothing finds you in this poisonous marsh, it nevertheless takes its toll on your party.")

    def go_around(self):
        self.clear_items()
        self.add_item(ContinueButton())

        self._dungeon_run.rooms_until_boss += 2

        return Embed(title="Go Around", description="The trek will be long, but it's better than risking going directly through this marsh. Your party sets off around the region and further onwards towards the heart of the forest.")

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