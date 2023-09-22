from __future__ import annotations

import discord

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.player import Player
from features.shared.statuseffect import LckDebuff
from features.stories.dungeon_run import DungeonRun
from features.stories.underworld_room_selection import UnderworldRoomSelectionView

from typing import Dict, List


class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: GoldenIdolView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        room_selection_view: UnderworldRoomSelectionView = UnderworldRoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class TakeItButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Take It")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: GoldenIdolView = self.view
        view.users_taking[interaction.user.id] = False

        if len(view.users_taking) == len(view.get_users()):
            response = view.resolve()
            await interaction.response.edit_message(content=None, embed=response, view=view)
        else:
            await interaction.response.edit_message(content=None, embed=view.get_initial_embed(), view=view)


class LeaveItButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Leave It")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: GoldenIdolView = self.view
        view.users_taking[interaction.user.id] = True

        if len(view.users_taking) == len(view.get_users()):
            response = view.resolve()
            await interaction.response.edit_message(content=None, embed=response, view=view)
        else:
            await interaction.response.edit_message(content=None, embed=view.get_initial_embed(), view=view)


class GoldenIdolView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run

        self.users_taking: Dict[int, bool] = {}
        
        self._display_initial_buttons()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_initial_embed(self):
        return Embed(title="Golden Idol", description=f"On a pedestal inside one of the buildings, a small statue made of gold stands tall: A robed figure with four arms stretched out seems to beckon you closer. It doesn’t appear to be trapped or attached to the pedestal -- you could try to take the statue or leave it behind.\n\n{len(self.users_taking)}/{len(self._users)} have decided on their course of action.")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(TakeItButton())
        self.add_item(LeaveItButton())

    def resolve(self):
        self.clear_items()
        self.add_item(ContinueButton())

        num_take = sum(choice == True for choice in self.users_taking.values())
        result: str = ""

        if num_take >= len(self._users) // 2:
            for user in self._users:
                player = self._get_player(user.id)
                player.get_dueling().status_effects.append(
                    LckDebuff(
                        turns_remaining=30,
                        value=-100,
                        source_str="Golden Idol"
                    )
                )
                player.get_inventory().add_coins(300)
            result = "The majority of you decide to take the idol with you. As you touch it, you suddenly have a sense of something bound to you being drained as hundreds of coins are generated for each of you."
        else:
            result = "The majority of you decide to leave it behind -- the option less likely to get you cursed or worse."

        return Embed(title="Golden Idol", description=result)

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