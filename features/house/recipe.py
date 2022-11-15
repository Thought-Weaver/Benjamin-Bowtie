from __future__ import annotations

import json

from enum import StrEnum
from features.expertise import ExpertiseClass
from features.inventory import Inventory
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, ItemKey
from types import MappingProxyType

from typing import Dict, List

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
    ConstitutionPotion = "recipes/consumable/potions/constitution_potion"
    DexterityPotion = "recipes/consumable/potions/dexterity_potion"
    FortitudePotion = "recipes/consumable/potions/fortitude_potion"
    GreaterConstitutionPotion = "recipes/consumable/potions/greater_constitution_potion"
    GreaterDexterityPotion = "recipes/consumable/potions/greater_dexterity_potion"
    GreaterHealthPotion = "recipes/consumable/potions/greater_health_potion"
    GreaterIntelligencePotion = "recipes/consumable/potions/greater_intelligence_potion"
    GreaterManaPotion = "recipes/consumable/potions/greater_mana_potion"
    GreaterPoison = "recipes/consumable/potions/greater_poison"
    GreaterStrengthPotion = "recipes/consumable/potions/greater_strength_potion"
    HealthPotion = "recipes/consumable/potions/health_potion"
    IntelligencePotion = "recipes/consumable/potions/intelligence_potion"
    LesserConstitutionPotion = "recipes/consumable/potions/lesser_constitution_potion"
    LesserDexterityPotion = "recipes/consumable/potions/lesser_dexterity_potion"
    LesserHealthPotion = "recipes/consumable/potions/lesser_health_potion"
    LesserIntelligencePotion = "recipes/consumable/potions/lesser_intelligence_potion"
    LesserManaPotion = "recipes/consumable/potions/lesser_mana_potion"
    LesserPoison = "recipes/consumable/potions/lesser_poison"
    LesserStrengthPotion = "recipes/consumable/potions/lesser_strength_potion"
    LuckPotion = "recipes/consumable/potions/luck_potion"
    ManaPotion = "recipes/consumable/potions/mana_potion"
    Poison = "recipes/consumable/potions/poison"
    SappingPotion = "recipes/consumable/potions/sapping_potion"
    StrengthPotion = "recipes/consumable/potions/strength_potion"

    # Alchemy Supplies
    CrystalVialWithFlawlessQuartz = "recipes/ingredient/alchemy_supplies/crystal_vial_with_flawless_quartz"
    CrystalVialWithQuartz = "recipes/ingredient/alchemy_supplies/crystal_vial_with_quartz"

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
            item = inventory.get_inventory_slots()[inventory.search_by_key(input_key)]
            
            if quantity > 0 and item is not None:
                if num == -1:
                    num = int(item.get_count() / quantity)
                else:
                    num = min(int(item.get_count() / quantity), num)
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
