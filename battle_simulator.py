from __future__ import annotations

import logging

from dataclasses import dataclass, field
from math import ceil
from multiprocessing import Pool, freeze_support
from pathlib import Path
from random import choice, choices

from features.expertise import ExpertiseClass
from features.npcs.abarra import Blacksmith
from features.npcs.copperbroad import Chef
from features.npcs.galos import Galos
from features.npcs.mrbones import MrBones
from features.npcs.npc import NPC, NPCDuelingPersonas, NPCRoles
from features.npcs.viktor import RandomItemMerchant
from features.npcs.yenna import Yenna
from features.shared.ability import *
from features.shared.enums import ClassTag, StateTag
from features.shared.item import LOADED_ITEMS, Item, ItemKey
from features.stories.forest.combat.npcs.bridge_golem import BridgeGolem
from features.stories.forest.combat.npcs.brigand import Brigand
from features.stories.forest.combat.npcs.colossal_undead_treant import ColossalUndeadTreant
from features.stories.forest.combat.npcs.deepwood_bear import DeepwoodBear
from features.stories.forest.combat.npcs.desiccated_undead_treant import DesiccatedUndeadTreant
from features.stories.forest.combat.npcs.evoker import Evoker
from features.stories.forest.combat.npcs.giant_snake import GiantSnake
from features.stories.forest.combat.npcs.horrifying_bone_amalgam import HorrifyingBoneAmalgam
from features.stories.forest.combat.npcs.hulking_bone_shambler import HulkingBoneShambler
from features.stories.forest.combat.npcs.marauder import Marauder
from features.stories.forest.combat.npcs.mystic import Mystic
from features.stories.forest.combat.npcs.small_snake import SmallSnake
from features.stories.forest.combat.npcs.song_of_the_woods import SongOfTheWoods
from features.stories.forest.combat.npcs.starving_dire_wolf import StarvingDireWolf
from features.stories.forest.combat.npcs.thief import Thief
from features.stories.forest.combat.npcs.timberwolf import Timberwolf
from features.stories.forest.combat.npcs.voidburnt_treant import VoidburntTreant
from features.stories.forest.combat.npcs.wailing_bones import WailingBones
from features.stories.forest.combat.npcs.whirling_bone_shambler import WhirlingBoneShambler
from features.stories.forest.combat.npcs.wild_boar import WildBoar
from features.stories.ocean.combat.npcs.ancient_kraken import AncientKraken
from features.stories.ocean.combat.npcs.banded_eel import BandedEel
from features.stories.ocean.combat.npcs.bloodcoral_behemoth import BloodcoralBehemoth
from features.stories.ocean.combat.npcs.brittle_star import BrittleStar
from features.stories.ocean.combat.npcs.crab_king import CrabKing
from features.stories.ocean.combat.npcs.crab_servant import CrabServant
from features.stories.ocean.combat.npcs.faceless_husk import FacelessHusk
from features.stories.ocean.combat.npcs.false_village import FalseVillage
from features.stories.ocean.combat.npcs.fish_maybe import FishMaybe
from features.stories.ocean.combat.npcs.giant_cone_snail import GiantConeSnail
from features.stories.ocean.combat.npcs.grand_lionfish import GrandLionfish
from features.stories.ocean.combat.npcs.jellyfish import Jellyfish
from features.stories.ocean.combat.npcs.lesser_kraken import LesserKraken
from features.stories.ocean.combat.npcs.lurking_isopod import LurkingIsopod
from features.stories.ocean.combat.npcs.mesmerfish import Mesmerfish
from features.stories.ocean.combat.npcs.mysterious_tentacle import MysteriousTentacle
from features.stories.ocean.combat.npcs.rockfish import Rockfish
from features.stories.ocean.combat.npcs.sand_lurker import SandLurker
from features.stories.ocean.combat.npcs.sandwyrm import Sandwyrm
from features.stories.ocean.combat.npcs.sea_dragon import SeaDragon
from features.stories.ocean.combat.npcs.shallows_shark import ShallowsShark
from features.stories.ocean.combat.npcs.stranglekelp_holdfast import StranglekelpHoldfast
from features.stories.ocean.combat.npcs.stranglekelp_host import StranglekelpHost
from features.stories.ocean.combat.npcs.titanfish import Titanfish
from features.stories.ocean.combat.npcs.voidseen_angler import VoidseenAngler
from features.stories.ocean.combat.npcs.wandering_bloodcoral import WanderingBloodcoral
from features.stories.ocean.combat.npcs.wriggling_mass import WrigglingMass
from features.stories.underworld.combat.npcs.agaric_alchemist import AgaricAlchemist
from features.stories.underworld.combat.npcs.assailing_tomb_guardian import AssailingTombGuardian
from features.stories.underworld.combat.npcs.blind_salamander import BlindSalamander
from features.stories.underworld.combat.npcs.breath_of_darkness import BreathOfDarkness
from features.stories.underworld.combat.npcs.chanterspell import Chanterspell
from features.stories.underworld.combat.npcs.choking_fog import ChokingFog
from features.stories.underworld.combat.npcs.chthonic_emissary import ChthonicEmissary
from features.stories.underworld.combat.npcs.cultist_of_avarice import CultistOfAvarice
from features.stories.underworld.combat.npcs.deathless_cap import DeathlessCap
from features.stories.underworld.combat.npcs.defending_tomb_guardian import DefendingTombGuardian
from features.stories.underworld.combat.npcs.echo_of_asterius import EchoOfAsterius
from features.stories.underworld.combat.npcs.echo_of_passerhawk import EchoOfPasserhawk
from features.stories.underworld.combat.npcs.echo_of_yenna import EchoOfYenna
from features.stories.underworld.combat.npcs.glowing_moss import GlowingMoss
from features.stories.underworld.combat.npcs.hen_of_the_caverns import HenOfTheCaverns
from features.stories.underworld.combat.npcs.ichordrink_bat import IchordrinkBat
from features.stories.underworld.combat.npcs.malevolent_morel import MalevolentMorel
from features.stories.underworld.combat.npcs.misty_apparition import MistyApparition
from features.stories.underworld.combat.npcs.mushroom_maze import MushroomMaze
from features.stories.underworld.combat.npcs.mycelium_tree import MyceliumTree
from features.stories.underworld.combat.npcs.pale_widow import PaleWidow
from features.stories.underworld.combat.npcs.quaking_tunnels import QuakingTunnels
from features.stories.underworld.combat.npcs.scratches_on_the_wall import ScratchesOnTheWall
from features.stories.underworld.combat.npcs.scuttledark_scorpion import ScuttledarkScorpion
from features.stories.underworld.combat.npcs.stonewalker import Stonewalker
from features.stories.underworld.combat.npcs.timelost_echo import TimelostEcho
from features.stories.underworld.combat.npcs.tunneldigger import Tunneldigger
from features.stories.underworld.combat.npcs.volatile_illusion import VolatileIllusion
from features.stories.underworld.combat.npcs.warping_anomaly import WarpingAnomaly
from features.stories.underworld.combat.npcs.waylaid_chest import WaylaidChest
from features.stories.underworld.combat.npcs.winding_tunnels import WindingTunnels
from simulation_duel import SimulationDuel

