from __future__ import annotations

import discord

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.player import Player
from features.shared.statuseffect import TurnSkipChance
from features.stories.dungeon_run import DungeonRun
from features.stories.underworld_room_selection import UnderworldRoomSelectionView

from typing import Dict, List


class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: TorchesGoOutView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        room_selection_view: UnderworldRoomSelectionView = UnderworldRoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class FocusButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Focus")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: TorchesGoOutView = self.view
        view.decisions[interaction.user.id] = 0

        if len(view.decisions) == len(view.get_users()):
            response = view.resolve()
            await interaction.response.edit_message(content=None, embed=response, view=view)
        else:
            await interaction.response.edit_message(content=None, embed=view.get_initial_embed(), view=view)


class PushThroughButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Push Through")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: TorchesGoOutView = self.view
        view.decisions[interaction.user.id] = 1

        if len(view.decisions) == len(view.get_users()):
            response = view.resolve()
            await interaction.response.edit_message(content=None, embed=response, view=view)
        else:
            await interaction.response.edit_message(content=None, embed=view.get_initial_embed(), view=view)


class HideButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Hide")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: TorchesGoOutView = self.view
        view.decisions[interaction.user.id] = 2

        if len(view.decisions) == len(view.get_users()):
            response = view.resolve()
            await interaction.response.edit_message(content=None, embed=response, view=view)
        else:
            await interaction.response.edit_message(content=None, embed=view.get_initial_embed(), view=view)


class TorchesGoOutView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run

        self.decisions: Dict[int, int] = {}
        
        self._display_initial_buttons()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_initial_embed(self):
        return Embed(title="The Torches Go Out", description=f"With a sudden gust of wind from further ahead, your torches flicker and die -- leaving you all alone in the darkness. Unable to relight them quickly, you find yourselves quickly gaining terror. You have a moment to try to steel yourselves and avoid succumbing to fear.\n\n{len(self.decisions)}/{len(self._users)} have decided on their course of action.")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(FocusButton())
        self.add_item(PushThroughButton())
        self.add_item(HideButton())

    def resolve(self):
        self.clear_items()
        self.add_item(ContinueButton())

        results: List[str] = []
        for user in self._users:
            player = self._get_player(user.id)
            
            faltering = TurnSkipChance(
                turns_remaining=4,
                value=1,
                source_str="Torches Go Out"
            )
            
            if self.decisions[user.id] == 0:
                if player.get_expertise().intelligence > 40:
                    results.append(f"{user.display_name} successfully focused their mind and relit their torch.")
                else:
                    results.append(f"{user.display_name} tried to focus their mind, but became paralyzed by fear.")
                    player.get_dueling().status_effects.append(faltering)
            elif self.decisions[user.id] == 1:
                if player.get_expertise().strength > 40:
                    results.append(f"{user.display_name} successfully pushed through and relit their torch.")
                else:
                    results.append(f"{user.display_name} tried to hold their breath, but became paralyzed by fear.")
                    player.get_dueling().status_effects.append(faltering)
            else:
                if player.get_expertise().dexterity > 40:
                    results.append(f"{user.display_name} successfully hid and relit their torch.")
                else:
                    results.append(f"{user.display_name} tried to hold their breath, but became paralyzed by fear.")
                    player.get_dueling().status_effects.append(faltering)

        final_str: str = "\n\n".join(results)
        return Embed(title="The Light Returns", description=f"{final_str}")

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