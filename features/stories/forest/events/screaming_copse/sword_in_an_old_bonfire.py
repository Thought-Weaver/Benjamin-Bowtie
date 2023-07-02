from __future__ import annotations

import discord

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.player import Player
from features.shared.item import LOADED_ITEMS, ItemKey
from features.stories.dungeon_run import DungeonRun
from features.stories.forest_room_selection import ForestRoomSelectionView

from typing import List


class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: SwordInAnOldBonfireView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        room_selection_view: ForestRoomSelectionView = ForestRoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class RestButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Rest")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: SwordInAnOldBonfireView = self.view
        if interaction.user.id == view.get_group_leader().id:
            response = view.rest()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class RemoveSwordButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Remove Sword")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: SwordInAnOldBonfireView = self.view
        if interaction.user.id == view.get_group_leader().id:
            response = view.remove_sword()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class SwordInAnOldBonfireView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run
        
        self._display_initial_buttons()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_initial_embed(self):
        return Embed(title="Sword in an Old Bonfire", description="In the harrowing mist of this place, you all come across the fading glow of an abandoned bonfire. Within it, you spy a coiled sword left behind -- it seems to be glowing with heat, perhaps providing the remaining warmth for the embers.\n\nYou could rest here around its warmth, attempt to remove the sword, or simply leave:")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(RestButton())
        self.add_item(RemoveSwordButton())
        self.add_item(ContinueButton())

    def rest(self):
        self.clear_items()
        self.add_item(ContinueButton())

        for user in self._users:
            player = self._get_player(user.id)
            player_expertise = player.get_expertise()

            player_expertise.heal(int(player_expertise.max_hp / 2))
            player_expertise.restore_mana(int(player_expertise.max_mana / 2))
        
        return Embed(title="Hearth and Home", description="Your party rests, restoring part of their health and mana.")

    def remove_sword(self):
        self.clear_items()
        self.add_item(ContinueButton())

        player = self._get_player(self._group_leader.id)
        item = LOADED_ITEMS.get_new_item(ItemKey.CoiledSword)
        player.get_inventory().add_item(item)

        damage_dealt = player.get_expertise().damage(25, player.get_dueling(), 0, True)

        return Embed(title="The Flame Extinguished", description=f"Your group leader grasps the sword tightly, pulling it slowly free from the bonfire and the muck beneath. The sword burns as it resists being removed, dealing {damage_dealt} damage -- but it does relent and a new item is added to your inventory.")

    def any_in_duels_currently(self):
        return any(self._get_player(user.id).get_dueling().is_in_combat for user in self._users)

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