from __future__ import annotations

import discord

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.player import Player
from features.shared.statuseffect import ConBuff, DmgVulnerability, TurnSkipChance
from features.stories.dungeon_run import DungeonRun, RoomSelectionView

from typing import List

class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: PetrifyingPlantView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        room_selection_view: RoomSelectionView = RoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class PickPlantButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Pick Plant")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: PetrifyingPlantView = self.view
        if interaction.user.id == view.get_group_leader().id:
            response = view.pick_flower()

            await interaction.response.edit_message(embed=response, view=view, content=None)


class PetrifyingPlantView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run

        self.rests_taken: int = 0
        
        self._display_initial_buttons()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_initial_embed(self):
        return Embed(title="Curious Plant", description=f"")

    def pick_flower(self):
        self.clear_items()
        self.add_item(ContinueButton())

        group_leader_player = self._get_player(self._group_leader.id)
        dodged = group_leader_player.get_expertise().dexterity > 20

        for user in self._users:
            if user != self._group_leader:
                player = self._get_player(user.id)

                buff = ConBuff(
                    turns_remaining=20,
                    value=5,
                    source_str="Petrifying Plant"
                )

                player.get_dueling().status_effects += [buff]

        group_leader_result_str: str = "Luckily, your group leader managed to dodge out of the way with their quick reflexes -- suspecting in close proximity its effect would be significantly worse."
        if not dodged:
            debuff = TurnSkipChance(
                turns_remaining=20,
                value=1,
                source_str="Petrifying Plant"
            )

            group_leader_player.get_dueling().status_effects += [debuff]
            
            group_leader_result_str = "Unfortunately, your group leader wasn't dextrous enough and got caught in the epicenter of the blast -- you see them now temporarily petrified still holding the flower in their hand."

        return Embed(title="A Grey Mist Released", description=f"As your party leader grasps the plant and pulls it from the ground, it suddenly explodes in a grey mist that suffuses everyone. As it clears, everyone else feels somewhat bolstered. {group_leader_result_str}")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(PickPlantButton())
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