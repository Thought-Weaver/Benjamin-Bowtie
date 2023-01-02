from __future__ import annotations

import json

from strenum import StrEnum
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
    Bread = "recipes/consumable/food/bread"
    CookedMinnow = "recipes/consumable/food/cooked_minnow"
    CookedRoughy = "recipes/consumable/food/cooked_roughy"
    Dumpling = "recipes/consumable/food/dumpling"
    FishCakeWithMinnow = "recipes/consumable/food/fish_cake_with_minnow"
    FishCakeWithRoughy = "recipes/consumable/food/fish_cake_with_roughy"
    FriedShrimp = "recipes/consumable/food/fried_shrimp"
    MushroomSalad = "recipes/consumable/food/mushroom_salad"
    MushroomStew = "recipes/consumable/food/mushroom_stew"
    VegetableFritter = "recipes/consumable/food/vegetable_fritter"

    # Potions
    AtrophyPotion = "recipes/consumable/potions/atrophy_potion"
    CharmPotion = "recipes/consumable/potions/charm_potion"
    CleansingPotion = "recipes/consumable/potions/cleansing_potion"
    ConstitutionPotion = "recipes/consumable/potions/constitution_potion"
    DexterityPotion = "recipes/consumable/potions/dexterity_potion"
    ExplosivePotion = "recipes/consumable/potions/explosive_potion"
    FearPotion = "recipes/consumable/potions/fear_potion"
    FortitudePotion = "recipes/consumable/potions/fortitude_potion"
    GreaterAtrophyPotion = "recipes/consumable/potions/greater_atrophy_potion"
    GreaterCharmPotion = "recipes/consumable/potions/greater_charm_potion"
    GreaterConstitutionPotion = "recipes/consumable/potions/greater_constitution_potion"
    GreaterDexterityPotion = "recipes/consumable/potions/greater_dexterity_potion"
    GreaterExplosivePotion = "recipes/consumable/potions/greater_explosive_potion"
    GreaterFearPotion = "recipes/consumable/potions/greater_fear_potion"
    GreaterHealthPotion = "recipes/consumable/potions/greater_health_potion"
    GreaterIntelligencePotion = "recipes/consumable/potions/greater_intelligence_potion"
    GreaterManaPotion = "recipes/consumable/potions/greater_mana_potion"
    GreaterPoison = "recipes/consumable/potions/greater_poison"
    GreaterPotionOfDecay = "recipes/consumable/potions/greater_potion_of_decay"
    GreaterSleepingDraught = "recipes/consumable/potions/greater_sleeping_draught"
    GreaterSmokebomb = "recipes/consumable/potions/greater_smokebomb"
    GreaterStrengthPotion = "recipes/consumable/potions/greater_strength_potion"
    HealthPotion = "recipes/consumable/potions/health_potion"
    IntelligencePotion = "recipes/consumable/potions/intelligence_potion"
    LesserAtrophyPotion = "recipes/consumable/potions/lesser_atrophy_potion"
    LesserCharmPotion = "recipes/consumable/potions/lesser_charm_potion"
    LesserConstitutionPotion = "recipes/consumable/potions/lesser_constitution_potion"
    LesserDexterityPotion = "recipes/consumable/potions/lesser_dexterity_potion"
    LesserExplosivePotion = "recipes/consumable/potions/lesser_explosive_potion"
    LesserFearPotion = "recipes/consumable/potions/lesser_fear_potion"
    LesserHealthPotion = "recipes/consumable/potions/lesser_health_potion"
    LesserIntelligencePotion = "recipes/consumable/potions/lesser_intelligence_potion"
    LesserManaPotion = "recipes/consumable/potions/lesser_mana_potion"
    LesserPoison = "recipes/consumable/potions/lesser_poison"
    LesserPotionOfDecay = "recipes/consumable/potions/lesser_potion_of_decay"
    LesserSleepingDraught = "recipes/consumable/potions/lesser_sleeping_draught"
    LesserSmokebomb = "recipes/consumable/potions/lesser_smokebomb"
    LesserPoisonWithPufferfish = "recipes/consumable/potions/lesser_poison_with_pufferfish"
    LesserStrengthPotion = "recipes/consumable/potions/lesser_strength_potion"
    LuckPotion = "recipes/consumable/potions/luck_potion"
    ManaPotion = "recipes/consumable/potions/mana_potion"
    Poison = "recipes/consumable/potions/poison"
    PotionOfDecay = "recipes/consumable/potions/potion_of_decay"
    SappingPotion = "recipes/consumable/potions/sapping_potion"
    SleepingDraught = "recipes/consumable/potions/sleeping_draught"
    Smokebomb = "recipes/consumable/potions/smokebomb"
    StrengthPotion = "recipes/consumable/potions/strength_potion"

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
        self.key = key
        self.icon = icon
        self.name = name
        self.value = value
        self.inputs = inputs
        self.outputs = outputs
        self.xp_reward_for_use = xp_reward_for_use

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