from typing import Dict, List, Type

# -----------------------------------------------------------------------------
# OVERVIEW
# -----------------------------------------------------------------------------

# This is a Monte Carlo battle simulator meant to assess whether or not dungeon
# run encounters are truly balanced. The algorithm per iteration is as follows:
#   (1) Generate a random set of 4 allies for a given level
#       (a) Choose a random dueling persona for the ally
#       (b) Level up and assign stats appropriately
#       (c) Assign random abilities based on xp levels
#       (d) Equip random gear at ally level or up to 10 levels lower
#       (e) Give the ally a random scattering of consumables
#   (2) Create a duel between the allies and instanced enemies
#   (3) Evaluate the stats of both sides post-duel to see the following:
#       (a) Which team won (ties count as losses)
#       (b) Abilities, attacks, and items used by each side
#       (c) Damage dealt, taken, and blocked by each side
#       (d) Attacks and abilities dodged by each side
#       (e) Crits for each side

# -----------------------------------------------------------------------------
# PERSONA AND CLASS RESULTS SUMMARY
# -----------------------------------------------------------------------------

# Lvl. 10-20
# Bruiser vs. Mage: 46% Bruiser victory, 19 turns
# Rogue vs. Mage: 46% Rogue victory, 18 turns
# Rogue vs. Bruiser: 46% Rogue victory, 22 turns
# Tank vs. Bruiser: 51% Tank victory, 25 turns
# Tank vs. Mage: 47% Tank victory, 19 turns
# Tank vs. Rogue: 53% Tank victory, 27 turns

# Lvl. 50-60
# Bruiser vs. Mage: 50% Bruiser victory, 17 turns
# Rogue vs. Mage: 43% Rogue victory, 18 turns
# Rogue vs. Bruiser: 46% Rogue victory, 22 turns
# Tank vs. Bruiser: 62% Tank victory, 26 turns
# Tank vs. Mage: 72% Tank victory, 22 turns
# Tank vs. Rogue: 69% Tank victory, 27 turns

# Lvl. 100-110
# Bruiser vs. Mage: 65% Bruiser victory, 21 turns
# Rogue vs. Mage: 59% Rogue victory, 26 turns
# Rogue vs. Bruiser: 41% Rogue victory, 26 turns
# Tank vs. Bruiser: 59% Tank victory, 31 turns
# Tank vs. Mage: 78% Tank victory, 33 turns
# Tank vs. Rogue: 71% Tank victory, 39 turns

# Lvl. 10-20:
# Alchemist vs. Fisher: 43% Alchemist victory, 17 turns
# Alchemist vs. Guardian: 50% Alchemist victory, 25 turns
# Alchemist vs. Merchant: 54% Alchemist victory, 22 turns
# Fisher vs. Guardian: 54% Fisher victory, 17 turns
# Fisher vs. Merchant: 62% Fisher victory, 15 turns
# Guardian vs. Merchant: 54% Guardian victory, 18 turns

# Lvl. 50-60
# Alchemist vs. Fisher: 44% Alchemist victory, 18 turns
# Alchemist vs. Guardian: 42% Alchemist victory, 23 turns
# Alchemist vs. Merchant: 61% Alchemist victory, 18 turns
# Fisher vs. Guardian: 46% Fisher victory, 18 turns
# Fisher vs. Merchant: 61% Fisher victory, 14 turns
# Guardian vs. Merchant: 64% Guardian victory, 17 turns

# Lvl. 100-110
# Alchemist vs. Fisher: 46% Alchemist victory, 36 turns
# Alchemist vs. Guardian: 24% Alchemist victory, 32 turns
# Alchemist vs. Merchant: 30% Alchemist victory, 21 turns
# Fisher vs. Guardian: 26% Fisher victory, 24 turns
# Fisher vs. Merchant: 31% Fisher victory, 15 turns
# Guardian vs. Merchant: 47% Guardian victory, 16 turns

# -----------------------------------------------------------------------------
# LOGGER
# -----------------------------------------------------------------------------

def setup_logger(name, log_file, level=logging.INFO):
    dt_fmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter("[{asctime}]\n\n{message}", dt_fmt, style='{')
    handler = logging.FileHandler(log_file, mode="w", encoding="utf-8", errors="replace")
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

# -----------------------------------------------------------------------------
# CONSTANTS
# -----------------------------------------------------------------------------

PERSONAS = [
    NPCDuelingPersonas.Bruiser,
    NPCDuelingPersonas.Healer,
    NPCDuelingPersonas.Mage,
    NPCDuelingPersonas.Rogue,
    NPCDuelingPersonas.Specialist,
    NPCDuelingPersonas.Tank
]

CONSUMABLE_KEYS = [
    item_key for item_key in ItemKey \
    if ClassTag.Consumable.Consumable in LOADED_ITEMS.get_item_state(item_key)["class_tags"]
]

