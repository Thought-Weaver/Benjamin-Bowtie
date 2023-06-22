from __future__ import annotations

import discord
import features.stories.ocean.ocean as ocean
import random

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.stories.ocean.combat.npcs.jellyfish import Jellyfish
from features.views.dueling_view import DuelView
from features.shared.constants import OCEAN_ROOMS
from features.shared.enums import ClassTag, OceanSection
from features.stories.dungeon_run import RoomSelectionView
from features.shared.item import LOADED_ITEMS, ItemKey, Rarity

from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from features.player import Player
    from features.stories.dungeon_run import DungeonRun

# -----------------------------------------------------------------------------
# WHISPERING WOODS INTRO ROOM
# -----------------------------------------------------------------------------

class CoralForestContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: VictoryView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        for player in view.get_players():
            if player.get_dungeon_run().ocean_best_act < OceanSection.CoralForest:
                player.get_dungeon_run().ocean_best_act = OceanSection.CoralForest

            player.get_dueling().status_effects = []
            player.get_expertise().heal(int(player.get_expertise().max_hp))
            player.get_expertise().restore_mana(int(player.get_expertise().max_mana))

        view.get_dungeon_run().previous_combat = -1
        view.get_dungeon_run().previous_event = -1

        room_select_view: RoomSelectionView = RoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_select_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_select_view, content=None)


class CoralForestIntroView(discord.ui.View):
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
        return Embed(title="The Coral Forest", description=f"The shallow waters continue to deepen as your party ventures forward, but here -- not yet at the drop into the darkness of the abyss -- life flourishes in the scintillating beams of light cascading from the ocean's surface.\n\nThe coral before had been somewhat sparse, mostly overshadowed by the rock, shells, and ever-present golden sands. This place, however, is a forest of corals in vibrant hues: twisting red coral rises like flame, branching purple coral is latticed across rocks to give an otherworldly appearance, and green shelf corals protrude akin to mushrooms in the forest.\n\nFor all its beauty, this coral forest is no doubt rife with dangerous wildlife and powers unknown.")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(CoralForestContinueButton())

    def get_bot(self):
        return self._bot

    def get_users(self):
        return self._users

    def get_players(self):
        return [self._get_player(user.id) for user in self._users]

    def get_database(self):
        return self._database

    def get_guild_id(self):
        return self._guild_id
    
    def get_group_leader(self):
        return self._group_leader
    
    def get_dungeon_run(self):
        return self._dungeon_run

# -----------------------------------------------------------------------------
# BOSS TREASURE ROOM
# -----------------------------------------------------------------------------

class TreasureRoomContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: JellyfishSwarmTreasureRoomView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(embed=view.get_initial_embed(), content="Error: You aren't the group leader and can't continue to the next room!", view=view)
            return
        
        dungeon_run: DungeonRun = view.get_dungeon_run()
        dungeon_run.rooms_until_boss = OCEAN_ROOMS
        dungeon_run.section = OceanSection.CoralForest
        dungeon_run.bosses_defeated += 1
        
        next_view: CoralForestIntroView = CoralForestIntroView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = next_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=next_view, content=None)


