from __future__ import annotations

import json
import random

from enum import StrEnum
from features.expertise import ExpertiseClass
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, ItemKey
from types import MappingProxyType

from typing import TYPE_CHECKING, Dict, List
if TYPE_CHECKING:
    from features.inventory import Inventory

# -----------------------------------------------------------------------------
# ENUMS
# -----------------------------------------------------------------------------

class RecipeKey(StrEnum):
    # Food
    AppleCider = "recipes/consumable/food/apple_cider"
    AzureberryJuice = "recipes/consumable/food/azureberry_juice"
    BoarSteak = "recipes/consumable/food/boar_steak"
    Bread = "recipes/consumable/food/bread"
    CookedAlgaefish = "recipes/consumable/food/cooked_algaefish"
    CookedBeefish = "recipes/consumable/food/cooked_beefish"
    CookedBlackscale = "recipes/consumable/food/cooked_blackscale"
    CookedBrownTench = "recipes/consumable/food/cooked_brown_tench"
    CookedGoldenTench = "recipes/consumable/food/cooked_golden_tench"
    CookedJumpfish = "recipes/consumable/food/cooked_jumpfish"
    CookedMinnow = "recipes/consumable/food/cooked_minnow"
    CookedPondEel = "recipes/consumable/food/cooked_pond_eel"
    CookedPondGuppy = "recipes/consumable/food/cooked_pond_guppy"
    CookedRockfish = "recipes/consumable/food/cooked_rockfish"
    CookedRoughy = "recipes/consumable/food/cooked_roughy"
    CookedRubyDartfish = "recipes/consumable/food/cooked_ruby_dartfish"
    CookedSandLurker = "recipes/consumable/food/cooked_sand_lurker"
    CookedTitanfish = "recipes/consumable/food/cooked_titanfish"
    CookedWyvernfish = "recipes/consumable/food/cooked_wyvernfish"
    Dumpling = "recipes/consumable/food/dumpling"
    ElsberryJuice = "recipes/consumable/food/elsberry_juice"
    FishCakeWithMinnow = "recipes/consumable/food/fish_cake_with_minnow"
    FishCakeWithRoughy = "recipes/consumable/food/fish_cake_with_roughy"
    FlamingCurry = "recipes/consumable/food/flaming_curry"
    ForestFishFeast = "recipes/consumable/food/forest_fish_feast"
    FriedShrimp = "recipes/consumable/food/fried_shrimp"
    GoldenHoneydrop = "recipes/consumable/food/golden_honeydrop"
    GoldenSalad = "recipes/consumable/food/golden_salad"
    MildAle = "recipes/consumable/food/mild_ale"
    MinnowSushi = "recipes/consumable/food/minnow_sushi"
    MixedVeggies = "recipes/consumable/food/mixed_veggies"
    MushroomSalad = "recipes/consumable/food/mushroom_salad"
    MushroomStew = "recipes/consumable/food/mushroom_stew"
    RazorgrassBall = "recipes/consumable/food/razorgrass_ball"
    RoastedPotato = "recipes/consumable/food/roasted_potato"
    RoughySushi = "recipes/consumable/food/roughy_sushi"
    SeafoodMedley = "recipes/consumable/food/seafood_medley"
    SpicedBoarSteak = "recipes/consumable/food/spiced_boar_steak"
    SpicedWolfSteak = "recipes/consumable/food/spiced_wolf_steak"
    SpicyMushroomFlatbread = "recipes/consumable/food/spicy_mushroom_flatbread"
    StewedFruit = "recipes/consumable/food/stewed_fruit"
    SundewDelight = "recipes/consumable/food/sundew_delight"
    SweetElsberryWine = "recipes/consumable/food/sweet_elsberry_wine"
    VegetableFritter = "recipes/consumable/food/vegetable_fritter"
    VegetableStew = "recipes/consumable/food/vegetable_stew"
    WolfSteak = "recipes/consumable/food/wolf_steak"

    # Potions
    Anpanacea = "recipes/consumable/potions/anpanacea"
    AtrophyPotion = "recipes/consumable/potions/atrophy_potion"
    CharmPotionWithMesmerfishEye = "recipes/consumable/potions/charm_potion_with_mesmerfish_eye"
    CharmPotion = "recipes/consumable/potions/charm_potion"
    CleansingPotion = "recipes/consumable/potions/cleansing_potion"
    ConstitutionPotionWithBrittleCore = "recipes/consumable/potions/constitution_potion_with_brittle_core"
    ConstitutionPotion = "recipes/consumable/potions/constitution_potion"
    CoralskinPotion = "recipes/consumable/potions/coralskin_potion"
    CriticalPotion = "recipes/consumable/potions/critical_potion"
    DexterityPotion = "recipes/consumable/potions/dexterity_potion"
    DiminishingPotion = "recipes/consumable/potions/diminishing_potion"
    EnfeeblingPotion = "recipes/consumable/potions/enfeebling_potion"
    ExplosivePotionWithBrittleSpines = "recipes/consumable/potions/explosive_potion_with_brittle_spines"
    ExplosivePotion = "recipes/consumable/potions/explosive_potion"
    FearPotion = "recipes/consumable/potions/fear_potion"
    FortitudePotionWithScorpionStinger = "recipes/consumable/potions/fortitude_potion_with_scorpion_stinger"
    FortitudePotion = "recipes/consumable/potions/fortitude_potion"
    GreaterAtrophyPotion = "recipes/consumable/potions/greater_atrophy_potion"
    GreaterCharmPotionWithMesmerfishEye = "recipes/consumable/potions/greater_charm_potion_with_mesmerfish_eye"
    GreaterCharmPotion = "recipes/consumable/potions/greater_charm_potion"
    GreaterConstitutionPotionWithBrittleCore = "recipes/consumable/potions/greater_constitution_potion_with_brittle_core"
    GreaterConstitutionPotion = "recipes/consumable/potions/greater_constitution_potion"
    GreaterCriticalPotion = "recipes/consumable/potions/greater_critical_potion"
    GreaterDexterityPotion = "recipes/consumable/potions/greater_dexterity_potion"
    GreaterEnfeeblingPotionWithChanterspell = "recipes/consumable/potions/greater_enfeebling_potion_with_chanterspell"
    GreaterEnfeeblingPotion = "recipes/consumable/potions/greater_enfeebling_potion"
    GreaterExplosivePotionWithCharredUndeadWood = "recipes/consumable/potions/greater_explosive_potion_with_charred_undead_wood"
    GreaterExplosivePotion = "recipes/consumable/potions/greater_explosive_potion"
    GreaterFearPotion = "recipes/consumable/potions/greater_fear_potion"
    GreaterHealthPotionWithBloodcoral = "recipes/consumable/potions/greater_health_potion_with_bloodcoral"
    GreaterHealthPotion = "recipes/consumable/potions/greater_health_potion"
    GreaterIntelligencePotionWithUnblinkingEye = "recipes/consumable/potions/greater_intelligence_potion_with_unblinking_eye"
    GreaterIntelligencePotion = "recipes/consumable/potions/greater_intelligence_potion"
    GreaterManaPotionWithSeaDragonLeaves = "recipes/consumable/potions/greater_mana_potion_with_sea_dragon_leaves"
    GreaterManaPotion = "recipes/consumable/potions/greater_mana_potion"
    GreaterPoisonWithLionfishSpines = "recipes/consumable/potions/greater_poison_with_lionfish_spines"
    GreaterPoison = "recipes/consumable/potions/greater_poison"
    GreaterPotionOfDeathResistWithVoidseenBone = "recipes/consumable/potions/greater_potion_of_death_resist_with_voidseen_bone"
    GreaterPotionOfDeathResist = "recipes/consumable/potions/greater_potion_of_death_resist"
    GreaterPotionOfDecay = "recipes/consumable/potions/greater_potion_of_decay"
    GreaterSleepingDraught = "recipes/consumable/potions/greater_sleeping_draught"
    GreaterSmokebomb = "recipes/consumable/potions/greater_smokebomb"
    GreaterStrengthPotion = "recipes/consumable/potions/greater_strength_potion"
    HealthPotion = "recipes/consumable/potions/health_potion"
    IntelligencePotion = "recipes/consumable/potions/intelligence_potion"
    LesserAtrophyPotion = "recipes/consumable/potions/lesser_atrophy_potion"
    LesserCharmPotionWithMesmerfishEye = "recipes/consumable/potions/lesser_charm_potion_with_mesmerfish_eye"
    LesserCharmPotion = "recipes/consumable/potions/lesser_charm_potion"
    LesserConstitutionPotion = "recipes/consumable/potions/lesser_constitution_potion"
    LesserCriticalPotion = "recipes/consumable/potions/lesser_critical_potion"
    LesserDexterityPotion = "recipes/consumable/potions/lesser_dexterity_potion"
    LesserEnfeeblingPotion = "recipes/consumable/potions/lesser_enfeebling_potion"
    LesserExplosivePotionWithBrittleSpines = "recipes/consumable/potions/lesser_explosive_potion_with_brittle_spines"
    LesserExplosivePotion = "recipes/consumable/potions/lesser_explosive_potion"
    LesserFearPotion = "recipes/consumable/potions/lesser_fear_potion"
    LesserHealthPotion = "recipes/consumable/potions/lesser_health_potion"
    LesserIntelligencePotion = "recipes/consumable/potions/lesser_intelligence_potion"
    LesserManaPotion = "recipes/consumable/potions/lesser_mana_potion"
    LesserPoisonWithPufferfish = "recipes/consumable/potions/lesser_poison_with_pufferfish"
    LesserPoison = "recipes/consumable/potions/lesser_poison"
    LesserPotionOfDeathResist = "recipes/consumable/potions/lesser_potion_of_death_resist"
    LesserPotionOfDecay = "recipes/consumable/potions/lesser_potion_of_decay"
    LesserSleepingDraught = "recipes/consumable/potions/lesser_sleeping_draught"
    LesserSmokebomb = "recipes/consumable/potions/lesser_smokebomb"
    LesserStrengthPotion = "recipes/consumable/potions/lesser_strength_potion"
    LuckPotion = "recipes/consumable/potions/luck_potion"
    ManaPotion = "recipes/consumable/potions/mana_potion"
    Poison = "recipes/consumable/potions/poison"
    PotionOfDeathResistWithVoidseenBone = "recipes/consumable/potions/potion_of_death_resist_with_voidseen_bone"
    PotionOfDeathResist = "recipes/consumable/potions/potion_of_death_resist"
    PotionOfDebilitation = "recipes/consumable/potions/potion_of_debilitation"
    PotionOfDecay = "recipes/consumable/potions/potion_of_decay"
    PotionOfEternalLife = "recipes/consumable/potions/potion_of_eternal_life"
    PotionOfFrailty = "recipes/consumable/potions/potion_of_frailty"
    PotionOfVulnerability = "recipes/consumable/potions/potion_of_vulnerability"
    SappingPotion = "recipes/consumable/potions/sapping_potion"
    SleepingDraughtWithSlumbershroom = "recipes/consumable/potions/sleeping_draught_with_slumbershroom"
    SleepingDraught = "recipes/consumable/potions/sleeping_draught"
    Smokebomb = "recipes/consumable/potions/smokebomb"
    StrengthPotion = "recipes/consumable/potions/strength_potion"
    SuperiorAtrophyPotionWithTreantCuttings = "recipes/consumable/potions/superior_atrophy_potion_with_treant_cuttings"
    SuperiorAtrophyPotion = "recipes/consumable/potions/superior_atrophy_potion"
    SuperiorConstitutionPotionWithBrittleCore = "recipes/consumable/potions/superior_constitution_potion_with_brittle_core"
    SuperiorConstitutionPotion = "recipes/consumable/potions/superior_constitution_potion"
    SuperiorCriticalPotion = "recipes/consumable/potions/superior_critical_potion"
    SuperiorDexterityPotionWithAnomalousMaterial = "recipes/consumable/potions/superior_dexterity_potion_with_anomalous_material"
    SuperiorDexterityPotion = "recipes/consumable/potions/superior_dexterity_potion"
    SuperiorExplosivePotionWithCharredUndeadWood = "recipes/consumable/potions/superior_explosive_potion_with_charred_undead_wood"
    SuperiorExplosivePotion = "recipes/consumable/potions/superior_explosive_potion"
    SuperiorHealthPotionWithBloodcoral = "recipes/consumable/potions/superior_health_potion_with_bloodcoral"
    SuperiorHealthPotion = "recipes/consumable/potions/superior_health_potion"
    SuperiorIntelligencePotionWithUnblinkingEye = "recipes/consumable/potions/superior_intelligence_potion_with_unblinking_eye"
    SuperiorIntelligencePotion = "recipes/consumable/potions/superior_intelligence_potion"
    SuperiorManaPotionWithManaSaturatedRoot = "recipes/consumable/potions/superior_mana_potion_with_mana_saturated_root"
    SuperiorManaPotion = "recipes/consumable/potions/superior_mana_potion"
    SuperiorPoisonWithLionfishSpines = "recipes/consumable/potions/superior_poison_with_lionfish_spines"
    SuperiorPoisonWithPaleVenom = "recipes/consumable/potions/superior_poison_with_pale_venom"
    SuperiorPoison = "recipes/consumable/potions/superior_poison"
    SuperiorPotionOfDecayWithMalevolentMorel = "recipes/consumable/potions/superior_potion_of_decay_with_malevolent_morel"
    SuperiorPotionOfDecay = "recipes/consumable/potions/superior_potion_of_decay"
    SuperiorSleepingDraughtWithGlowingMoss = "recipes/consumable/potions/superior_sleeping_draught_with_glowing_moss"
    SuperiorSleepingDraught = "recipes/consumable/potions/superior_sleeping_draught"
    SuperiorSmokebomb = "recipes/consumable/potions/superior_smokebomb"
    SuperiorStrengthPotion = "recipes/consumable/potions/superior_strength_potion"

    # Alchemy Supplies
    CrystalVialWithFlawlessQuartz = "recipes/ingredient/alchemy_supplies/crystal_vial_with_flawless_quartz"
    CrystalVialWithQuartz = "recipes/ingredient/alchemy_supplies/crystal_vial_with_quartz"

    # Equipment
    
    # Amulet
    CopperNecklace = "recipes/equipment/amulet/copper_necklace"
    GoldNecklace = "recipes/equipment/amulet/gold_necklace"
    SilverNecklace = "recipes/equipment/amulet/silver_necklace"

    # Boots
    AmberiteGreaves = "recipes/equipment/boots/amberite_greaves"
    AmberitePlateGreaves = "recipes/equipment/boots/amberite_plate_greaves"
    IronGreaves = "recipes/equipment/boots/iron_greaves"
    IronPlateGreaves = "recipes/equipment/boots/iron_plate_greaves"
    LeatherBoots = "recipes/equipment/boots/leather_boots"
    MothsilkBoots = "recipes/equipment/boots/mothsilk_boots"
    MythrilGreaves = "recipes/equipment/boots/mythril_greaves"
    MythrilPlateGreaves = "recipes/equipment/boots/mythril_plate_greaves"
    OrichalcumGreaves = "recipes/equipment/boots/orichalcum_greaves"
    OrichalcumPlateGreaves = "recipes/equipment/boots/orichalcum_plate_greaves"
    SilverGreaves = "recipes/equipment/boots/silver_greaves"
    SilverPlateGreaves = "recipes/equipment/boots/silver_plate_greaves"
    SpidersilkBoots = "recipes/equipment/boots/spidersilk_boots"

    # Chest Armor
    AmberiteCuirass = "recipes/equipment/chest_armor/amberite_cuirass"
    AmberitePlateCuirass = "recipes/equipment/chest_armor/amberite_plate_cuirass"
    IronCuirass = "recipes/equipment/chest_armor/iron_cuirass"
    IronPlateCuirass = "recipes/equipment/chest_armor/iron_plate_cuirass"
    LeatherJerkin = "recipes/equipment/chest_armor/leather_jerkin"
    MothsilkRobe = "recipes/equipment/chest_armor/mothsilk_robe"
    MythrilCuirass = "recipes/equipment/chest_armor/mythril_cuirass"
    MythrilPlateCuirass = "recipes/equipment/chest_armor/mythril_plate_cuirass"
    OrichalcumCuirass = "recipes/equipment/chest_armor/orichalcum_cuirass"
    OrichalcumPlateCuirass = "recipes/equipment/chest_armor/orichalcum_plate_cuirass"
    SilverCuirass = "recipes/equipment/chest_armor/silver_cuirass"
    SilverPlateCuirass = "recipes/equipment/chest_armor/silver_plate_cuirass"
    SpidersilkRobe = "recipes/equipment/chest_armor/spidersilk_robe"

    # Gloves
    AmberiteGauntlets = "recipes/equipment/gloves/amberite_gauntlets"
    AmberitePlateGauntlets = "recipes/equipment/gloves/amberite_plate_gauntlets"
    IronGauntlets = "recipes/equipment/gloves/iron_gauntlets"
    IronPlateGauntlets = "recipes/equipment/gloves/iron_plate_gauntlets"
    LeatherGloves = "recipes/equipment/gloves/leather_gloves"
    MothsilkGloves = "recipes/equipment/gloves/mothsilk_gloves"
    MythrilGauntlets = "recipes/equipment/gloves/mythril_gauntlets"
    MythrilPlateGauntlets = "recipes/equipment/gloves/mythril_plate_gauntlets"
    OrichalcumGauntlets = "recipes/equipment/gloves/orichalcum_gauntlets"
    OrichalcumPlateGauntlets = "recipes/equipment/gloves/orichalcum_plate_gauntlets"
    SilverGauntlets = "recipes/equipment/gloves/silver_gauntlets"
    SilverPlateGauntlets = "recipes/equipment/gloves/silver_plate_gauntlets"
    SpidersilkGloves = "recipes/equipment/gloves/spidersilk_gloves"

    # Helmet
    AmberiteHelmet = "recipes/equipment/helmet/amberite_helmet"
    AmberitePlateHelmet = "recipes/equipment/helmet/amberite_plate_helmet"
    IronHelmet = "recipes/equipment/helmet/iron_helmet"
    IronPlateHelmet = "recipes/equipment/helmet/iron_plate_helmet"
    LeatherHelmet = "recipes/equipment/helmet/leather_helmet"
    MothsilkCowl = "recipes/equipment/helmet/mothsilk_cowl"
    MythrilHelmet = "recipes/equipment/helmet/mythril_helmet"
    MythrilPlateHelmet = "recipes/equipment/helmet/mythril_plate_helmet"
    OrichalcumHelmet = "recipes/equipment/helmet/orichalcum_helmet"
    OrichalcumPlateHelmet = "recipes/equipment/helmet/orichalcum_plate_helmet"
    SilverHelmet = "recipes/equipment/helmet/silver_helmet"
    SilverPlateHelmet = "recipes/equipment/helmet/silver_plate_helmet"
    SpidersilkCowl = "recipes/equipment/helmet/spidersilk_cowl"

    # Leggings
    AmberiteLeggings = "recipes/equipment/leggings/amberite_leggings"
    AmberitePlateLeggings = "recipes/equipment/leggings/amberite_plate_leggings"
    IronLeggings = "recipes/equipment/leggings/iron_leggings"
    IronPlateLeggings = "recipes/equipment/leggings/iron_plate_leggings"
    LeatherLeggings = "recipes/equipment/leggings/leather_leggings"
    MythrilLeggings = "recipes/equipment/leggings/mythril_leggings"
    MythrilPlateLeggings = "recipes/equipment/leggings/mythril_plate_leggings"
    OrichalcumLeggings = "recipes/equipment/leggings/orichalcum_leggings"
    OrichalcumPlateLeggings = "recipes/equipment/leggings/orichalcum_plate_leggings"
    SilverLeggings = "recipes/equipment/leggings/silver_leggings"
    SilverPlateLeggings = "recipes/equipment/leggings/silver_plate_leggings"

    # Offhand
    WoodenBuckler = "recipes/equipment/offhand/wooden_buckler"

    # Rings
    CopperRing = "recipes/equipment/ring/copper_ring"
    GoldRing = "recipes/equipment/ring/gold_ring"
    SilverRing = "recipes/equipment/ring/silver_ring"

    # Gardening
    Compost = "recipes/gardening/soil/compost"
    Ichordross = "recipes/gardening/soil/ichordross"

    # Materials
    AmberiteIngot = "recipes/ingredient/materials/amberite_ingot"
    CopperIngot = "recipes/ingredient/materials/copper_ingot"
    GoldIngot = "recipes/ingredient/materials/gold_ingot"
    IronIngot = "recipes/ingredient/materials/iron_ingot"
    Leather = "recipes/ingredient/materials/leather"
    LeatherScraps = "recipes/ingredient/materials/leather_scraps"
    MothsilkBolt = "recipes/ingredient/materials/mothsilk_bolt"
    MythrilIngot = "recipes/ingredient/materials/mythril_ingot"
    OrichalcumIngot = "recipes/ingredient/materials/orichalcum_ingot"
    SilverIngot = "recipes/ingredient/materials/silver_ingot"
    SpidersilkBolt = "recipes/ingredient/materials/spidersilk_bolt"
    ThickLeather = "recipes/ingredient/materials/thick_leather"
    VoidseenIngot = "recipes/ingredient/materials/voidseen_ingot"

    # Weapons

    # Daggers
    IronDagger = "recipes/weapon/dagger/iron_dagger"

    # Greatswords
    IronGreatsword = "recipes/weapon/greatsword/iron_greatsword"

    # Knuckles
    IronKnuckles = "recipes/weapon/knuckles/iron_knuckles"
    
    # Spears
    IronSpear = "recipes/weapon/spear/iron_spear"
    
    # Staves
    LithewoodStaff = "recipes/weapon/staff/lithewood_staff"
    WrathbarkStaff = "recipes/weapon/staff/wrathbark_staff"
    
    # Swords
    IronSword = "recipes/weapon/sword/iron_sword"