EQUIPMENT_KEYS = [
    item_key for item_key in ItemKey \
    if ClassTag.Equipment.Equipment in LOADED_ITEMS.get_item_state(item_key)["class_tags"]
]

GEM_KEYS = [
    item_key for item_key in ItemKey \
    if ClassTag.Valuable.Gemstone in LOADED_ITEMS.get_item_state(item_key)["class_tags"]
]

# -----------------------------------------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------------------------------------

def generate_inventory(npc: NPC):
    item_keys = choices(CONSUMABLE_KEYS, k=randint(2, 6))

    for item_key in item_keys:
        item = LOADED_ITEMS.get_new_item(item_key)
        item.add_amount(randint(0, 3))
        npc.get_inventory().add_item(item)

    npc.get_inventory().add_coins(int(npc.get_expertise().level ** 2.2))


def get_valid_abilities(npc: NPC) -> List[Ability]:
    def filter_none(lst: List[Ability | None]):
        result: List[Ability] = []
        for a in lst:
            if a is not None:
                result.append(a)
        return result

    def choose_ability_from_list(ability_list: List[type], xp_class_level: int):
        ability: Ability | None = None
        for ability_class in ability_list:
            possible_ability: Ability = ability_class()
            if xp_class_level >= possible_ability.get_level_requirement():
                if ability is None or possible_ability.get_level_requirement() > ability.get_level_requirement():
                    ability = possible_ability
        return ability

    alchemist_abilities = filter_none(list(map(lambda lst: choose_ability_from_list(lst, npc.get_expertise()._alchemist._level), ALCHEMIST_ABILITIES)))
    fisher_abilities = filter_none(list(map(lambda lst: choose_ability_from_list(lst, npc.get_expertise()._fisher._level), FISHER_ABILITIES)))
    guardian_abilities = filter_none(list(map(lambda lst: choose_ability_from_list(lst, npc.get_expertise()._guardian._level), GUARDIAN_ABILITIES)))
    merchant_abilities = filter_none(list(map(lambda lst: choose_ability_from_list(lst, npc.get_expertise()._merchant._level), MERCHANT_ABILITIES)))

    if len(alchemist_abilities) == 0 and len(fisher_abilities) == 0 and len(guardian_abilities) == 0 and len(merchant_abilities) == 0:
        return []

    npc_expertise = npc.get_expertise()

    weights = [
        *[npc_expertise._alchemist._level for _ in range(len(alchemist_abilities))],
        *[npc_expertise._fisher._level for _ in range(len(fisher_abilities))],
        *[npc_expertise._guardian._level for _ in range(len(guardian_abilities))],
        *[npc_expertise._merchant._level for _ in range(len(merchant_abilities))]
    ]

    # Numpy has betrayed me, so this will have to do for now.
    non_unique_abilities = choices(
        [*alchemist_abilities, *fisher_abilities, *guardian_abilities, *merchant_abilities],
        k=npc_expertise.memory,
        weights=weights
    )

    final_abilities: Dict[str, Ability] = {}
    for a in non_unique_abilities:
        final_abilities[a.get_name()] = a

    return list(final_abilities.values())


def generate_random_equipment(npc: NPC):
    tags = [
        ClassTag.Equipment.Helmet,
        ClassTag.Equipment.ChestArmor,
        ClassTag.Equipment.Gloves,
        ClassTag.Equipment.Boots,
        ClassTag.Equipment.Amulet,
        ClassTag.Equipment.Ring,
        ClassTag.Equipment.Leggings,
        ClassTag.Equipment.MainHand,
        ClassTag.Equipment.OffHand
    ]

    valid_equipment: Dict[ClassTag.Equipment, List[Item]] = { tag: [] for tag in tags }
    
    npc_level: int = npc.get_expertise().level
    for item_key in EQUIPMENT_KEYS:
        item = LOADED_ITEMS.get_new_item(item_key)

        if ClassTag.Equipment.Amulet in item.get_class_tags():
            valid_equipment[ClassTag.Equipment.Amulet].append(item)
            continue
        if ClassTag.Equipment.Ring in item.get_class_tags():
            valid_equipment[ClassTag.Equipment.Ring].append(item)
            continue
        
        if item.get_value() > 1 and item.get_level_requirement() > 0 and int(npc_level * 0.6) <= item.get_level_requirement() and item.meets_requirements(npc_level, npc.get_combined_attributes()):
            primary_tag: ClassTag.Equipment = ClassTag.Equipment.Equipment
            for tag in tags:
                if tag in item.get_class_tags():
                    primary_tag = tag
                    break
            
            valid_equipment[primary_tag].append(item)

    npc_equipment = npc.get_equipment()
    for tag in tags:
        if len(valid_equipment[tag]) > 0:
            final_item: Item = choice(valid_equipment[tag])
            
            if StateTag.NeedsIdentification in final_item.get_state_tags():
                final_item.get_state_tags().remove(StateTag.NeedsIdentification)
            
            if len(final_item.get_altering_item_keys()) > 0:
                num_gems = len(final_item.get_altering_item_keys())
                gems = choices(GEM_KEYS, k=num_gems)
                final_item.set_altering_item_keys(gems)

            npc_equipment.equip_item_to_slot(tag, final_item)


def setup_bruiser(npc: NPC, level: int):
    # Assign xp class levels
    alchemist_level: int = ceil(0.25 * level)
    fisher_level: int = ceil(0 * level)
    guardian_level: int = ceil(0.5 * level)
    merchant_level: int = ceil(0.25 * level)

    xp = npc.get_expertise()
    xp.add_xp_to_class_until_level(alchemist_level, ExpertiseClass.Alchemist)
    xp.add_xp_to_class_until_level(fisher_level, ExpertiseClass.Fisher)
    xp.add_xp_to_class_until_level(guardian_level, ExpertiseClass.Guardian)
    xp.add_xp_to_class_until_level(merchant_level, ExpertiseClass.Merchant)

    # Assign attribute points
    for _ in range(level):
        attr = choices(
            [Attribute.Constitution, Attribute.Strength, Attribute.Dexterity, Attribute.Intelligence, Attribute.Luck, Attribute.Memory],
            weights=[0.3, 0.4, 0.1, 0, 0.1, 0.1]
        )[0]

        if attr == Attribute.Constitution:
            npc.get_expertise().constitution += 1
        elif attr == Attribute.Strength:
            npc.get_expertise().strength += 1
        elif attr == Attribute.Dexterity:
            npc.get_expertise().dexterity += 1
        elif attr == Attribute.Intelligence:
            npc.get_expertise().intelligence += 1
        elif attr == Attribute.Luck:
            npc.get_expertise().luck += 1
        else:
            npc.get_expertise().memory += 1


