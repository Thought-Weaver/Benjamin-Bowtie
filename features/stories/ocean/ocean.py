from __future__ import annotations
import random

import discord
import features.companions.companion

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.player import Player
from features.shared.constants import OCEAN_ROOMS
from features.shared.enums import CompanionKey, OceanSection
from features.stories.dungeon_run import DungeonRun

from features.stories.ocean.combat.abyssal_plain.ancient_kraken_duel import AncientKrakenDuelView
from features.stories.ocean.combat.abyssal_plain.faceless_husks_duel import FacelessHusksDuelView
from features.stories.ocean.combat.abyssal_plain.fish_maybe_duel import FishMaybeDuelView
from features.stories.ocean.combat.abyssal_plain.lurking_isopod_duel import LurkingIsopodDuelView
from features.stories.ocean.combat.abyssal_plain.mysterious_tentacle_duel import MysteriousTentacleDuelView
from features.stories.ocean.combat.abyssal_plain.sandwyrm_duel import SandwyrmDuelView
from features.stories.ocean.combat.abyssal_plain.voidseen_angler_duel import VoidseenAnglerDuelView
from features.stories.ocean.combat.abyssal_plain.wriggling_mass_duel import WrigglingMassDuelView
from features.stories.ocean.combat.coral_forest.banded_eel_duel import BandedEelDuelView
from features.stories.ocean.combat.coral_forest.bloodcoral_behemoth_duel import AbyssalPlainIntroView, BloodcoralBehemothDuelView
from features.stories.ocean.combat.coral_forest.grand_lionfish_duel import GrandLionfishDuelView
from features.stories.ocean.combat.coral_forest.rockfish_duel import RockfishDuelView
from features.stories.ocean.combat.coral_forest.sand_lurker_duel import SandLurkerDuelView
from features.stories.ocean.combat.coral_forest.sea_dragons_duel import SeaDragonsDuelView
from features.stories.ocean.combat.coral_forest.wandering_bloodcoral_duel import WanderingBloodcoralDuelView
from features.stories.ocean.combat.tidewater_shallows.brittle_star_duel import BrittleStarDuelView
from features.stories.ocean.combat.tidewater_shallows.giant_cone_snail_duel import GiantConeSnailDuelView

from features.stories.ocean.combat.tidewater_shallows.jellyfish_swarm_duel import CoralForestIntroView, JellyfishSwarmDuelView
from features.stories.ocean.combat.tidewater_shallows.lesser_kraken_duel import LesserKrakenDuelView
from features.stories.ocean.combat.tidewater_shallows.mesmerfish_swarm_duel import MesmerfishSwarmDuelView
from features.stories.ocean.combat.tidewater_shallows.shallows_shark_duel import ShallowsSharkDuelView
from features.stories.ocean.combat.tidewater_shallows.stranglekelp_forest_duel import StranglekelpForestDuelView
from features.stories.ocean.combat.tidewater_shallows.stranglekelp_host_duel import StranglekelpHostDuelView
from features.stories.ocean.combat.tidewater_shallows.titanfish_duel import TitanfishDuelView
from features.stories.ocean.events.abyssal_plain.hydrothermal_vents import HydrothermalVentsView
from features.stories.ocean.events.abyssal_plain.sandstorm import SandstormView
from features.stories.ocean.events.abyssal_plain.strange_effigy import StrangeEffigyView
from features.stories.ocean.events.abyssal_plain.underwater_whirlpool import UnderwaterWhirlpoolView
from features.stories.ocean.events.coral_forest.bloodcoral_polyps import BloodcoralPolypsView
from features.stories.ocean.events.coral_forest.coral_grove import CoralForestCoralGroveView
from features.stories.ocean.events.coral_forest.glowing_coral import GlowingCoralView
from features.stories.ocean.events.coral_forest.school_of_fish import CoralForestSchoolOfFishView
from features.stories.ocean.events.coral_forest.the_hook import TheHookView
from features.stories.ocean.events.coral_forest.voice_of_the_sea import VoiceOfTheSeaView
from features.stories.ocean.events.tidewater_shallows.a_curious_crab import ACuriousCrabView
from features.stories.ocean.events.tidewater_shallows.ancient_shipwreck import AncientShipwreckView
from features.stories.ocean.events.tidewater_shallows.coral_grove import TidewaterShallowsCoralGroveView
from features.stories.ocean.events.tidewater_shallows.dangerous_current import DangerousCurrentView
from features.stories.ocean.events.tidewater_shallows.giant_clams import GiantClamsView
from features.stories.ocean.events.tidewater_shallows.school_of_fish import TidewaterShallowsSchoolOfFishView
from features.stories.ocean.events.tidewater_shallows.wayward_conch import WaywardConchView
from features.stories.ocean.merchant.mysterious_merchant import MysteriousMerchantView
from features.stories.ocean.treasure.abyssal_plain_treasure import AbyssalPlainTreasureRoomView
from features.stories.ocean.treasure.coral_forest_treasure import CoralForestTreasureRoomView
from features.stories.ocean.treasure.tidewater_shallows_treasure import TidewaterShallowsTreasureRoomView
from features.stories.ocean_room_selection import OceanRoomSelectionView
from features.stories.story import Story

