from __future__ import annotations

import discord
import random

import features.companions.companion

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.npcs.mysterious_merchant import MysteriousMerchantView
from features.player import Player
from features.shared.constants import FOREST_ROOMS
from features.shared.enums import CompanionKey, ForestSection
from features.stories.dungeon_run import DungeonRun, RoomSelectionView
from features.stories.forest.combat.quiet_grove.bridge_golem_duel import BridgeGolemDuelView
from features.stories.forest.combat.quiet_grove.brigand_mystic_duel import BrigandMysticDuelView
from features.stories.forest.combat.quiet_grove.deepwood_bear_duel import BearDuelView
from features.stories.forest.combat.quiet_grove.evoker_brigand_thief_duel import EvokerBrigandThiefDuelView
from features.stories.forest.combat.quiet_grove.evoker_mystic_duel import EvokerMysticDuelView
from features.stories.forest.combat.quiet_grove.giant_snake_duel import GiantSnakeDuelView
from features.stories.forest.combat.quiet_grove.thief_marauder_duel import ThiefMarauderDuelView
from features.stories.forest.combat.quiet_grove.timberwolves_duel import TimberwolvesDuelView
from features.stories.forest.combat.quiet_grove.triple_snake_duel import TripleSnakeDuelView
from features.stories.forest.combat.quiet_grove.wild_boar_duel import WildBoarDuelView
from features.stories.forest.combat.screaming_copse.briar_wall_duel import BriarWallDuelView
from features.stories.forest.combat.screaming_copse.horrifying_bone_amalgam_duel import HorrifyingBoneAmalgamDuelView
from features.stories.forest.combat.screaming_copse.starving_dire_wolves_duel import StarvingDireWolvesDuelView
from features.stories.forest.combat.screaming_copse.undead_treants_duel import UndeadTreantsDuelView
from features.stories.forest.combat.screaming_copse.voidburnt_treant_duel import VoidburntTreantDuelView
from features.stories.forest.combat.screaming_copse.wailing_bones_duel import WailingBonesDuelView
from features.stories.forest.combat.whispering_woods.armored_centipede_duel import ArmoredCentipedeDuelView
from features.stories.forest.combat.whispering_woods.bladedancer_stormcaller_duel import BladedancerStormcallerDuelView
from features.stories.forest.combat.whispering_woods.dire_wolves_duel import DireWolvesDuelView
from features.stories.forest.combat.whispering_woods.double_shadowsneak_duel import DoubleShadowsneakDuelView
from features.stories.forest.combat.whispering_woods.fleeing_treant_duel import FleeingTreantDuelView
from features.stories.forest.combat.whispering_woods.ironbound_bladedancer_duel import IronboundBladedancerDuelView
from features.stories.forest.combat.whispering_woods.lifestitcher_ironbound_duel import LifestitcherIronboundDuelView
from features.stories.forest.combat.whispering_woods.lifestitcher_shadowsneak_duel import LifestitcherShadowsneakDuelView
from features.stories.forest.combat.whispering_woods.mad_knights_duel import MadKnightsDuelView
from features.stories.forest.combat.whispering_woods.treants_duel import TreantsDuelView
from features.stories.forest.combat.whispering_woods.triple_stormcaller_duel import TripleStormcallerDuelView
from features.stories.forest.events.quiet_grove.aestival_light import AestivalLightView
from features.stories.forest.events.quiet_grove.camp_of_fools import CampOfFoolsView
from features.stories.forest.events.quiet_grove.fishing_pond import QuietGroveFishingPondView
from features.stories.forest.events.quiet_grove.jackalope import JackalopeView
from features.stories.forest.events.quiet_grove.the_path_is_lost import ThePathIsLostView
from features.stories.forest.events.quiet_grove.wandering_cook import WanderingCookView
from features.stories.forest.events.quiet_grove.wild_herbs import QuietGroveWildHerbsView
from features.stories.forest.events.quiet_grove.wildlife_gathering import WildlifeGatheringView
from features.stories.forest.events.screaming_copse.a_nearby_roar import ANearbyRoarView
from features.stories.forest.events.screaming_copse.dangerous_undergrowth import DangerousUndergrowthView
from features.stories.forest.events.screaming_copse.dark_between_the_stars import DarkBetweenTheStarsView
from features.stories.forest.events.screaming_copse.fishing_pond import ScreamingCopseFishingPondView
from features.stories.forest.events.screaming_copse.hallucinatory_smoke import HallucinatorySmokeView
from features.stories.forest.events.screaming_copse.stagnant_water import StagnantWaterView
from features.stories.forest.events.screaming_copse.sword_in_an_old_bonfire import SwordInAnOldBonfireView
from features.stories.forest.events.screaming_copse.wild_herbs import ScreamingCopseWildHerbsView
from features.stories.forest.events.whispering_woods.chorus_of_the_wind import ChorusOfTheWindView
from features.stories.forest.events.whispering_woods.colorful_mushrooms import ColorfulMushroomsView
from features.stories.forest.events.whispering_woods.fishing_pond import WhisperingWoodsFishingPondView
from features.stories.forest.events.whispering_woods.form_in_the_fog import FormInTheFogView
from features.stories.forest.events.whispering_woods.omen_of_disaster import OmenOfDisasterView
from features.stories.forest.events.whispering_woods.petrifying_plant import PetrifyingPlantView
from features.stories.forest.events.whispering_woods.riddle_bird import RiddleBirdView
from features.stories.forest.events.whispering_woods.the_sound import TheSoundView
from features.stories.forest.events.whispering_woods.unnamed_grave import UnnamedGraveView
from features.stories.forest.events.whispering_woods.wild_herbs import WhisperingWoodsWildHerbsView
from features.stories.forest.events.whispering_woods.witch_of_the_woods import WitchOfTheWoodsView
from features.stories.forest.treasure.quiet_grove_treasure import QuietGroveTreasureRoomView
from features.stories.forest.treasure.screaming_copse_treasure import ScreamingCopseTreasureRoomView
from features.stories.forest.treasure.whispering_woods_treasure import WhisperingWoodsTreasureRoomView
from features.stories.story import Story

