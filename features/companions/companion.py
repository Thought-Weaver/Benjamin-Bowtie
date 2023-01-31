from __future__ import annotations

from abc import abstractmethod
from math import ceil

from features.companions.abilities import PINCHI, BearDownI, BeetleBashI, BouncingKickI, BulkEnduranceI, ChargeI, CoiledStrikeI, CraftWebI, DeadlyVenomI, DeflectionI, DiveI, EruptionOfBoneI, ExposeTummyI, FeathersFlyI, FleeI, GhostlyMovementI, GlassPierceI, GoreI, GraspingClawsI, GustI, HibernateI, HippityHopI, HypnoticGazeI, InnervateI, IntoTheShadowsI, IsThatAFlyI, LuckyPawsI, LungeI, ManaBurnI, ManaLeechI, ManaLeechII, ManaLeechIII, ManaLeechIV, ManaLeechV, MesmerizeI, MightOfTheVoidI, MightyBoneFistI, MiniCrabnadoI, MysticShroudI, PatientStrikeI, PeckPeckPeckI, PlatedArmorI, PowerfulPierceI, PummelI, RecklessBiteI, ScuttleI, ShellterI, ShriekingCawI, SiphoningSwipeI, StrikeFromBehindI, TerraspinI, TheDarkBarkI, ThickHideI, ToTheSkiesI, TowerStanceI, ToxungenI, UndeathIsJustTheBeginningI, WhatLuckI, WingbeatI, WithTheWindI, WrapTheMealI, QuickeningPaceV, QuickeningPaceIV, QuickeningPaceIII, QuickeningPaceII, QuickeningPaceI, ToweringArmorV, ToweringArmorIV, ToweringArmorIII, ToweringArmorII, ToweringArmorI, ThrowTheBonesV, ThrowTheBonesIV, ThrowTheBonesIII, ThrowTheBonesII, ThrowTheBonesI, VenomousBiteV, VenomousBiteIV, VenomousBiteIII, VenomousBiteII, VenomousBiteI, IsThatAFlyV, IsThatAFlyIV, IsThatAFlyIII, IsThatAFlyII, SneakyManeuversV, SneakyManeuversIV, SneakyManeuversIII, SneakyManeuversII, SneakyManeuversI, WebShotV, WebShotIV, WebShotIII, WebShotII, WebShotI, PINCHV, PINCHIV, PINCHIII, PINCHII, MightOfTheVoidV, MightOfTheVoidIV, MightOfTheVoidIII, MightOfTheVoidII
from features.companions.npcs.blue_flitterwing_butterfly import BlueFlitterwingButterfly
from features.companions.npcs.deepwood_cub import DeepwoodCub
from features.companions.npcs.fleetfoot_rabbit import FleetfootRabbit
from features.companions.npcs.flying_fox import FlyingFox
from features.companions.npcs.giant_tower_beetle import GiantTowerBeetle
from features.companions.npcs.gnashtusk_boar import GnashtuskBoar
from features.companions.npcs.miniature_bone_golem import MiniatureBoneGolem
from features.companions.npcs.pale_walker_spider import PaleWalkerSpider
from features.companions.npcs.pondlover_frog import PondloverFrog
from features.companions.npcs.scuttledark_scorpion import ScuttledarkScorpion
from features.companions.npcs.shadowfoot_raccoon import ShadowfootRaccoon
from features.companions.npcs.silverwing_owl import SilverwingOwl
from features.companions.npcs.sunbask_turtle import SunbaskTurtle
from features.companions.npcs.tangleweb_spider import TanglewebSpider
from features.companions.npcs.tidewater_crab import TidewaterCrab
from features.companions.npcs.verdant_slitherer import VerdantSlitherer
from features.companions.npcs.voidseen_pup import VoidseenPup
from features.companions.npcs.wanderbound_raven import WanderboundRaven

from features.npcs.npc import NPC
from features.shared.attributes import Attributes
from features.shared.constants import BASE_BEST_TIER_POINTS, BASE_GOOD_TIER_POINTS, BASE_GREAT_TIER_POINTS
from features.shared.effect import Effect, EffectType, ItemEffectCategory
from features.shared.enums import ClassTag, CompanionKey, CompanionTier
from features.shared.item import ItemKey, Rarity
from features.shared.statuseffect import StatusEffectKey

from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from features.shared.ability import Ability

# -----------------------------------------------------------------------------
# BASE CLASS
# -----------------------------------------------------------------------------

