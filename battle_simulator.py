from __future__ import annotations

import logging

from dataclasses import dataclass, field
from math import ceil
from multiprocessing import Pool, freeze_support
from pathlib import Path
from random import choice, choices

from features.expertise import ExpertiseClass
from features.npcs.npc import NPC, NPCDuelingPersonas, NPCRoles
from features.shared.ability import *
from features.shared.enums import ClassTag, StateTag
from features.shared.item import LOADED_ITEMS, Item, ItemKey
from features.stories.forest.combat.npcs.brigand import Brigand
from features.stories.forest.combat.npcs.colossal_undead_treant import ColossalUndeadTreant
from features.stories.forest.combat.npcs.deepwood_bear import DeepwoodBear
from features.stories.forest.combat.npcs.desiccated_undead_treant import DesiccatedUndeadTreant
from features.stories.forest.combat.npcs.evoker import Evoker
from features.stories.forest.combat.npcs.giant_snake import GiantSnake
from features.stories.forest.combat.npcs.horrifying_bone_amalgam import HorrifyingBoneAmalgam
from features.stories.forest.combat.npcs.marauder import Marauder
from features.stories.forest.combat.npcs.mystic import Mystic
from features.stories.forest.combat.npcs.small_snake import SmallSnake
from features.stories.forest.combat.npcs.starving_dire_wolf import StarvingDireWolf
from features.stories.forest.combat.npcs.thief import Thief
from features.stories.forest.combat.npcs.timberwolf import Timberwolf
from features.stories.forest.combat.npcs.voidburnt_treant import VoidburntTreant
from features.stories.forest.combat.npcs.wailing_bones import WailingBones
from features.stories.forest.combat.npcs.wild_boar import WildBoar
from features.stories.ocean.combat.npcs.giant_cone_snail import GiantConeSnail
from features.stories.ocean.combat.npcs.jellyfish import Jellyfish
from features.stories.ocean.combat.npcs.lesser_kraken import LesserKraken
from features.stories.ocean.combat.npcs.mesmerfish import Mesmerfish
from features.stories.ocean.combat.npcs.shallows_shark import ShallowsShark
from features.stories.ocean.combat.npcs.stranglekelp_holdfast import StranglekelpHoldfast
from features.stories.ocean.combat.npcs.stranglekelp_host import StranglekelpHost
from features.stories.ocean.combat.npcs.titanfish import Titanfish
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

ALCHEMIST_ABILITIES: List[List[Type[Ability]]] = [
    [IncenseI, IncenseII, IncenseIII],
    [PreparePotionsI, PreparePotionsII, PreparePotionsIII],
    [VitalityTransferI, VitalityTransferII, VitalityTransferIII],
    [CleanseI],
    [ToxicCloudI, ToxicCloudII, ToxicCloudIII, ToxicCloudIV],
    [SmokescreenI, SmokescreenII, SmokescreenIII],
    [EmpowermentI, EmpowermentII],
    [FesteringVaporI, FesteringVaporII, FesteringVaporIII],
    [PoisonousSkinI],
    [RegenerationI, RegenerationII, RegenerationIII],
    [ParalyzingFumesI, ParalyzingFumesII],
    [QuickAccessI]
]

FISHER_ABILITIES: List[List[Type[Ability]]] = [
    [SeaSprayI, SeaSprayII, SeaSprayIII, SeaSprayIV, SeaSprayV],
    [CrabnadoI, CrabnadoII, CrabnadoIII],
    [CurseOfTheSeaI, CurseOfTheSeaII, CurseOfTheSeaIII],
    [HookI, HookII, HookIII],
    [WrathOfTheWavesI, WrathOfTheWavesII, WrathOfTheWavesIII],
    [HighTideI, HighTideII, HighTideIII, HighTideIV],
    [ThunderingTorrentI, ThunderingTorrentII, ThunderingTorrentIII, ThunderingTorrentIV],
    [DrownInTheDeepI, DrownInTheDeepII, DrownInTheDeepIII],
    [WhirlpoolI, WhirlpoolII, WhirlpoolIII, WhirlpoolIV],
    [ShatteringStormI, ShatteringStormII, ShatteringStormIII],
]

