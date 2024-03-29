from __future__ import annotations

import discord
import features.stories.forest.forest as forest
import random

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.views.dueling_view import DuelView
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, ItemKey, Rarity
from features.stories.forest.combat.npcs.wilderdragon import Wilderdragon

from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from features.player import Player
    from features.stories.dungeon_run import DungeonRun

# -----------------------------------------------------------------------------
# FINAL WORDS
# -----------------------------------------------------------------------------

class ForestFinalWordsView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def _generate_run_info(self):
        info_str: str = (
            f"Rooms Explored: {self._dungeon_run.rooms_explored}\n\n"
            f"Combat Encounters: {self._dungeon_run.combat_encounters}\n"
            f"Treasure Rooms Found: {self._dungeon_run.treasure_rooms_encountered}\n"
            f"Shopkeeps Met: {self._dungeon_run.shopkeeps_encountered}\n"
            f"Events Encountered: {self._dungeon_run.events_encountered}\n\n"
            f"Rests Taken: {self._dungeon_run.rests_taken}\n"
            f"Bosses Defeated: {self._dungeon_run.bosses_defeated}"
        )
        return info_str

    def _update_player_stats(self):
        for user in self._users:
            player = self._get_player(user.id)
            ps = player.get_stats().dungeon_runs

            ps.forest_rooms_explored += self._dungeon_run.rooms_explored
            ps.forest_combat_encounters += self._dungeon_run.combat_encounters
            ps.forest_treasure_rooms_encountered += self._dungeon_run.treasure_rooms_encountered
            ps.forest_shopkeeps_encountered += self._dungeon_run.shopkeeps_encountered
            ps.forest_events_encountered += self._dungeon_run.events_encountered
            ps.forest_rests_taken += self._dungeon_run.rests_taken
            ps.forest_bosses_defeated += self._dungeon_run.bosses_defeated
            ps.forest_adventures_won += 1
            ps.forest_adventures_played += 1

    def get_initial_embed(self):
        post_run_info_str: str = self._generate_run_info()

        self._update_player_stats()

        return Embed(title="The Journey Home", description=f"With the forest freed of the terrifying power that grasped it, you all begin the long journey back to the village. Your party is victorious!\n\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\n{post_run_info_str}")

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
        
        view: WilderdragonTreasureRoomView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(embed=view.get_initial_embed(), content="Error: You aren't the group leader and can't continue to the next room!", view=view)
            return
        
        dungeon_run: DungeonRun = view.get_dungeon_run()
        dungeon_run.bosses_defeated += 1
        
        for player in view.get_players():
            player.get_dungeon_run().in_dungeon_run = False

        next_view: ForestFinalWordsView = ForestFinalWordsView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = next_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=next_view, content=None)


class WilderdragonTreasureRoomView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run

        self._prob_map = {
            Rarity.Epic: 0.3,
            Rarity.Legendary: 0.6,
            Rarity.Artifact: 0.1,
        }
        
        self._min_level = 20
        self._max_level = 30
        self._valid_class_tags = [ClassTag.Equipment.Equipment]
        self._possible_rewards: List[ItemKey] = [
            ItemKey.BlessingOfTheMarshes, ItemKey.EldritchBane, ItemKey.FontOfIchor, ItemKey.GildedThread, ItemKey.HeraldOfDeath,
            ItemKey.PrecisionsWeave, ItemKey.Giantcrushers, ItemKey.Windwalkers, ItemKey.CloakOfTheThreeEyedSerpent,
            ItemKey.Mindclasp, ItemKey.EndureTheEnd, ItemKey.HerbwovenMask, ItemKey.MortalBlow, ItemKey.StoneMitts,
            ItemKey.FalseShield, ItemKey.SacrificialNeedle, ItemKey.PoisonwoodStaff, ItemKey.EdgeOfGlory, ItemKey.WarlocksPactblade,
            ItemKey.InnerFocus, ItemKey.UnendingAvarice
        ]
        for item_key in ItemKey:
            item = LOADED_ITEMS.get_new_item(item_key)
            if any(tag in item.get_class_tags() for tag in self._valid_class_tags):
                if Rarity.Epic < item.get_rarity() < Rarity.Cursed:
                    if ClassTag.Equipment.Equipment in item.get_class_tags():
                        if self._min_level <= item.get_level_requirement() <= self._max_level:
                            self._possible_rewards.append(item_key)
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
            rewards = random.choices(self._possible_rewards, k=4 if get_additional_reward else 3, weights=self._weights)
            
            for reward_key in rewards:
                item = LOADED_ITEMS.get_new_item(reward_key)
                player.get_inventory().add_item(item)
                result_str += f"{user.display_name} found {item.get_full_name_and_count()}\n"
            
            result_str += "\n"

        return result_str

    def get_initial_embed(self):
        return Embed(title="Wilderdragon's Treasure", description=f"In the Wilderdragon's lair, you find some incredible items!\n\n{self._treasure_result_str}")

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
    
    def get_players(self):
        return [self._get_player(user.id) for user in self._users]

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

        next_view: WilderdragonTreasureRoomView = WilderdragonTreasureRoomView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
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
        return Embed(title="The Fire Snuffed Out", description="The Wilderdragon remains before you in pieces, its fire faded away, and suddenly you all become aware of the silence. Eerie silence. There is no shifting of the briars, no shambling of the undead, nothing at all. It would seem, having defeated this creature, whatever effects it was causing on the forest have likewise ended -- the curse has been destroyed.")

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
        
        view: WilderdragonDuelView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the duel.")
            return
        
        if view.any_in_duels_currently():
            await interaction.response.edit_message(content="At least one person is already in a duel. This duel has been cancelled.")
            return

        victory_view: VictoryView = VictoryView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        defeat_view: forest.ForestDefeatView = forest.ForestDefeatView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())

        duel_view: DuelView = DuelView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_players(), [Wilderdragon()], player_victory_post_view=victory_view, player_loss_post_view=defeat_view)
        initial_info: Embed = duel_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=duel_view, content=None)


class WilderdragonDuelView(discord.ui.View):
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
        return Embed(title="The Flame and the Void", description="Pressing through the remains of the briar wall, a warm clearing -- though still far from the greenery and life of the outer woods -- opens before your party. There, in the center of the woods, you see what razed this land to the ground: An animated draconic creature, formed from the dead wood; its six eyes and gaping maw are lit by a burning, dark purplish flame and its antler-like horns seem to actually be bone, stretching down and woven throughout its entire body.\n\nIt roars an unearthly cry as you enter and unfurls bony wings that extend outwards to the sky!")

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