def setup_healer(npc: NPC, level: int):
    # Assign xp class levels
    alchemist_level: int = ceil(0.5 * level)
    fisher_level: int = ceil(0.125 * level)
    guardian_level: int = ceil(0.125 * level)
    merchant_level: int = ceil(0.25 * level)

    xp = npc.get_expertise()
    xp.add_xp_to_class_until_level(alchemist_level, ExpertiseClass.Alchemist)
    xp.add_xp_to_class_until_level(fisher_level, ExpertiseClass.Fisher)
    xp.add_xp_to_class_until_level(guardian_level, ExpertiseClass.Guardian)
    xp.add_xp_to_class_until_level(merchant_level, ExpertiseClass.Merchant)

    # Assign attribute points
    for _ in range(level):
        attr = choices(
            [Attribute.Constitution, Attribute.Strength, Attribute.Dexterity, Attribute.Intelligence, Attribute.Luck, Attribute.Memory],
            weights=[0.3, 0, 0.1, 0.4, 0.1, 0.1]
        )[0]

        if attr == Attribute.Constitution:
            npc.get_expertise().constitution += 1
        elif attr == Attribute.Strength:
            npc.get_expertise().strength += 1
        elif attr == Attribute.Dexterity:
            npc.get_expertise().dexterity += 1
        elif attr == Attribute.Intelligence:
            npc.get_expertise().intelligence += 1
        elif attr == Attribute.Luck:
            npc.get_expertise().luck += 1
        else:
            npc.get_expertise().memory += 1


def setup_mage(npc: NPC, level: int):
    # Assign xp class levels
    alchemist_level: int = ceil(0 * level)
    fisher_level: int = ceil(0.5 * level)
    guardian_level: int = ceil(0.25 * level)
    merchant_level: int = ceil(0.25 * level)

    xp = npc.get_expertise()
    xp.add_xp_to_class_until_level(alchemist_level, ExpertiseClass.Alchemist)
    xp.add_xp_to_class_until_level(fisher_level, ExpertiseClass.Fisher)
    xp.add_xp_to_class_until_level(guardian_level, ExpertiseClass.Guardian)
    xp.add_xp_to_class_until_level(merchant_level, ExpertiseClass.Merchant)

    # Assign attribute points
    for _ in range(level):
        attr = choices(
            [Attribute.Constitution, Attribute.Strength, Attribute.Dexterity, Attribute.Intelligence, Attribute.Luck, Attribute.Memory],
            weights=[0.2, 0, 0.1, 0.5, 0.1, 0.1]
        )[0]

        if attr == Attribute.Constitution:
            npc.get_expertise().constitution += 1
        elif attr == Attribute.Strength:
            npc.get_expertise().strength += 1
        elif attr == Attribute.Dexterity:
            npc.get_expertise().dexterity += 1
        elif attr == Attribute.Intelligence:
            npc.get_expertise().intelligence += 1
        elif attr == Attribute.Luck:
            npc.get_expertise().luck += 1
        else:
            npc.get_expertise().memory += 1


def setup_rogue(npc: NPC, level: int):
    # Assign xp class levels
    alchemist_level: int = ceil(0.25 * level)
    fisher_level: int = ceil(0 * level)
    guardian_level: int = ceil(0.5 * level)
    merchant_level: int = ceil(0.25 * level)

    xp = npc.get_expertise()
    xp.add_xp_to_class_until_level(alchemist_level, ExpertiseClass.Alchemist)
    xp.add_xp_to_class_until_level(fisher_level, ExpertiseClass.Fisher)
    xp.add_xp_to_class_until_level(guardian_level, ExpertiseClass.Guardian)
    xp.add_xp_to_class_until_level(merchant_level, ExpertiseClass.Merchant)

    # Assign attribute points
    for _ in range(level):
        attr = choices(
            [Attribute.Constitution, Attribute.Strength, Attribute.Dexterity, Attribute.Intelligence, Attribute.Luck, Attribute.Memory],
            weights=[0.2, 0.1, 0.5, 0, 0.1, 0.1]
        )[0]

        if attr == Attribute.Constitution:
            npc.get_expertise().constitution += 1
        elif attr == Attribute.Strength:
            npc.get_expertise().strength += 1
        elif attr == Attribute.Dexterity:
            npc.get_expertise().dexterity += 1
        elif attr == Attribute.Intelligence:
            npc.get_expertise().intelligence += 1
        elif attr == Attribute.Luck:
            npc.get_expertise().luck += 1
        else:
            npc.get_expertise().memory += 1


def setup_specialist(npc: NPC, level: int):
    # Assign xp class levels
    alchemist_level: int = ceil(0.5 * level)
    fisher_level: int = ceil(0.5 * level)
    guardian_level: int = ceil(0 * level)
    merchant_level: int = ceil(0 * level)

    xp = npc.get_expertise()
    xp.add_xp_to_class_until_level(alchemist_level, ExpertiseClass.Alchemist)
    xp.add_xp_to_class_until_level(fisher_level, ExpertiseClass.Fisher)
    xp.add_xp_to_class_until_level(guardian_level, ExpertiseClass.Guardian)
    xp.add_xp_to_class_until_level(merchant_level, ExpertiseClass.Merchant)

    # Assign attribute points
    for _ in range(level):
        attr = choices(
            [Attribute.Constitution, Attribute.Strength, Attribute.Dexterity, Attribute.Intelligence, Attribute.Luck, Attribute.Memory],
            weights=[0.3, 0, 0.1, 0.5, 0, 0.1]
        )[0]

        if attr == Attribute.Constitution:
            npc.get_expertise().constitution += 1
        elif attr == Attribute.Strength:
            npc.get_expertise().strength += 1
        elif attr == Attribute.Dexterity:
            npc.get_expertise().dexterity += 1
        elif attr == Attribute.Intelligence:
            npc.get_expertise().intelligence += 1
        elif attr == Attribute.Luck:
            npc.get_expertise().luck += 1
        else:
            npc.get_expertise().memory += 1


