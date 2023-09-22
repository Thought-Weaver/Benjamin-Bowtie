from __future__ import annotations

import datetime
import discord
import features.companions.companion
import random

from bot import BenjaminBowtieBot
from discord.ext import commands
from features.shared.constants import UNDERWORLD_ROOMS
from features.shared.enums import CompanionKey, UnderworldSection
from features.shared.item import LOADED_ITEMS, ItemKey
from features.stories.dungeon_run import DungeonRun
from features.stories.story import Story
from features.stories.underworld.combat.fungal_caverns.agaric_alchemists_duel import AgaricAlchemistsDuelView
from features.stories.underworld.combat.fungal_caverns.blind_salamander_duel import BlindSalamanderDuelView
from features.stories.underworld.combat.fungal_caverns.chanterspell_duel import ChanterspellDuelView
from features.stories.underworld.combat.fungal_caverns.deathless_caps_duel import DeathlessCapsDuelView
from features.stories.underworld.combat.fungal_caverns.glowing_moss_duel import GlowingMossDuelView
from features.stories.underworld.combat.fungal_caverns.hen_of_the_caverns_duel import HenOfTheCavernsDuelView
from features.stories.underworld.combat.fungal_caverns.malevolent_morel_duel import MalevolentMorelDuelView
from features.stories.underworld.combat.fungal_caverns.mushroom_maze import MushroomMazeDuelView, TombsIngressIntroView
from features.stories.underworld.combat.fungal_caverns.mycelium_tree_duel import MyceliumTreeDuelView
from features.stories.underworld.combat.misty_tunnels.breath_of_darkness_duel import BreathOfDarknessDuelView
from features.stories.underworld.combat.misty_tunnels.choking_fog_duel import ChokingFogDuelView
from features.stories.underworld.combat.misty_tunnels.ichordrink_bats_duel import IchordrinkBatsDuelView
from features.stories.underworld.combat.misty_tunnels.misty_apparition_duel import MistyApparitionDuelView
from features.stories.underworld.combat.misty_tunnels.pale_widows_duel import PaleWidowDuelView
from features.stories.underworld.combat.misty_tunnels.scuttledark_scorpion_duel import ScuttledarkScorpionDuelView
from features.stories.underworld.combat.misty_tunnels.stonewalker_duel import StonewalkerDuelView
from features.stories.underworld.combat.misty_tunnels.tunneldigger_duel import FungalCavernsIntroView, TunneldiggerDuelView
from features.stories.underworld.combat.misty_tunnels.winding_tunnels_duel import WindingTunnelsDuelView
from features.stories.underworld.combat.tombs_ingress.cultists_of_avarice_duel import CultistsOfAvariceDuelView
from features.stories.underworld.combat.tombs_ingress.eyeless_echoes_duel import EyelessEchoesDuelView
from features.stories.underworld.combat.tombs_ingress.molten_gold_duel import MoltenGoldDuelView
from features.stories.underworld.combat.tombs_ingress.quaking_tunnels import QuakingTunnelsDuelView
from features.stories.underworld.combat.tombs_ingress.scratches_on_the_wall_duel import ScratchesOnTheWallDuelView
from features.stories.underworld.combat.tombs_ingress.timelost_echo_duel import TimelostEchoDuelView
from features.stories.underworld.combat.tombs_ingress.tomb_guardians_duel import TombGuardiansDuelView
from features.stories.underworld.combat.tombs_ingress.warping_anomaly_duel import WarpingAnomalyDuelView
from features.stories.underworld.combat.tombs_ingress.waylaid_chest_duel import WaylaidChestDuelView
from features.stories.underworld.events.fungal_caverns.crimson_rot import CrimsonRotView
from features.stories.underworld.events.fungal_caverns.deep_hole import DeepHoleView
from features.stories.underworld.events.fungal_caverns.dense_clusters import DenseClustersView
from features.stories.underworld.events.fungal_caverns.grand_mushroom_staff import GrandMushroomStaffView
from features.stories.underworld.events.fungal_caverns.mushroom_grove import MushroomGroveView
from features.stories.underworld.events.fungal_caverns.ore_vein import FungalCavernsOreVeinView
from features.stories.underworld.events.fungal_caverns.purple_cloud import PurpleCloudView
from features.stories.underworld.events.fungal_caverns.underground_lake import FungalCavernsUndergroundLakeView
from features.stories.underworld.events.misty_tunnels.crack_in_the_wall import CrackInTheWallView
from features.stories.underworld.events.misty_tunnels.dead_spelunker import DeadSpelunkerView
from features.stories.underworld.events.misty_tunnels.form_in_the_fog import FormInTheFogView
from features.stories.underworld.events.misty_tunnels.ore_vein import MistyTunnelsOreVeinView
from features.stories.underworld.events.misty_tunnels.spider_nest import SpiderNestView
from features.stories.underworld.events.misty_tunnels.torches_go_out import TorchesGoOutView
from features.stories.underworld.events.misty_tunnels.underground_lake import MistyTunnelsUndergroundLakeView
from features.stories.underworld.events.tombs_ingress.arcane_traps import ArcaneTrapsView
from features.stories.underworld.events.tombs_ingress.echo_of_knowledge import EchoOfKnowledgeView
from features.stories.underworld.events.tombs_ingress.golden_idol import GoldenIdolView
from features.stories.underworld.events.tombs_ingress.heavy_stone_door import HeavyStoneDoorView
from features.stories.underworld.events.tombs_ingress.old_notes import OldNotesView
from features.stories.underworld.events.tombs_ingress.ore_vein import TombsIngressOreVeinView
from features.stories.underworld.events.tombs_ingress.supply_room import SupplyRoomView
from features.stories.underworld.events.tombs_ingress.underground_lake import TombsIngressUndergroundLakeView
from features.stories.underworld.merchant.mysterious_merchant import MysteriousMerchantView
from features.stories.underworld.treasure.fungal_caverns_treasure import FungalCavernsTreasureRoomView
from features.stories.underworld.treasure.misty_tunnels_treasure import MistyTunnelsTreasureRoomView
from features.stories.underworld.treasure.tombs_ingress_treasure import TombsIngressTreasureRoomView
from features.stories.underworld_room_selection import UnderworldRoomSelectionView

