from __future__ import annotations

import discord

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.player import Player
from features.shared.statuseffect import DexDebuff
from features.stories.dungeon_run import DungeonRun, RoomSelectionView

from typing import Dict, List


class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: HallucinatorySmokeView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        room_selection_view: RoomSelectionView = RoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class FocusButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Focus")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: HallucinatorySmokeView = self.view
        view.users_focused[interaction.user.id] = True

        if len(view.users_focused) == len(view.get_users()):
            response = view.resolve()
            await interaction.response.edit_message(content=None, embed=response, view=view)
        else:
            await interaction.response.edit_message(content=None, embed=view.get_initial_embed(), view=view)


class HoldBreathButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Hold Breath")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: HallucinatorySmokeView = self.view
        view.users_focused[interaction.user.id] = False

        if len(view.users_focused) == len(view.get_users()):
            response = view.resolve()
            await interaction.response.edit_message(content=None, embed=response, view=view)
        else:
            await interaction.response.edit_message(content=None, embed=view.get_initial_embed(), view=view)


class HallucinatorySmokeView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run

        self.users_focused: Dict[int, bool] = {}
        
        self._display_initial_buttons()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_initial_embed(self):
        return Embed(title="Hallucinatory Smoke", description=f"The mist grows thicker here, darker than it was before. As you try to move through it, you find your vision beginning to swim as the world becomes a swirl of strange colors. Each of you doesn't have much time to act, but two options pierce through the fog that is becoming your mind.\n\n{len(self.users_focused)}/{len(self._users)} have decided on their course of action.")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(FocusButton())
        self.add_item(HoldBreathButton())

    def resolve(self):
        self.clear_items()
        self.add_item(ContinueButton())

        results: List[str] = []
        for user in self._users:
            player = self._get_player(user.id)
            if self.users_focused[user.id]:
                if player.get_expertise().intelligence > 30:
                    results.append(f"{user.display_name} successfully focused their mind and made it through the smoke.")
                else:
                    results.append(f"{user.display_name} tried to focus their mind, but became lost in the smoke -- the party found them far astray from the path some time later.")
                    self._dungeon_run.rooms_until_boss += 1
            else:
                if player.get_expertise().constitution > 30:
                    results.append(f"{user.display_name} successfully held their breath and made it through the smoke.")
                else:
                    results.append(f"{user.display_name} tried to hold their breath, but it proved too difficult a task and they became lost in the smoke -- the party found them far astray from the path some time later.")
                    self._dungeon_run.rooms_until_boss += 1

        final_str: str = "\n\n".join(results)
        return Embed(title="Through the Smoke", description=f"{final_str}")

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