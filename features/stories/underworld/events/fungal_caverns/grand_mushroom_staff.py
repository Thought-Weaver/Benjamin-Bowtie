from __future__ import annotations

import discord

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.player import Player
from features.shared.item import LOADED_ITEMS, ItemKey
from features.stories.dungeon_run import DungeonRun
from features.stories.underworld_room_selection import UnderworldRoomSelectionView

from typing import List


class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: GrandMushroomStaffView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        room_selection_view: UnderworldRoomSelectionView = UnderworldRoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class RemoveStaffButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Remove Staff")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: GrandMushroomStaffView = self.view
        if interaction.user.id == view.get_group_leader().id:
            response = view.remove_staff()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class GrandMushroomStaffView(discord.ui.View):
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
        return Embed(title="The Grand Mushroom Staff", description="There! You can scarcely believe your eyes, but atop a mossy ridge stands an artifact of legend: Fungisvol, the grand mushroom staff, a powerful item that can only be wielded by those dedicated to the path of the mushrooms.")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(RemoveStaffButton())
        self.add_item(ContinueButton())

    def remove_staff(self):
        self.clear_items()
        self.add_item(ContinueButton())

        worthy_player: Player | None = None
        name: str = ""
        max_mushroom_items: int = 1
        for user in self._users:
            player = self._get_player(user.id)
            num_mushroom_items: int = 0
            for item in player.get_equipment().get_all_equipped_items():
                if "mushroom" in item.get_name().lower():
                    num_mushroom_items += 1
            if num_mushroom_items > max_mushroom_items:
                max_mushroom_items = num_mushroom_items
                worthy_player = player
                name = user.display_name
        
        result: str = "You realize that none of you are. The staff remains stuck in place, waiting for the one who has demonstrated a true dedication to mushrooms."
        if worthy_player is not None:
            item = LOADED_ITEMS.get_new_item(ItemKey.Fungisvol)
            worthy_player.get_inventory().add_item(item)
            result = f"{name} grasps the staff as mushrooms begin to sprout around them and variegated lights dance around you all -- they've done it! Having demonstrated a dedication to the mushrooms, Fungisvol is now yours."

        return Embed(title="Pull It Free", description=f"Each of you may be worthy, and as you try to pull it free...\n\n{result}")

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