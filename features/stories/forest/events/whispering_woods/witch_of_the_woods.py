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
        
        view: WitchOfTheWoodsView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        room_selection_view: RoomSelectionView = RoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class ApproachButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Approach")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: WitchOfTheWoodsView = self.view
        if interaction.user.id == view.get_group_leader().id:
            response = view.approach()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class WitchOfTheWoodsView(discord.ui.View):
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
            if any(ClassTag.Consumable.Potion in LOADED_ITEMS.get_item_state(output)["class_tags"] for output in recipe.outputs):
                self._possible_recipes.append(recipe)

        self._display_initial_buttons()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_initial_embed(self):
        return Embed(title="A Strange Hut", description="Off the path, you spot a short hut with smoke rising from an opening in the top. The door creaks open and a light beckons you to come closer.")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(ApproachButton())
        self.add_item(ContinueButton())

    def any_in_duels_currently(self):
        return any(self._get_player(user.id).get_dueling().is_in_combat for user in self._users)

    def approach(self):
        self.clear_items()
        self.add_item(ContinueButton())

        recipe: Recipe = random.choice(self._possible_recipes)
        result_str: str = f"\n\nYou all learned how to make {recipe.get_name_and_icon()}!"

        return Embed(title="Witch of the Woods", description=f"You all approach the hut, careful but curious. From the warm firelight, an old woman with leaves and twigs tattered in her greying hair looks over all of you. She invites you inside for a time and teaches you something that might aid your future adventures: {result_str}\n\nAs you depart and are returning to the path, the hut sprouts giant spider legs and skitters deeper into the woods.")

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