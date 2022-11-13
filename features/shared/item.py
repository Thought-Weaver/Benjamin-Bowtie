from __future__ import annotations

import json

from aenum import Enum, skip
from random import randint
from enum import StrEnum

from features.shared.constants import DEX_DMG_SCALE

from types import MappingProxyType
from typing import TYPE_CHECKING, List

from features.shared.effect import EFFECT_PRIORITY, EffectType
if TYPE_CHECKING:
    from features.expertise import Attributes
    from features.shared.effect import Effect

# -----------------------------------------------------------------------------
# ENUMS
# -----------------------------------------------------------------------------

class Rarity(StrEnum):
    Unknown = "Unknown"
    Common = "Common"
    Uncommon = "Uncommon"
    Rare = "Rare"
    Epic = "Epic"
    Legendary = "Legendary"
    Artifact = "Artifact"


# Using aenum and @skip to create an Enum of StrEnums
# As a result, there can't be any top-level keys
class ClassTag(Enum):
    # Items that can be equipped
    @skip
    class Equipment(StrEnum):
        Equipment = "Equipment"
        Helmet = "Helmet"
        ChestArmor = "Chest_Armor"
        Gloves = "Gloves"
        Boots = "Boots"
        Amulet = "Amulet"
        Ring = "Ring"
        Leggings = "Leggings"
        MainHand = "Main_Hand"
        OffHand = "Off_Hand"

    # Weapon types that can be generated
    @skip
    class Weapon(StrEnum):
        Weapon = "Weapon"
        Dagger = "Dagger"
        Sword = "Sword"
        Greatsword = "Greatsword"
        Knuckles = "Knuckles"
        Spear = "Spear"
        Bow = "Bow"
        Staff = "Staff"
        Shield = "Shield"

    # Items that can be stacked and used for certain effects
    @skip
    class Consumable(StrEnum):
        Consumable = "Consumable"
        UsableOutsideDuels = "Usable_Outside_Duels"
        UsableWithinDuels = "Usable_Within_Duels"
        Potion = "Potion"
        Food = "Food"
        AbilityScroll = "Ability_Scroll"

    # Items that can be used as part of crafting consumables
    @skip
    class Ingredient(StrEnum):
        Ingredient = "Ingredient"
        Herb = "Herb"
        RawFish = "Raw_Fish" # Might be good to separate fish from other foods
        RawFood = "Raw_Food" # Like uncooked potatoes, meat, etc.
        Spice = "Spice" # Specifically for cooking
        PotionIngredient = "Potion_Ingredient"
        CraftingMaterial = "CraftingMaterial"

    @skip
    class Creature(StrEnum):
        Creature = "Creature"
        Fish = "Fish"

    # Items that might might only be good for money.
    @skip
    class Valuable(StrEnum):
        Valuable = "Valuable"
        Gemstone = "Gemstone"

    @skip
    class Readable(StrEnum):
        Readable = "Readable"
        Scroll = "Scroll"

    @skip
    class Gardening(StrEnum):
        Gardening = "Gardening"
        Seed = "Seed"
        Soil = "Soil"
        GrowthAssist = "Growth_Assist"

    @skip
    class Misc(StrEnum):
        IsUnique = "Is_Unique"
        NeedsIdentification = "Needs_Identification"
        Junk = "Junk"


class StateTag(Enum):
    pass


