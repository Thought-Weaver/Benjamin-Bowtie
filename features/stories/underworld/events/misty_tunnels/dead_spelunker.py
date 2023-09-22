from __future__ import annotations

import discord
import random

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.player import Player
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, ItemKey, Rarity
from features.stories.dungeon_run import DungeonRun
from features.stories.underworld.combat.misty_tunnels.dead_spelunker_duel import DeadSpelunkerDuelView
from features.stories.underworld_room_selection import UnderworldRoomSelectionView

from typing import List

class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DeadSpelunkerView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        room_selection_view: UnderworldRoomSelectionView = UnderworldRoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class SearchButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Search")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DeadSpelunkerView = self.view
        if interaction.user.id == view.get_group_leader().id:
            if random.random() < 0.25:
                shipwreck_duel_view: DeadSpelunkerDuelView = DeadSpelunkerDuelView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
                initial_info: Embed = shipwreck_duel_view.get_initial_embed()

                await interaction.response.edit_message(content=None, embed=initial_info, view=shipwreck_duel_view)
            else:
                response = view.search()
                await interaction.response.edit_message(content=None, embed=response, view=view)


class DeadSpelunkerView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run

        self._prob_map = {
            Rarity.Uncommon: 0.6,
            Rarity.Rare: 0.3,
            Rarity.Epic: 0.1
        }
        
        self._min_level = 60
        self._max_level = 70
        self._valid_class_tags = [ClassTag.Equipment.Equipment, ClassTag.Valuable.Gemstone, ClassTag.Consumable.Potion]
        self._possible_rewards: List[ItemKey] = []
        for item_key in ItemKey:
            item = LOADED_ITEMS.get_new_item(item_key)
            if any(tag in item.get_class_tags() for tag in self._valid_class_tags):
                if Rarity.Common < item.get_rarity() < Rarity.Legendary:
                    if ClassTag.Equipment.Equipment in item.get_class_tags():
                        if self._min_level <= item.get_level_requirement() <= self._max_level:
                            self._possible_rewards.append(item_key)
                    else:
                        self._possible_rewards.append(item_key)
        self._weights = [self._prob_map[LOADED_ITEMS.get_new_item(item_key).get_rarity()] for item_key in self._possible_rewards]

        self._display_initial_buttons()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_initial_embed(self):
        return Embed(title="Dead Spelunker", description=f"To the side of one of the tunnels, you spot a fate you'd rather avoid: Clutching a satchel and rope is a skeleton, once a spelunker looking for excitement or treasure. You could try to search the body, but there's every chance you'll alert something nearby to your presence.")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(SearchButton())
        self.add_item(ContinueButton())

    def any_in_duels_currently(self):
        return any(self._get_player(user.id).get_dueling().is_in_combat for user in self._users)

    def _generate_and_add_treasure(self):
        result_str: str = ""

        for user in self._users:
            player = self._get_player(user.id)

            rewards = random.choices(self._possible_rewards, k=1, weights=self._weights)
            
            for reward_key in rewards:
                item = LOADED_ITEMS.get_new_item(reward_key)
                player.get_inventory().add_item(item)
                result_str += f"{user.display_name} found {item.get_full_name_and_count()}\n"
            
            result_str += "\n"

        return result_str

    def search(self):
        self.clear_items()
        self.add_item(ContinueButton())

        reward_str = self._generate_and_add_treasure()

        return Embed(title="In the Bag", description=f"Luckily whatever got them didn't take what the person was carrying and you all find some treasure!\n\n{reward_str}")

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