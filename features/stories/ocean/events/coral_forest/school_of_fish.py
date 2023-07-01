from __future__ import annotations

import discord
import random

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.expertise import ExpertiseClass
from features.player import Player
from features.shared.item import LOADED_ITEMS, ItemKey
from features.stories.dungeon_run import DungeonRun, RoomSelectionView

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.shared.item import Item


class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: CoralForestSchoolOfFishView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        room_selection_view: RoomSelectionView = RoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class FishButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Fish")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: CoralForestSchoolOfFishView = self.view
        if interaction.user not in view.fished_users:
            mail_message = view.fish(interaction.user)
            
            await interaction.response.edit_message(content=None, embed=view.get_initial_embed(), view=view)
            await interaction.user.send(mail_message)
            

class CoralForestSchoolOfFishView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run

        # Each player can only fish once
        self.fished_users: List[discord.User] = []
        
        self._display_initial_buttons()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_initial_embed(self):
        return Embed(title="School of Fish", description=f"Swimming in the open water are too many fish to count!\n\n{len(self.fished_users)}/{len(self._users)} have grabbed a fish.")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(FishButton())
        self.add_item(ContinueButton())

    def any_in_duels_currently(self):
        return any(self._get_player(user.id).get_dueling().is_in_combat for user in self._users)

    def fish(self, user: discord.User):
        player = self._get_player(user.id)
        player_stats = player.get_stats()

        LUCK_MOD = 0.005 # Luck adjusts total bias by 0.5% per point
        # More than 50 might break the game, so let's just cap that
        total_luck: int = min(player.get_combined_attributes().luck, 50)
        rand_val = random.choices(
            [0, 1, 2, 3, 4], k=1,
            weights=[
                0.3 - LUCK_MOD * total_luck,
                0.3 + 6 * (LUCK_MOD * total_luck) / 16,
                0.2 + 4 * (LUCK_MOD * total_luck) / 16,
                0.15 + 3 * (LUCK_MOD * total_luck) / 16,
                0.05 + 2 * (LUCK_MOD * total_luck) / 16
            ]
        )[0]

        xp_to_add: int = 0
        fishing_result: Item | None = None

        if rand_val == 0:
            items = [
                LOADED_ITEMS.get_new_item(ItemKey.Minnow), 
                LOADED_ITEMS.get_new_item(ItemKey.Roughy), 
                LOADED_ITEMS.get_new_item(ItemKey.Shrimp)
            ]
            fishing_result = random.choice(items)
            xp_to_add = 3
            player_stats.fish.common_fish_caught += 1
        elif rand_val == 1:
            items = [
                LOADED_ITEMS.get_new_item(ItemKey.Pufferfish)
            ]
            fishing_result = random.choice(items)
            xp_to_add = 5
            player_stats.fish.uncommon_fish_caught += 1
        elif rand_val == 2:
            items = [
                LOADED_ITEMS.get_new_item(ItemKey.Squid),
                LOADED_ITEMS.get_new_item(ItemKey.Shark)
            ]
            fishing_result = random.choice(items)
            xp_to_add = 8
            player_stats.fish.rare_fish_caught += 1
        elif rand_val == 3:
            items = [
                LOADED_ITEMS.get_new_item(ItemKey.RubyDartfish)
            ]
            fishing_result = random.choice(items)
            xp_to_add = 13
            player_stats.fish.epic_fish_caught += 1
        else:
            items = [
                LOADED_ITEMS.get_new_item(ItemKey.Beefish),
                LOADED_ITEMS.get_new_item(ItemKey.Wyvernfish)
            ]
            fishing_result = random.choice(items)
            xp_to_add = 21
            player_stats.fish.legendary_fish_caught += 1
        
        assert(fishing_result is not None)

        player.get_inventory().add_item(fishing_result)
        final_xp = player.get_expertise().add_xp_to_class(xp_to_add, ExpertiseClass.Fisher, player.get_equipment())

        description = f"You caught {fishing_result.get_full_name()} worth {fishing_result.get_value_str()}! It's been added to your b!inventory."
        if final_xp > 0:
            description += f"\n\n*(+{final_xp} {ExpertiseClass.Fisher} xp)*"

        self.fished_users.append(user)

        return description

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