class ItemKey(StrEnum):
    # Fishing Results
    AncientVase = "items/valuable/ancient_vase"
    BasicBoots = "items/equipment/boots/basic_boots"
    ClumpOfLeaves = "items/misc/junk/clump_of_leaves"
    Conch = "items/misc/junk/conch"
    Crab = "items/creature/fish/crab"
    Diamond = "items/valuable/gemstone/diamond"
    FishMaybe = "items/creature/fish/fish_maybe"
    Lobster = "items/creature/fish/lobster"
    Minnow = "items/creature/fish/minnow"
    MysteriousScroll = "items/readable/scroll/mysterious_scroll"
    Oyster = "items/creature/fish/oyster"
    Pufferfish = "items/creature/fish/pufferfish"
    Roughy = "items/creature/fish/roughy"
    Shark = "items/creature/fish/shark"
    Shrimp = "items/creature/fish/shrimp"
    Squid = "items/creature/fish/squid"

    # Wishing Well Results
    SunlessSteps = "items/equipment/boots/sunless_steps"
    SunlessHeart = "items/equipment/chest_armor/sunless_heart"
    SunlessGrip = "items/equipment/gloves/sunless_grip"
    SunlessMind = "items/equipment/helmet/sunless_mind"
    SunlessStride = "items/equipment/leggings/sunless_stride"
    SunlessWill = "items/equipment/ring/sunless_will"
    SunlessChains = "items/equipment/amulet/sunless_chains"

    # Potions
    LesserHealthPotion = "items/consumable/potions/lesser_health_potion"
    HealthPotion = "items/consumable/potions/health_potion"
    GreaterHealthPotion = "items/consumable/potions/greater_health_potion"
    LesserManaPotion = "items/consumable/potions/lesser_mana_potion"
    ManaPotion = "items/consumable/potions/mana_potion"
    GreaterManaPotion = "items/consumable/potions/greater_mana_potion"

    # Herbs
    AntlerCoral = "items/ingredient/herbs/antler_coral"
    Asptongue = "items/ingredient/herbs/asptongue"
    BandedCoral = "items/ingredient/herbs/banded_coral"
    BlazeCluster = "items/ingredient/herbs/blaze_cluster"
    Bloodcrown = "items/ingredient/herbs/bloodcrown"
    Bramblefrond = "items/ingredient/herbs/bramblefrond"
    DawnsGlory = "items/ingredient/herbs/dawns_glory"
    DragonsTeeth = "items/ingredient/herbs/dragons_teeth"
    DreamMaker = "items/ingredient/herbs/dream_maker"
    Fissureleaf = "items/ingredient/herbs/fissureleaf"
    FoolsDelight = "items/ingredient/herbs/fools_delight"
    ForgottenTears = "items/ingredient/herbs/forgotten_tears"
    Frostwort = "items/ingredient/herbs/frostwort"
    GoldenClover = "items/ingredient/herbs/golden_clover"
    Graspleaf = "items/ingredient/herbs/graspleaf"
    GraveMoss = "items/ingredient/herbs/grave_moss"
    Hushvine = "items/ingredient/herbs/hushvine"
    Lichbloom = "items/ingredient/herbs/lichbloom"
    Lithewood = "items/ingredient/herbs/lithewood"
    MagesBane = "items/ingredient/herbs/mages_bane"
    Manabloom = "items/ingredient/herbs/manabloom"
    Meddlespread = "items/ingredient/herbs/meddlespread"
    Razorgrass = "items/ingredient/herbs/razorgrass"
    Riverblossom = "items/ingredient/herbs/riverblossom"
    Rotstalk = "items/ingredient/herbs/rotstalk"
    Seaclover = "items/ingredient/herbs/seaclover"
    Shellflower = "items/ingredient/herbs/shellflower"
    Shellplate = "items/ingredient/herbs/shellplate"
    Shelterfoil = "items/ingredient/herbs/shelterfoil"
    Shiverroot = "items/ingredient/herbs/shiverroot"
    SingingCoral = "items/ingredient/herbs/singing_coral"
    SirensKiss = "items/ingredient/herbs/sirens_kiss"
    Snowdew = "items/ingredient/herbs/snowdew"
    SpeckledCap = "items/ingredient/herbs/speckled_cap"
    SpidersGrove = "items/ingredient/herbs/spiders_grove"
    Stranglekelp = "items/ingredient/herbs/stranglekelp"
    Sungrain = "items/ingredient/herbs/sungrain"
    Wanderweed = "items/ingredient/herbs/wanderweed"
    Witherheart = "items/ingredient/herbs/witherheart"
    Wrathbark = "items/ingredient/herbs/wrathbark"

    # Weapons
    BasicDagger = "items/weapon/dagger/basic_dagger"
    BasicSword = "items/weapon/dagger/basic_sword"

    # Cooked Food
    CookedRoughy = "items/consumable/food/cooked_roughy"

    # Seeds
    AsptongueSeed = "items/gardening/seed/asptongue_seed"
    BlazeClusterSpores = "items/gardening/seed/blaze_cluster_spores"
    BloodcrownSpores = "items/gardening/seed/bloodcrown_spores"
    BramblefrondSeed = "items/gardening/seed/bramblefrond_seed"
    DawnsGlorySeed = "items/gardening/seed/dawns_glory_seed"
    DragonsTeethSeed = "items/gardening/seed/dragons_teeth_seed"
    DreamMakerSeed = "items/gardening/seed/dream_maker_seed"
    FissureleafSeed = "items/gardening/seed/fissureleaf_seed"
    FoolsDelightSpores = "items/gardening/seed/fools_delight_spores"
    ForgottenTearsSeed = "items/gardening/seed/forgotten_tears_seed"
    FrostwortSeed = "items/gardening/seed/frostwort_seed"
    GoldenCloverSeed = "items/gardening/seed/golden_clover_seed"
    GraspleafSeed = "items/gardening/seed/graspleaf_seed"
    GraveMossSpores = "items/gardening/seed/grave_moss_spores"
    HushvineSeed = "items/gardening/seed/hushvine_seed"
    LichbloomSeed = "items/gardening/seed/lichbloom_seed"
    MagesBaneSeed = "items/gardening/seed/mages_bane_seed"
    ManabloomSeed = "items/gardening/seed/manabloom_seed"
    MeddlespreadSpores = "items/gardening/seed/meddlespread_spores"
    RazorgrassSeed = "items/gardening/seed/razorgrass_seed"
    RiverblossomSeed = "items/gardening/seed/riverblossom_seed"
    RotstalkSeed = "items/gardening/seed/rotstalk_seed"
    SeacloverSeed = "items/gardening/seed/seaclover_seed"
    ShellflowerSeed = "items/gardening/seed/shellflower_seed"
    ShelterfoilSeed = "items/gardening/seed/shelterfoil_seed"
    SirensKissSeed = "items/gardening/seed/sirens_kiss_seed"
    SnowdewSeed = "items/gardening/seed/snowdew_seed"
    SpeckledCapSpores = "items/gardening/seed/speckled_cap_spores"
    SpidersGroveSpores = "items/gardening/seed/spiders_grove_spores"
    SungrainSeed = "items/gardening/seed/sungrain_seed"
    WanderweedSeed = "items/gardening/seed/wanderweed_seed"
    WitherheartSeed = "items/gardening/seed/witherheart_seed"

    # Misc
    CursedStone = "items/equipment/offhand/cursed_stone"
    GoldenKnucklebone = "items/equipment/offhand/golden_knucklebone"
    PurifiedHeart = "items/equipment/offhand/purified_heart"