class Companion():
    def __init__(self, icon: str, display_name: str, key: CompanionKey, rarity: Rarity, value: int, has_active_ability: bool, duel_xp_gain: int, pet_battle_xp_gain: int, preferred_foods: List[ItemKey], valid_food_categories: List[ClassTag], best_tier_items: List[ItemKey], talisman: ItemKey):        
        self._id: str = ""

        self._icon = icon
        self._display_name = display_name
        self._key = key
        self._rarity = rarity
        self._value = value
        self._has_active_ability = has_active_ability
        
        self.duel_xp_gain = duel_xp_gain
        self.pet_battle_xp_gain = pet_battle_xp_gain

        self._xp: int = 0
        self._level: int = 0
        self._remaining_xp: int = 1

        self._companion_tier_points: int = 0
        self._companion_tier: CompanionTier = CompanionTier.NoTier

        self.preferred_foods: List[ItemKey] = preferred_foods
        self.valid_food_categories: List[ClassTag] = valid_food_categories
        self.fed_this_tick: bool = False
        self.custom_named: bool = False

        self.talisman: ItemKey = talisman
        self.talisman_given: bool = False

        self._best_tier_items: List[ItemKey] = best_tier_items

    # This will either return an Ability or an Effect, scaled based on the level of the companion, or
    # None if the requirements aren't met. Some Effects from companions only apply when attacking or similar,
    # hence the usage of the effect_category parameter.
    @abstractmethod
    def get_dueling_ability(self, effect_category: ItemEffectCategory | None) -> Effect | Ability | None:
        pass

    @abstractmethod
    def get_pet_battle_entity(self) -> NPC:
        # So, the concept here is that each Companion will reference an NPC which will be instantised based on the level
        # of the Companion; the abilities and stats, notably, will be determined based on that input level.
        pass

    @abstractmethod
    def get_base_abilities(self) -> List[Ability]:
        pass

    @abstractmethod
    def get_attribute_scaling(self) -> Attributes:
        # Negative values indicate x per level rather than positive values which indicate 1 per x level
        pass

    def get_xp_to_level(self, level: int) -> int:
        return ceil(5 + 15 * level * (level - 1) + (2 ** ((level - 1) / 15.0) - 1) / (1 - 2 ** (-1 / 15.0)))

    def level_up_check(self) -> int:
        org_level = self._level
        while self._remaining_xp <= 0:
            self._level += 1
            self._remaining_xp = self.get_xp_to_level(self._level + 1) - self._xp
        return self._level - org_level

    def add_xp(self, xp_to_add: int) -> int:
        org_level = self._level

        self._xp = max(0, self._xp + xp_to_add)
        self._remaining_xp = self.get_xp_to_level(self._level + 1) - self._xp

        self.level_up_check()

        return self._level - org_level

    def add_companion_points(self, points: int):
        self._companion_tier_points += points
        if self._companion_tier_points >= BASE_BEST_TIER_POINTS:
            self._companion_tier = CompanionTier.Best
        elif self._companion_tier_points >= BASE_GREAT_TIER_POINTS:
            self._companion_tier = CompanionTier.Great
        elif self._companion_tier_points >= BASE_GOOD_TIER_POINTS:
            self._companion_tier = CompanionTier.Good

    def get_points_to_next_tier_str(self):
        if self._companion_tier == CompanionTier.Good:
            return f"{BASE_GREAT_TIER_POINTS - self._companion_tier_points} points remaining to Great Bond"
        elif self._companion_tier == CompanionTier.Great:
            return f"{BASE_BEST_TIER_POINTS - self._companion_tier_points} points remaining to Best Bond"
        elif self._companion_tier == CompanionTier.Best:
            return f"{self._companion_tier_points} companion points"
        return f"{BASE_GOOD_TIER_POINTS - self._companion_tier_points} points remaining to Good Bond"

    def get_icon_and_name(self):
        return f"{self._icon} {self._display_name}"

    def get_name(self):
        return self._display_name

    def set_name(self, name: str):
        self._display_name = name

    def get_icon(self):
        return self._icon

    def get_key(self):
        return self._key

    def get_value(self):
        return self._value

    def get_has_active_ability(self):
        return self._has_active_ability

    def get_tier(self):
        return self._companion_tier

    def get_tier_str(self):
        if self._companion_tier == CompanionTier.Good:
            return "Good Bond"
        elif self._companion_tier == CompanionTier.Great:
            return "Great Bond"
        elif self._companion_tier == CompanionTier.Best:
            return "Best Bond"
        return "No Bond"
    
    def get_best_tier_items(self):
        return self._best_tier_items

    def set_id(self, id: str):
        self._id = id

    def __str__(self, use_base_abilities=False) -> str:
        display_string = f"**{self.get_icon_and_name()}**\n*{self._rarity} Companion*\n\n"

        display_string += f"Level: {self._level} *({self.get_xp_to_level(self._level + 1) - self._xp} xp to next)*\n"
        display_string += f"{self.get_tier_str()} *({self.get_points_to_next_tier_str()})*"

        display_string += "\n\n﹋﹋﹋﹋﹋﹋﹋﹋\n"
        
        dueling_ability = self.get_dueling_ability(effect_category=None)
        if self._has_active_ability:
            display_string += "**Active Dueling Ability**\n\n"
        else:
            display_string += "**Passive Dueling Ability**\n\n"
        display_string += "᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n" + str(dueling_ability) + "\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆"

        display_string += "\n\n﹋﹋﹋﹋﹋﹋﹋﹋\n"

        pet_battle_entity = self.get_pet_battle_entity()
        expertise = pet_battle_entity.get_expertise()
        display_string += (
            f"**Attributes**\n\n"
            f"Constitution: {expertise.constitution}\n"
            f"Strength: {expertise.strength}\n"
            f"Dexterity: {expertise.dexterity}\n"
            f"Intelligence: {expertise.intelligence}\n"
            f"Luck: {expertise.luck}\n"
            f"Memory: {expertise.memory}"
        )

        display_string += "\n\n﹋﹋﹋﹋﹋﹋﹋﹋\n"

        abilities = []
        if use_base_abilities:
            abilities = self.get_base_abilities()
        else:
            abilities = pet_battle_entity.get_dueling().abilities
        
        display_string += "**Companion Battle Abilities**\n\n" + "\n".join([f"᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{str(ability)}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆" for ability in abilities])

        display_string += "\n\n﹋﹋﹋﹋﹋﹋﹋﹋\n"

        display_string += (
            f"**Weapon**\n\n"
            f"{pet_battle_entity.get_equipment().get_item_in_slot(ClassTag.Equipment.MainHand)}"
        )

        display_string += "\n\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆"

        return display_string

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", "")

        self._icon = state.get("_icon", "")
        self._display_name = state.get("_display_name", "")
        self._key = state.get("_key", CompanionKey.Unknown)
        self._rarity = state.get("_rarity", Rarity.Unknown)
        self._has_active_ability = state.get("_has_active_ability", False)
        self._duel_xp_gain = state.get("_duel_xp_gain", 1)

        self._xp = state.get("_xp", 0)
        self._level = state.get("_level", 0)
        self._remaining_xp = state.get("_remaining_xp", 1)

        self._companion_tier_points = state.get("_companion_tier_points", 0)
        self._companion_tier = state.get("_companion_tier", CompanionTier.NoTier)

        self.preferred_foods = state.get("preferred_foods", [])
        self.valid_food_categories = state.get("valid_food_categories", [])
        self.fed_this_tick = state.get("fed_this_tick", False)
        self.custom_named = state.get("custom_named", False)

        self.talisman = state.get("talisman", ItemKey.ClumpOfLeaves)
        self.talisman_given = state.get("talisman_given", False)

        self._best_tier_items = state.get("_best_tier_items", [])

# -----------------------------------------------------------------------------
# COMPANION CLASSES
# -----------------------------------------------------------------------------

class BlueFlitterwingButterflyCompanion(Companion):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDD8B",
            display_name="Blue Flitterwing Butterfly",
            key=CompanionKey.BlueFlitterwingButterfly,
            rarity=Rarity.Common,
            value=50,
            has_active_ability=True,
            duel_xp_gain=4,
            pet_battle_xp_gain=6,
            preferred_foods=[ItemKey.AzureberryJuice, ItemKey.CrownberryJuice, ItemKey.SundewDelight],
            valid_food_categories=[ClassTag.Consumable.Food, ClassTag.Ingredient.Herb, ClassTag.Ingredient.RawFish, ClassTag.Ingredient.RawFood],
            best_tier_items=[],
            talisman=ItemKey.FlitterwingTalisman
        )

    def get_dueling_ability(self, effect_category: ItemEffectCategory | None) -> Ability:
        if self._level >= 40:
            return ManaLeechV()
        elif self._level >= 30:
            return ManaLeechIV()
        elif self._level >= 20:
            return ManaLeechIII()
        elif self._level >= 10:
            return ManaLeechII()
        else:
            return ManaLeechI()

    def get_pet_battle_entity(self) -> NPC:
        entity = BlueFlitterwingButterfly(self._level)
        entity.set_id(self._id)
        return entity

    def get_base_abilities(self) -> List[Ability]:
        return [MesmerizeI(), InnervateI(), WingbeatI()]

    def get_attribute_scaling(self) -> Attributes:
        return Attributes(4, 5, 2, 1, 2, 5)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

        self._id = state.get("_id", "")

        self._display_name = state.get("_display_name", "Blue Flitterwing Butterfly")

        self._xp = state.get("_xp", 0)
        self._level = state.get("_level", 0)
        self._remaining_xp = state.get("_remaining_xp", 1)

        self._companion_tier_points = state.get("_companion_tier_points", 0)
        self._companion_tier = state.get("_companion_tier", CompanionTier.NoTier)

        self.fed_this_tick = state.get("fed_this_tick", False)
        self.custom_named = state.get("custom_named", False)
        self.talisman_given = state.get("talisman_given", False)


