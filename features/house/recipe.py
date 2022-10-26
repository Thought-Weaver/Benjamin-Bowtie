from __future__ import annotations

import json
from features.expertise import ExpertiseClass

from features.shared.item import LOADED_ITEMS, ClassTag, ItemKey
from strenum import StrEnum
from types import MappingProxyType

from typing import Dict, List

# -----------------------------------------------------------------------------
# ENUMS
# -----------------------------------------------------------------------------

class RecipeKey(StrEnum):
    pass

# -----------------------------------------------------------------------------
# RECIPE CLASS
# -----------------------------------------------------------------------------

class Recipe():
    def __init__(self, key: str, icon: str, name: str, inputs: Dict[ItemKey, int], outputs: Dict[ItemKey, int], xp_reward_for_use: Dict[ExpertiseClass, int]):
        # Figuring out whether the recipe should be displayed can be evaluated
        # based on the class tags of the outputs. The only problem with this is
        # that it makes filtering slower.
        self.key = key
        self.icon = icon
        self.name = name
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
            recipe_data.get("inputs", {}),
            recipe_data.get("outputs", {}),
            recipe_data.get("xp_reward_for_use", {})
        )

    def get_name_and_icon(self):
        return f"{self.icon} {self.name}"

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

        display_string += f"{input_display}\n\n====>\n\n"
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
        if state.get("_key", "") not in LOADED_RECIPES.get_all_keys():
            return

        base_data = LOADED_RECIPES.get_recipe_state(state["_key"])

        self.key = base_data.get("key", "")
        self.icon = base_data.get("icon", "")
        self.name = base_data.get("name", "")
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
