from __future__ import annotations

import discord

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.player import Player
from features.shared.statuseffect import ConDebuff, DexBuff, DmgBuff, DmgVulnerability, IntBuff, StrBuff
from features.stories.dungeon_run import DungeonRun
from features.stories.underworld_room_selection import UnderworldRoomSelectionView

from typing import List, Set


class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: CrackInTheWallView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        room_selection_view: UnderworldRoomSelectionView = UnderworldRoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class PeekInButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Peek In")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: CrackInTheWallView = self.view
        if interaction.user.id not in view.players_decided:
            response = view.peek_in(interaction.user.id, interaction.user.display_name)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ListenButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Listen")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: CrackInTheWallView = self.view
        if interaction.user.id not in view.players_decided:
            response = view.listen(interaction.user.id, interaction.user.display_name)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class DoNothingButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Do Nothing")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: CrackInTheWallView = self.view
        if interaction.user.id not in view.players_decided:
            response = view.do_nothing(interaction.user.id, interaction.user.display_name)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class CrackInTheWallView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run

        self.players_decided: Set[int] = set()
        self.result_str: str = ""
        
        self._display_initial_buttons()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_initial_embed(self):
        return Embed(title="Crack in the Wall", description=f"Along the corridor wall, a bit of unexpected light catches your attention. From a crack along the wall -- no more than a few hands’ width large -- something like torchlight appears to be seeping out. The shadows cast against the opposite wall in a way not unlike a person pacing in front of the flame.\n\n{len(self.players_decided)}/{len(self._users)} have made a choice")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(PeekInButton())
        self.add_item(ListenButton())
        self.add_item(DoNothingButton())

    def peek_in(self, user_id: int, name: str):
        player = self._get_player(user_id)

        str_buff = StrBuff(
            turns_remaining=15,
            value=10,
            source_str="Crack in the Wall"
        )

        dex_buff = DexBuff(
            turns_remaining=15,
            value=10,
            source_str="Crack in the Wall"
        )

        int_buff = IntBuff(
            turns_remaining=15,
            value=10,
            source_str="Crack in the Wall"
        )

        con_debuff = ConDebuff(
            turns_remaining=15,
            value=-10,
            source_str="Crack in the Wall"
        )

        player.get_dueling().status_effects += [str_buff, dex_buff, int_buff, con_debuff]

        self.result_str += f"{name} peeked in and something they saw haunts them, granting +10 Str, Dex, and Int, but -10 Con for the next duel\n"
        self.players_decided.add(user_id)

        if len(self.players_decided) == len(self._users):
            self.clear_items()
            self.add_item(ContinueButton())

            return Embed(title="Something Strange", description=f"The shadows danced and whispers beckoned...\n\n{self.result_str}")
        else:
            return self.get_initial_embed()

    def listen(self, user_id: int, name: str):
        player = self._get_player(user_id)

        dmg_buff = DmgBuff(
            turns_remaining=15,
            value=0.25,
            source_str="Crack in the Wall"
        )

        dmg_vuln = DmgVulnerability(
            turns_remaining=15,
            value=0.25,
            source_str="Crack in the Wall"
        )

        player.get_dueling().status_effects += [dmg_buff, dmg_vuln]

        self.result_str += f"{name} listened and something they heard haunts them, granting +25% damage dealt but also causing a 25% damage vulnerability for the next duel\n"
        self.players_decided.add(user_id)

        if len(self.players_decided) == len(self._users):
            self.clear_items()
            self.add_item(ContinueButton())
            
            return Embed(title="Something Strange", description=f"The shadows danced and whispers beckoned...\n\n{self.result_str}")
        else:
            return self.get_initial_embed()

    def do_nothing(self, user_id: int, name: str):
        self.result_str += f"{name} chose to do nothing\n"
        self.players_decided.add(user_id)

        if len(self.players_decided) == len(self._users):
            self.clear_items()
            self.add_item(ContinueButton())
        
            return Embed(title="Something Strange", description=f"The shadows danced and whispers beckoned...\n\n{self.result_str}")
        else:
            return self.get_initial_embed()

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