class DeepwoodCubCompanion(Companion):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC3B",
            display_name="Deepwood Cub",
            key=CompanionKey.DeepwoodCub,
            rarity=Rarity.Rare,
            value=500,
            has_active_ability=False,
            duel_xp_gain=3,
            pet_battle_xp_gain=5,
            preferred_foods=[ItemKey.Honeyfruit, ItemKey.Crownberry],
            valid_food_categories=[ClassTag.Consumable.Food, ClassTag.Ingredient.Herb, ClassTag.Ingredient.RawFish, ClassTag.Ingredient.RawFood],
            best_tier_items=[],
            talisman=ItemKey.DeepwoodTalisman
        )

    def get_dueling_ability(self, effect_category: ItemEffectCategory | None) -> Effect | None:
        if effect_category is not None and effect_category != ItemEffectCategory.Permanent:
            return None
        
        if self._level >= 40:
            return Effect(
                EffectType.DmgResist,
                effect_value=0.05,
                effect_time=-1,
                conditions=[],
                condition_values=[]
            )
        elif self._level >= 30:
            return Effect(
                EffectType.DmgResist,
                effect_value=0.04,
                effect_time=-1,
                conditions=[],
                condition_values=[]
            )
        elif self._level >= 20:
            return Effect(
                EffectType.DmgResist,
                effect_value=0.03,
                effect_time=-1,
                conditions=[],
                condition_values=[]
            )
        elif self._level >= 10:
            return Effect(
                EffectType.DmgResist,
                effect_value=0.02,
                effect_time=-1,
                conditions=[],
                condition_values=[]
            )
        else:
            return Effect(
                EffectType.DmgResist,
                effect_value=0.01,
                effect_time=-1,
                conditions=[],
                condition_values=[]
            )

    def get_pet_battle_entity(self) -> NPC:
        entity = DeepwoodCub(self._level)
        entity.set_id(self._id)
        return entity

    def get_base_abilities(self) -> List[Ability]:
        return [BearDownI(), HibernateI(), BulkEnduranceI()]

    def get_attribute_scaling(self) -> Attributes:
        return Attributes(1, 1, 5, 5, 3, 5)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

        self._id = state.get("_id", "")

        self._display_name = state.get("_display_name", "Deepwood Cub")

        self._xp = state.get("_xp", 0)
        self._level = state.get("_level", 0)
        self._remaining_xp = state.get("_remaining_xp", 1)

        self._companion_tier_points = state.get("_companion_tier_points", 0)
        self._companion_tier = state.get("_companion_tier", CompanionTier.NoTier)

        self.fed_this_tick = state.get("fed_this_tick", False)
        self.custom_named = state.get("custom_named", False)
        self.talisman_given = state.get("talisman_given", False)


class FleetfootRabbitCompanion(Companion):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC30",
            display_name="Fleetfoot Rabbit",
            key=CompanionKey.FleetfootRabbit,
            rarity=Rarity.Common,
            value=100,
            has_active_ability=True,
            duel_xp_gain=3,
            pet_battle_xp_gain=5,
            preferred_foods=[ItemKey.Fissureleaf, ItemKey.Sweetroot],
            valid_food_categories=[ClassTag.Consumable.Food, ClassTag.Ingredient.Herb, ClassTag.Ingredient.RawFish, ClassTag.Ingredient.RawFood],
            best_tier_items=[],
            talisman=ItemKey.LuckyPawTalisman
        )

    def get_dueling_ability(self, effect_category: ItemEffectCategory | None) -> Ability:
        if self._level >= 40:
            return QuickeningPaceV()
        elif self._level >= 30:
            return QuickeningPaceIV()
        elif self._level >= 20:
            return QuickeningPaceIII()
        elif self._level >= 10:
            return QuickeningPaceII()
        else:
            return QuickeningPaceI()

    def get_pet_battle_entity(self) -> NPC:
        entity = FleetfootRabbit(self._level)
        entity.set_id(self._id)
        return entity

    def get_base_abilities(self) -> List[Ability]:
        return [FleeI(), WhatLuckI(), PummelI()]

    def get_attribute_scaling(self) -> Attributes:
        return Attributes(4, 5, 1, 4, 1, 5)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

        self._id = state.get("_id", "")

        self._display_name = state.get("_display_name", "Fleetfoot Rabbit")

        self._xp = state.get("_xp", 0)
        self._level = state.get("_level", 0)
        self._remaining_xp = state.get("_remaining_xp", 1)

        self._companion_tier_points = state.get("_companion_tier_points", 0)
        self._companion_tier = state.get("_companion_tier", CompanionTier.NoTier)

        self.fed_this_tick = state.get("fed_this_tick", False)
        self.custom_named = state.get("custom_named", False)
        self.talisman_given = state.get("talisman_given", False)


class FlyingFoxCompanion(Companion):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDD8A",
            display_name="Flying Fox",
            key=CompanionKey.FlyingFox,
            rarity=Rarity.Uncommon,
            value=300,
            has_active_ability=False,
            duel_xp_gain=4,
            pet_battle_xp_gain=6,
            preferred_foods=[ItemKey.Minnow, ItemKey.Roughy, ItemKey.FishCake, ItemKey.CookedMinnow, ItemKey.CookedRoughy],
            valid_food_categories=[ClassTag.Consumable.Food, ClassTag.Ingredient.Herb, ClassTag.Ingredient.RawFish, ClassTag.Ingredient.RawFood],
            best_tier_items=[],
            talisman=ItemKey.FoxsFeatherTalisman
        )

    def get_dueling_ability(self, effect_category: ItemEffectCategory | None) -> Effect | None:
        if effect_category is not None and effect_category != ItemEffectCategory.Permanent:
            return None
        
        if self._level >= 40:
            return Effect(
                EffectType.DexMod,
                effect_value=5,
                effect_time=-1,
                conditions=[],
                condition_values=[]
            )
        elif self._level >= 30:
            return Effect(
                EffectType.DexMod,
                effect_value=4,
                effect_time=-1,
                conditions=[],
                condition_values=[]
            )
        elif self._level >= 20:
            return Effect(
                EffectType.DexMod,
                effect_value=3,
                effect_time=-1,
                conditions=[],
                condition_values=[]
            )
        elif self._level >= 10:
            return Effect(
                EffectType.DexMod,
                effect_value=2,
                effect_time=-1,
                conditions=[],
                condition_values=[]
            )
        else:
            return Effect(
                EffectType.DexMod,
                effect_value=1,
                effect_time=-1,
                conditions=[],
                condition_values=[]
            )

    def get_pet_battle_entity(self) -> NPC:
        entity = FlyingFox(self._level)
        entity.set_id(self._id)
        return entity

    def get_base_abilities(self) -> List[Ability]:
        return [LungeI(), ToTheSkiesI(), GustI()]

    def get_attribute_scaling(self) -> Attributes:
        return Attributes(3, 3, 1, 1, 2, 5)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

        self._id = state.get("_id", "")

        self._display_name = state.get("_display_name", "Flying Fox")

        self._xp = state.get("_xp", 0)
        self._level = state.get("_level", 0)
        self._remaining_xp = state.get("_remaining_xp", 1)

        self._companion_tier_points = state.get("_companion_tier_points", 0)
        self._companion_tier = state.get("_companion_tier", CompanionTier.NoTier)

        self.fed_this_tick = state.get("fed_this_tick", False)
        self.custom_named = state.get("custom_named", False)
        self.talisman_given = state.get("talisman_given", False)


