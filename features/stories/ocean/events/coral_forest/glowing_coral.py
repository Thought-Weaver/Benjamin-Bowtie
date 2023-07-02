from __future__ import annotations

import discord
import random

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.player import Player
from features.stories.dungeon_run import DungeonRun
from features.stories.ocean_room_selection import OceanRoomSelectionView

from typing import List, Set


class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: GlowingCoralView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        room_selection_view: OceanRoomSelectionView = OceanRoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class PurpleButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Purple")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: GlowingCoralView = self.view
        if interaction.user.id not in view.players_decided:
            response = view.touch_purple(interaction.user.id, interaction.user.display_name)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class RedButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Red")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: GlowingCoralView = self.view
        if interaction.user.id not in view.players_decided:
            response = view.touch_red(interaction.user.id, interaction.user.display_name)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ResistButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Resist")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: GlowingCoralView = self.view
        if interaction.user.id not in view.players_decided:
            response = view.resist(interaction.user.id, interaction.user.display_name)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class GlowingCoralView(discord.ui.View):
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
        return Embed(title="Glowing Coral", description=f"Among the various colored corals of this forest, you find a particularly odd one nestled in a small cavernous opening. The coral itself is flat and white, but across its form run lines of dark red and purple, separated across its two halves. You each feel an odd inclination to touch it.\n\n{len(self.players_decided)}/{len(self._users)} have made a choice")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(RedButton())
        self.add_item(PurpleButton())
        self.add_item(ResistButton())

    def touch_purple(self, user_id: int, name: str):
        player = self._get_player(user_id)
        player.get_expertise().restore_mana(int(player.get_expertise().max_mana * 0.25))
        player.get_dungeon_run().corruption += 2

        self.result_str += f"{name} touched the purple section of the coral and replenished 25% of their mana\n"
        self.players_decided.add(user_id)

        if len(self.players_decided) == len(self._users):
            self.clear_items()
            self.add_item(ContinueButton())

            return Embed(title="Coursing Power", description=f"The strange coral reached out to each of you...\n\n{self.result_str}")
        else:
            return self.get_initial_embed()

    def touch_red(self, user_id: int, name: str):
        player = self._get_player(user_id)
        player.get_expertise().heal(int(player.get_expertise().max_hp * 0.25))
        player.get_dungeon_run().corruption += 2

        self.result_str += f"{name} touched the red section of the coral and replenished 25% of their health\n"
        self.players_decided.add(user_id)

        if len(self.players_decided) == len(self._users):
            self.clear_items()
            self.add_item(ContinueButton())
            
            return Embed(title="Coursing Power", description=f"The strange coral reached out to each of you...\n\n{self.result_str}")
        else:
            return self.get_initial_embed()

    def resist(self, user_id: int, name: str):
        player = self._get_player(user_id)
        resists: bool = random.random() < 0.05 * player.get_dungeon_run().corruption

        if not resists:
            if random.random() < 0.5:
                return self.touch_red(user_id, name)
            else:
                return self.touch_purple(user_id, name)
        else:
            self.result_str += f"{name} resisted the influence of the glowing coral\n"
            self.players_decided.add(user_id)

            if len(self.players_decided) == len(self._users):
                self.clear_items()
                self.add_item(ContinueButton())
            
                return Embed(title="Coursing Power", description=f"The strange coral reached out to each of you...\n\n{self.result_str}")
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