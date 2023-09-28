from __future__ import annotations

import discord
from features.stories.story import Story
import random

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.views.dueling_view import DuelView
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, ItemKey, Rarity
from features.stories.underworld.combat.npcs.chthonic_emissary import ChthonicEmissary

from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from features.player import Player
    from features.stories.dream.dream import DreamStory
    from features.stories.dungeon_run import DungeonRun

# -----------------------------------------------------------------------------
# FINAL WORDS
# -----------------------------------------------------------------------------

class UnderworldFinalWordsView(discord.ui.View):
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
        num_stirred: int = sum(self._get_player(user.id).get_stats().wishingwell.something_stirs for user in self._users)

        for user in self._users:
            player = self._get_player(user.id)
            ps = player.get_stats().dungeon_runs

            ps.underworld_rooms_explored += self._dungeon_run.rooms_explored
            ps.underworld_combat_encounters += self._dungeon_run.combat_encounters
            ps.underworld_treasure_rooms_encountered += self._dungeon_run.treasure_rooms_encountered
            ps.underworld_shopkeeps_encountered += self._dungeon_run.shopkeeps_encountered
            ps.underworld_events_encountered += self._dungeon_run.events_encountered
            ps.underworld_rests_taken += self._dungeon_run.rests_taken
            ps.underworld_bosses_defeated += self._dungeon_run.bosses_defeated
            ps.underworld_adventures_won += 1
            ps.underworld_adventures_played += 1
            ps.best_chthonic_emissary_win = min(12, max(ps.best_chthonic_emissary_win, int(num_stirred / 10)))

    def get_initial_embed(self):
        post_run_info_str: str = self._generate_run_info()

        self._update_player_stats()

        return Embed(title="Return to the Sunlight", description=f"{post_run_info_str}")

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
        
        view: ChthonicEmissaryTreasureRoomView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(embed=view.get_initial_embed(), content="Error: You aren't the group leader and can't continue to the next room!", view=view)
            return
        
        dungeon_run: DungeonRun = view.get_dungeon_run()
        dungeon_run.bosses_defeated += 1
        
        for player in view.get_players():
            player.get_dungeon_run().in_dungeon_run = False

        next_view: UnderworldFinalWordsView = UnderworldFinalWordsView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = next_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=next_view, content=None)


class ChthonicEmissaryTreasureRoomView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run

        self._prob_map = {
            Rarity.Epic: 0.35,
            Rarity.Legendary: 0.45,
            Rarity.Artifact: 0.2,
        }
        
        self._min_level = 80
        self._max_level = 90
        self._valid_class_tags = [ClassTag.Equipment.Equipment, ClassTag.Valuable.Gemstone]
        self._possible_rewards: List[ItemKey] = [
            ItemKey.MagesRetort, ItemKey.ProlificArcana, ItemKey.ScarletVow, ItemKey.WarriorsApproach, 
            ItemKey.DeliverARemedy, ItemKey.Thoughtpierce, ItemKey.MemoryOfTheRedDawn, ItemKey.ANewDream,
            ItemKey.Earthbreakers, ItemKey.HandsOfThunder, ItemKey.ParasiticEmbrace, ItemKey.Sunbracers,
            ItemKey.WarMagesHand, ItemKey.DefianceOfTheVoid, ItemKey.SpellbladesWard, ItemKey.AssassinsBlade,
            ItemKey.EdgeOfFate, ItemKey.NecromancersTwistedEffigy, ItemKey.UnseenFists, ItemKey.CrashingWaves,
            ItemKey.HarrowingEnd, ItemKey.DeathspeakersSpire, ItemKey.WillOfTheStorm, ItemKey.DruidsBrokenVow,
            ItemKey.GravityWell
        ]
        for item_key in ItemKey:
            item = LOADED_ITEMS.get_new_item(item_key)
            if any(tag in item.get_class_tags() for tag in self._valid_class_tags):
                if Rarity.Epic < item.get_rarity() < Rarity.Cursed:
                    if ClassTag.Equipment.Equipment in item.get_class_tags():
                        if self._min_level <= item.get_level_requirement() <= self._max_level:
                            self._possible_rewards.append(item_key)
                    else:
                        # Add additional gemstone keys to increase probability
                        self._possible_rewards += [item_key for _ in range(10)]
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
            rewards = random.choices(self._possible_rewards, k=6 if get_additional_reward else 4, weights=self._weights)
            
            for reward_key in rewards:
                item = LOADED_ITEMS.get_new_item(reward_key)
                player.get_inventory().add_item(item)
                result_str += f"{user.display_name} found {item.get_full_name_and_count()}\n"
            
            result_str += "\n"

        return result_str

    def get_initial_embed(self):
        return Embed(title="Endless Riches", description=f"The inner city holds many treasures for you to find as you depart this place -- some more worth taking than others:\n\n{self._treasure_result_str}")

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
# EMISSARY DECISION
# -----------------------------------------------------------------------------

class EmissaryDecisionContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: VictoryView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        next_view: ChthonicEmissaryTreasureRoomView = ChthonicEmissaryTreasureRoomView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = next_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=next_view, content=None)


class EmissaryDecisionView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun, show_break_chains: bool):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run

        self._show_break_chains = show_break_chains

        self._display_initial_buttons()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_reward(self):
        num_stirred: int = sum(self._get_player(user.id).get_stats().wishingwell.something_stirs for user in self._users)
        key: ItemKey = ItemKey.InvitationToTheDreamTier0

        if num_stirred >= 10:
            key = ItemKey.InvitationToTheDreamTier1
        elif num_stirred >= 20:
            key = ItemKey.InvitationToTheDreamTier2
        elif num_stirred >= 30:
            key = ItemKey.InvitationToTheDreamTier3
        elif num_stirred >= 40:
            key = ItemKey.InvitationToTheDreamTier4
        elif num_stirred >= 50:
            key = ItemKey.InvitationToTheDreamTier5
        elif num_stirred >= 60:
            key = ItemKey.InvitationToTheDreamTier6
        elif num_stirred >= 70:
            key = ItemKey.InvitationToTheDreamTier7
        elif num_stirred >= 80:
            key = ItemKey.InvitationToTheDreamTier8
        elif num_stirred >= 90:
            key = ItemKey.InvitationToTheDreamTier9
        elif num_stirred >= 100:
            key = ItemKey.InvitationToTheDreamTier10
        elif num_stirred >= 110:
            key = ItemKey.InvitationToTheDreamTier11
        elif num_stirred >= 120:
            key = ItemKey.InvitationToTheDreamTier12
        
        return LOADED_ITEMS.get_new_item(key)

    def get_initial_embed(self):
        if self._show_break_chains:
            for user in self._users:
                player = self._get_player(user.id)
                reward = self.get_reward()
                player.get_inventory().add_item(reward)

            dream_story: DreamStory = self._database[str(self._guild_id)]["stories"][Story.Dream]
            dream_story.gateway_open = True

            return Embed(title="Break the Chains", description=(
                    "With the bonds of mana nearly depleted, severing them entirely takes little effort; with one last bit of resistance, they begin to flash and fade into oblivion.\n\n"
                    "Its arms unbound, the entity falls to the golden ground below, landing with a billowing wind that forces you all backwards away from the grand pillars that were its former prison.\n\n"
                    "At first, nothing happens: It lays there, unmoving, as though the act of shattering its bonds was what was actually needed to defeat it. Silence pierces the enormous cavern as you all wait with bated breath to see what will transpire.\n\n"
                    "Then, with great effort, one of its hands raises upwards and smashes against the ground, pushing it back upright as it flies into the air. All four of its arms stretch wide as it howls in an alien shriek, smoke billowing out from its robe in all directions.\n\n"
                    "There's a sound like the sky itself being torn asunder, and in your mind suddenly you can all hear voices shouting: WE WELCOME YOU TO THE DREAM. And then, collapsing in a vortex that threatens to pull you all in, the entity disappears and the cavern quakes violently as it begins to fall apart.\n\n"
                    "_Each of you has received an Invitation to the Dream._"
                )
            )
        else:
            return Embed(title="Leave It Bound", description=(
                    "You turn away from it, knowing that while you don't possess the means to destroy the emissary, leaving it weak and chained will at least buy you more time to think of a solution -- if there's even a way to truly end its existence.\n\n"
                    "The arcane bindings begin to renew themselves with the creature's lack of resistance, leaving you all free to scour the horde of treasure accumulated here: Each temple seems to have been dedicated to a different type of wealth, including everything from food to gems to gold, though it has all since been merged in a gargantuan sprawl on the cavern floor.\n\n"
                    "Some drawings in the temple seem to show the journey of individuals called to this place by visitations in a dream; many were nobles and merchants, but some were ordinary people with a hunger for more. Within the temples too, you find several items of incredible value -- priceless artifacts that have long been lost to the ages.\n\n"
                    "Gathering what you can, you begin to make your way away from the caverns and back home to the village. Undertaking this journey may be a rite you all have to endure, to keep the emissary weak and unable to fulfill its task -- again and again until humanity has faded away."
                )
            )

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(EmissaryDecisionContinueButton())

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
# DUEL VICTORY
# -----------------------------------------------------------------------------

class BreakTheChainsButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Break the Chains")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: VictoryView = self.view

        user_id: int = interaction.user.id
        if user_id not in view.break_the_chains and user_id not in view.leave_it_bound:
            view.break_the_chains.append(user_id)

        await interaction.response.edit_message(embed=view.get_initial_embed(), view=view, content=None)


class LeaveItBoundButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Leave it Bound")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: VictoryView = self.view

        user_id: int = interaction.user.id
        if user_id not in view.break_the_chains and user_id not in view.leave_it_bound:
            view.leave_it_bound.append(user_id)

        await interaction.response.edit_message(embed=view.get_initial_embed(), view=view, content=None)


class ContinueDecisionButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: VictoryView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return
        
        if len(view.leave_it_bound) == len(view.get_users()):
            next_view: EmissaryDecisionView = EmissaryDecisionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run(), show_break_chains=False)
            initial_info: Embed = next_view.get_initial_embed()

            await interaction.response.edit_message(embed=initial_info, view=next_view, content=None)
        elif len(view.break_the_chains) == len(view.get_users()):
            next_view: EmissaryDecisionView = EmissaryDecisionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run(), show_break_chains=True)
            initial_info: Embed = next_view.get_initial_embed()

            await interaction.response.edit_message(embed=initial_info, view=next_view, content=None)
        else:
            victory_view: EmissaryDecisionView = EmissaryDecisionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run(), show_break_chains=True)
            defeat_view: EmissaryDecisionView = EmissaryDecisionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run(), show_break_chains=False)

            duel_view: DuelView = DuelView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_break_players(), view.get_leave_players(), player_victory_post_view=victory_view, player_loss_post_view=defeat_view)
            initial_info: Embed = duel_view.get_initial_embed()

            await interaction.response.edit_message(embed=initial_info, view=duel_view, content=None)


class VictoryView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run

        self.break_the_chains: List[int] = []
        self.leave_it_bound: List[int] = []

        self._display_initial_buttons()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_initial_embed(self):
        self.update_buttons()

        warning_str: str = "\n\n_Your party disagrees about what action to take. A duel will have to decide the path to follow._" if len(self.break_the_chains) > 0 and len(self.leave_it_bound) > 0 else ""

        return Embed(title="Shackled and Broken", description=(
                "The entity collapses before you, weakened and beaten -- but not destroyed. It hangs limply in its shackles, and you now find yourselves with a choice to make.\n\n"
                f"{len(self.break_the_chains)}/{len(self._users)} have chosen to break its chains\n"
                f"{len(self.leave_it_bound)}/{len(self._users)} have chosen to leave it bound{warning_str}"
            )
        )

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(BreakTheChainsButton())
        self.add_item(LeaveItBoundButton())

    def update_buttons(self):
        self.clear_items()
        self.add_item(BreakTheChainsButton())
        self.add_item(LeaveItBoundButton())

        if len(self.break_the_chains) + len(self.leave_it_bound) == len(self._users):
            self.add_item(ContinueDecisionButton())

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

    def get_break_players(self):
        return [self._get_player(user_id) for user_id in self.break_the_chains]
    
    def get_leave_players(self):
        return [self._get_player(user_id) for user_id in self.leave_it_bound]