class GiantTowerBeetleCompanion(Companion):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEB2",
            display_name="Giant Tower Beetle",
            key=CompanionKey.GiantTowerBeetle,
            rarity=Rarity.Uncommon,
            value=300,
            has_active_ability=True,
            duel_xp_gain=3,
            pet_battle_xp_gain=5,
            preferred_foods=[ItemKey.Compost, ItemKey.Shellflower],
            valid_food_categories=[ClassTag.Consumable.Food, ClassTag.Ingredient.Herb, ClassTag.Ingredient.RawFish, ClassTag.Ingredient.RawFood, ClassTag.Gardening.Soil],
            best_tier_items=[],
            talisman=ItemKey.TowerTalisman
        )

    def get_dueling_ability(self, effect_category: ItemEffectCategory | None) -> Ability:
        if self._level >= 40:
            return ToweringArmorV()
        elif self._level >= 30:
            return ToweringArmorIV()
        elif self._level >= 20:
            return ToweringArmorIII()
        elif self._level >= 10:
            return ToweringArmorII()
        else:
            return ToweringArmorI()

    def get_pet_battle_entity(self) -> NPC:
        entity = GiantTowerBeetle(self._level)
        entity.set_id(self._id)
        return entity

    def get_base_abilities(self) -> List[Ability]:
        return [PlatedArmorI(), TowerStanceI(), BeetleBashI()]

    def get_attribute_scaling(self) -> Attributes:
        return Attributes(1, 1, 5, 5, 3, 5)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

        self._id = state.get("_id", "")

        self._display_name = state.get("_display_name", "Giant Tower Beetle")

        self._xp = state.get("_xp", 0)
        self._level = state.get("_level", 0)
        self._remaining_xp = state.get("_remaining_xp", 1)

        self._companion_tier_points = state.get("_companion_tier_points", 0)
        self._companion_tier = state.get("_companion_tier", CompanionTier.NoTier)

        self.fed_this_tick = state.get("fed_this_tick", False)
        self.custom_named = state.get("custom_named", False)
        self.talisman_given = state.get("talisman_given", False)


class GnashtuskBoarCompanion(Companion):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC17",
            display_name="Gnashtusk Boar",
            key=CompanionKey.GnashtuskBoar,
            rarity=Rarity.Common,
            value=200,
            has_active_ability=False,
            duel_xp_gain=4,
            pet_battle_xp_gain=6,
            preferred_foods=[ItemKey.Sweetroot, ItemKey.Elsberries, ItemKey.Crownberry],
            valid_food_categories=[ClassTag.Consumable.Food, ClassTag.Ingredient.Herb, ClassTag.Ingredient.RawFish, ClassTag.Ingredient.RawFood],
            best_tier_items=[],
            talisman=ItemKey.GnashtuskTalisman
        )

    def get_dueling_ability(self, effect_category: ItemEffectCategory | None) -> Effect | None:
        if effect_category is not None and effect_category != ItemEffectCategory.OnSuccessfulAttack:
            return None
        
        if self._level >= 40:
            return Effect(
                EffectType.DmgBuffBleeding,
                effect_value=0.05,
                effect_time=-1,
                conditions=[],
                condition_values=[]
            )
        elif self._level >= 30:
            return Effect(
                EffectType.DmgBuffBleeding,
                effect_value=0.1,
                effect_time=-1,
                conditions=[],
                condition_values=[]
            )
        elif self._level >= 20:
            return Effect(
                EffectType.DmgBuffBleeding,
                effect_value=0.15,
                effect_time=-1,
                conditions=[],
                condition_values=[]
            )
        elif self._level >= 10:
            return Effect(
                EffectType.DmgBuffBleeding,
                effect_value=0.2,
                effect_time=-1,
                conditions=[],
                condition_values=[]
            )
        else:
            return Effect(
                EffectType.DmgBuffBleeding,
                effect_value=0.25,
                effect_time=-1,
                conditions=[],
                condition_values=[]
            )

    def get_pet_battle_entity(self) -> NPC:
        entity = GnashtuskBoar(self._level)
        entity.set_id(self._id)
        return entity

    def get_base_abilities(self) -> List[Ability]:
        return [GoreI(), ThickHideI(), ChargeI()]

    def get_attribute_scaling(self) -> Attributes:
        return Attributes(1, 1, 4, 5, 4, 5)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

        self._id = state.get("_id", "")

        self._display_name = state.get("_display_name", "Gnashtusk Boar")

        self._xp = state.get("_xp", 0)
        self._level = state.get("_level", 0)
        self._remaining_xp = state.get("_remaining_xp", 1)

        self._companion_tier_points = state.get("_companion_tier_points", 0)
        self._companion_tier = state.get("_companion_tier", CompanionTier.NoTier)

        self.fed_this_tick = state.get("fed_this_tick", False)
        self.custom_named = state.get("custom_named", False)
        self.talisman_given = state.get("talisman_given", False)


class MiniatureBoneGolemCompanion(Companion):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC80",
            display_name="Miniature Bone Golem",
            key=CompanionKey.MinatureBoneGolem,
            rarity=Rarity.Legendary,
            value=2500,
            has_active_ability=True,
            duel_xp_gain=2,
            pet_battle_xp_gain=4,
            preferred_foods=[ItemKey.CrackedQuartz, ItemKey.Quartz, ItemKey.FlawlessQuartz],
            valid_food_categories=[ClassTag.Ingredient.CraftingMaterial, ClassTag.Equipment.Equipment],
            best_tier_items=[],
            talisman=ItemKey.SkullTalisman
        )

    def get_dueling_ability(self, effect_category: ItemEffectCategory | None) -> Ability:
        if self._level >= 40:
            return ThrowTheBonesV()
        elif self._level >= 30:
            return ThrowTheBonesIV()
        elif self._level >= 20:
            return ThrowTheBonesIII()
        elif self._level >= 10:
            return ThrowTheBonesII()
        else:
            return ThrowTheBonesI()

    def get_pet_battle_entity(self) -> NPC:
        entity = MiniatureBoneGolem(self._level)
        entity.set_id(self._id)
        return entity

    def get_base_abilities(self) -> List[Ability]:
        return [UndeathIsJustTheBeginningI(), MightyBoneFistI(), EruptionOfBoneI()]
    
    def get_attribute_scaling(self) -> Attributes:
        return Attributes(2, 1, -2, 5, -2, 5)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

        self._id = state.get("_id", "")

        self._display_name = state.get("_display_name", "Miniature Bone Golem")

        self._xp = state.get("_xp", 0)
        self._level = state.get("_level", 0)
        self._remaining_xp = state.get("_remaining_xp", 1)

        self._companion_tier_points = state.get("_companion_tier_points", 0)
        self._companion_tier = state.get("_companion_tier", CompanionTier.NoTier)

        self.fed_this_tick = state.get("fed_this_tick", False)
        self.custom_named = state.get("custom_named", False)
        self.talisman_given = state.get("talisman_given", False)