def setup_tank(npc: NPC, level: int):
    # Assign xp class levels
    alchemist_level: int = ceil(0.25 * level)
    fisher_level: int = ceil(0 * level)
    guardian_level: int = ceil(0.75 * level)
    merchant_level: int = ceil(0 * level)

    xp = npc.get_expertise()
    xp.add_xp_to_class_until_level(alchemist_level, ExpertiseClass.Alchemist)
    xp.add_xp_to_class_until_level(fisher_level, ExpertiseClass.Fisher)
    xp.add_xp_to_class_until_level(guardian_level, ExpertiseClass.Guardian)
    xp.add_xp_to_class_until_level(merchant_level, ExpertiseClass.Merchant)

    # Assign attribute points
    for _ in range(level):
        attr = choices(
            [Attribute.Constitution, Attribute.Strength, Attribute.Dexterity, Attribute.Intelligence, Attribute.Luck, Attribute.Memory],
            weights=[0.6, 0.2, 0.1, 0, 0, 0.1]
        )[0]

        if attr == Attribute.Constitution:
            npc.get_expertise().constitution += 1
        elif attr == Attribute.Strength:
            npc.get_expertise().strength += 1
        elif attr == Attribute.Dexterity:
            npc.get_expertise().dexterity += 1
        elif attr == Attribute.Intelligence:
            npc.get_expertise().intelligence += 1
        elif attr == Attribute.Luck:
            npc.get_expertise().luck += 1
        else:
            npc.get_expertise().memory += 1


def generate_npc_for_persona(persona: NPCDuelingPersonas, level: int, index: int) -> NPC:
    npc = NPC(f"NPC {index}", NPCRoles.Unknown, persona, {})

    if persona == NPCDuelingPersonas.Bruiser:
        setup_bruiser(npc, level)
    elif persona == NPCDuelingPersonas.Healer:
        setup_healer(npc, level)
    elif persona == NPCDuelingPersonas.Mage:
        setup_mage(npc, level)
    elif persona == NPCDuelingPersonas.Rogue:
        setup_rogue(npc, level)
    elif persona == NPCDuelingPersonas.Specialist:
        setup_specialist(npc, level)
    else:
        setup_tank(npc, level)

    # Assign abilities
    abilities = get_valid_abilities(npc)
    npc.get_dueling().abilities = abilities

    # Assign equipment
    generate_random_equipment(npc)

    # Update stats
    npc.get_expertise().update_stats(npc.get_combined_attributes())

    # Generate inventory items
    generate_inventory(npc)

    return npc


def setup_alchemist(npc: NPC, level: int):
    # Assign xp class levels
    alchemist_level: int = ceil(0.8 * level)
    fisher_level: int = ceil(0 * level)
    guardian_level: int = ceil(0.1 * level)
    merchant_level: int = ceil(0.1 * level)

    xp = npc.get_expertise()
    xp.add_xp_to_class_until_level(alchemist_level, ExpertiseClass.Alchemist)
    xp.add_xp_to_class_until_level(fisher_level, ExpertiseClass.Fisher)
    xp.add_xp_to_class_until_level(guardian_level, ExpertiseClass.Guardian)
    xp.add_xp_to_class_until_level(merchant_level, ExpertiseClass.Merchant)

    # Assign attribute points
    for _ in range(level):
        attr = choices(
            [Attribute.Constitution, Attribute.Strength, Attribute.Dexterity, Attribute.Intelligence, Attribute.Luck, Attribute.Memory],
            weights=[0.3, 0, 0.1, 0.5, 0, 0.1]
        )[0]

        if attr == Attribute.Constitution:
            npc.get_expertise().constitution += 1
        elif attr == Attribute.Strength:
            npc.get_expertise().strength += 1
        elif attr == Attribute.Dexterity:
            npc.get_expertise().dexterity += 1
        elif attr == Attribute.Intelligence:
            npc.get_expertise().intelligence += 1
        elif attr == Attribute.Luck:
            npc.get_expertise().luck += 1
        else:
            npc.get_expertise().memory += 1


def setup_fisher(npc: NPC, level: int):
    # Assign xp class levels
    alchemist_level: int = ceil(0 * level)
    fisher_level: int = ceil(0.8 * level)
    guardian_level: int = ceil(0.1 * level)
    merchant_level: int = ceil(0.1 * level)

    xp = npc.get_expertise()
    xp.add_xp_to_class_until_level(alchemist_level, ExpertiseClass.Alchemist)
    xp.add_xp_to_class_until_level(fisher_level, ExpertiseClass.Fisher)
    xp.add_xp_to_class_until_level(guardian_level, ExpertiseClass.Guardian)
    xp.add_xp_to_class_until_level(merchant_level, ExpertiseClass.Merchant)

    # Assign attribute points
    for _ in range(level):
        attr = choices(
            [Attribute.Constitution, Attribute.Strength, Attribute.Dexterity, Attribute.Intelligence, Attribute.Luck, Attribute.Memory],
            weights=[0.3, 0, 0.1, 0.5, 0, 0.1]
        )[0]

        if attr == Attribute.Constitution:
            npc.get_expertise().constitution += 1
        elif attr == Attribute.Strength:
            npc.get_expertise().strength += 1
        elif attr == Attribute.Dexterity:
            npc.get_expertise().dexterity += 1
        elif attr == Attribute.Intelligence:
            npc.get_expertise().intelligence += 1
        elif attr == Attribute.Luck:
            npc.get_expertise().luck += 1
        else:
            npc.get_expertise().memory += 1