from typing import List, TYPE_CHECKING, Set, Tuple
if TYPE_CHECKING:
    from features.player import Player
    from features.stats import Stats

# -----------------------------------------------------------------------------
# UNDERWORLD DEFEAT VIEW
# -----------------------------------------------------------------------------

class UnderworldDefeatView(discord.ui.View):
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
        
        return discord.Embed(title="Away from the Darkness", description=f"With your party defeated, you all flee the caves barely alive.\n\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\n{post_run_info_str}")

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
# UNDERWORLD REST VIEW
# -----------------------------------------------------------------------------

class RestContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: UnderworldRestView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        for player in view.get_players():
            player.get_dungeon_run().in_rest_area = False

        room_selection_view = UnderworldRoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: discord.Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class UnderworldRestButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Rest")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: UnderworldRestView = self.view
        if interaction.user not in view.rested_users:
            response = view.rest(interaction.user) # type: ignore
            await interaction.response.edit_message(content=None, embed=response, view=view)


class UnderworldRestView(discord.ui.View):
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
        return discord.Embed(title="A Quiet Nook", description=f"Nestled within the stone, you find a small, isolated cave where you can rest for a time, restoring 50% of your health and mana.\n\n{len(self.rested_users)}/{len(self._users)} players have rested.{additional_info}")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(UnderworldRestButton())
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
                    companion_result_str += "\n\nIn your sleep, amid nightmares that seem far too real, you awake with a start to find something curled up beside your feet. A small cat, fur dark as the night, with beautiful eyes shimmering white with shards of color dancing in the irises. It purrs and calms you, driving away the fear you felt from the dreams. It's been added as a companion in b!companions."

                    player.get_stats().companions.companions_found += 1
            else:
                if CompanionKey.VoidseenPup not in companions.companions.keys():
                    companions.companions[CompanionKey.VoidseenPup] = features.companions.companion.VoidseenPupCompanion()
                    companions.companions[CompanionKey.VoidseenPup].set_id(player.get_id())
                    companion_result_str += "\n\nIn your sleep, amid nightmares that seem far too real, you awake with a start to find something curled up beside your feet. A small pup, fur dark as the night, with beautiful eyes shimmering white with shards of color dancing in the irises. It looks up at you, one ear floppy the other pointed straight up, then nuzzles you with its nose. Your newfound companion brings a profound sense of calm, driving away the terrifying dreams. It's been added as a companion in b!companions."

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
# MISTY TUNNELS ENTRANCE VIEW
# -----------------------------------------------------------------------------