class PaleWalkerSpiderCompanion(Companion):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD77\uFE0F",
            display_name="Pale Walker",
            key=CompanionKey.PaleWalkerSpider,
            rarity=Rarity.Epic,
            value=1500,
            has_active_ability=True,
            duel_xp_gain=2,
            pet_battle_xp_gain=4,
            preferred_foods=[ItemKey.Grub],
            valid_food_categories=[ClassTag.Consumable.Food, ClassTag.Ingredient.Herb, ClassTag.Ingredient.RawFish, ClassTag.Ingredient.RawFood],
            best_tier_items=[],
            talisman=ItemKey.PaleTalisman
        )

    def get_dueling_ability(self, effect_category: ItemEffectCategory | None) -> Ability:
        if self._level >= 40:
            return VenomousBiteV()
        elif self._level >= 30:
            return VenomousBiteIV()
        elif self._level >= 20:
            return VenomousBiteIII()
        elif self._level >= 10:
            return VenomousBiteII()
        else:
            return VenomousBiteI()

    def get_pet_battle_entity(self) -> NPC:
        entity = PaleWalkerSpider(self._level)
        entity.set_id(self._id)
        return entity

    def get_base_abilities(self) -> List[Ability]:
        return [DeadlyVenomI(), GhostlyMovementI(), GlassPierceI()]

    def get_attribute_scaling(self) -> Attributes:
        return Attributes(3, 5, 1, 1, 1, 5)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

        self._id = state.get("_id", "")

        self._display_name = state.get("_display_name", "Pale Walker")

        self._xp = state.get("_xp", 0)
        self._level = state.get("_level", 0)
        self._remaining_xp = state.get("_remaining_xp", 1)

        self._companion_tier_points = state.get("_companion_tier_points", 0)
        self._companion_tier = state.get("_companion_tier", CompanionTier.NoTier)

        self.fed_this_tick = state.get("fed_this_tick", False)
        self.custom_named = state.get("custom_named", False)
        self.talisman_given = state.get("talisman_given", False)


class PondloverFrogCompanion(Companion):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC38",
            display_name="Pondlover Frog",
            key=CompanionKey.PondloverFrog,
            rarity=Rarity.Common,
            value=100,
            has_active_ability=True,
            duel_xp_gain=3,
            pet_battle_xp_gain=5,
            preferred_foods=[ItemKey.Grub, ItemKey.Seaclover],
            valid_food_categories=[ClassTag.Consumable.Food, ClassTag.Ingredient.Herb, ClassTag.Ingredient.RawFish, ClassTag.Ingredient.RawFood],
            best_tier_items=[],
            talisman=ItemKey.PondloverTalisman
        )

    def get_dueling_ability(self, effect_category: ItemEffectCategory | None) -> Ability:
        if self._level >= 40:
            return IsThatAFlyV()
        elif self._level >= 30:
            return IsThatAFlyIV()
        elif self._level >= 20:
            return IsThatAFlyIII()
        elif self._level >= 10:
            return IsThatAFlyII()
        else:
            return IsThatAFlyI()

    def get_pet_battle_entity(self) -> NPC:
        entity = PondloverFrog(self._level)
        entity.set_id(self._id)
        return entity

    def get_base_abilities(self) -> List[Ability]:
        return [IsThatAFlyI(), HippityHopI(), BouncingKickI()]

    def get_attribute_scaling(self) -> Attributes:
        return Attributes(2, 4, 1, 2, 3, 5)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

        self._id = state.get("_id", "")

        self._display_name = state.get("_display_name", "Pondlover Frog")

        self._xp = state.get("_xp", 0)
        self._level = state.get("_level", 0)
        self._remaining_xp = state.get("_remaining_xp", 1)

        self._companion_tier_points = state.get("_companion_tier_points", 0)
        self._companion_tier = state.get("_companion_tier", CompanionTier.NoTier)

        self.fed_this_tick = state.get("fed_this_tick", False)
        self.custom_named = state.get("custom_named", False)
        self.talisman_given = state.get("talisman_given", False)


class ScuttledarkScorpionCompanion(Companion):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDD82",
            display_name="Scuttledark Scorpion",
            key=CompanionKey.ScuttledarkScorpion,
            rarity=Rarity.Rare,
            value=500,
            has_active_ability=False,
            duel_xp_gain=3,
            pet_battle_xp_gain=5,
            preferred_foods=[ItemKey.Grub],
            valid_food_categories=[ClassTag.Consumable.Food, ClassTag.Ingredient.Herb, ClassTag.Ingredient.RawFish, ClassTag.Ingredient.RawFood],
            best_tier_items=[],
            talisman=ItemKey.ScuttledarkTalisman
        )

    def get_dueling_ability(self, effect_category: ItemEffectCategory | None) -> Effect | None:
        if effect_category is not None and effect_category != ItemEffectCategory.Permanent:
            return None
        
        if self._level >= 40:
            return Effect(
                EffectType.PiercingDmg,
                effect_value=5,
                effect_time=-1,
                conditions=[],
                condition_values=[]
            )
        elif self._level >= 30:
            return Effect(
                EffectType.PiercingDmg,
                effect_value=4,
                effect_time=-1,
                conditions=[],
                condition_values=[]
            )
        elif self._level >= 20:
            return Effect(
                EffectType.PiercingDmg,
                effect_value=3,
                effect_time=-1,
                conditions=[],
                condition_values=[]
            )
        elif self._level >= 10:
            return Effect(
                EffectType.PiercingDmg,
                effect_value=2,
                effect_time=-1,
                conditions=[],
                condition_values=[]
            )
        else:
            return Effect(
                EffectType.PiercingDmg,
                effect_value=1,
                effect_time=-1,
                conditions=[],
                condition_values=[]
            )

    def get_pet_battle_entity(self) -> NPC:
        entity = ScuttledarkScorpion(self._level)
        entity.set_id(self._id)
        return entity

    def get_base_abilities(self) -> List[Ability]:
        return [PowerfulPierceI(), IntoTheShadowsI(), GraspingClawsI()]

    def get_attribute_scaling(self) -> Attributes:
        return Attributes(2, 1, 4, 2, 4, 5)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

        self._id = state.get("_id", "")

        self._display_name = state.get("_display_name", "Scuttledark Scorpion")

        self._xp = state.get("_xp", 0)
        self._level = state.get("_level", 0)
        self._remaining_xp = state.get("_remaining_xp", 1)

        self._companion_tier_points = state.get("_companion_tier_points", 0)
        self._companion_tier = state.get("_companion_tier", CompanionTier.NoTier)

        self.fed_this_tick = state.get("fed_this_tick", False)
        self.custom_named = state.get("custom_named", False)
        self.talisman_given = state.get("talisman_given", False)