def setup_guardian(npc: NPC, level: int):
    # Assign xp class levels
    alchemist_level: int = ceil(0 * level)
    fisher_level: int = ceil(0 * level)
    guardian_level: int = ceil(0.9 * level)
    merchant_level: int = ceil(0.1 * level)

    xp = npc.get_expertise()
    xp.add_xp_to_class_until_level(alchemist_level, ExpertiseClass.Alchemist)
    xp.add_xp_to_class_until_level(fisher_level, ExpertiseClass.Fisher)
    xp.add_xp_to_class_until_level(guardian_level, ExpertiseClass.Guardian)
    xp.add_xp_to_class_until_level(merchant_level, ExpertiseClass.Merchant)

    # Assign attribute points
    for _ in range(level):
        attr = choices(
            [Attribute.Constitution, Attribute.Strength, Attribute.Dexterity, Attribute.Intelligence, Attribute.Luck, Attribute.Memory],
            weights=[0.4, 0.4, 0.1, 0, 0, 0.1]
        )[0]

        if attr == Attribute.Constitution:
            npc.get_expertise().constitution += 1
        elif attr == Attribute.Strength:
            npc.get_expertise().strength += 1
        elif attr == Attribute.Dexterity:
            npc.get_expertise().dexterity += 1
        elif attr == Attribute.Intelligence:
            npc.get_expertise().intelligence += 1
        elif attr == Attribute.Luck:
            npc.get_expertise().luck += 1
        else:
            npc.get_expertise().memory += 1


def setup_merchant(npc: NPC, level: int):
    # Assign xp class levels
    alchemist_level: int = ceil(0 * level)
    fisher_level: int = ceil(0 * level)
    guardian_level: int = ceil(0.1 * level)
    merchant_level: int = ceil(0.9 * level)

    xp = npc.get_expertise()
    xp.add_xp_to_class_until_level(alchemist_level, ExpertiseClass.Alchemist)
    xp.add_xp_to_class_until_level(fisher_level, ExpertiseClass.Fisher)
    xp.add_xp_to_class_until_level(guardian_level, ExpertiseClass.Guardian)
    xp.add_xp_to_class_until_level(merchant_level, ExpertiseClass.Merchant)

    # Assign attribute points
    for _ in range(level):
        attr = choices(
            [Attribute.Constitution, Attribute.Strength, Attribute.Dexterity, Attribute.Intelligence, Attribute.Luck, Attribute.Memory],
            weights=[0.25, 0, 0, 0.35, 0.3, 0.1]
        )[0]

        if attr == Attribute.Constitution:
            npc.get_expertise().constitution += 1
        elif attr == Attribute.Strength:
            npc.get_expertise().strength += 1
        elif attr == Attribute.Dexterity:
            npc.get_expertise().dexterity += 1
        elif attr == Attribute.Intelligence:
            npc.get_expertise().intelligence += 1
        elif attr == Attribute.Luck:
            npc.get_expertise().luck += 1
        else:
            npc.get_expertise().memory += 1


def generate_npc_for_class(xp_class: ExpertiseClass, level: int, index: int) -> NPC:
    persona = NPCDuelingPersonas.Unknown
    if xp_class == ExpertiseClass.Alchemist:
        persona = NPCDuelingPersonas.Mage
    elif xp_class == ExpertiseClass.Fisher:
        persona = NPCDuelingPersonas.Mage
    elif xp_class == ExpertiseClass.Guardian:
        persona = NPCDuelingPersonas.Bruiser
    elif xp_class == ExpertiseClass.Merchant:
        persona = NPCDuelingPersonas.Mage

    npc = NPC(f"NPC {index}", NPCRoles.Unknown, persona, {})

    if xp_class == ExpertiseClass.Alchemist:
        setup_alchemist(npc, level)
    elif xp_class == ExpertiseClass.Fisher:
        setup_fisher(npc, level)
    elif xp_class == ExpertiseClass.Guardian:
        setup_guardian(npc, level)
    elif xp_class == ExpertiseClass.Merchant:
        setup_merchant(npc, level)

    # Assign abilities
    abilities = get_valid_abilities(npc)
    npc.get_dueling().abilities = abilities

    # Assign equipment
    generate_random_equipment(npc)

    # Update stats
    npc.get_expertise().update_stats(npc.get_combined_attributes())

    # Generate inventory items
    generate_inventory(npc)

    return npc

# -----------------------------------------------------------------------------
# LOGGING HELPER FUNCTIONS
# -----------------------------------------------------------------------------

def get_full_equipment_str(npc: NPC):
    player_equipment: Equipment = npc.get_equipment()
    base_none_equipped_str: str = "᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\nNone Equipped\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆"

    helmet = player_equipment.get_item_in_slot(ClassTag.Equipment.Helmet)
    gloves = player_equipment.get_item_in_slot(ClassTag.Equipment.Gloves)
    amulet = player_equipment.get_item_in_slot(ClassTag.Equipment.Amulet)
    ring = player_equipment.get_item_in_slot(ClassTag.Equipment.Ring)
    chest_armor = player_equipment.get_item_in_slot(ClassTag.Equipment.ChestArmor)
    main_hand = player_equipment.get_item_in_slot(ClassTag.Equipment.MainHand)
    off_hand = player_equipment.get_item_in_slot(ClassTag.Equipment.OffHand)
    leggings = player_equipment.get_item_in_slot(ClassTag.Equipment.Leggings)
    boots = player_equipment.get_item_in_slot(ClassTag.Equipment.Boots)

    equipment_strs = [
        f"**Helmet:**\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{str(helmet)}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆" if helmet is not None else "**Helmet:**\n" + base_none_equipped_str,
        f"**Gloves:**\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{str(gloves)}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆" if gloves is not None else "**Gloves:**\n" + base_none_equipped_str,
        f"**Amulet:**\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{str(amulet)}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆" if amulet is not None else "**Amulet:**\n" + base_none_equipped_str,
        f"**Ring:**\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{str(ring)}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆" if ring is not None else "**Ring:**\n" + base_none_equipped_str,
        f"**Chest Armor:**\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{str(chest_armor)}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆" if chest_armor is not None else "**Chest Armor:**\n" + base_none_equipped_str,
        f"**Main Hand:**\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{str(main_hand)}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆" if main_hand is not None else "**Main Hand:**\n" + base_none_equipped_str,
        f"**Off Hand:**\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{str(off_hand)}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆" if off_hand is not None else "**Off Hand:**\n" + base_none_equipped_str,
        f"**Leggings:**\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{str(leggings)}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆" if leggings is not None else "**Leggings:**\n" + base_none_equipped_str,
        f"**Boots:**\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{str(boots)}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆" if boots is not None else "**Boots:**\n" + base_none_equipped_str
    ]

    return "\n\n".join(equipment_strs)