# -----------------------------------------------------------------------------
# CLASSES
# -----------------------------------------------------------------------------

class ItemEffects():
    def __init__(self, permanent: List[Effect]=[], on_turn_start: List[Effect]=[], on_turn_end: List[Effect]=[], on_damaged: List[Effect]=[], on_successful_ability_used: List[Effect]=[], on_successful_attack: List[Effect]=[], on_attacked: List[Effect]=[], on_ability_used_against: List[Effect]=[]):
        # Permanent is a special case since it doesn't ever trigger like the others and therefore encapsulates
        # the concept of inherent item mods which are going to be referenced in a bunch of places.
        self.permanent: List[Effect] = permanent
        
        self.on_turn_start: List[Effect] = on_turn_start
        self.on_turn_end: List[Effect] = on_turn_end
        self.on_damaged: List[Effect] = on_damaged # After taking damage from any source (post reduction and armor)
        self.on_successful_ability_used: List[Effect] = on_successful_ability_used
        self.on_successful_attack: List[Effect] = on_successful_attack
        self.on_attacked: List[Effect] = on_attacked # On being attacked (not dodged)
        self.on_ability_used_against: List[Effect] = on_ability_used_against

    def get_permanent_attribute_mods(self) -> Attributes:
        attr_mods = Attributes(0, 0, 0, 0, 0, 0)
        for effect in self.permanent:
            if effect.effect_type == EffectType.ConMod:
                attr_mods.constitution += int(effect.effect_value)
            if effect.effect_type == EffectType.StrMod:
                attr_mods.strength += int(effect.effect_value)
            if effect.effect_type == EffectType.DexMod:
                attr_mods.dexterity += int(effect.effect_value)
            if effect.effect_type == EffectType.IntMod:
                attr_mods.intelligence += int(effect.effect_value)
            if effect.effect_type == EffectType.LckMod:
                attr_mods.luck += int(effect.effect_value)
            if effect.effect_type == EffectType.MemMod:
                attr_mods.memory += int(effect.effect_value)
        return attr_mods

    def has_item_effect(self, effect_type: EffectType):
        all_effects: List[List[Effect]] = [
            self.permanent,
            self.on_turn_start,
            self.on_turn_end,
            self.on_damaged,
            self.on_successful_ability_used,
            self.on_successful_attack,
            self.on_attacked,
            self.on_ability_used_against
        ]
        return any(any(effect.effect_type == effect_type for effect in effect_group) for effect_group in all_effects)        

    def sort_by_priority(self, effects: List[Effect]):
        return sorted(effects, key=lambda effect: EFFECT_PRIORITY[effect.effect_type])

    def __add__(self, other: ItemEffects):
        return ItemEffects(
            self.sort_by_priority(self.permanent + other.permanent),
            self.sort_by_priority(self.on_turn_start + other.on_turn_start),
            self.sort_by_priority(self.on_turn_end + other.on_turn_end),
            self.sort_by_priority(self.on_damaged + other.on_damaged),
            self.sort_by_priority(self.on_successful_ability_used + other.on_successful_ability_used),
            self.sort_by_priority(self.on_successful_attack + other.on_successful_attack),
            self.sort_by_priority(self.on_attacked + other.on_attacked),
            self.sort_by_priority(self.on_ability_used_against + other.on_ability_used_against)
        )

    def __str__(self):
        display_string = ""

        permanent_effect_str = "\n".join([str(effect) for effect in self.permanent])
        display_string += permanent_effect_str

        on_turn_start_str = "\n".join([str(effect) for effect in self.on_turn_start])
        if on_turn_start_str != "":
            display_string += "\n\nAt the start of your turn:\n\n" + on_turn_start_str
        
        on_turn_end_str = "\n".join([str(effect) for effect in self.on_turn_end])
        if on_turn_end_str != "":
            display_string += "\n\nAt the end of your turn:\n\n" + on_turn_end_str
        
        on_successful_ability_used_str = "\n".join([str(effect) for effect in self.on_successful_ability_used])
        if on_successful_ability_used_str != "":
            display_string += "\n\nWhen you successfully use an ability:\n\n" + on_successful_ability_used_str
        
        on_successful_attack_str = "\n".join([str(effect) for effect in self.on_successful_attack])
        if on_successful_attack_str != "":
            display_string += "\n\nWhen you successfully attack:\n\n" + on_successful_attack_str
        
        on_attacked_str = "\n".join([str(effect) for effect in self.on_attacked])
        if on_attacked_str != "":
            display_string += "\n\nWhen you're attacked:\n\n" + on_attacked_str

        on_ability_used_against_str = "\n".join([str(effect) for effect in self.on_ability_used_against])
        if on_ability_used_against_str != "":
            display_string += "\n\nWhen an ability is used on you:\n\n" + on_ability_used_against_str

        return display_string

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.permanent = state.get("permanent", [])
        self.on_turn_start = state.get("on_turn_start", [])
        self.on_turn_end = state.get("on_turn_end", [])
        self.on_damaged = state.get("on_damaged", [])
        self.on_successful_ability_used = state.get("on_successful_ability_used", [])
        self.on_successful_attack = state.get("on_successful_attack", [])
        self.on_attacked = state.get("on_attacked", [])
        self.on_ability_used_against = state.get("on_ability_used_against", [])


