from __future__ import annotations

import discord
import random

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.player import Player
from features.shared.item import LOADED_ITEMS, ItemKey
from features.stories.dungeon_run import DungeonRun
from features.stories.ocean_room_selection import OceanRoomSelectionView

from typing import Dict, List, Tuple


class ContinueButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: GiantClamsView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        room_selection_view: OceanRoomSelectionView = OceanRoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class ClamButton(discord.ui.Button):
    def __init__(self, index: int, row: int, item_key: ItemKey | None):
        super().__init__(style=discord.ButtonStyle.secondary, row=row, label="‍", emoji="\uD83E\uDDAA")

        self._index = index
        self._item_key = item_key

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: GiantClamsView = self.view
        if interaction.user.id not in view.clams_selected.keys():
            response = view.select_clam(interaction.user.id, self._index, self._item_key)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class GiantClamsView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run
        
        self.clams_selected: Dict[int, Tuple[int, ItemKey | None]] = {}

        self._display_initial_buttons()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def _get_selected_clams_str(self):
        result_str: str = ""
        for user_id, (index, _) in self.clams_selected.items():
            name = next(user.display_name for user in self._users if user.id == user_id)
            result_str += f"\n{name} chose clam {index}"
        return result_str

    def get_initial_embed(self):
        clams_selected_str = self._get_selected_clams_str()
        return Embed(title="Giant Clams", description=f"Continuing along the continental shelf to the abyss below, your foot suddenly strikes something in the sand -- hard and elliptical in shape. Reaching down, you find a giant clam! You look around for a moment and realize this place is a clam field and a perfect place for harvesting rare pearls.\n\nYou each get to choose a clam:\n{clams_selected_str}")

    def _display_initial_buttons(self):
        self.clear_items()

        for i in range(4):
            for j in range(4):
                item_key = random.choices([None, ItemKey.CrackedPearl, ItemKey.Pearl, ItemKey.FlawlessPearl], [0.2, 0.4, 0.3, 0.1])[0]
                self.add_item(ClamButton((i + 1) * (j + 1), i, item_key))
        self.add_item(ContinueButton(4))

    def select_clam(self, user_id: int, index: int, item_key: ItemKey | None):
        self.clams_selected[user_id] = (index, item_key)

        if len(self.clams_selected.keys()) == len(self._users):
            self.clear_items()
            self.add_item(ContinueButton(0))

            result_str: str = ""
            for user_id, (_, item_key) in self.clams_selected.items(): 
                name = next(user.display_name for user in self._users if user.id == user_id)
                
                if item_key is not None:
                    item = LOADED_ITEMS.get_new_item(item_key)
                    player = self._get_player(user_id)
                    player.get_inventory().add_item(item)

                    result_str += f"\n{name} received {item.get_full_name()}"
                else:
                    result_str += f"\n{name} received nothing"

            return Embed(title="Shimmering Pearls", description=f"You open the clams to find:\n{result_str}")
        else:
            return self.get_initial_embed()

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