# -----------------------------------------------------------------------------
# RECIPE CLASS
# -----------------------------------------------------------------------------

class Recipe():
    def __init__(self, key: RecipeKey, icon: str, name: str, value: int, inputs: Dict[ItemKey, int], outputs: Dict[ItemKey, int], xp_reward_for_use: Dict[ExpertiseClass, int]):
        # Figuring out whether the recipe should be displayed can be evaluated
        # based on the class tags of the outputs. The only problem with this is
        # that it makes filtering slower.
        self.key: RecipeKey = key
        self.icon: str = icon
        self.name: str = name
        self.value: int = value
        self.inputs: Dict[ItemKey, int] = inputs
        self.outputs: Dict[ItemKey, int] = outputs
        self.xp_reward_for_use: Dict[ExpertiseClass, int] = xp_reward_for_use

    def any_output_has_any_class_tag(self, class_tags: List[ClassTag]):
        # Checks whether any of the outputs has any of the class tags in the
        # list of class tags passed in. This is used for filtering and the list
        # of class tags is kept by the view doing the filtering.
        for tag in class_tags:
            for output_key in self.outputs.keys():
                item_class_tags = LOADED_ITEMS.get_item_state(output_key).get("class_tags", [])
                if tag in item_class_tags:
                    return True
        return False

    @staticmethod
    def load_from_state(recipe_data: dict):
        return Recipe(
            recipe_data.get("key", ""),
            recipe_data.get("icon", ""),
            recipe_data.get("name", ""),
            recipe_data.get("value", 0),
            recipe_data.get("inputs", {}),
            recipe_data.get("outputs", {}),
            recipe_data.get("xp_reward_for_use", {})
        )

    def get_name_and_icon(self):
        return f"{self.icon} {self.name}"

    def num_can_be_made(self, inventory: Inventory):
        num = -1
        for input_key, quantity in self.inputs.items():
            item_index = inventory.search_by_key(input_key)
            if item_index == -1:
                num = 0
                break

            item = inventory.get_inventory_slots()[item_index]
            
            if quantity > 0 and item is not None:
                if num == -1:
                    num = int(item.get_count() / quantity)
                else:
                    num = min(int(item.get_count() / quantity), num)
            else:
                num = 0
                break
        return num

    def __eq__(self, obj) -> bool:
        if not isinstance(obj, Recipe):
            return False

        return (self.key == obj.key and self.inputs == obj.inputs and self.outputs == obj.outputs)

    def __str__(self):
        display_string = f"**{self.get_name_and_icon()}**\n\n"
        input_strs = []
        for item_key, quantity in self.inputs.items():
            item_data = LOADED_ITEMS.get_item_state(item_key)
            input_strs.append(f"{item_data['icon']} {item_data['name']} (x{quantity})\n")
        input_display = '\n'.join(input_strs)

        display_string += f"{input_display}\n==>\n\n"
        output_strs = []
        for item_key, quantity in self.outputs.items():
            item_data = LOADED_ITEMS.get_item_state(item_key)
            output_strs.append(f"{item_data['icon']} {item_data['name']} (x{quantity})\n")
        output_display = '\n'.join(output_strs)
        display_string += output_display

        return display_string

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        if state.get("key", "") not in LOADED_RECIPES.get_all_keys():
            return

        base_data = LOADED_RECIPES.get_recipe_state(state["key"])

        self.key = base_data.get("key", "")
        self.icon = base_data.get("icon", "")
        self.name = base_data.get("name", "")
        self.value = base_data.get("value", 0)
        self.inputs = base_data.get("inputs", {})
        self.outputs = base_data.get("outputs", {})
        self.xp_reward_for_use = base_data.get("xp_reward_for_use", {})

