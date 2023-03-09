from __future__ import annotations

import discord
import random

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.house.recipe import LOADED_RECIPES, RecipeKey
from features.player import Player
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS
from features.stories.dungeon_run import DungeonRun, RoomSelectionView

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.house.recipe import Recipe

class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: WanderingCookView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        room_selection_view: RoomSelectionView = RoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class AcceptButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Accept")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: WanderingCookView = self.view
        if interaction.user.id == view.get_group_leader().id:
            response = view.accept()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class WanderingCookView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run

        self._possible_recipes = []
        for recipe_key in RecipeKey:
            recipe = LOADED_RECIPES.get_new_recipe(recipe_key)
            if any(ClassTag.Consumable.Food in LOADED_ITEMS.get_item_state(output)["class_tags"] for output in recipe.outputs):
                self._possible_recipes.append(recipe)

        self._display_initial_buttons()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_initial_embed(self):
        return Embed(title="Wanderer by a Fire", description="A small fire catches your attention off the path and the figure sitting there seems to be alone, surrounded by various metal objects and packs. They don't seem like weapons, but it's difficult to tell from this distance.\n\nTurning, the figure sees you and calls out, \"Oi there, come on over! There's plenty o' food to go around.\"")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(AcceptButton())
        self.add_item(ContinueButton())

    def any_in_duels_currently(self):
        return any(self._get_player(user.id).get_dueling().is_in_combat for user in self._users)

    def accept(self):
        self.clear_items()
        self.add_item(ContinueButton())

        recipe: Recipe = random.choice(self._possible_recipes)
        result_str: str = f"\n\nYou all learned how to make {recipe.get_name_and_icon()}!"

        return Embed(title="A Delicious Meal", description=f"You join this journeyman, who you quickly discover is a cook, for a good meal. Between laughter and grand tales of his journeys, he also takes the time to teach you how to cook something yourselves: {result_str}")

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