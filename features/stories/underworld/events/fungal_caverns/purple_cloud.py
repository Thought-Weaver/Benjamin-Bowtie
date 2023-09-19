from __future__ import annotations

import discord

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.player import Player
from features.shared.statuseffect import FixedDmgTick
from features.stories.dungeon_run import DungeonRun
from features.stories.underworld_room_selection import UnderworldRoomSelectionView

from typing import Dict, List


class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: PurpleCloudView = self.view

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
        
        view: PurpleCloudView = self.view
        view.users_pressing_on[interaction.user.id] = False

        if len(view.users_pressing_on) == len(view.get_users()):
            response = view.resolve()
            await interaction.response.edit_message(content=None, embed=response, view=view)
        else:
            await interaction.response.edit_message(content=None, embed=view.get_initial_embed(), view=view)


class PressThroughButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Press Through")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: PurpleCloudView = self.view
        view.users_pressing_on[interaction.user.id] = True

        if len(view.users_pressing_on) == len(view.get_users()):
            response = view.resolve()
            await interaction.response.edit_message(content=None, embed=response, view=view)
        else:
            await interaction.response.edit_message(content=None, embed=view.get_initial_embed(), view=view)


class PurpleCloudView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run

        self.users_pressing_on: Dict[int, bool] = {}
        
        self._display_initial_buttons()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_initial_embed(self):
        return Embed(title="Purple Cloud", description=f"Ahead of you, the mists that have maintained their presence in this place are instead replaced by some kind of violet haze hanging in the air. The mushrooms surrounding it are black and withered and the moss a brown sludge. You could try to pass through it or find another, longer way around.\n\n{len(self.users_pressing_on)}/{len(self._users)} have decided on their course of action.")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(GoAroundButton())
        self.add_item(PressThroughButton())

    def resolve(self):
        self.clear_items()
        self.add_item(ContinueButton())

        num_press_on = sum(choice == True for choice in self.users_pressing_on.values())
        result: str = ""

        if num_press_on >= len(self._users) // 2:
            for user in self._users:
                player = self._get_player(user.id)
                player.get_dueling().status_effects.append(
                    FixedDmgTick(
                        turns_remaining=5,
                        value=75,
                        source_str="Purple Cloud"
                    )
                )
            result = "The majority decides to press on through the cloud. As you move through the haze, you all start coughing -- lightly at first and then more intensely. You manage to reach the other side, but not without consequence."
        else:
            self._dungeon_run.rooms_until_boss += 3
            result = "The majority decides to take the long way around, which will increase the length of the journey, but was definitely the safer route."

        return Embed(title="Past the Cloud", description=result)

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