from typing import List, Set, Tuple

# -----------------------------------------------------------------------------
# OCEAN DEFEAT VIEW
# -----------------------------------------------------------------------------

class OceanDefeatView(discord.ui.View):
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
        
        return Embed(title="To the Surface", description=f"With your party defeated, you all flee the ocean barely alive.\n\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\n{post_run_info_str}")

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
# OCEAN REST VIEW
# -----------------------------------------------------------------------------

class RestContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: OceanRestView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        for player in view.get_players():
            player.get_dungeon_run().in_rest_area = False

        room_selection_view = OceanRoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class OceanRestButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Rest")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: OceanRestView = self.view
        if interaction.user not in view.rested_users:
            response = view.rest(interaction.user) # type: ignore
            await interaction.response.edit_message(content=None, embed=response, view=view)


class OceanRestView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run

        # Each player can only get one rest per rest room
        self.rested_users: List[discord.User] = []
        
        self._display_initial_buttons()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_initial_embed(self, additional_info: str=""):
        return Embed(title="Quiet Waters", description=f"Along your journey through the ocean depths, you find a relatively safe and undisturbed region where you can rest for a time, restoring 50% of your health and mana.\n\n{len(self.rested_users)}/{len(self._users)} players have rested.{additional_info}")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(OceanRestButton())
        self.add_item(RestContinueButton())

    def any_in_duels_currently(self):
        return any(self._get_player(user.id).get_dueling().is_in_combat for user in self._users)

    def rest(self, user: discord.User):
        player = self._get_player(user.id)
        player_expertise = player.get_expertise()
        player_dueling = player.get_dueling()

        player_dueling.status_effects = []
        player_expertise.heal(int(player_expertise.max_hp / 2))
        player_expertise.restore_mana(int(player_expertise.max_mana / 2))

        companion_result_str: str = ""
        if random.random() < 0.001 + (0.001 * player.get_combined_attributes().luck) / 10:
            companions = player.get_companions()
            if random.random() < 0.5:
                if CompanionKey.VoidseenCat not in companions.companions.keys():
                    companions.companions[CompanionKey.VoidseenCat] = features.companions.companion.VoidseenCatCompanion()
                    companions.companions[CompanionKey.VoidseenCat].set_id(player.get_id())
                    companion_result_str += f"\n\nIn your sleep, amid nightmares that seem far too real, you awake with a start to find something curled up beside your feet. A small cat, fur dark as the night, with beautiful eyes shimmering white with shards of color dancing in the irises. It purrs and calms you, driving away the fear you felt from the dreams. It's been added as a companion for {user.display_name} in b!companions."

                    player.get_stats().companions.companions_found += 1
            else:
                if CompanionKey.VoidseenPup not in companions.companions.keys():
                    companions.companions[CompanionKey.VoidseenPup] = features.companions.companion.VoidseenPupCompanion()
                    companions.companions[CompanionKey.VoidseenPup].set_id(player.get_id())
                    companion_result_str += f"\n\nIn your sleep, amid nightmares that seem far too real, you awake with a start to find something curled up beside your feet. A small pup, fur dark as the night, with beautiful eyes shimmering white with shards of color dancing in the irises. It looks up at you, one ear floppy the other pointed straight up, then nuzzles you with its nose. Your newfound companion brings a profound sense of calm, driving away the terrifying dreams. It's been added as a companion for {user.display_name} in b!companions."

                    player.get_stats().companions.companions_found += 1

        self.rested_users.append(user)

        return self.get_initial_embed()

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
# TIDEWATER SHALLOWS ENTRANCE VIEW
# -----------------------------------------------------------------------------

class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")
    
    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: TidewaterShallowsEntranceView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(embed=view.get_initial_embed(), content="Error: You aren't the group leader and can't continue to the next room!", view=view)
            return
        
        room_select_view = OceanRoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_select_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_select_view, content=None)


class TidewaterShallowsEntranceView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        super().__init__(timeout=900)

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
        return Embed(title="Tidewater Shallows", description="This is the beginning of a journey into another world entirely: The depths of the ocean which harbor something unknown, something that has been calling to each of you.\n\nYou all step into the cold seawater, feeling the waves lap at you as you descend further and further. There's a moment of panic as the water begins to crest over your heads, but you take a deep breath and submerge entirely.\n\nThe water is clear and doesn't even seem to sting your eyes; the sand is a beautiful white-gold with shimmering patterns from the light above. Every step keeps you relatively grounded to the ocean floor -- the potions Yenna made must also have helped with the buoyancy.\n\nThe way ahead is open to you, a sense of direction guiding you into the vast ocean beyond.")

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

