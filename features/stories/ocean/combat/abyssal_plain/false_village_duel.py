from __future__ import annotations

import discord
import features.stories.ocean.ocean as ocean
import random

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.views.dueling_view import DuelView
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, ItemKey, Rarity
from features.stories.ocean.combat.npcs.false_village import FalseVillage

from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from features.player import Player
    from features.stories.dungeon_run import DungeonRun

# -----------------------------------------------------------------------------
# FINAL WORDS
# -----------------------------------------------------------------------------

class OceanFinalWordsView(discord.ui.View):
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
        
        view: FalseVillageTreasureRoomView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(embed=view.get_initial_embed(), content="Error: You aren't the group leader and can't continue to the next room!", view=view)
            return
        
        dungeon_run: DungeonRun = view.get_dungeon_run()
        dungeon_run.bosses_defeated += 1
        
        for player in view.get_players():
            player.get_dungeon_run().in_dungeon_run = False

        next_view: OceanFinalWordsView = OceanFinalWordsView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = next_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=next_view, content=None)


class FalseVillageTreasureRoomView(discord.ui.View):
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
            Rarity.Legendary: 0.5,
            Rarity.Artifact: 0.15,
        }
        
        self._min_level = 50
        self._max_level = 60
        self._valid_class_tags = [ClassTag.Equipment.Equipment, ClassTag.Valuable.Gemstone]
        self._possible_rewards: List[ItemKey] = [
            ItemKey.AbarrasGreatsword, ItemKey.GalosRapier, ItemKey.BreathOfTheWraith, ItemKey.DreadmarshSymbol,
            ItemKey.FatesScorn, ItemKey.GrandAlchemistsSeal, ItemKey.Daggerfoot, ItemKey.StunningReproach,
            ItemKey.TakeTheirSoles, ItemKey.TransmutingSteps, ItemKey.DestinyEnclosure,  ItemKey.MantleOfStars,
            ItemKey.TwistingForm, ItemKey.VassalbaneRaiment, ItemKey.MushroomCommunion, ItemKey.BoonOfTheMushroomKing,
            ItemKey.NotABloodyChance, ItemKey.MarshhawksTalons, ItemKey.BloomcrestGreatshield, ItemKey.ExtensionOfSelf,
            ItemKey.FaultyPossibility, ItemKey.SterlingOmen, ItemKey.HungerForIchor, ItemKey.FangCairn, ItemKey.UnboundArcana,
            
            ItemKey.Hushsteps, ItemKey.KestrelsFlight, ItemKey.PathOfTheBarbarian, ItemKey.PathOfTheBramblewalker,
            ItemKey.TurnToGold, ItemKey.UnrequitedLove, ItemKey.Wavebringers, ItemKey.Heartseeker,
            ItemKey.TerminalDream, ItemKey.BurningFists, ItemKey.FishersCrown, ItemKey.RoarOfTheBear,
            ItemKey.APaleFuture, ItemKey.BramblesBoundary, ItemKey.PierceTheVeil, ItemKey.BeholdFinality
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
                        self._possible_rewards += [item_key for _ in range(15)]
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
        return Embed(title="Amid the Ruins", description=f"Perhaps you weren't the first to be called here? Perhaps these too are creations of the false village? Though you cannot say, indeed, in the rubble of the false village, you find some powerful items:\n\n{self._treasure_result_str}")

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

        next_view: FalseVillageTreasureRoomView = FalseVillageTreasureRoomView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
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
        return Embed(title="JOIN US JOIN US", description="COME HITHER TO US FISHER KING. YOUR THRONE IS WAITING. Why shouldn't you? After all, they've prepared all this for your arrival; they're only trying to understand you, to understand what humans are. Just let go. Just give in. Just give in. Just give in.\n\nBut there, as the false village grows and forms a cage from which you'll never escape, a glimmer of hope pierces the encroaching darkness: A crack in the barrier before you, a sliver of an opportunity beckoning you towards freedom.\n\nYou rush towards the opening, defying the twisting realm that would bind you here forever. There's an unearthly sound, like the tearing of flesh meets the shattering of glass -- and you burst free into open waters with their own horrors, but away from the eldritch power.\n\nBehind you, it begins to grow new tendrils, reaching out towards you as you flee; the entire mass seems to shudder in fury and pain from the damage you dealt, slowly collapsing as you swim further and further away.\n\nThe thing that sustained the village begins to wane, losing its grip on the real world. The monstrous entity disintegrates into smaller and smaller pieces, eventually dissolving into spectral fragments that become nothingness. But something lingers here, a presence that hasn't yet abated -- and will, with time, begin anew.")

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
# FALSE VILLAGE DEFEAT VIEW
# -----------------------------------------------------------------------------

class FalseVillageDefeatView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun, players_joined_willingly: List[Player]):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run
        self._players_joined_willingly = players_joined_willingly

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

            ps.ocean_rooms_explored += self._dungeon_run.rooms_explored
            ps.ocean_combat_encounters += self._dungeon_run.combat_encounters
            ps.ocean_treasure_rooms_encountered += self._dungeon_run.treasure_rooms_encountered
            ps.ocean_shopkeeps_encountered += self._dungeon_run.shopkeeps_encountered
            ps.ocean_events_encountered += self._dungeon_run.events_encountered
            ps.ocean_rests_taken += self._dungeon_run.rests_taken
            ps.ocean_bosses_defeated += self._dungeon_run.bosses_defeated
            ps.ocean_adventures_played += 1

    def get_initial_embed(self):
        post_run_info_str: str = self._generate_run_info()
        
        self._update_player_stats()

        return Embed(title="Become One", description=f"Running through the false village -- trying desperately to find any way out of the contorting, horrifying maze -- it grasps at you with tendrils reaching from every morphing building. Every instinct is screaming at you to run, to somehow retreat to the comparative safety of the open waters. But there's no way out.\n\nPanic begins to grip your mind as you realize the horrible truth: This village has become your prison. The once-distant lights that guided you forward are beginning to dance with a madness as everything twists and turns; the chorus has become incomprehensible as words overlap in screeching noise.\n\nThen it all begins to go dark as the anglerfish stalks are consumed by the engulfing mass around you. WE BUILD IT UNTIL NOTHING REMAINS. The abyss gazes back at you without solace, only a bleak and unforgiving void. DON'T YOU WANT THESE WAVES TO DRAG YOU AWAY?\n\nBut in the darkness, there's suddenly a flash of light, a nova so bright it begins to burn your eyes. As you fade into unconsciousness, a hand grasps yours and begins to pull, desperate to keep you alive.\n\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\n{post_run_info_str}")

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
        
        view: FalseVillageDuelView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the duel.")
            return
        
        if view.any_in_duels_currently():
            await interaction.response.edit_message(content="At least one person is already in a duel. This duel has been cancelled.")
            return

        victory_view: VictoryView = VictoryView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        defeat_view: ocean.OceanDefeatView = ocean.OceanDefeatView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())

        duel_view: DuelView = DuelView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_players(), [FalseVillage()], player_victory_post_view=victory_view, player_loss_post_view=defeat_view)
        initial_info: Embed = duel_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=duel_view, content=None)


class FalseVillageDuelView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run

        self.times_pressed: int = 0

        self.players_joined_willingly: List[Player] = []
        self.players_joined_with_fail: List[Player] = []
        self.resisted_names: List[str] = []
        self.players_resisted: List[Player] = []
        
        self._display_initial_buttons()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_initial_embed(self):
        return Embed(title="Flesh and Stone", description="The very fabric of the village begins to warp and contort; buildings unravel and reform melded together as the ground itself undulates with a lifelike retching. All around you, what should be inanimate structures are becoming some gargantuan horror.\n\nIts form defies reason, an abomination that shouldn't be possible, with jagged spines like hooks, writhing tentacles, and a body of corrupted materials that screams in your mind with an unending psychic pain. Each pulse of its fleshy bulk sends tremors through the water, shaking your bodies and twisting the essence of whatever is close to it.\n\nThe words you heard refrained again and again wandering the false village are echoed out now with distorted sounds that seem more animalistic than human. This manifestation is one last attempt to maintain itself, abandoning all illusions of human mimicry. In the darkness, lights begin to form again -- this time appearing exactly like stars in the night sky, as something behind it watches the final battle unfold.")

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