GUARDIAN_ABILITIES: List[List[Type[Ability]]] = [
    [WhirlwindI, WhirlwindII, WhirlwindIII, WhirlwindIV],
    [SecondWindI, SecondWindII, SecondWindIII],
    [ScarArmorI, ScarArmorII],
    [UnbreakingI, UnbreakingII],
    [CounterstrikeI, CounterstrikeII, CounterstrikeIII],
    [BidedAttackI, BidedAttackII, BidedAttackIII],
    [TauntI, TauntII, TauntIII],
    [PiercingStrikeI, PiercingStrikeII, PiercingStrikeIII],
    [PressTheAdvantageI, PressTheAdvantageII, PressTheAdvantageIII],
    [EvadeI, EvadeII, EvadeIII],
    [HeavySlamI, HeavySlamII, HeavySlamIII]
]

MERCHANT_ABILITIES: List[List[Type[Ability]]] = [
    [ContractWealthForPowerI, ContractWealthForPowerII, ContractWealthForPowerIII],
    [BoundToGetLuckyI, BoundToGetLuckyII, BoundToGetLuckyIII, BoundToGetLuckyIV, BoundToGetLuckyV],
    [SilkspeakingI],
    [ATidySumI, ATidySumII, ATidySumIII],
    [CursedCoinsI, CursedCoinsII, CursedCoinsIII, CursedCoinsIV],
    [UnseenRichesI, UnseenRichesII, UnseenRichesIII],
    [ContractManaToBloodI, ContractManaToBloodII, ContractManaToBloodIII],
    [ContractBloodForBloodI, ContractBloodForBloodII, ContractBloodForBloodIII],
    [DeepPocketsI, DeepPocketsII, DeepPocketsIII]
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

        if int(npc_level * 0.6) <= item.get_level_requirement() and item.meets_requirements(npc_level, npc.get_combined_attributes()):
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
            weights=[0.4, 0.3, 0.1, 0, 0.1, 0.1]
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
            weights=[0.35, 0, 0.1, 0.35, 0.1, 0.1]
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
            weights=[0.35, 0, 0.1, 0.35, 0.1, 0.1]
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
            weights=[0.35, 0.1, 0.35, 0, 0.1, 0.1]
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
            weights=[0.4, 0, 0.1, 0.4, 0, 0.1]
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
    # [Mesmerfish, Mesmerfish, Mesmerfish],
    # [StranglekelpHost],
    # [StranglekelpHoldfast, StranglekelpHoldfast],
    # [Titanfish],
    # [Jellyfish, Jellyfish, Jellyfish]

    # [WildBoar, WildBoar],
    # [SmallSnake, SmallSnake, SmallSnake],
    # [GiantSnake],
    # [DeepwoodBear],
    # [Timberwolf, Timberwolf, Timberwolf, Timberwolf],
    # [Brigand, Mystic],
    # [Evoker, Brigand, Thief],
    # [Evoker, Mystic],
    # [Thief, Marauder]

    [DesiccatedUndeadTreant, ColossalUndeadTreant],
    [VoidburntTreant],
    [StarvingDireWolf, StarvingDireWolf],
    [WailingBones],
    [HorrifyingBoneAmalgam]
]
ALLY_CLASS_RANGE: range = range(20, 30)

SIMULATION_ITERATIONS = 128
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

def generate_ally_npcs():
    allies_per_sim: List[List[NPC]] = []
    for _ in range(SIMULATION_ITERATIONS):
        allies: List[NPC] = []
        for j in range(NUM_ALLIES):
            persona = choice(PERSONAS)
            level = randint(ALLY_CLASS_RANGE.start, ALLY_CLASS_RANGE.stop)
            ally = generate_npc_for_persona(persona, level, j)
            
            allies.append(ally)
        allies_per_sim.append(allies)
    return allies_per_sim