from typing import List, Set

# -----------------------------------------------------------------------------
# FOREST DEFEAT VIEW
# -----------------------------------------------------------------------------

class ForestDefeatView(discord.ui.View):
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

    def get_initial_embed(self):
        post_run_info_str: str = self._generate_run_info()
        return Embed(title="Flee the Forest", description=f"With your party defeated, you all flee the forest barely alive.\n\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\n{post_run_info_str}")

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
# FOREST REST VIEW
# -----------------------------------------------------------------------------

class RestContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: ForestRestView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        for player in view.get_players():
            player.set_is_in_rest_area(False)

        room_selection_view: RoomSelectionView = RoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class ForestRestButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Rest")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: ForestRestView = self.view
        if interaction.user not in view.rested_users:
            response = view.rest(interaction.user)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ForestRestView(discord.ui.View):
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
        return Embed(title="A Warm Bonfire", description=f"You all gather around a fire and can rest for a moment among the trees, restoring 50% of your health and mana.\n\n{len(self.rested_users)}/{len(self._users)} players have rested.{additional_info}")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(ForestRestButton())
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
        if random.random() < 0.0002:
            companions = player.get_companions()
            if random.random() < 0.5:
                if CompanionKey.VoidseenCat not in companions.companions.keys():
                    companions.companions[CompanionKey.VoidseenCat] = features.companions.companion.VoidseenCatCompanion()
                    companions.companions[CompanionKey.VoidseenCat].set_id(player.get_id())
                    companion_result_str += "\n\nIn your sleep, amid nightmares that seem far too real, you awake with a start to find something curled up beside your feet. A small cat, fur dark as the night, with beautiful eyes shimmering white with shards of color dancing in the irises. It purrs and calms you, driving away the fear you felt from the dreams. It's been added as a companion in b!companions."

                    player.get_stats().companions.companions_found += 1
            else:
                if CompanionKey.VoidseenPup not in companions.companions.keys():
                    companions.companions[CompanionKey.VoidseenPup] = features.companions.companion.VoidseenPupCompanion()
                    companions.companions[CompanionKey.VoidseenPup].set_id(player.get_id())
                    companion_result_str += "\n\nIn your sleep, amid nightmares that seem far too real, you awake with a start to find something curled up beside your feet. A small pup, fur dark as the night, with beautiful eyes shimmering white with shards of color dancing in the irises. It looks up at you, one ear floppy the other pointed straight up, then nuzzles you with its nose. Your newfound companion brings a profound sense of calm, driving away the terrifying dreams. It's been added as a companion in b!companions."

                    player.get_stats().companions.companions_found += 1

        self.rested_users.append(user)

        return self.get_initial_embed(companion_result_str)

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
# QUIET GROVE ENTRANCE VIEW
# -----------------------------------------------------------------------------

