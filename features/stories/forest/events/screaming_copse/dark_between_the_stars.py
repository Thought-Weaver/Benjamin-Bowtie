from __future__ import annotations

import discord
import features.companions.companion
import random

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.player import Player
from features.shared.enums import CompanionKey
from features.stories.dungeon_run import DungeonRun
from features.stories.forest_room_selection import ForestRoomSelectionView

from typing import List


class RestContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DarkBetweenTheStarsView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        room_selection_view = ForestRoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class ForestRestButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Rest")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DarkBetweenTheStarsView = self.view
        if interaction.user not in view.rested_users:
            response = view.rest(interaction.user)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class StargazeButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Stargaze")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DarkBetweenTheStarsView = self.view
        response = view.stargaze()
        await interaction.response.edit_message(content=None, embed=response, view=view)


class DarkBetweenTheStarsView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run

        # Each player can only get one rest per rest room
        self.rested_users: List[discord.User] = []
        
        self._display_initial_buttons()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_initial_embed(self, additional_info: str=""):
        return Embed(title="A Warm Bonfire", description=f"You all gather around a fire and can rest for a moment among the trees, restoring part of your health and mana.\n\n{len(self.rested_users)}/{len(self._users)} players have rested.{additional_info}")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(ForestRestButton())
        self.add_item(StargazeButton())
        self.add_item(RestContinueButton())

    def any_in_duels_currently(self):
        return any(self._get_player(user.id).get_dueling().is_in_combat for user in self._users)

    def rest(self, user: discord.User):
        player = self._get_player(user.id)
        player_expertise = player.get_expertise()
        player_dueling = player.get_dueling()

        player_dueling.status_effects = []
        player_expertise.heal(int(player_expertise.max_hp / 2))
        player_expertise.restore_mana(int(player_expertise.max_mana / 2))

        companion_result_str: str = ""
        if random.random() < 0.001 + (0.001 * player.get_combined_attributes().luck) / 10:
            companions = player.get_companions()
            if random.random() < 0.5:
                if CompanionKey.VoidseenCat not in companions.companions.keys():
                    companions.companions[CompanionKey.VoidseenCat] = features.companions.companion.VoidseenCatCompanion()
                    companions.companions[CompanionKey.VoidseenCat].set_id(player.get_id())
                    companion_result_str += "\n\nIn your sleep, amid nightmares that seem far too real, you awake with a start to find something curled up beside your feet. A small cat, fur dark as the night, with beautiful eyes shimmering white with shards of color dancing in the irises. It purrs and calms you, driving away the fear you felt from the dreams. It's been added as a companion in b!companions."

                    player.get_stats().companions.companions_found += 1
            else:
                if CompanionKey.VoidseenPup not in companions.companions.keys():
                    companions.companions[CompanionKey.VoidseenPup] = features.companions.companion.VoidseenPupCompanion()
                    companions.companions[CompanionKey.VoidseenPup].set_id(player.get_id())
                    companion_result_str += "\n\nIn your sleep, amid nightmares that seem far too real, you awake with a start to find something curled up beside your feet. A small pup, fur dark as the night, with beautiful eyes shimmering white with shards of color dancing in the irises. It looks up at you, one ear floppy the other pointed straight up, then nuzzles you with its nose. Your newfound companion brings a profound sense of calm, driving away the terrifying dreams. It's been added as a companion in b!companions."

                    player.get_stats().companions.companions_found += 1

        self.rested_users.append(user)

        return self.get_initial_embed(companion_result_str)

    def stargaze(self):
        self.clear_items()
        self.add_item(ForestRestButton())
        self.add_item(RestContinueButton())

        return self.get_initial_embed("\n\nThe stars... what stars? You seem to remember them being there, but then the fire begins to fade away, your vision tunnelling deeper, deeper, deeper. There are no stars in the sky. No, there's only darkness -- an endless inescapable void and the things that lurk within it. They hunger for your dreams, for your greed, for understanding, for the sake of burning it all away. Listen closely. You can hear them. You can hear them.")

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