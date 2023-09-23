from __future__ import annotations

import discord
import random

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.player import Player
from features.shared.ability import TIMEWEAVING_ABILITIES, Ability
from features.stories.dungeon_run import DungeonRun
from features.stories.underworld_room_selection import UnderworldRoomSelectionView

from typing import List, Set

class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: EchoOfKnowledgeView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        room_selection_view: UnderworldRoomSelectionView = UnderworldRoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class InvestigateButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Investigate")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: EchoOfKnowledgeView = self.view
        if interaction.user not in view.investigated_users:
            mail_message = view.investigate(interaction.user)
            
            await interaction.response.edit_message(content=None, embed=view.get_initial_embed(), view=view)
            await interaction.user.send(mail_message)
            

class EchoOfKnowledgeView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run

        self.investigated_users: Set[discord.User] = set()
        
        self._display_initial_buttons()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_initial_embed(self):
        return Embed(title="Echo of Knowledge", description=f"Some of the mists here are almost glowing with a charged arcane power. In one particular location, you see them converging into a small spherical vortex. Each of you could choose to investigate it or leave it be.\n\n{len(self.investigated_users)}/{len(self._users)} have investigated.")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(InvestigateButton())
        self.add_item(ContinueButton())

    def any_in_duels_currently(self):
        return any(self._get_player(user.id).get_dueling().is_in_combat for user in self._users)

    def investigate(self, user: discord.User):
        player = self._get_player(user.id)

        time_abilities_available = [ab_class for ab_class in TIMEWEAVING_ABILITIES if not any(isinstance(ab, ab_class) for ab in player.get_dueling().available_abilities)]
        
        description: str = ""
        if len(time_abilities_available) > 0:
            ability_class = random.choice(time_abilities_available)
            ability: Ability = ability_class()
            player.get_dueling().available_abilities.append(ability)

            description = f"As you approach the conflux, a memory or understanding of some kind shifts from the echo and into you. You've gained {ability.get_icon_and_name()} as an ability!"
        else:
            description = "As you approach the conflux, you get the sense that there's nothing more to learn from this echo. You already have all the timeweaving abilities it will afford you."

        self.investigated_users.add(user)

        return description

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