class ShadowfootRaccoonCompanion(Companion):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDD9D",
            display_name="Shadowfoot Raccoon",
            key=CompanionKey.ShadowfootRaccoon,
            rarity=Rarity.Rare,
            value=500,
            has_active_ability=True,
            duel_xp_gain=3,
            pet_battle_xp_gain=5,
            preferred_foods=[ItemKey.Minnow, ItemKey.Roughy, ItemKey.CookedMinnow, ItemKey.CookedRoughy, ItemKey.FishCake],
            valid_food_categories=[ClassTag.Consumable.Food, ClassTag.Ingredient.Herb, ClassTag.Ingredient.RawFish, ClassTag.Ingredient.RawFood],
            best_tier_items=[],
            talisman=ItemKey.LuckyRockTalisman
        )

    def get_dueling_ability(self, effect_category: ItemEffectCategory | None) -> Ability:
        if self._level >= 40:
            return SneakyManeuversV()
        elif self._level >= 30:
            return SneakyManeuversIV()
        elif self._level >= 20:
            return SneakyManeuversIII()
        elif self._level >= 10:
            return SneakyManeuversII()
        else:
            return SneakyManeuversI()

    def get_pet_battle_entity(self) -> NPC:
        entity = ShadowfootRaccoon(self._level)
        entity.set_id(self._id)
        return entity

    def get_base_abilities(self) -> List[Ability]:
        return [StrikeFromBehindI(), LuckyPawsI(), IntoTheShadowsI()]

    def get_attribute_scaling(self) -> Attributes:
        return Attributes(2, 4, 1, 2, 1, 5)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

        self._id = state.get("_id", "")

        self._display_name = state.get("_display_name", "Shadowfoot Raccoon")

        self._xp = state.get("_xp", 0)
        self._level = state.get("_level", 0)
        self._remaining_xp = state.get("_remaining_xp", 1)

        self._companion_tier_points = state.get("_companion_tier_points", 0)
        self._companion_tier = state.get("_companion_tier", CompanionTier.NoTier)

        self.fed_this_tick = state.get("fed_this_tick", False)
        self.custom_named = state.get("custom_named", False)
        self.talisman_given = state.get("talisman_given", False)


class SilverwingOwlCompanion(Companion):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDD89",
            display_name="Silverwing Owl",
            key=CompanionKey.SilverwingOwl,
            rarity=Rarity.Rare,
            value=800,
            has_active_ability=False,
            duel_xp_gain=3,
            pet_battle_xp_gain=5,
            preferred_foods=[ItemKey.Azureberries, ItemKey.Minnow, ItemKey.Roughy],
            valid_food_categories=[ClassTag.Consumable.Food, ClassTag.Ingredient.Herb, ClassTag.Ingredient.RawFish, ClassTag.Ingredient.RawFood],
            best_tier_items=[],
            talisman=ItemKey.SilverwingFeatherTalisman
        )

    def get_dueling_ability(self, effect_category: ItemEffectCategory | None) -> Effect | None:
        if effect_category is not None and effect_category != ItemEffectCategory.OnTurnStart:
            return None
        
        if self._level >= 40:
            return Effect(
                EffectType.RestoreMana,
                effect_value=5,
                effect_time=-1,
                conditions=[],
                condition_values=[]
            )
        elif self._level >= 30:
            return Effect(
                EffectType.RestoreMana,
                effect_value=4,
                effect_time=-1,
                conditions=[],
                condition_values=[]
            )
        elif self._level >= 20:
            return Effect(
                EffectType.RestoreMana,
                effect_value=3,
                effect_time=-1,
                conditions=[],
                condition_values=[]
            )
        elif self._level >= 10:
            return Effect(
                EffectType.RestoreMana,
                effect_value=2,
                effect_time=-1,
                conditions=[],
                condition_values=[]
            )
        else:
            return Effect(
                EffectType.RestoreMana,
                effect_value=1,
                effect_time=-1,
                conditions=[],
                condition_values=[]
            )

    def get_pet_battle_entity(self) -> NPC:
        entity = SilverwingOwl(self._level)
        entity.set_id(self._id)
        return entity

    def get_base_abilities(self) -> List[Ability]:
        return [MysticShroudI(), FeathersFlyI(), WithTheWindI()]

    def get_attribute_scaling(self) -> Attributes:
        return Attributes(2, 4, 2, 1, 2, 5)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

        self._id = state.get("_id", "")

        self._display_name = state.get("_display_name", "Silverwing Owl")

        self._xp = state.get("_xp", 0)
        self._level = state.get("_level", 0)
        self._remaining_xp = state.get("_remaining_xp", 1)

        self._companion_tier_points = state.get("_companion_tier_points", 0)
        self._companion_tier = state.get("_companion_tier", CompanionTier.NoTier)

        self.fed_this_tick = state.get("fed_this_tick", False)
        self.custom_named = state.get("custom_named", False)
        self.talisman_given = state.get("talisman_given", False)


class SunbaskTurtleCompanion(Companion):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC22",
            display_name="Sunbask Turtle",
            key=CompanionKey.SunbaskTurtle,
            rarity=Rarity.Common,
            value=100,
            has_active_ability=False,
            duel_xp_gain=3,
            pet_battle_xp_gain=5,
            preferred_foods=[ItemKey.Crownberry, ItemKey.Honeyfruit, ItemKey.Stranglekelp],
            valid_food_categories=[ClassTag.Consumable.Food, ClassTag.Ingredient.Herb, ClassTag.Ingredient.RawFish, ClassTag.Ingredient.RawFood],
            best_tier_items=[],
            talisman=ItemKey.SunbaskTalisman
        )

    def get_dueling_ability(self, effect_category: ItemEffectCategory | None) -> Effect | None:
        if effect_category is not None and effect_category != ItemEffectCategory.Permanent:
            return None
        
        if self._level >= 40:
            return Effect(
                EffectType.DmgReflect,
                effect_value=0.05,
                effect_time=-1,
                conditions=[],
                condition_values=[]
            )
        elif self._level >= 30:
            return Effect(
                EffectType.DmgReflect,
                effect_value=0.04,
                effect_time=-1,
                conditions=[],
                condition_values=[]
            )
        elif self._level >= 20:
            return Effect(
                EffectType.DmgReflect,
                effect_value=0.03,
                effect_time=-1,
                conditions=[],
                condition_values=[]
            )
        elif self._level >= 10:
            return Effect(
                EffectType.DmgReflect,
                effect_value=0.02,
                effect_time=-1,
                conditions=[],
                condition_values=[]
            )
        else:
            return Effect(
                EffectType.DmgReflect,
                effect_value=0.01,
                effect_time=-1,
                conditions=[],
                condition_values=[]
            )

    def get_pet_battle_entity(self) -> NPC:
        entity = SunbaskTurtle(self._level)
        entity.set_id(self._id)
        return entity

    def get_base_abilities(self) -> List[Ability]:
        return [DeflectionI(), ShellterI(), TerraspinI()]

    def get_attribute_scaling(self) -> Attributes:
        return Attributes(1, 3, 4, 3, 1, 5)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

        self._id = state.get("_id", "")

        self._display_name = state.get("_display_name", "Sunbask Turtle")

        self._xp = state.get("_xp", 0)
        self._level = state.get("_level", 0)
        self._remaining_xp = state.get("_remaining_xp", 1)

        self._companion_tier_points = state.get("_companion_tier_points", 0)
        self._companion_tier = state.get("_companion_tier", CompanionTier.NoTier)

        self.fed_this_tick = state.get("fed_this_tick", False)
        self.custom_named = state.get("custom_named", False)
        self.talisman_given = state.get("talisman_given", False)


