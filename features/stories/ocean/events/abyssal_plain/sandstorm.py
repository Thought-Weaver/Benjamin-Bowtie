from __future__ import annotations

import discord

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.player import Player
from features.shared.statuseffect import ConDebuff, DmgDebuff
from features.stories.dungeon_run import DungeonRun
from features.stories.ocean_room_selection import OceanRoomSelectionView

from typing import Dict, List


class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: SandstormView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        room_selection_view: OceanRoomSelectionView = OceanRoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class TakeCoverButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Take Cover")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: SandstormView = self.view
        view.users_taking_cover[interaction.user.id] = True

        if len(view.users_taking_cover) == len(view.get_users()):
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
        
        view: SandstormView = self.view
        view.users_taking_cover[interaction.user.id] = False

        if len(view.users_taking_cover) == len(view.get_users()):
            response = view.resolve()
            await interaction.response.edit_message(content=None, embed=response, view=view)
        else:
            await interaction.response.edit_message(content=None, embed=view.get_initial_embed(), view=view)


class SandstormView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run

        self.users_taking_cover: Dict[int, bool] = {}
        
        self._display_initial_buttons()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_initial_embed(self):
        return Embed(title="Sandstorm", description=f"Trudging your way across a barren stretch of ocean floor, the dark begins to form into a fog of sand as powerful currents toss it around chaotically. All around you, it's as though an endless gale has arisen and it becomes incredibly difficult to see.\n\nYou could try to weather the storm hiding against some rocks, which would mean a long time without rest, or push through and be weakened afterwards.\n\n{len(self.users_taking_cover)}/{len(self._users)} have decided on their course of action.")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(TakeCoverButton())
        self.add_item(PushThroughButton())

    def resolve(self):
        self.clear_items()
        self.add_item(ContinueButton())

        results: List[str] = []
        for user in self._users:
            player = self._get_player(user.id)
            if self.users_taking_cover[user.id]:
                player.get_dueling().status_effects.append(ConDebuff(-1, -10, "Sandstorm"))
                results.append(f"{user.display_name} took cover behind some rocks and weathered the storm, but was drained by the time the storm ended.")
            else:
                player.get_dueling().status_effects.append(DmgDebuff(-1, 0.25, "Sandstorm"))
                results.append(f"{user.display_name} pushed through the storm, but was weakened by the strenuous effort.")

        final_str: str = "\n\n".join(results)
        return Embed(title="Chaos and Tumult", description=f"{final_str}")

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