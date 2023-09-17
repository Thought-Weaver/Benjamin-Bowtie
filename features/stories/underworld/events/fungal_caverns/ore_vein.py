from __future__ import annotations

import discord
import random

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.player import Player
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, ItemKey, Rarity
from features.stories.dungeon_run import DungeonRun
from features.stories.underworld_room_selection import UnderworldRoomSelectionView

from typing import List


class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: FungalCavernsOreVeinView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        room_selection_view = UnderworldRoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class FungalCavernsOreVeinView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run
        
        self._prob_map = {
            Rarity.Common: 0.2,
            Rarity.Uncommon: 0.3,
            Rarity.Rare: 0.25,
            Rarity.Epic: 0.2,
            Rarity.Legendary: 0.05
        }

        self._possible_rewards: List[ItemKey] = [ItemKey.IronOre, ItemKey.CopperOre, ItemKey.SilverOre, ItemKey.GoldOre, ItemKey.AmberiteOre, ItemKey.OrichalcumOre, ItemKey.MythrilOre, ItemKey.VoidseenOre]
        self._weights = [self._prob_map[LOADED_ITEMS.get_new_item(item_key).get_rarity()] for item_key in self._possible_rewards]

        self._display_initial_buttons()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def _generate_and_add_ores(self):
        result_str: str = ""

        for user in self._users:
            player = self._get_player(user.id)
            ore_keys = random.choices(self._possible_rewards, k=random.randint(3, 5), weights=self._weights)

            for ore_key in ore_keys:
                item = LOADED_ITEMS.get_new_item(ore_key)
                item.add_amount(random.randint(0, 3))

                player.get_inventory().add_item(item)
                result_str += f"{user.display_name} found {item.get_full_name_and_count()}\n"

            result_str += "\n"

        return result_str

    def get_initial_embed(self):
        ore_results: str = self._generate_and_add_ores()
        return Embed(title="Ore Vein", description=f"Though smaller veins of ore have been present through this section of the caves, you notice a series of larger ones nearby that could be mined for ore!\n\n{ore_results}")

    def _display_initial_buttons(self):
        self.clear_items()
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