class TanglewebSpiderCompanion(Companion):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD77\uFE0F",
            display_name="Tangleweb Spider",
            key=CompanionKey.TanglewebSpider,
            rarity=Rarity.Common,
            value=50,
            has_active_ability=True,
            duel_xp_gain=4,
            pet_battle_xp_gain=6,
            preferred_foods=[ItemKey.Grub],
            valid_food_categories=[ClassTag.Consumable.Food, ClassTag.Ingredient.Herb, ClassTag.Ingredient.RawFish, ClassTag.Ingredient.RawFood],
            best_tier_items=[],
            talisman=ItemKey.TanglewebTalisman
        )

    def get_dueling_ability(self, effect_category: ItemEffectCategory | None) -> Ability:
        if self._level >= 40:
            return WebShotV()
        elif self._level >= 30:
            return WebShotIV()
        elif self._level >= 20:
            return WebShotIII()
        elif self._level >= 10:
            return WebShotII()
        else:
            return WebShotI()

    def get_pet_battle_entity(self) -> NPC:
        entity = TanglewebSpider(self._level)
        entity.set_id(self._id)
        return entity

    def get_base_abilities(self) -> List[Ability]:
        return [PatientStrikeI(), CraftWebI(), WrapTheMealI()]

    def get_attribute_scaling(self) -> Attributes:
        return Attributes(2, 4, 2, 1, 1, 5)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

        self._id = state.get("_id", "")

        self._display_name = state.get("_display_name", "Tangleweb Spider")

        self._xp = state.get("_xp", 0)
        self._level = state.get("_level", 0)
        self._remaining_xp = state.get("_remaining_xp", 1)

        self._companion_tier_points = state.get("_companion_tier_points", 0)
        self._companion_tier = state.get("_companion_tier", CompanionTier.NoTier)

        self.fed_this_tick = state.get("fed_this_tick", False)
        self.custom_named = state.get("custom_named", False)
        self.talisman_given = state.get("talisman_given", False)


class TidewaterCrabCompanion(Companion):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDD80",
            display_name="Tidewater Crab",
            key=CompanionKey.TidewaterCrab,
            rarity=Rarity.Common,
            value=100,
            has_active_ability=True,
            duel_xp_gain=3,
            pet_battle_xp_gain=5,
            preferred_foods=[ItemKey.Roughy, ItemKey.Minnow, ItemKey.Shrimp],
            valid_food_categories=[ClassTag.Consumable.Food, ClassTag.Ingredient.Herb, ClassTag.Ingredient.RawFish, ClassTag.Ingredient.RawFood],
            best_tier_items=[],
            talisman=ItemKey.CrabTalisman
        )

    def get_dueling_ability(self, effect_category: ItemEffectCategory | None) -> Ability:
        if self._level >= 40:
            return PINCHV()
        elif self._level >= 30:
            return PINCHIV()
        elif self._level >= 20:
            return PINCHIII()
        elif self._level >= 10:
            return PINCHII()
        else:
            return PINCHI()

    def get_pet_battle_entity(self) -> NPC:
        entity = TidewaterCrab(self._level)
        entity.set_id(self._id)
        return entity

    def get_base_abilities(self) -> List[Ability]:
        return [PINCHI(), ScuttleI(), MiniCrabnadoI()]

    def get_attribute_scaling(self) -> Attributes:
        return Attributes(1, 1, 4, 3, 3, 5)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

        self._id = state.get("_id", "")

        self._display_name = state.get("_display_name", "Tidewater Crab")

        self._xp = state.get("_xp", 0)
        self._level = state.get("_level", 0)
        self._remaining_xp = state.get("_remaining_xp", 1)

        self._companion_tier_points = state.get("_companion_tier_points", 0)
        self._companion_tier = state.get("_companion_tier", CompanionTier.NoTier)

        self.fed_this_tick = state.get("fed_this_tick", False)
        self.custom_named = state.get("custom_named", False)
        self.talisman_given = state.get("talisman_given", False)


class VerdantSlithererCompanion(Companion):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC0D",
            display_name="Verdant Slitherer",
            key=CompanionKey.VerdantSlitherer,
            rarity=Rarity.Common,
            value=100,
            has_active_ability=False,
            duel_xp_gain=4,
            pet_battle_xp_gain=6,
            preferred_foods=[],
            valid_food_categories=[ClassTag.Consumable.Food, ClassTag.Ingredient.Herb, ClassTag.Ingredient.RawFish, ClassTag.Ingredient.RawFood],
            best_tier_items=[],
            talisman=ItemKey.VerdantTalisman
        )

    def get_dueling_ability(self, effect_category: ItemEffectCategory | None) -> Effect | None:
        if effect_category is not None and effect_category != ItemEffectCategory.OnSuccessfulAttack:
            return None
        
        if self._level >= 40:
            return Effect(
                EffectType.DmgBuffPoisoned,
                effect_value=0.05,
                effect_time=-1,
                conditions=[],
                condition_values=[]
            )
        elif self._level >= 30:
            return Effect(
                EffectType.DmgBuffPoisoned,
                effect_value=0.1,
                effect_time=-1,
                conditions=[],
                condition_values=[]
            )
        elif self._level >= 20:
            return Effect(
                EffectType.DmgBuffPoisoned,
                effect_value=0.15,
                effect_time=-1,
                conditions=[],
                condition_values=[]
            )
        elif self._level >= 10:
            return Effect(
                EffectType.DmgBuffPoisoned,
                effect_value=0.2,
                effect_time=-1,
                conditions=[],
                condition_values=[]
            )
        else:
            return Effect(
                EffectType.DmgBuffPoisoned,
                effect_value=0.25,
                effect_time=-1,
                conditions=[],
                condition_values=[]
            )

    def get_pet_battle_entity(self) -> NPC:
        entity = VerdantSlitherer(self._level)
        entity.set_id(self._id)
        return entity

    def get_base_abilities(self) -> List[Ability]:
        return [ToxungenI(), HypnoticGazeI(), CoiledStrikeI()]

    def get_attribute_scaling(self) -> Attributes:
        return Attributes(3, 2, 2, 1, 3, 5)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

        self._id = state.get("_id", "")

        self._display_name = state.get("_display_name", "Verdant Slitherer")

        self._xp = state.get("_xp", 0)
        self._level = state.get("_level", 0)
        self._remaining_xp = state.get("_remaining_xp", 1)

        self._companion_tier_points = state.get("_companion_tier_points", 0)
        self._companion_tier = state.get("_companion_tier", CompanionTier.NoTier)

        self.fed_this_tick = state.get("fed_this_tick", False)
        self.custom_named = state.get("custom_named", False)
        self.talisman_given = state.get("talisman_given", False)