class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: QuietGroveEntranceView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(embed=view.get_initial_embed(), content="Error: You aren't the group leader and can't continue to the next room!", view=view)
            return
        
        room_select_view: RoomSelectionView = RoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_select_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_select_view, content=None)


class QuietGroveEntranceView(discord.ui.View):
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
        return Embed(title="The Quiet Grove", description="The wind stirs through the expanse of trees in this first section of the forest as you all prepare to journey forwards. Soft chirping from birds and rustling in the bushes pervades the air with a normal tranquility that forests often invite.\n\nThough this journey will certainly be rife with dangers, from wild animals to bandits, the path ahead to the bridge into the deeper woods beyond is clear.\n\nIt's time for the adventure to begin!")

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
# FOREST DUNGEON ENTRANCE VIEW
# -----------------------------------------------------------------------------

class StartButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.green, label="Start")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: ForestDungeonEntranceView = self.view

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
            player.set_is_in_dungeon_run(True)

        entrance_view: QuietGroveEntranceView = QuietGroveEntranceView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = entrance_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=entrance_view, content=None)


class AcceptButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Accept")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: ForestDungeonEntranceView = self.view
        view.accepted_users.add(interaction.user.id)
        await interaction.response.edit_message(embed=view.get_initial_embed(), view=view, content=None)


class ForestDungeonEntranceView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User]):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = DungeonRun(Story.Forest, FOREST_ROOMS, ForestSection.QuietGrove)
        
        self.accepted_users: Set[int] = set()

        self._display_initial_buttons()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_initial_embed(self):
        if len(self._users) == len(self.accepted_users):
            self.clear_items()
            self.add_item(StartButton())

        return Embed(title="The Forest", description=f"Standing before the entrance to the old woods, your party stares down the path into the seemingly endless expanse of trees.\n\nYour group leader is {self._group_leader.display_name}. When your party is ready, you may enter the forest.\n\n{len(self.accepted_users)}/{len(self._users)} are ready to begin the journey.")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(AcceptButton())

    def any_in_duels_currently(self):
        return any(self._get_player(user.id).get_dueling().is_in_combat for user in self._users)

    def any_in_dungeons_currently(self):
        return any(self._get_player(user.id).is_in_dungeon_run() for user in self._users)

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
# FOREST STORY CLASS
# -----------------------------------------------------------------------------