# -----------------------------------------------------------------------------
# EMISSARY DEFEAT VIEW
# -----------------------------------------------------------------------------

class ChthonicEmissaryDefeatView(discord.ui.View):
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

            ps.underworld_rooms_explored += self._dungeon_run.rooms_explored
            ps.underworld_combat_encounters += self._dungeon_run.combat_encounters
            ps.underworld_treasure_rooms_encountered += self._dungeon_run.treasure_rooms_encountered
            ps.underworld_shopkeeps_encountered += self._dungeon_run.shopkeeps_encountered
            ps.underworld_events_encountered += self._dungeon_run.events_encountered
            ps.underworld_rests_taken += self._dungeon_run.rests_taken
            ps.underworld_bosses_defeated += self._dungeon_run.bosses_defeated
            ps.underworld_adventures_played += 1

    def get_initial_embed(self):
        post_run_info_str: str = self._generate_run_info()
        
        self._update_player_stats()

        return Embed(title="Flee Mortals", description=f"It's impossible. It cannot be defeated, you realize in horror. Its shackles remain in place for now, but only barely, so you seize the opportunity to flee -- run, run back to the gate and hope never to return.\n\nAnother beam of destruction erupts from above as you try to escape, the heat of it nearly searing the flesh from your bones. You trip and stumble over piles of gold, knowing at any second you could become a pile of ash.\n\nYou reach the doors and manage to teleport through to the other side. But just as you do, you hear a guttural laugh -- as though a being with a thousand mouths chuckled from the pit of its stomach at your departure.\n\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\n{post_run_info_str}")

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

# -----------------------------------------------------------------------------
# DUEL INTRO
# -----------------------------------------------------------------------------
 
class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: ChthonicEmissaryDuelView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the duel.")
            return
        
        if view.any_in_duels_currently():
            await interaction.response.edit_message(content="At least one person is already in a duel. This duel has been cancelled.")
            return

        victory_view: VictoryView = VictoryView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        defeat_view: ChthonicEmissaryDefeatView = ChthonicEmissaryDefeatView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())

        duel_view: DuelView = DuelView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_players(), [ChthonicEmissary(num_stirred=view.num_stirred)], player_victory_post_view=victory_view, player_loss_post_view=defeat_view)
        initial_info: Embed = duel_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=duel_view, content=None)


class ChthonicEmissaryDuelView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run

        self.num_stirred: int = sum(self._get_player(user.id).get_stats().wishingwell.something_stirs for user in users)

        self._display_initial_buttons()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_initial_embed(self):
        return Embed(title="The Inner City", description=(
            "Before you is a grand staircase and a vision of opulence you can scarcely believe: In this valley of a cavern, you can see gold, gems, and equipment more than any empire of the world must have. It stretches across the floor of the cavern seemingly interminably, only broken by towering ziggurats with symbols and writing in the same language you saw in the outer city.\n\n"
            "At the center of these ziggurats is something massive, a being whose form stretches to the ceiling above. Four massive, almost skeletal hands are bound with grand chains enchanted with similar patterns as the doors you just passed through. The hands are the only exposed portion you can see, for its head and the rest of its body are covered in some kind of shadowy, immaterial cloth that expands outwards at the bottom into a hazy smoke.\n\n"
            "Slowly, it begins to raise its head as you enter its domain. Under the shadowy veil, the maw of sparse fangs and six ruby hexagonal eyes gaze down at you -- there is no emotion to be gleaned, but something about this otherworldly being strikes you as intelligent: It has a purpose to fulfill, and you are an opportunity to finally break its shackles.\n\n"
            f"It has been stirred {self.num_stirred} times by all party members, granting it {int(self.num_stirred / 10)} additional abilities."
        ))

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