def run_simulation(allies: List[NPC], enemies: List[NPC], dir_name: str, sim_index: int) -> SimulationResult:
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
    
    duel: SimulationDuel = SimulationDuel(allies, enemies, logger, MAX_TURNS)

    allies_won: int = any(ally.get_stats().dueling.duels_won > 0 for ally in allies)
    if allies_won:
        result.allies_won = True
        logger.log(level=logging.INFO, msg="Allies won!")
    else:
        logger.log(level=logging.INFO, msg="Enemies won!")
    
    logger.log(level=logging.INFO, msg=f"Turns taken: {duel.turns_taken}")

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

def run_simulations_for_enemy_class(enemy_class_list: List[Type]):
    # Setup files
    base_enemy_name: str = "".join(filter(lambda ch: not ch.isdigit(), enemy_class_list[0]().get_name().lower().replace(" ", "_")))
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

    ally_npcs: List[List[NPC]] = generate_ally_npcs()
    enemy_npcs: List[List[NPC]] = [[enemy(name_suffix=f" {j}") for j, enemy in enumerate(enemy_class_list)] for _ in range(SIMULATION_ITERATIONS)]

    pool = Pool(processes=8)
    results: List[SimulationResult] = pool.starmap(run_simulation, zip(ally_npcs, enemy_npcs, [dir_name for _ in range(SIMULATION_ITERATIONS)], [i for i in range(SIMULATION_ITERATIONS)]))
    pool.close()
    pool.join()

    for result in results:
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

    # Log average data
    with open(f"./simulation_results/{base_enemy_name}/average_data.txt", "w") as f:
        f.write(
            (
                f"Ally Average Data:\n\n"
                f"Attacks Done: {total_attacks_done[0] / SIMULATION_ITERATIONS}\n"
                f"Abilities Used: {total_abilities_used[0] / SIMULATION_ITERATIONS}\n"
                f"Items Used: {total_items_used[0] / SIMULATION_ITERATIONS}\n\n"
                f"Damage Dealt: {total_dmg_dealt[0] / SIMULATION_ITERATIONS}\n"
                f"Damage Taken: {total_dmg_taken[0] / SIMULATION_ITERATIONS}\n"
                f"Damage Blocked/Reduced: {total_dmg_blocked[0] / SIMULATION_ITERATIONS}\n\n"
                f"Attacks Dodged: {total_attacks_dodged[0] / SIMULATION_ITERATIONS}\n"
                f"Abilities Dodged: {total_abilities_dodged[0] / SIMULATION_ITERATIONS}\n"
                f"Crits: {total_crits[0] / SIMULATION_ITERATIONS}\n\n"

                f"Enemy Average Data:\n\n"
                f"Attacks Done: {total_attacks_done[1] / SIMULATION_ITERATIONS}\n"
                f"Abilities Used: {total_abilities_used[1] / SIMULATION_ITERATIONS}\n"
                f"Items Used: {total_items_used[1] / SIMULATION_ITERATIONS}\n\n"
                f"Damage Dealt: {total_dmg_dealt[1] / SIMULATION_ITERATIONS}\n"
                f"Damage Taken: {total_dmg_taken[1] / SIMULATION_ITERATIONS}\n"
                f"Damage Blocked/Reduced: {total_dmg_blocked[1] / SIMULATION_ITERATIONS}\n\n"
                f"Attacks Dodged: {total_attacks_dodged[1] / SIMULATION_ITERATIONS}\n"
                f"Abilities Dodged: {total_abilities_dodged[1] / SIMULATION_ITERATIONS}\n"
                f"Crits: {total_crits[1] / SIMULATION_ITERATIONS}\n\n"
                
                f"Percent Ally Victory: {ally_victories / SIMULATION_ITERATIONS}"
            )
        )
    
    print(f"{base_enemy_name} simulations complete!")


if __name__ == "__main__":
    freeze_support()
    
    for enemy_class in ENEMY_CLASSES:
        run_simulations_for_enemy_class(enemy_class)