class JellyfishSwarmTreasureRoomView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run

        self._prob_map = {
            Rarity.Rare: 0.5,
            Rarity.Epic: 0.3,
            Rarity.Legendary: 0.2
        }
        
        self._min_level = 30
        self._max_level = 40
        self._valid_class_tags = [ClassTag.Equipment.Equipment, ClassTag.Valuable.Gemstone, ClassTag.Consumable.Potion]
        self._possible_rewards: List[ItemKey] = []
        for item_key in ItemKey:
            item = LOADED_ITEMS.get_new_item(item_key)
            if any(tag in item.get_class_tags() for tag in self._valid_class_tags):
                if Rarity.Uncommon < item.get_rarity() < Rarity.Cursed:
                    if ClassTag.Equipment.Equipment in item.get_class_tags():
                        if self._min_level <= item.get_level_requirement() <= self._max_level:
                            self._possible_rewards.append(item_key)
                    else:
                        # Add additional non-equipment keys to increase probability
                        self._possible_rewards += [item_key for _ in range(5)]
        self._weights = [self._prob_map[LOADED_ITEMS.get_new_item(item_key).get_rarity()] for item_key in self._possible_rewards]

        self._EXTRA_REWARD_LUCK_PROB = 0.01

        self._treasure_result_str = self._generate_and_add_treasure()

        self._display_initial_buttons()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def _generate_and_add_treasure(self):
        result_str: str = ""

        for user in self._users:
            player = self._get_player(user.id)
            total_luck = player.get_combined_attributes().luck

            get_additional_reward = random.random() < total_luck * self._EXTRA_REWARD_LUCK_PROB
            rewards = random.choices(self._possible_rewards, k=3 if get_additional_reward else 2, weights=self._weights)
            
            for reward_key in rewards:
                item = LOADED_ITEMS.get_new_item(reward_key)
                player.get_inventory().add_item(item)
                result_str += f"{user.display_name} found {item.get_full_name_and_count()}\n"
            
            result_str += "\n"

        return result_str

    def get_initial_embed(self):
        return Embed(title="The Remainder", description=f"As you progressed through the jellyfish swarm, you found treasure chests amid shattered wood and bones -- perhaps from the remains of a shipwreck.\n\n{self._treasure_result_str}")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(TreasureRoomContinueButton())

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

# -----------------------------------------------------------------------------
# DUEL VICTORY
# -----------------------------------------------------------------------------

class DuelVictoryContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: VictoryView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        next_view: JellyfishSwarmTreasureRoomView = JellyfishSwarmTreasureRoomView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = next_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=next_view, content=None)


class VictoryView(discord.ui.View):
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
        return Embed(title="Past the Jellyfish", description=f"Having made it through the swarm alive, the rest of the ocean awaits.")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(DuelVictoryContinueButton())

    def get_bot(self):
        return self._bot

    def get_users(self):
        return self._users

    def get_players(self):
        return [self._get_player(user.id) for user in self._users]

    def get_database(self):
        return self._database

    def get_guild_id(self):
        return self._guild_id
    
    def get_group_leader(self):
        return self._group_leader
    
    def get_dungeon_run(self):
        return self._dungeon_run

# -----------------------------------------------------------------------------
# DUEL INTRO
# -----------------------------------------------------------------------------

class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: JellyfishSwarmDuelView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the duel.")
            return
        
        if view.any_in_duels_currently():
            await interaction.response.edit_message(content="At least one person is already in a duel. This duel has been cancelled.")
            return

        victory_view: VictoryView = VictoryView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        defeat_view: ocean.OceanDefeatView = ocean.OceanDefeatView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())

        duel_view: DuelView = DuelView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_players(), [Jellyfish(), Jellyfish(), Jellyfish(), Jellyfish()], player_victory_post_view=victory_view, player_loss_post_view=defeat_view)
        initial_info: Embed = duel_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=duel_view, content=None)


class JellyfishSwarmDuelView(discord.ui.View):
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
        return Embed(title="The Shallow Edge", description="As your party continues along the continental shelf, you find thousands upon thousands of large jellyfish floating mindlessly throughout the cold water. Their vibrant orange stingers billow outwards from clear caps, indicating their poisonous nature. Though they're not aggressive, making it through the swarm won't be a simple task: Avoiding the stingers will likely be impossible and it's difficult to see how far left you have to go before the next region of the ocean.")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(ContinueButton())

    def any_in_duels_currently(self):
        return any(self._get_player(user.id).get_dueling().is_in_combat for user in self._users)

    def get_bot(self):
        return self._bot

    def get_users(self):
        return self._users

    def get_players(self):
        return [self._get_player(user.id) for user in self._users]

    def get_database(self):
        return self._database

    def get_guild_id(self):
        return self._guild_id
    
    def get_group_leader(self):
        return self._group_leader
    
    def get_dungeon_run(self):
        return self._dungeon_run