# -----------------------------------------------------------------------------
# SIMULATION SETTINGS
# -----------------------------------------------------------------------------

ENEMY_CLASSES: List[List[type]] = [
    [ChthonicEmissary]
]
ALLY_CLASS_RANGE: range = range(90, 100)

SIMULATION_ITERATIONS = 256
NUM_ALLIES = 4
MAX_TURNS = 1000

# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------

@dataclass
class SimulationResult():
    attacks_done: List[int] = field(default_factory=lambda: [0, 0])
    abilities_used: List[int] = field(default_factory=lambda: [0, 0])
    items_used: List[int] = field(default_factory=lambda: [0, 0])

    dmg_dealt: List[int] = field(default_factory=lambda: [0, 0])
    dmg_taken: List[int] = field(default_factory=lambda: [0, 0])
    dmg_blocked: List[int] = field(default_factory=lambda: [0, 0])

    attacks_dodged: List[int] = field(default_factory=lambda: [0, 0])
    abilities_dodged: List[int] = field(default_factory=lambda: [0, 0])
    crits: List[int] = field(default_factory=lambda: [0, 0])

    allies_won: bool = False
    turns_taken_per_entity: float = 0

def generate_ally_npcs(preset_persona: NPCDuelingPersonas | None=None, preset_class: ExpertiseClass | None=None):
    allies_per_sim: List[List[NPC]] = []
    for _ in range(SIMULATION_ITERATIONS):
        allies: List[NPC] = []
        for j in range(NUM_ALLIES):
            level = randint(ALLY_CLASS_RANGE.start, ALLY_CLASS_RANGE.stop)
            if preset_class is None:
                persona = choice(PERSONAS) if preset_persona is None else preset_persona
                ally = generate_npc_for_persona(persona, level, j)
                allies.append(ally)
            else:
                ally = generate_npc_for_class(preset_class, level, j)
                allies.append(ally)
        allies_per_sim.append(allies)
    return allies_per_sim

def run_simulation(allies: List[NPC], enemies: List[NPC], dir_name: str, sim_index: int) -> SimulationResult | None:
    logger = setup_logger(f"simulation_logger_{sim_index}", f"{dir_name}/simulation_{sim_index}.log")

    result = SimulationResult()

    for ally in allies:
        attr_str: str = str(ally.get_combined_attributes())
        equip_str: str = get_full_equipment_str(ally)
        ability_str: str = ", ".join(list(map(lambda a: a.get_name(), ally.get_dueling().abilities)))
        item_str: str = ", ".join(list(map(lambda item: item.get_name_and_count(), ally.get_inventory().get_inventory_slots())))

        logger.log(level=logging.INFO, msg=(
            f"{ally.get_name()} ({ally._dueling_persona})\n\n"
            f"Attributes:\n\n{attr_str}\n\n"
            f"Equipment:\n\n{equip_str}\n\n"
            f"Abilities: {ability_str}\n\n"
            f"Items: {item_str}")
        )

    try:
        duel: SimulationDuel = SimulationDuel(allies, enemies, logger, MAX_TURNS)
    except:
        return None

    allies_won: int = any(ally.get_stats().dueling.duels_won > 0 for ally in allies)
    if allies_won:
        result.allies_won = True
        logger.log(level=logging.INFO, msg="Allies won!")
    else:
        logger.log(level=logging.INFO, msg="Enemies won!")
    
    logger.log(level=logging.INFO, msg=f"Turns taken: {duel.turns_taken}")
    result.turns_taken_per_entity = duel.turns_taken / (len(allies) + len(enemies))

    for j, team in enumerate([allies, enemies]):
        if j == 0:
            logger.log(level=logging.INFO, msg="Ally Stats:")
        else:
            logger.log(level=logging.INFO, msg="Enemy Stats:")
        
        attacks_done: int = 0
        abilities_used: int = 0
        items_used: int = 0

        dmg_dealt: int = 0
        dmg_taken: int = 0
        dmg_blocked: int = 0

        attacks_dodged: int = 0
        abilities_dodged: int = 0
        crits: int = 0

        for entity in team:
            attacks_done += entity.get_stats().dueling.attacks_done
            abilities_used += entity.get_stats().dueling.abilities_used
            items_used += entity.get_stats().dueling.items_used

            dmg_dealt += entity.get_stats().dueling.damage_dealt
            dmg_taken += entity.get_stats().dueling.damage_taken
            dmg_blocked += entity.get_stats().dueling.damage_blocked_or_reduced

            attacks_dodged += entity.get_stats().dueling.attacks_dodged
            abilities_dodged += entity.get_stats().dueling.abilities_dodged

            crits += entity.get_stats().dueling.critical_hit_successes

        result.attacks_done[j] += attacks_done
        result.abilities_used[j] += abilities_used
        result.items_used[j] += items_used

        result.dmg_dealt[j] += dmg_dealt
        result.dmg_taken[j] += dmg_taken
        result.dmg_blocked[j] += dmg_blocked

        result.attacks_dodged[j] += attacks_dodged
        result.abilities_dodged[j] += abilities_dodged
        result.crits[j] += crits

        logger.log(level=logging.INFO, msg=(
            f"Attacks Done: {attacks_done}\n"
            f"Abilities Used: {abilities_used}\n"
            f"Items Used: {items_used}\n\n"
            f"Damage Dealt: {dmg_dealt}\n"
            f"Damage Taken: {dmg_taken}\n"
            f"Damage Blocked/Reduced: {dmg_blocked}\n\n"
            f"Attacks Dodged: {attacks_dodged}\n"
            f"Abilities Dodged: {abilities_dodged}\n"
            f"Crits: {crits}"
        ))
    
    return result