class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")
    
    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: MistyTunnelsEntranceView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(embed=view.get_initial_embed(), content="Error: You aren't the group leader and can't continue to the next room!", view=view)
            return
        
        room_select_view = UnderworldRoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: discord.Embed = room_select_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_select_view, content=None)


class MistyTunnelsEntranceView(discord.ui.View):
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
        return discord.Embed(title="Misty Tunnels", description="The seaside cave entrance has a presence you can't quite understand. Something deeper within awaits you all -- something powerful sealed away by the Fellowship ages ago. Mists rise to meet you as you all prepare to set forth.")

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
# UNDERWORLD DUNGEON ENTRANCE VIEW
# -----------------------------------------------------------------------------

class StartButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.green, label="Start")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: UnderworldDungeonEntranceView = self.view

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

        for user in view.get_users():
            await user.send((
                "Earlier this same night, Quinan came over to your table and with a glassy look in her eyes whispered in your ear, \"Go to the back room.\" Curious, you ventured into the darkness where you could hear the sound of knucklebones being played. The door, further down the hall than you think the tavern is long, opened of its own accord.\n\n"
                "Sitting there, enrobed in the shadows, was Mr. Bones. With a raspy voice like rusted metal on stone, it addressed you, \"She... will... tell... you... lies...\" And then straightening in its chair, with more vigor it continued, \"My master does not deserve the chains. Set free. Rewards uncountable will be yours.\" With that request, you found yourself outside the room and looking over your back saw the door was gone."
            ))

        starting_section: UnderworldSection | None = view.get_starting_section()
        if starting_section is None or starting_section == UnderworldSection.MistyTunnels:
            mt_entrance_view: MistyTunnelsEntranceView = MistyTunnelsEntranceView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
            initial_info: discord.Embed = mt_entrance_view.get_initial_embed()

            await interaction.response.edit_message(embed=initial_info, view=mt_entrance_view, content=None)
        elif starting_section == UnderworldSection.FungalCaverns:
            fc_entrance_view: FungalCavernsIntroView = FungalCavernsIntroView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
            initial_info: discord.Embed = fc_entrance_view.get_initial_embed()

            await interaction.response.edit_message(embed=initial_info, view=fc_entrance_view, content=None)
        elif starting_section == UnderworldSection.TombsIngress:
            ti_entrance_view: TombsIngressIntroView = TombsIngressIntroView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
            initial_info: discord.Embed = ti_entrance_view.get_initial_embed()

            await interaction.response.edit_message(embed=initial_info, view=ti_entrance_view, content=None)


class AcceptButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Accept")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: UnderworldDungeonEntranceView = self.view
        view.accepted_users.add(interaction.user.id)
        await interaction.response.edit_message(embed=view.get_initial_embed(), view=view, content=None)