# -----------------------------------------------------------------------------
# OCEAN DUNGEON ENTRANCE VIEW
# -----------------------------------------------------------------------------

class StartButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.green, label="Start")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: OceanDungeonEntranceView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(embed=view.get_initial_embed(), content="Error: You aren't the group leader and can't start this adventure!", view=view)
            return
        
        if view.any_in_duels_currently():
            await interaction.response.edit_message(embed=None, view=None, content="At least one person is in a duel. You cannot start this adventure.")
            return
        
        if view.any_in_dungeons_currently():
            await interaction.response.edit_message(embed=None, view=None, content="At least one person is already on an adventure. You cannot start this adventure.")
            return

        for player in view.get_players():
            player.get_dungeon_run().in_dungeon_run = True
            player.get_dungeon_run().corruption = 0

        starting_section: OceanSection | None = view.get_starting_section()
        if starting_section is None or starting_section == OceanSection.TidewaterShallows:
            ts_entrance_view: TidewaterShallowsEntranceView = TidewaterShallowsEntranceView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
            initial_info: Embed = ts_entrance_view.get_initial_embed()

            await interaction.response.edit_message(embed=initial_info, view=ts_entrance_view, content=None)
        elif starting_section == OceanSection.CoralForest:
            cf_entrance_view: CoralForestIntroView = CoralForestIntroView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
            initial_info: Embed = cf_entrance_view.get_initial_embed()

            await interaction.response.edit_message(embed=initial_info, view=cf_entrance_view, content=None)
        elif starting_section == OceanSection.AbyssalPlain:
            ap_entrance_view: AbyssalPlainIntroView = AbyssalPlainIntroView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
            initial_info: Embed = ap_entrance_view.get_initial_embed()

            await interaction.response.edit_message(embed=initial_info, view=ap_entrance_view, content=None)


class AcceptButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Accept")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: OceanDungeonEntranceView = self.view
        view.accepted_users.add(interaction.user.id)
        await interaction.response.edit_message(embed=view.get_initial_embed(), view=view, content=None)


class OceanDungeonEntranceView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], starting_section: OceanSection | None):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = DungeonRun(Story.Ocean, OCEAN_ROOMS, starting_section if starting_section is not None else OceanSection.TidewaterShallows)
        self._starting_section = starting_section
        
        self.accepted_users: Set[int] = set()

        self._display_initial_buttons()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_initial_embed(self):
        if len(self._users) == len(self.accepted_users):
            self.clear_items()
            self.add_item(StartButton())

        return Embed(title="The Ocean", description=(
            f"Looking at the horizon of the ocean, your party begins the final preparations to find the source of the mysterious scrolls and oddities that have been turning up in the village.\n\nBefore you can set out, however, Yenna meets you on the beach, offering some cautionary words, \"There are powers beyond this world whose true nature we only barely understand. Know your own mind, beware those who would control you.\"\n\nShe reaches into her satchel and retrieves a few potions for you all. \"Drink these, they'll let you breathe underwater and help keep you alive against the dangers of the deep. Stranglekelp won't permanently infest you and bloodcoral won't do lasting damage, though more than that they can't save you from,\" she says. With a nod farewell and a sign of good fortune, she turns away and back to her tent.\n\nThe ocean awaits.\n\n"
            "**Recommendations:**\n\n_Tidewater Shallows: 4+ Players (Lvl. 30-40)_\n_Coral Forest: 4+ Players (Lvl. 40-50)_\n_Abyssal Plain: 4+ Players (Lvl. 50-60)_\n_Final Boss: 4+ Players (Lvl. 60-70)_\n\n"
            f"Your group leader is {self._group_leader.display_name}. When your party is ready, you may enter the ocean.\n\n"
            f"{len(self.accepted_users)}/{len(self._users)} are ready to begin the journey.")
        )

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(AcceptButton())

    def any_in_duels_currently(self):
        return any(self._get_player(user.id).get_dueling().is_in_combat for user in self._users)

    def any_in_dungeons_currently(self):
        return any(self._get_player(user.id).get_dungeon_run().in_dungeon_run for user in self._users)

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
    
    def get_starting_section(self):
        return self._starting_section

# -----------------------------------------------------------------------------
# OCEAN STORY CLASS
# -----------------------------------------------------------------------------

