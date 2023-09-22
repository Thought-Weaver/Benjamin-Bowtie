from __future__ import annotations

import discord

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.player import Player
from features.shared.statuseffect import ConDebuff, DexDebuff, IntDebuff, LckDebuff, StrDebuff
from features.stories.dungeon_run import DungeonRun
from features.stories.underworld_room_selection import UnderworldRoomSelectionView

from typing import Dict, List


class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: ArcaneTrapsView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        room_selection_view: UnderworldRoomSelectionView = UnderworldRoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class DodgeButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Dodge")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: ArcaneTrapsView = self.view
        view.decisions[interaction.user.id] = 0

        if len(view.decisions) == len(view.get_users()):
            response = view.resolve()
            await interaction.response.edit_message(content=None, embed=response, view=view)
        else:
            await interaction.response.edit_message(content=None, embed=view.get_initial_embed(), view=view)


class EndureButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Endure")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: ArcaneTrapsView = self.view
        view.decisions[interaction.user.id] = 1

        if len(view.decisions) == len(view.get_users()):
            response = view.resolve()
            await interaction.response.edit_message(content=None, embed=response, view=view)
        else:
            await interaction.response.edit_message(content=None, embed=view.get_initial_embed(), view=view)


class ArcaneTrapsView(discord.ui.View):
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
        return Embed(title="Arcane Traps", description=f"Continuing your journey to what waits within, a sudden burst of force erupts from a nearby wall -- a trap triggered by proximity, it occurs to you in a flash. You have a moment to react, either by dodging out of the way or steeling yourself against the blow.\n\n{len(self.decisions)}/{len(self._users)} have decided on their course of action.")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(DodgeButton())
        self.add_item(EndureButton())

    def resolve(self):
        self.clear_items()
        self.add_item(ContinueButton())

        results: List[str] = []
        for user in self._users:
            player = self._get_player(user.id)
            
            ses = [
                ConDebuff(
                    turns_remaining=30,
                    value=-15,
                    source_str="Arcane Traps"
                ),
                StrDebuff(
                    turns_remaining=30,
                    value=-15,
                    source_str="Arcane Traps"
                ),
                DexDebuff(
                    turns_remaining=30,
                    value=-15,
                    source_str="Arcane Traps"
                ),
                IntDebuff(
                    turns_remaining=30,
                    value=-15,
                    source_str="Arcane Traps"
                ),
                LckDebuff(
                    turns_remaining=30,
                    value=-15,
                    source_str="Arcane Traps"
                )
            ]
            
            if self.decisions[user.id] == 0:
                if player.get_expertise().dexterity > 40:
                    results.append(f"{user.display_name} successfully dodged out of the way of the effect of the traps.")
                else:
                    results.append(f"{user.display_name} tried to dodge out of the way, but was caught by the edge of the arcane explosion.")
                    player.get_dueling().status_effects += ses
            else:
                if player.get_expertise().constitution > 40:
                    results.append(f"{user.display_name} successfully endured the weakening effects of the traps.")
                else:
                    results.append(f"{user.display_name} tried to steel themselves, but became overwhelmed by the arcane explosion and succumbed to its effects.")
                    player.get_dueling().status_effects += ses

        final_str: str = "\n\n".join(results)
        return Embed(title="Past the Traps", description=f"{final_str}")

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