# -----------------------------------------------------------------------------
# LOADED RECIPES
# -----------------------------------------------------------------------------

class LoadedRecipes():
    _states: MappingProxyType[RecipeKey, dict] = MappingProxyType({
        recipe_key.value: json.load(open(f"./features/{recipe_key.value}.json", "r")) for recipe_key in RecipeKey
    })

    def get_random_recipe_using_item(self, item_key: ItemKey, required_output_class_tags: List[ClassTag], known_recipe_keys: List[RecipeKey] | None=None):
        recipe_keys: List[RecipeKey] = []
        for recipe_key, recipe_state in self._states.items():
            input_quantity_needed: int = recipe_state["inputs"].get(item_key, 0)

            output_contains_any_tag: bool = True
            if len(required_output_class_tags) > 0:
                output_contains_any_tag = any(tag in LOADED_ITEMS.get_new_item(output_key).get_class_tags() for output_key in recipe_state["outputs"].keys() for tag in required_output_class_tags)
        
            if input_quantity_needed > 0 and output_contains_any_tag and (known_recipe_keys is None or recipe_key not in known_recipe_keys):
                recipe_keys.append(recipe_key)

        if len(recipe_keys) == 0:
            return None

        return random.choice(recipe_keys)

    def get_all_keys(self):
        return self._states.keys()

    def get_recipe_state(self, key: RecipeKey):
        return self._states[key]

    def get_new_recipe(self, key: RecipeKey):
        return Recipe.load_from_state(self._states[key])

# -----------------------------------------------------------------------------
# GLOBALS
# -----------------------------------------------------------------------------

LOADED_RECIPES = LoadedRecipes()
