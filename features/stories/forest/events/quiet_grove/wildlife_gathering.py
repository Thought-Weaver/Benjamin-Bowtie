from __future__ import annotations

import discord

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.companions.companion import FlyingFoxCompanion, SilverwingOwlCompanion, SunbaskTurtleCompanion
from features.player import Player
from features.shared.enums import CompanionKey
from features.stories.dungeon_run import DungeonRun, RoomSelectionView

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.companions.companion import Companion


class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: WildlifeGatheringView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        room_selection_view: RoomSelectionView = RoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class TurtleButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Turtle")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: WildlifeGatheringView = self.view
        if interaction.user.id != view.get_group_leader().id:
            response = view.choose_animal(CompanionKey.SunbaskTurtle)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class OwlButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Owl")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: WildlifeGatheringView = self.view
        if interaction.user.id != view.get_group_leader().id:
            response = view.choose_animal(CompanionKey.SilverwingOwl)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class FoxButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Fox")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: WildlifeGatheringView = self.view
        if interaction.user.id != view.get_group_leader().id:
            response = view.choose_animal(CompanionKey.FlyingFox)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class WildlifeGatheringView(discord.ui.View):
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

    def choose_animal(self, companion_key: CompanionKey):
        self.clear_items()
        self.add_item(ContinueButton())

        for user in self._users:
            player = self._get_player(user.id)
            companions = player.get_companions()

            if companion_key not in companions.companions.keys():
                new_companion: Companion | None = None
                if companion_key == CompanionKey.SunbaskTurtle:
                    new_companion = SunbaskTurtleCompanion()
                elif companion_key == CompanionKey.SilverwingOwl:
                    new_companion = SilverwingOwlCompanion()
                elif companion_key == CompanionKey.FlyingFox:
                    new_companion = FlyingFoxCompanion()

                if new_companion is not None:
                    companions.companions[companion_key] = new_companion
                    companions.companions[companion_key].set_id(player.get_id())

                player.get_stats().companions.companions_found += 1

        return Embed(title="Stone Statue", description="Your party approaches the statue and its eyes begin to glow. Suddenly, a wind picks up around you and a small companion appears before each of you! A new companion has been added to b!companions.")

    def get_initial_embed(self):
        return Embed(title="The Path is Lost", description="In the fading light of day and a dense thicket, you find yourselves uncertain how to get back on the path.\n\nA couple options come to mind:")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(TurtleButton())
        self.add_item(OwlButton())
        self.add_item(FoxButton())
        self.add_item(ContinueButton())

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