class VoidseenCatCompanion(Companion):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDE3C",
            display_name="Voidseen Cat",
            key=CompanionKey.VoidseenCat,
            rarity=Rarity.Legendary,
            value=5000,
            has_active_ability=False,
            duel_xp_gain=3,
            pet_battle_xp_gain=5,
            preferred_foods=[ItemKey.Azureberries, ItemKey.Minnow, ItemKey.Roughy],
            valid_food_categories=[ClassTag.Consumable.Food, ClassTag.Ingredient.Herb, ClassTag.Ingredient.RawFish, ClassTag.Ingredient.RawFood],
            best_tier_items=[],
            talisman=ItemKey.VoidmindTalisman
        )

    def get_dueling_ability(self, effect_category: ItemEffectCategory | None) -> Effect | None:
        if effect_category is not None and effect_category != ItemEffectCategory.Permanent:
            return None
        
        if self._level >= 40:
            return Effect(
                EffectType.ResistStatusEffect,
                effect_value=1,
                effect_time=-1,
                conditions=[],
                condition_values=[],
                associated_status_effect=StatusEffectKey.Charmed
            )
        elif self._level >= 30:
            return Effect(
                EffectType.ResistStatusEffect,
                effect_value=0.8,
                effect_time=-1,
                conditions=[],
                condition_values=[],
                associated_status_effect=StatusEffectKey.Charmed
            )
        elif self._level >= 20:
            return Effect(
                EffectType.ResistStatusEffect,
                effect_value=0.6,
                effect_time=-1,
                conditions=[],
                condition_values=[],
                associated_status_effect=StatusEffectKey.Charmed
            )
        elif self._level >= 10:
            return Effect(
                EffectType.ResistStatusEffect,
                effect_value=0.4,
                effect_time=-1,
                conditions=[],
                condition_values=[],
                associated_status_effect=StatusEffectKey.Charmed
            )
        else:
            return Effect(
                EffectType.ResistStatusEffect,
                effect_value=0.2,
                effect_time=-1,
                conditions=[],
                condition_values=[],
                associated_status_effect=StatusEffectKey.Charmed
            )

    def get_pet_battle_entity(self) -> NPC:
        entity = VerdantSlitherer(self._level)
        entity.set_id(self._id)
        return entity

    def get_base_abilities(self) -> List[Ability]:
        return [SiphoningSwipeI(), ExposeTummyI(), ManaBurnI()]

    def get_attribute_scaling(self) -> Attributes:
        return Attributes(2, 3, 2, 1, -2, 5)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

        self._id = state.get("_id", "")

        self._display_name = state.get("_display_name", "Voidseen Cat")

        self._xp = state.get("_xp", 0)
        self._level = state.get("_level", 0)
        self._remaining_xp = state.get("_remaining_xp", 1)

        self._companion_tier_points = state.get("_companion_tier_points", 0)
        self._companion_tier = state.get("_companion_tier", CompanionTier.NoTier)

        self.fed_this_tick = state.get("fed_this_tick", False)
        self.custom_named = state.get("custom_named", False)
        self.talisman_given = state.get("talisman_given", False)


class VoidseenPupCompanion(Companion):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC36",
            display_name="Voidseen Pup",
            key=CompanionKey.VoidseenPup,
            rarity=Rarity.Legendary,
            value=5000,
            has_active_ability=True,
            duel_xp_gain=3,
            pet_battle_xp_gain=5,
            preferred_foods=[],
            valid_food_categories=[ClassTag.Consumable.Food, ClassTag.Ingredient.Herb, ClassTag.Ingredient.RawFish, ClassTag.Ingredient.RawFood],
            best_tier_items=[],
            talisman=ItemKey.VoidforceTalisman
        )

    def get_dueling_ability(self, effect_category: ItemEffectCategory | None) -> Ability:
        if self._level >= 40:
            return MightOfTheVoidV()
        elif self._level >= 30:
            return MightOfTheVoidIV()
        elif self._level >= 20:
            return MightOfTheVoidIII()
        elif self._level >= 10:
            return MightOfTheVoidII()
        else:
            return MightOfTheVoidI()

    def get_pet_battle_entity(self) -> NPC:
        entity = VoidseenPup(self._level)
        entity.set_id(self._id)
        return entity

    def get_base_abilities(self) -> List[Ability]:
        return [MightOfTheVoidI(), RecklessBiteI(), TheDarkBarkI()]

    def get_attribute_scaling(self) -> Attributes:
        return Attributes(2, 1, 2, 3, -2, 5)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

        self._id = state.get("_id", "")

        self._display_name = state.get("_display_name", "Voidseen Pup")

        self._xp = state.get("_xp", 0)
        self._level = state.get("_level", 0)
        self._remaining_xp = state.get("_remaining_xp", 1)

        self._companion_tier_points = state.get("_companion_tier_points", 0)
        self._companion_tier = state.get("_companion_tier", CompanionTier.NoTier)

        self.fed_this_tick = state.get("fed_this_tick", False)
        self.custom_named = state.get("custom_named", False)
        self.talisman_given = state.get("talisman_given", False)


class WanderboundRavenCompanion(Companion):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC26",
            display_name="Wanderbound Raven",
            key=CompanionKey.WanderboundRaven,
            rarity=Rarity.Common,
            value=250,
            has_active_ability=False,
            duel_xp_gain=3,
            pet_battle_xp_gain=4,
            preferred_foods=[ItemKey.Azureberries, ItemKey.AzureberryJuice],
            valid_food_categories=[ClassTag.Consumable.Food, ClassTag.Ingredient.Herb, ClassTag.Ingredient.RawFish, ClassTag.Ingredient.RawFood],
            best_tier_items=[],
            talisman=ItemKey.WanderboundTalisman
        )

    def get_dueling_ability(self, effect_category: ItemEffectCategory | None) -> Effect | None:
        if effect_category is not None and effect_category != ItemEffectCategory.Permanent:
            return None
        
        if self._level >= 40:
            return Effect(
                EffectType.AdjustedManaCosts,
                effect_value=-0.2,
                effect_time=-1,
                conditions=[],
                condition_values=[]
            )
        elif self._level >= 30:
            return Effect(
                EffectType.AdjustedManaCosts,
                effect_value=-0.16,
                effect_time=-1,
                conditions=[],
                condition_values=[]
            )
        elif self._level >= 20:
            return Effect(
                EffectType.AdjustedManaCosts,
                effect_value=-0.12,
                effect_time=-1,
                conditions=[],
                condition_values=[]
            )
        elif self._level >= 10:
            return Effect(
                EffectType.AdjustedManaCosts,
                effect_value=-0.08,
                effect_time=-1,
                conditions=[],
                condition_values=[]
            )
        else:
            return Effect(
                EffectType.AdjustedManaCosts,
                effect_value=-0.04,
                effect_time=-1,
                conditions=[],
                condition_values=[]
            )

    def get_pet_battle_entity(self) -> NPC:
        entity = WanderboundRaven(self._level)
        entity.set_id(self._id)
        return entity

    def get_base_abilities(self) -> List[Ability]:
        return [ShriekingCawI(), PeckPeckPeckI(), DiveI()]

    def get_attribute_scaling(self) -> Attributes:
        return Attributes(3, 5, 1, 1, 4, 5)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

        self._id = state.get("_id", "")

        self._display_name = state.get("_display_name", "Wanderbound Raven")

        self._xp = state.get("_xp", 0)
        self._level = state.get("_level", 0)
        self._remaining_xp = state.get("_remaining_xp", 1)

        self._companion_tier_points = state.get("_companion_tier_points", 0)
        self._companion_tier = state.get("_companion_tier", CompanionTier.NoTier)

        self.fed_this_tick = state.get("fed_this_tick", False)
        self.custom_named = state.get("custom_named", False)
        self.talisman_given = state.get("talisman_given", False)