class ArmorStats():
    def __init__(self, armor_amount=0):
        self._armor_amount = armor_amount

    def get_armor_amount(self):
        return self._armor_amount

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._armor_amount = state.get("armor_amount", 0)


class WeaponStats():
    def __init__(self, min_damage=0, max_damage=0):
        self._min_damage = min_damage
        self._max_damage = max_damage
    
    def get_range_str(self):
        return f"{self._min_damage}-{self._max_damage} base damage"

    def get_random_damage(self, attacker_attrs: Attributes, item_effects: ItemEffects | None):
        damage = randint(self._min_damage, self._max_damage)
        # TODO: How should these stack? Should this logic be here now? Should I just allow items to specify how much they scale
        # from Dex since that's possible now?
        if item_effects is not None and any(effect.effect_type == EffectType.DmgBuffFromDex for effect in item_effects.permanent):
            damage += min(int(damage * DEX_DMG_SCALE * max(attacker_attrs.dexterity, 0)), damage)
        return randint(self._min_damage, self._max_damage)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._min_damage = state.get("min_damage", 0)
        self._max_damage = state.get("max_damage", 0)


class ConsumableStats():
    def __init__(self, num_targets: int=0, target_own_group: bool=True):
        self._num_targets = num_targets
        self._target_own_group = target_own_group

    def get_num_targets(self):
        return self._num_targets

    def get_target_own_group(self):
        return self._target_own_group

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._num_targets = state.get("num_targets", 0)
        self._target_own_group = state.get("target_own_group", True)