class ForestStory():
    def __init__(self):
        pass

    @staticmethod
    def generate_shopkeep_room(bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        return MysteriousMerchantView(bot, database, guild_id, users, dungeon_run)

    @staticmethod
    def generate_rest_room(bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        return ForestRestView(bot, database, guild_id, users, dungeon_run)
    
    @staticmethod
    def generate_treasure_room(bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        if dungeon_run.section == ForestSection.ScreamingCopse:
            return ScreamingCopseTreasureRoomView(bot, database, guild_id, users, dungeon_run)
        elif dungeon_run.section == ForestSection.WhisperingWoods:
            return WhisperingWoodsTreasureRoomView(bot, database, guild_id, users, dungeon_run)
        else:
            return QuietGroveTreasureRoomView(bot, database, guild_id, users, dungeon_run)

    @staticmethod
    def generate_combat_room(bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        if dungeon_run.section == ForestSection.QuietGrove:
            rand_val: int = random.randint(0, 8)
            if rand_val == 0:
                return BrigandMysticDuelView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 1:
                return BearDuelView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 2:
                return EvokerBrigandThiefDuelView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 3:
                return EvokerMysticDuelView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 4:
                return GiantSnakeDuelView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 5:
                return ThiefMarauderDuelView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 6:
                return TimberwolvesDuelView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 7:
                return TripleSnakeDuelView(bot, database, guild_id, users, dungeon_run)
            else:
                return WildBoarDuelView(bot, database, guild_id, users, dungeon_run)
        elif dungeon_run.section == ForestSection.WhisperingWoods:
            rand_val: int = random.randint(0, 9)
            if rand_val == 0:
                return ArmoredCentipedeDuelView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 1:
                return BladedancerStormcallerDuelView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 2:
                return DireWolvesDuelView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 3:
                return DoubleShadowsneakDuelView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 4:
                return IronboundBladedancerDuelView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 5:
                return LifestitcherIronboundDuelView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 6:
                return LifestitcherShadowsneakDuelView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 7:
                return MadKnightsDuelView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 8:
                return TreantsDuelView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 9:
                return TripleStormcallerDuelView(bot, database, guild_id, users, dungeon_run)
        elif dungeon_run.section == ForestSection.ScreamingCopse:
            rand_val: int = random.randint(0, 4)
            if rand_val == 0:
                return HorrifyingBoneAmalgamDuelView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 1:
                return StarvingDireWolvesDuelView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 2:
                return UndeadTreantsDuelView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 3:
                return VoidburntTreantDuelView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 4:
                return WailingBonesDuelView(bot, database, guild_id, users, dungeon_run)

    @staticmethod
    def generate_event_room(bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        if dungeon_run.section == ForestSection.QuietGrove:
            rand_val: int = random.randint(0, 7)
            if rand_val == 0:
                return AestivalLightView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 1:
                return CampOfFoolsView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 2:
                return QuietGroveFishingPondView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 3:
                return JackalopeView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 4:
                return ThePathIsLostView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 5:
                return WanderingCookView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 6:
                return QuietGroveWildHerbsView(bot, database, guild_id, users, dungeon_run)
            else:
                return WildlifeGatheringView(bot, database, guild_id, users, dungeon_run)
        elif dungeon_run.section == ForestSection.WhisperingWoods:
            rand_val = random.randint(0, 10)
            if rand_val == 0:
                return ChorusOfTheWindView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 1:
                return ColorfulMushroomsView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 2:
                return WhisperingWoodsFishingPondView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 3:
                return FormInTheFogView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 4:
                return OmenOfDisasterView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 5:
                return PetrifyingPlantView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 6:
                return RiddleBirdView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 7:
                return TheSoundView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 8:
                return UnnamedGraveView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 9:
                return WhisperingWoodsWildHerbsView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 10:
                return WitchOfTheWoodsView(bot, database, guild_id, users, dungeon_run)
        elif dungeon_run.section == ForestSection.ScreamingCopse:
            rand_val = random.randint(0, 7)
            if rand_val == 0:
                return ANearbyRoarView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 1:
                return DangerousUndergrowthView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 2:
                return DarkBetweenTheStarsView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 3:
                return ScreamingCopseFishingPondView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 4:
                return HallucinatorySmokeView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 5:
                return StagnantWaterView(bot, database, guild_id, users, dungeon_run)
            elif rand_val == 6:
                return SwordInAnOldBonfireView(bot, database, guild_id, users, dungeon_run)
            else:
                return ScreamingCopseWildHerbsView(bot, database, guild_id, users, dungeon_run)

    @staticmethod
    def generate_boss_room(bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        if dungeon_run.section == ForestSection.QuietGrove:
            return BridgeGolemDuelView(bot, database, guild_id, users, dungeon_run)
        elif dungeon_run.section == ForestSection.WhisperingWoods:
            return FleeingTreantDuelView(bot, database, guild_id, users, dungeon_run)
        elif dungeon_run.section == ForestSection.ScreamingCopse:
            return BriarWallDuelView(bot, database, guild_id, users, dungeon_run)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        pass
