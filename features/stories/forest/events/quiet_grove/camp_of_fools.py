from __future__ import annotations

import discord

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.player import Player
from features.shared.statuseffect import DmgBuff
from features.stories.dungeon_run import DungeonRun, RoomSelectionView

from typing import List

class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: CampOfFoolsView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        room_selection_view: RoomSelectionView = RoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class JoinThemButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Join Them")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: CampOfFoolsView = self.view
        if interaction.user.id != view.get_group_leader().id:
            response = view.join_them()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class CampOfFoolsView(discord.ui.View):
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
        return Embed(title="A Merry Band of Fools", description="Somewhere off the path, you heard a joyful jig being played on the lute and boisterous voices singing loud. It seems to be a travelling troupe making their way through the woods! Perhaps, if you wanted, they'd let you join them for the night.")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(JoinThemButton())
        self.add_item(ContinueButton())

    def join_them(self):
        self.clear_items()
        self.add_item(ContinueButton())

        for user in self._users:
            buff = DmgBuff(
                turns_remaining=10,
                value=0.25,
                source_str="A Merry Band of Fools"
            )

            player = self._get_player(user.id)
            
            player.get_dueling().status_effects.append(buff)
        
            coins_to_take: int = min(50, player.get_inventory().get_coins())
            player.get_inventory().remove_coins(coins_to_take)

        return Embed(title="A Grand Feast", description="You meander over to their camp and find yourselves indeed welcomed with open arms. There's drinking, dancing, and general carousing to be had throughout the night increasing your spirits. As dawn strikes the next day, you all awaken to find the troupe gone -- and your pockets now short 50 coin.")

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