def run_simulations_for_enemy_class(enemy_class_list: List[Type], num_stirred: int=-1):
    # Setup files
    base_enemy_name: str = ""
    if num_stirred >= 0:
        base_enemy_name = "".join(filter(lambda ch: not ch.isdigit(), enemy_class_list[0](num_stirred=num_stirred).get_name().lower().replace(" ", "_"))).replace("?", "") + "_" + str(num_stirred)
    else:
        base_enemy_name = "".join(filter(lambda ch: not ch.isdigit(), enemy_class_list[0]().get_name().lower().replace(" ", "_"))).replace("?", "")
    dir_name: str = f"./simulation_results/{base_enemy_name}"

    Path(dir_name).mkdir(parents=True, exist_ok=True)

    # Total stats
    ally_victories: int = 0
    
    total_attacks_done: List[int] = [0, 0]
    total_abilities_used: List[int] = [0, 0]
    total_items_used: List[int] = [0, 0]

    total_dmg_dealt: List[int] = [0, 0]
    total_dmg_taken: List[int] = [0, 0]
    total_dmg_blocked: List[int] = [0, 0]

    total_attacks_dodged: List[int] = [0, 0]
    total_abilities_dodged: List[int] = [0, 0]
    total_crits: List[int] = [0, 0]

    total_turns_taken_per_entity: float = 0

    ally_npcs: List[List[NPC]] = generate_ally_npcs()
    enemy_npcs: List[List[NPC]] = []
    if num_stirred >= 0:
        enemy_npcs = [[enemy(name_suffix=f" {j}", num_stirred=num_stirred) for j, enemy in enumerate(enemy_class_list)] for _ in range(SIMULATION_ITERATIONS)]
    else:
        enemy_npcs = [[enemy(name_suffix=f" {j}") for j, enemy in enumerate(enemy_class_list)] for _ in range(SIMULATION_ITERATIONS)]

    pool = Pool(processes=4)
    results: List[SimulationResult | None] = pool.starmap(run_simulation, zip(ally_npcs, enemy_npcs, [dir_name for _ in range(SIMULATION_ITERATIONS)], [i for i in range(SIMULATION_ITERATIONS)]))
    pool.close()
    pool.join()

    final_results: List[SimulationResult] = [result for result in results if result is not None]
    for result in final_results:
        for j in range(2):
            total_attacks_done[j] += result.attacks_done[j]
            total_abilities_used[j] += result.abilities_used[j]
            total_items_used[j] += result.items_used[j]

            total_dmg_dealt[j] += result.dmg_dealt[j]
            total_dmg_taken[j] += result.dmg_taken[j]
            total_dmg_blocked[j] += result.dmg_blocked[j]

            total_attacks_dodged[j] += result.attacks_dodged[j]
            total_abilities_dodged[j] += result.abilities_dodged[j]
            total_crits[j] += result.crits[j]
        
        ally_victories += 1 if result.allies_won else 0
        total_turns_taken_per_entity += result.turns_taken_per_entity

    num_valid_simulations: int = len(final_results)
    # Log average data
    with open(f"./simulation_results/{base_enemy_name}/average_data.txt", "w") as f:
        f.write(
            (
                f"Ally Average Data:\n\n"
                f"Attacks Done: {total_attacks_done[0] / num_valid_simulations}\n"
                f"Abilities Used: {total_abilities_used[0] / num_valid_simulations}\n"
                f"Items Used: {total_items_used[0] / num_valid_simulations}\n\n"
                f"Damage Dealt: {total_dmg_dealt[0] / num_valid_simulations}\n"
                f"Damage Taken: {total_dmg_taken[0] / num_valid_simulations}\n"
                f"Damage Blocked/Reduced: {total_dmg_blocked[0] / num_valid_simulations}\n\n"
                f"Attacks Dodged: {total_attacks_dodged[0] / num_valid_simulations}\n"
                f"Abilities Dodged: {total_abilities_dodged[0] / num_valid_simulations}\n"
                f"Crits: {total_crits[0] / num_valid_simulations}\n\n"

                f"Enemy Average Data:\n\n"
                f"Attacks Done: {total_attacks_done[1] / num_valid_simulations}\n"
                f"Abilities Used: {total_abilities_used[1] / num_valid_simulations}\n"
                f"Items Used: {total_items_used[1] / num_valid_simulations}\n\n"
                f"Damage Dealt: {total_dmg_dealt[1] / num_valid_simulations}\n"
                f"Damage Taken: {total_dmg_taken[1] / num_valid_simulations}\n"
                f"Damage Blocked/Reduced: {total_dmg_blocked[1] / num_valid_simulations}\n\n"
                f"Attacks Dodged: {total_attacks_dodged[1] / num_valid_simulations}\n"
                f"Abilities Dodged: {total_abilities_dodged[1] / num_valid_simulations}\n"
                f"Crits: {total_crits[1] / num_valid_simulations}\n\n"
                
                f"Percent Ally Victory: {ally_victories / num_valid_simulations}\n"
                f"Average Turns Taken (per entity): {total_turns_taken_per_entity / num_valid_simulations}\n"
                f"Valid Simulations: {len(final_results)}"
            )
        )
    
    print(f"{base_enemy_name} simulations complete!")


if __name__ == "__main__":
    freeze_support()
    
    for i in range(0, 130, 10):
        for enemy_class in ENEMY_CLASSES:
            run_simulations_for_enemy_class(enemy_class, i)

    # for enemy_class in ENEMY_CLASSES:
    #     run_simulations_for_enemy_class(enemy_class)