class OceanStory():
    def __init__(self):
        self.first_to_find_maybe_fish_id: int = -1

    @staticmethod
    def generate_shopkeep_room(bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        return MysteriousMerchantView(bot, database, guild_id, users, dungeon_run)

    @staticmethod
    def generate_rest_room(bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        return OceanRestView(bot, database, guild_id, users, dungeon_run)
    
    @staticmethod
    def generate_treasure_room(bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        if dungeon_run.section == OceanSection.AbyssalPlain:
            return AbyssalPlainTreasureRoomView(bot, database, guild_id, users, dungeon_run)
        elif dungeon_run.section == OceanSection.CoralForest:
            return CoralForestTreasureRoomView(bot, database, guild_id, users, dungeon_run)
        else:
            return TidewaterShallowsTreasureRoomView(bot, database, guild_id, users, dungeon_run)

    @staticmethod
    def generate_combat_room(bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun) -> Tuple[discord.ui.View, int]:
        if dungeon_run.section == OceanSection.TidewaterShallows:
            rand_val: int = random.choice([i for i in range(0, 8) if i != dungeon_run.previous_combat])
            if rand_val == 0:
                return BrittleStarDuelView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 1:
                return GiantConeSnailDuelView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 2:
                return LesserKrakenDuelView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 3:
                return MesmerfishSwarmDuelView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 4:
                return ShallowsSharkDuelView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 5:
                return StranglekelpForestDuelView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 6:
                return StranglekelpHostDuelView(bot, database, guild_id, users, dungeon_run), rand_val
            else:
                return TitanfishDuelView(bot, database, guild_id, users, dungeon_run), rand_val
        elif dungeon_run.section == OceanSection.CoralForest:
            rand_val: int = random.choice([i for i in range(0, 6) if i != dungeon_run.previous_combat])
            if rand_val == 0:
                return BandedEelDuelView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 1:
                return GrandLionfishDuelView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 2:
                return RockfishDuelView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 3:
                return SandLurkerDuelView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 4:
                return SeaDragonsDuelView(bot, database, guild_id, users, dungeon_run), rand_val
            else:
                return WanderingBloodcoralDuelView(bot, database, guild_id, users, dungeon_run), rand_val
        else:
            rand_val: int = random.choice([i for i in range(0, 7) if i != dungeon_run.previous_combat])
            if rand_val == 0:
                return AncientKrakenDuelView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 1:
                return FacelessHusksDuelView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 2:
                return FishMaybeDuelView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 3:
                return LurkingIsopodDuelView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 4:
                return MysteriousTentacleDuelView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 5:
                return VoidseenAnglerDuelView(bot, database, guild_id, users, dungeon_run), rand_val
            else:
                return WrigglingMassDuelView(bot, database, guild_id, users, dungeon_run), rand_val

    @staticmethod
    def generate_event_room(bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun) -> Tuple[discord.ui.View, int]:
        if dungeon_run.section == OceanSection.TidewaterShallows:
            rand_val: int = random.choice([i for i in range(0, 7) if i != dungeon_run.previous_event])
            if rand_val == 0:
                return AncientShipwreckView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 1:
                return TidewaterShallowsCoralGroveView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 2:
                return DangerousCurrentView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 3:
                return GiantClamsView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 4:
                return TidewaterShallowsSchoolOfFishView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 5:
                return WaywardConchView(bot, database, guild_id, users, dungeon_run), rand_val
            else:
                return ACuriousCrabView(bot, database, guild_id, users, dungeon_run), rand_val
        elif dungeon_run.section == OceanSection.CoralForest:
            rand_val: int = random.choice([i for i in range(0, 6) if i != dungeon_run.previous_event])
            if rand_val == 0:
                return BloodcoralPolypsView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 1:
                return CoralForestCoralGroveView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 2:
                return GlowingCoralView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 3:
                return CoralForestSchoolOfFishView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 4:
                return TheHookView(bot, database, guild_id, users, dungeon_run), rand_val
            else:
                return VoiceOfTheSeaView(bot, database, guild_id, users, dungeon_run), rand_val
        else:
            rand_val: int = random.choice([i for i in range(0, 4) if i != dungeon_run.previous_event])
            if rand_val == 0:
                return HydrothermalVentsView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 1:
                return SandstormView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 2:
                return StrangeEffigyView(bot, database, guild_id, users, dungeon_run), rand_val
            else:
                return UnderwaterWhirlpoolView(bot, database, guild_id, users, dungeon_run), rand_val

    @staticmethod
    def generate_boss_room(bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        if dungeon_run.section == OceanSection.TidewaterShallows:
            return JellyfishSwarmDuelView(bot, database, guild_id, users, dungeon_run)
        elif dungeon_run.section == OceanSection.CoralForest:
            return BloodcoralBehemothDuelView(bot, database, guild_id, users, dungeon_run)
        else:
            return SandwyrmDuelView(bot, database, guild_id, users, dungeon_run)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.first_to_find_maybe_fish_id = state.get("first_to_find_maybe_fish_id", -1)
