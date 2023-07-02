from __future__ import annotations

import discord
import random

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.player import Player
from features.shared.statuseffect import ConBuff, DexBuff, IntBuff, LckBuff, StrBuff
from features.stories.dungeon_run import DungeonRun
from features.stories.ocean_room_selection import OceanRoomSelectionView

from typing import List


class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: StrangeEffigyView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        room_selection_view: OceanRoomSelectionView = OceanRoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class ApproachButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Approach")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: StrangeEffigyView = self.view
        if interaction.user.id == view.get_group_leader().id:
            response = view.approach()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ResistButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Resist")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: StrangeEffigyView = self.view
        if interaction.user.id == view.get_group_leader().id:
            response = view.resist()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class StrangeEffigyView(discord.ui.View):
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
        return Embed(title="Strange Effigy", description="At first, you thought the object before you was just an oddly shaped rock, but as you approach closer, you realize it's something constructed: A curious homunculus with tendrils rests nestled in the sand, formed of kelp, conches, bone, and sand.\n\nYou get a sense of power from it, perhaps something that would be a boon for all of you in the trials ahead.")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(ApproachButton())
        self.add_item(ResistButton())

    def approach(self):
        self.clear_items()
        self.add_item(ContinueButton())

        for user in self._users:
            player = self._get_player(user.id)

            buffs = [
                ConBuff(-1, 5, "Strange Effigy"),
                StrBuff(-1, 5, "Strange Effigy"),
                DexBuff(-1, 5, "Strange Effigy"),
                IntBuff(-1, 5, "Strange Effigy"),
                LckBuff(-1, 5, "Strange Effigy")
            ]

            player.get_dueling().status_effects += buffs
            player.get_dungeon_run().corruption += 3

        return Embed(title="You'll Be Better", description=f"You move towards the strange effigy and a darkness seems to creep around all of you, something that almost wants to... taste you. It recedes, however, and you all find yourselves feeling empowered with whatever it left behind.")

    def resist(self):
        self.clear_items()
        self.add_item(ContinueButton())

        player = self._get_player(self._group_leader.id)
        resists: bool = random.random() < 0.05 * player.get_dungeon_run().corruption

        if not resists:
            return self.approach()
        else:
            return Embed(title="Don't Leave", description=f"Deciding it's better left where it lays, you ignore the sensation and continue through the darkness of the abyss.")

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