class UnderworldDungeonEntranceView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, context: commands.Context, database: dict, guild_id: int, users: List[discord.User], starting_section: UnderworldSection | None):
        super().__init__(timeout=900)

        self._bot = bot
        self._context = context
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = DungeonRun(Story.Underworld, UNDERWORLD_ROOMS, starting_section if starting_section is not None else UnderworldSection.MistyTunnels)
        self._starting_section = starting_section
        
        self.accepted_users: Set[int] = set()

        self._display_initial_buttons()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def _td_format(self, td_object):
        seconds = int(td_object.total_seconds())
        periods = [
            ('year',        60*60*24*365),
            ('month',       60*60*24*30),
            ('day',         60*60*24),
            ('hour',        60*60),
            ('minute',      60),
            ('second',      1)
        ]

        strings=[]
        for period_name, period_seconds in periods:
            if seconds > period_seconds:
                period_value, seconds = divmod(seconds, period_seconds)
                has_s = 's' if period_value > 1 else ''
                strings.append("%s %s%s" % (period_value, period_name, has_s))

        # Take only the top two for better formatting
        return ", ".join(strings[:2])

    def get_initial_embed(self):
        if len(self._users) == len(self.accepted_users):
            self.clear_items()
            self.add_item(StartButton())

        joined_at: datetime.datetime = self._context.guild.get_member(self._bot.user.id).joined_at # type: ignore
        time_in_server = datetime.datetime.now() - joined_at.replace(tzinfo=None)
        village_existence_str = self._td_format(time_in_server)

        return discord.Embed(title="The Underworld", description=(
            "Late into the evening, as you're enjoying some time at the tavern, the doors are opened carefully and quietly. Who should step through but Yenna, with a look of concern clear on her face. She beckons you all to come to her tent for a discussion of grave importance.\n\n"
            "The candles shed little light in the interior of her home, creating a distinctly ominous atmosphere. \"I have spoken little of my past since I arrived in this village, as a matter of caution,\" she says slowly, \"But having seen your journeys so far and since you traveled from elsewhere to this place, I believe I can trust you.\"\n\n"
            "She takes out her cards and shuffles them, then places three in front of you. She flips the first over: The Fool, a symbol of failure and mockery. \"I was once part of a group called the Fellowship of the Eyeless, who swore to work in secret and protect people against the things beyond the pale, from the Dreaming and the Dark Between the Stars.\"\n\n"
            "Behind her, a vignette of shadows begins to play as she speaks, \"We ventured below, into the Sunless Underworld, only to find people and a being of terrifying power. I... barely made it out alive. Most of the rest didn't. Luckily, a mage we brought with us was adept in timeweaving and was able to seal it away, though we could not defeat it entirely.\"\n\n"
            "She flips over the next card, staring into you though you cannot see beneath her hood: The Dreamer, a symbol of mystery and ambition. \"But it wasn't permanent. Something has been stirring below the earth and I fear it will soon break free.\"\n\n"
            f"\"Though I was loath to ever return here, when I heard of something new appearing in this same place, I knew I had to investigate. That something was this very village -- it came into existence {village_existence_str} ago, out of nowhere.\"\n\n"
            "She flips over the last card, a solemn tone in her voice: The Void, a symbol of destruction and endings. \"What I ask you now is to do what we could not, to face this thing while it's still chained below the world and destroy it. I don't know if it can be done, but someone has to try or I fear for what it will unleash upon us all.\"\n\n"
            "**Recommendations:**\n\n_Misty Tunnels: 4+ Players (Lvl. 60-70)_\n_Fungal Caverns: 4+ Players (Lvl. 70-80)_\n_Tomb's Ingress: 4+ Players (Lvl. 80-90)_\n_Final Boss: 4+ Players (Lvl. 90-100)_\n\n"
            f"Your group leader is {self._group_leader.display_name}. When your party is ready, you may enter the caves.\n\n"
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
# UNDERWORLD STORY CLASS
# -----------------------------------------------------------------------------

class UnderworldStory():
    def __init__(self):
        self._something_stirs: int = 0
        self.remaining_sunless_keys: List[ItemKey] = [
            ItemKey.SunlessStride,
            ItemKey.SunlessChains,
            ItemKey.SunlessGrip,
            ItemKey.SunlessSteps,
            ItemKey.SunlessMind,
            ItemKey.SunlessHeart,
            ItemKey.SunlessWill
        ]
        self.first_to_stir_id: int = -1

    def get_wishing_well_response(self, user_id: int, player_stats: Stats):
        embed = discord.Embed(
            title="You toss the coin in...",
            description="It plummets into the darkness below and hits the bottom with a resounding clink."
        )
        if self._something_stirs == 0:
            self.first_to_stir_id = user_id
            embed = discord.Embed(
                title="You toss the coin in...",
                description=(
                    "It plummets into the darkness below. "
                    "Down, down it goes -- past the bottom of the well, through rock and flowing fire into deeper darkness still, down into a place the living believe only superstition.\n\n"
                    "Somewhere deep in the sunless underworld... something stirs."
                )
            )
        elif player_stats.wishingwell.something_stirs == 0:
            embed = discord.Embed(
                title="You toss the coin in...",
                description=(
                    "It plummets into the darkness below. "
                    "The coin of someone else, yes, but it too slips beyond the material into the shadows. There is no sound to you above; it is simply gone in a haunting silence.\n\n"
                    "Somewhere deep in the sunless underworld... something stirs."
                )
            )
        else:
            embed = discord.Embed(
                title="You toss the coin in...",
                description=(
                    "It plummets into the darkness below. "
                    "You've come again. And your coin, like the other before it, descends descends descends. The darkness grabs it close, pulling the coin quickly towards its inevitable destination.\n\n"
                    "Somewhere deep in the sunless underworld... something stirs."
                )
            )

        self._something_stirs += 1
        return embed

    def get_wishing_well_item(self):
        if len(self.remaining_sunless_keys) > 0:
            rand_index: int = random.randint(0, max(0, len(self.remaining_sunless_keys) - 1))
            item_key: ItemKey = self.remaining_sunless_keys.pop(rand_index)

            return LOADED_ITEMS.get_new_item(item_key)
        else:
            rand_key = random.choices(
                [
                    ItemKey.CrackedAgate, ItemKey.CrackedAmethyst, ItemKey.CrackedBloodstone, ItemKey.CrackedDiamond,
                    ItemKey.CrackedEmerald, ItemKey.CrackedJade, ItemKey.CrackedLapis, ItemKey.CrackedMalachite,
                    ItemKey.CrackedMoonstone, ItemKey.CrackedOpal, ItemKey.CrackedOnyx, ItemKey.CrackedPeridot,
                    ItemKey.CrackedQuartz, ItemKey.CrackedRuby, ItemKey.CrackedSapphire, ItemKey.CrackedTanzanite,
                    ItemKey.CrackedTopaz, ItemKey.CrackedTurquoise, ItemKey.CrackedZircon,

                    ItemKey.Agate, ItemKey.Amethyst, ItemKey.Bloodstone, ItemKey.Diamond,
                    ItemKey.Emerald, ItemKey.Jade, ItemKey.Lapis, ItemKey.Malachite,
                    ItemKey.Moonstone, ItemKey.Opal, ItemKey.Onyx, ItemKey.Peridot,
                    ItemKey.Quartz, ItemKey.Ruby, ItemKey.Sapphire, ItemKey.Tanzanite,
                    ItemKey.Topaz, ItemKey.Turquoise, ItemKey.Zircon,
                    
                    ItemKey.FlawlessAgate, ItemKey.FlawlessAmethyst, ItemKey.FlawlessBloodstone, ItemKey.FlawlessDiamond,
                    ItemKey.FlawlessEmerald, ItemKey.FlawlessJade, ItemKey.FlawlessLapis, ItemKey.FlawlessMalachite,
                    ItemKey.FlawlessMoonstone, ItemKey.FlawlessOpal, ItemKey.FlawlessOnyx, ItemKey.FlawlessPeridot,
                    ItemKey.FlawlessQuartz, ItemKey.FlawlessRuby, ItemKey.FlawlessSapphire, ItemKey.FlawlessTanzanite,
                    ItemKey.FlawlessTopaz, ItemKey.FlawlessTurquoise, ItemKey.FlawlessZircon
                ], 
                k=1,
                weights=[
                    0.035 * 2/76, 0.035 * 5/76, 0.035 * 6/76, 0.035 * 3/76,
                    0.035 * 7/76, 0.035 * 6/76, 0.035 * 1/76, 0.035 * 4/76,
                    0.035 * 2/76, 0.035 * 2/76, 0.035 * 2/76, 0.035 * 8/76,
                    0.035 * 10/76, 0.035 * 1/76, 0.035 * 1/76, 0.035 * 2/76,
                    0.035 * 1/76, 0.035 * 6/76, 0.035 * 5/76,

                    0.01 * 2/76, 0.01 * 5/76, 0.01 * 6/76, 0.01 * 3/76,
                    0.01 * 7/76, 0.01 * 6/76, 0.01 * 1/76, 0.01 * 4/76,
                    0.01 * 2/76, 0.01 * 2/76, 0.01 * 2/76, 0.01 * 8/76,
                    0.01 * 10/76, 0.01 * 1/76, 0.01 * 1/76, 0.01 * 2/76,
                    0.01 * 1/76, 0.01 * 6/76, 0.01 * 5/76,

                    0.005 * 2/76, 0.005 * 5/76, 0.005 * 6/76, 0.005 * 3/76,
                    0.005 * 7/76, 0.005 * 6/76, 0.005 * 1/76, 0.005 * 4/76,
                    0.005 * 2/76, 0.005 * 2/76, 0.005 * 2/76, 0.005 * 8/76,
                    0.005 * 10/76, 0.005 * 1/76, 0.005 * 1/76, 0.005 * 2/76,
                    0.005 * 1/76, 0.005 * 6/76, 0.005 * 5/76,
                ]
            )[0]
            return LOADED_ITEMS.get_new_item(rand_key)

    @staticmethod
    def generate_shopkeep_room(bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        return MysteriousMerchantView(bot, database, guild_id, users, dungeon_run)

    @staticmethod
    def generate_rest_room(bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        return UnderworldRestView(bot, database, guild_id, users, dungeon_run)
    
    @staticmethod
    def generate_treasure_room(bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        if dungeon_run.section == UnderworldSection.MistyTunnels:
            return MistyTunnelsTreasureRoomView(bot, database, guild_id, users, dungeon_run)
        elif dungeon_run.section == UnderworldSection.FungalCaverns:
            return FungalCavernsTreasureRoomView(bot, database, guild_id, users, dungeon_run)
        else:
            return TombsIngressTreasureRoomView(bot, database, guild_id, users, dungeon_run)

    @staticmethod
    def generate_combat_room(bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun) -> Tuple[discord.ui.View, int]:
        if dungeon_run.section == UnderworldSection.MistyTunnels:
            rand_val: int = random.choice([i for i in range(0, 8) if i != dungeon_run.previous_event])
            if rand_val == 0:
                return BreathOfDarknessDuelView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 1:
                return ChokingFogDuelView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 2:
                return IchordrinkBatsDuelView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 3:
                return MistyApparitionDuelView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 4:
                return PaleWidowDuelView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 5:
                return ScuttledarkScorpionDuelView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 6:
                return StonewalkerDuelView(bot, database, guild_id, users, dungeon_run), rand_val
            else:
                return WindingTunnelsDuelView(bot, database, guild_id, users, dungeon_run), rand_val
        elif dungeon_run.section == UnderworldSection.FungalCaverns:
            rand_val: int = random.choice([i for i in range(0, 8) if i != dungeon_run.previous_event])
            if rand_val == 0:
                return AgaricAlchemistsDuelView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 1:
                return BlindSalamanderDuelView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 2:
                return ChanterspellDuelView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 3:
                return DeathlessCapsDuelView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 4:
                return GlowingMossDuelView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 5:
                return HenOfTheCavernsDuelView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 6:
                return MalevolentMorelDuelView(bot, database, guild_id, users, dungeon_run), rand_val
            else:
                return MyceliumTreeDuelView(bot, database, guild_id, users, dungeon_run), rand_val
        else:
            rand_val: int = random.choice([i for i in range(0, 8) if i != dungeon_run.previous_event])
            if rand_val == 0:
                return CultistsOfAvariceDuelView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 1:
                return MoltenGoldDuelView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 2:
                return QuakingTunnelsDuelView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 3:
                return ScratchesOnTheWallDuelView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 4:
                return TimelostEchoDuelView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 5:
                return TombGuardiansDuelView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 6:
                return WarpingAnomalyDuelView(bot, database, guild_id, users, dungeon_run), rand_val
            else:
                return WaylaidChestDuelView(bot, database, guild_id, users, dungeon_run), rand_val

    @staticmethod
    def generate_event_room(bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun) -> Tuple[discord.ui.View, int]:
        if dungeon_run.section == UnderworldSection.MistyTunnels:
            rand_val: int = random.choice([i for i in range(0, 7) if i != dungeon_run.previous_event])
            if rand_val == 0:
                return CrackInTheWallView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 1:
                return DeadSpelunkerView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 2:
                return FormInTheFogView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 3:
                return MistyTunnelsOreVeinView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 4:
                return SpiderNestView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 5:
                return TorchesGoOutView(bot, database, guild_id, users, dungeon_run), rand_val
            else:
                return MistyTunnelsUndergroundLakeView(bot, database, guild_id, users, dungeon_run), rand_val
        elif dungeon_run.section == UnderworldSection.FungalCaverns:
            rand_val: int = random.choice([i for i in range(0, 8) if i != dungeon_run.previous_event])
            if rand_val == 0:
                return CrimsonRotView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 1:
                return DeepHoleView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 2:
                return DenseClustersView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 3:
                return GrandMushroomStaffView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 4:
                return MushroomGroveView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 5:
                return FungalCavernsOreVeinView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 6:
                return PurpleCloudView(bot, database, guild_id, users, dungeon_run), rand_val
            else:
                return FungalCavernsUndergroundLakeView(bot, database, guild_id, users, dungeon_run), rand_val
        else:
            rand_val: int = random.choice([i for i in range(0, 4) if i != dungeon_run.previous_event])
            if rand_val == 0:
                return ArcaneTrapsView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 1:
                return EchoOfKnowledgeView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 2:
                return GoldenIdolView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 3:
                return HeavyStoneDoorView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 4:
                return OldNotesView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 5:
                return TombsIngressOreVeinView(bot, database, guild_id, users, dungeon_run), rand_val
            elif rand_val == 6:
                return SupplyRoomView(bot, database, guild_id, users, dungeon_run), rand_val
            else:
                return TombsIngressUndergroundLakeView(bot, database, guild_id, users, dungeon_run), rand_val

    @staticmethod
    def generate_boss_room(bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        if dungeon_run.section == UnderworldSection.MistyTunnels:
            return TunneldiggerDuelView(bot, database, guild_id, users, dungeon_run)
        elif dungeon_run.section == UnderworldSection.FungalCaverns:
            return MushroomMazeDuelView(bot, database, guild_id, users, dungeon_run)
        else:
            return EyelessEchoesDuelView(bot, database, guild_id, users, dungeon_run)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._something_stirs = state.get("_something_stirs", 0)
        self.first_to_stir_id = state.get("first_to_stir_id", -1)
        self.remaining_sunless_keys = state.get("remaining_sunless_keys",
            [
                ItemKey.SunlessStride,
                ItemKey.SunlessChains,
                ItemKey.SunlessGrip,
                ItemKey.SunlessSteps,
                ItemKey.SunlessMind,
                ItemKey.SunlessHeart,
                ItemKey.SunlessWill
            ]
        )