class Item():
    def __init__(self, key: ItemKey, icon: str, name: str, value: int, rarity: Rarity, description: str, flavor_text:str, class_tags: List[ClassTag], state_tags: List[StateTag]=[], count=1, level_requirement=0, item_effects: ItemEffects | None=None, altering_item_keys: List[ItemKey]=[], armor_stats: ArmorStats | None=None, weapon_stats: WeaponStats | None=None, consumable_stats: ConsumableStats | None=None):
        self._key: ItemKey = key
        self._icon = icon
        self._name = name
        self._value = value
        self._rarity = rarity
        self._description = description
        self._flavor_text = flavor_text
        self._class_tags = class_tags
        self._state_tags = state_tags
        self._count = count
        self._level_requirement = level_requirement
        self._item_effects = item_effects
        self._altering_item_keys = altering_item_keys

        self._armor_stats = armor_stats
        self._weapon_stats = weapon_stats
        self._consumable_stats = consumable_stats

    @staticmethod
    def load_from_state(item_data: dict):
        armor_data = item_data.get("armor_stats")
        armor_stats = None
        if armor_data is not None:
            armor_stats = ArmorStats()
            armor_stats.__setstate__(armor_data)
        
        weapon_data = item_data.get("weapon_stats")
        weapon_stats = None
        if weapon_data is not None:
            weapon_stats = WeaponStats()
            weapon_stats.__setstate__(weapon_data)

        consumable_data = item_data.get("consumable_stats")
        consumable_stats = None
        if consumable_data is not None:
            consumable_stats = ConsumableStats()
            consumable_stats.__setstate__(consumable_data)

        item_effects_data = item_data.get("effects")
        item_effects = None
        if item_effects_data is not None:
            item_effects = ItemEffects()
            item_effects.__setstate__(item_effects_data)
        
        return Item(
            item_data.get("key", ""),
            item_data.get("icon", ""),
            item_data.get("name", ""),
            item_data.get("value", 0),
            item_data.get("rarity", Rarity.Unknown),
            item_data.get("description", ""),
            item_data.get("flavor_text", ""),
            item_data.get("class_tags", []),
            item_data.get("state_tags", []),
            item_data.get("count", 1),
            item_data.get("level_requirement", 0),
            item_effects,
            item_data.get("altering_item_keys", []),
            armor_stats,
            weapon_stats,
            consumable_stats
        )

    def remove_amount(self, amount: int):
        if amount <= self._count:
            result = Item(
                self._key,
                self._icon,
                self._name,
                self._value,
                self._rarity,
                self._description,
                self._flavor_text,
                self._class_tags,
                self._state_tags,
                amount,
                self._level_requirement,
                self._item_effects,
                self._altering_item_keys,
                self._armor_stats,
                self._weapon_stats,
                self._consumable_stats)
            self._count -= amount
            return result
        return None

    def add_amount(self, amount: int):
        self._count += amount

    def get_name(self) -> str:
        return self._name

    def get_full_name(self) -> str:
        return f"{self._icon} {self._name}"

    def get_name_and_count(self) -> str:
        if self._count > 1:
            return f"{self._name} ({self._count})"
        return f"{self._name}"

    def get_full_name_and_count(self) -> str:
        if self._count > 1:
            return f"{self._icon} {self._name} ({self._count})"
        return f"{self._icon} {self._name}"

    def get_value(self) -> int:
        return self._value

    def get_value_str(self) -> str:
        if self._value == 1:
            return "1 coin"
        return f"{self._value} coins"

    def get_count(self) -> int:
        return self._count

    def get_icon(self) -> str:
        return self._icon

    def get_rarity(self) -> Rarity:
        return self._rarity

    def get_description(self) -> str:
        return self._description
    
    def get_flavor_text(self) -> str:
        return self._flavor_text

    def get_class_tags(self) -> List[ClassTag]:
        return self._class_tags

    def get_state_tags(self) -> List[StateTag]:
        return self._state_tags

    def set_state_tags(self, new_tags: List[StateTag]) -> None:
        self._state_tags += new_tags

    def get_key(self) -> ItemKey:
        return self._key

    def get_level_requirement(self) -> int:
        return self._level_requirement

    def get_item_effects(self) -> (ItemEffects | None):
        if self._item_effects is None:
            return None

        # Start with this item's base effects
        combined_effects = self._item_effects

        # Add in everything from items that are altering it
        for item_key in self._altering_item_keys:
            item_effects_data = LOADED_ITEMS.get_item_state(item_key).get("effects")
            item_effects = None
            if item_effects_data is not None:
                item_effects = ItemEffects()
                item_effects.__setstate__(item_effects_data)
            
            if item_effects is not None:
                combined_effects += item_effects

        return combined_effects

    def get_altering_item_keys(self) -> List[ItemKey]:
        return self._altering_item_keys

    def get_armor_stats(self) -> (ArmorStats | None):
        return self._armor_stats

    def get_weapon_stats(self) -> (WeaponStats | None):
        return self._weapon_stats

    def get_consumable_stats(self) -> (ConsumableStats | None):
        return self._consumable_stats

    def __str__(self):
        display_string = f"**{self.get_full_name()}**\n*{self._rarity} Item*" + (" (Unique)" if ClassTag.Misc.IsUnique in self._class_tags else "") + "\n\n"
        
        has_any_stats: bool = False

        if self._armor_stats is not None:
            has_any_stats = True
            display_string += f"{self._armor_stats.get_armor_amount()} Armor\n"

        if self._weapon_stats is not None:
            has_any_stats = True
            display_string += f"{self._weapon_stats.get_range_str()}\n"

        if self._consumable_stats is not None:
            has_any_stats = True
            target_str: str = ""
            if self._consumable_stats._num_targets == -1:
                target_str = "Targets All\n"
            if self._consumable_stats._num_targets == 0:
                target_str = "Targets Self\n"
            if self._consumable_stats._num_targets == 1:
                target_str = "1 Target\n"
            if self._consumable_stats._num_targets > 1:
                target_str = f"1-{self._consumable_stats._num_targets} Targets\n"
            display_string += target_str

        if self._item_effects is not None:
            has_any_stats = True
            display_string += f"{self._item_effects}"

        if has_any_stats:
            display_string += "\n"

        if ClassTag.Misc.NeedsIdentification in self._class_tags:
            display_string += "*Needs Identification*\n\n"

        if self._description != "":
            display_string += f"{self._description}\n\n"
        if self._flavor_text != "":
            display_string += f"*{self._flavor_text}*\n\n"

        if self._count > 1:
            display_string += f"Quantity: *{self._count}*\n"
        
        display_string += f"Value: *{self._value}* each\n"
        display_string += f"Level Requirement: {self._level_requirement}"
        
        return display_string

    def __eq__(self, obj) -> bool:
        if not isinstance(obj, Item):
            return False
        
        if (ClassTag.Misc.IsUnique in self.get_state_tags() or
            ClassTag.Misc.IsUnique in obj.get_state_tags()):
            return False

        return (self._key == obj.get_key() and 
                self._state_tags == obj.get_state_tags() and
                self._altering_item_keys == obj.get_altering_item_keys())

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        # TODO: This handles the case where I've deleted an item JSON or the key
        # doesn't exist, but it should ideally somehow make this None instead of an Item,
        # though an Item with everything default will work too because it should
        # be cleaned up by the inventory automatically. I'll need to figure that out
        # at some point in the future.
        if state.get("_key", "") not in LOADED_ITEMS.get_all_keys():
            return
        
        base_data = LOADED_ITEMS.get_item_state(state["_key"])

        # Always replace these values; the base data overrides them.
        self._key = base_data.get("key", "")
        self._icon = base_data.get("icon", "")
        self._name = base_data.get("name", "")
        self._value = base_data.get("value", 0)
        self._rarity = base_data.get("rarity", Rarity.Unknown)
        self._description = base_data.get("description", "")
        self._flavor_text = base_data.get("flavor_text", "")
        self._level_requirement = base_data.get("level_requirement", 0)
        self._class_tags = base_data.get("class_tags", [])

        armor_data = base_data.get("armor_stats")
        if armor_data is not None:
            self._armor_stats = ArmorStats()
            self._armor_stats.__setstate__(armor_data)
        else:
            self._armor_stats = None
        
        weapon_data = base_data.get("weapon_stats")
        if weapon_data is not None:
            self._weapon_stats = WeaponStats()
            self._weapon_stats.__setstate__(weapon_data)
        else:
            self._weapon_stats = None

        consumable_data = base_data.get("consumable_stats")
        if consumable_data is not None:
            self._consumable_stats = ConsumableStats()
            self._consumable_stats.__setstate__(consumable_data)
        else:
            self._consumable_stats = None

        item_effects_data = base_data.get("item_effects")
        if item_effects_data is not None:
            self._item_effects = ItemEffects()
            self._item_effects.__setstate__(item_effects_data)
        else:
            self._item_effects = None

        # These are stateful values and we use what's loaded from the database.
        self._state_tags = state.get("_state_tags", [])
        self._count = state.get("_count", 1)
        self._altering_item_keys = state.get("_altering_item_keys", [])

# I'm doing it this way because having a dict[ItemKey, Item] would
# mean that using the items in the dict would all point to the same
# reference of the object. That seems extremely risky, even if I copy
# the object every time I use the dict.

# The reason I don't want to use Item.load_from_key every
# time I need a new object is because I/O operations are expensive and
# with multiple potentially happening every second, that could yield
# a lot of errors due to the file being locked.
class LoadedItems():
    _states: MappingProxyType[ItemKey, dict] = MappingProxyType({
        item_key.value: json.load(open(f"./features/{item_key.value}.json", "r")) for item_key in ItemKey
    })

    def get_all_keys(self):
        return self._states.keys()

    def get_item_state(self, key: ItemKey):
        return self._states[key]

    def get_new_item(self, key: ItemKey):
        return Item.load_from_state(self._states[key])

# -----------------------------------------------------------------------------
# GLOBALS
# -----------------------------------------------------------------------------

LOADED_ITEMS = LoadedItems()
