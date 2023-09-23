from __future__ import annotations

import discord

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.player import Player
from features.stories.dungeon_run import DungeonRun
from features.stories.underworld.combat.fungal_caverns.dense_clusters_duel import DenseClustersDuelView
from features.stories.underworld_room_selection import UnderworldRoomSelectionView

from typing import Dict, List


class DuelContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DenseClustersView = self.view
        if interaction.user.id == view.get_group_leader().id:
            duel_view: DenseClustersDuelView = DenseClustersDuelView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
            initial_info: Embed = duel_view.get_initial_embed()

            await interaction.response.edit_message(content=None, embed=initial_info, view=duel_view)


class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DenseClustersView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        room_selection_view: UnderworldRoomSelectionView = UnderworldRoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class GoAroundButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Go Around")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DenseClustersView = self.view
        view.clear_the_way[interaction.user.id] = False

        if len(view.clear_the_way) == len(view.get_users()):
            response = view.resolve()
            await interaction.response.edit_message(content=None, embed=response, view=view)
        else:
            await interaction.response.edit_message(content=None, embed=view.get_initial_embed(), view=view)


class ClearTheWayButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Clear the Way")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DenseClustersView = self.view
        view.clear_the_way[interaction.user.id] = True

        if len(view.clear_the_way) == len(view.get_users()):
            response = view.resolve()
            await interaction.response.edit_message(content=None, embed=response, view=view)
        else:
            await interaction.response.edit_message(content=None, embed=view.get_initial_embed(), view=view)


class DenseClustersView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run

        self.clear_the_way: Dict[int, bool] = {}
        
        self._display_initial_buttons()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_initial_embed(self):
        return Embed(title="Dense Clusters", description=f"The mushrooms growing from the ground and walls grow thick in this particular tunnel; while you think the right direction is forward, you'd have to clear the way through a particularly dense section of mushroom creatures. You could, however, find an alternative path, but it’d make the journey a bit longer.\n\n{len(self.clear_the_way)}/{len(self._users)} have decided on their course of action.")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(GoAroundButton())
        self.add_item(ClearTheWayButton())

    def resolve(self):
        self.clear_items()

        num_clear = sum(choice == True for choice in self.clear_the_way.values())
        result: str = ""

        if num_clear > len(self._users) // 2:
            result = "The majority decided it would be best to clear the path forward, hacking through the mushrooms to reach the other side."
            self.add_item(DuelContinueButton())
        else:
            self._dungeon_run.rooms_until_boss += 3
            result = "The majority decided to take the long way around, which will increase the length of the journey, but was definitely the safer route."
            self.add_item(ContinueButton())

        return Embed(title="A Path Forward", description=result)

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