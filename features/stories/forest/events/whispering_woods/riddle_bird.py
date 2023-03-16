from __future__ import annotations

import discord
import random

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.player import Player
from features.stories.dungeon_run import DungeonRun, RoomSelectionView

from typing import List

# -----------------------------------------------------------------------------
# MODAL
# -----------------------------------------------------------------------------

class AnswerModal(discord.ui.Modal):
    def __init__(self, database: dict, guild_id: int, users: List[discord.User], view: RiddleBirdView, message: discord.Message):
        super().__init__(title=f"Reply to the Riddle Bird")

        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._view = view
        self._message = message

        self._answer_input: discord.ui.TextInput = discord.ui.TextInput(
            label="Answer",
            default="",
            required=True,
            max_length=15
        )
        self.add_item(self._answer_input)

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    async def on_submit(self, interaction: discord.Interaction):
        answer = self._answer_input.value.lower()

        response_embed = Embed()
        if answer in self._view.answers:
            coin = random.randint(100, 200)
            response_embed = Embed(
                title="Riddle Bird",
                description=f"The bird caws and cackles in delight at you having solved the riddle! Its eyes alight and before you a chest with {coin} coin is presented."
            )

            for user in self._users:
                player = self._get_player(user.id)
                player.get_inventory().add_coins(coin)
        else:
            damage = random.randint(5, 10)
            response_embed = Embed(
                title="Riddle Bird",
                description="The bird caws in anger and dives for your eyes! It only manages to deal a bit of damage before you all flee from the danger."
            )

            # TODO: Implement a check to see if this kills the party?
            for user in self._users:
                player = self._get_player(user.id)
                player.get_expertise().damage(damage, player.get_dueling(), 0, True)

        self._view.clear_items()
        self._view.add_item(ContinueButton())

        await self._message.edit(view=self, embed=response_embed)
        await interaction.response.defer()

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        await interaction.response.send_message("Error: Something has gone terribly wrong.")

# -----------------------------------------------------------------------------
# RIDDLE BIRD VIEW
# -----------------------------------------------------------------------------

class AnswerButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Answer")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: RiddleBirdView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return
        
        await interaction.response.send_modal(AnswerModal(
                view.get_database(),
                view.get_guild_id(),
                view.get_users(),
                view,
                interaction.message
            )
        )


class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: RiddleBirdView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        room_selection_view: RoomSelectionView = RoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class PlayButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Play")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: RiddleBirdView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't accept the Riddle Bird's deal.")
            return

        response = view.get_riddle_embed()
        await interaction.response.edit_message(embed=response, view=view, content=None)


class RiddleBirdView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run

        self._possible_riddles = {
            "I live from but a single breath; any touch could spell my death; a rainbow spins upon my eye; make me right and I can fly.":
                ["bubble", "bubbles"],
            "I have oceans without water, mountains without land, cities without people, and deserts without sand.":
                ["maps", "map"],
            "Walk on the living, they don't even mumble. Walk on the dead, they mutter and grumble.":
                ["leaves"],
            "I lick the trees yet have no tongue, to spread and make the forest young; from the storm can come my birth, dancing round me make thy mirth.":
                ["fire", "flames", "fires", "flame", "bonfire", "bonfires"],
            "Silver, brass, copper, gold; given, bought, stolen, sold; symbols of wealth, or power, or love; forged like a sword, fits like a glove.":
                ["ring", "rings"],
            "What always runs but never walks; often murmurs, never talks; has a bed, but never sleeps; an open mouth that never eats?":
                ["river", "rivers"],
            "You walk over, you walk under; in times of war, they're burnt asunder.":
                ["bridge", "bridges"],
            "Fondle and ogle me until you're insane, but no blow can harm me or cause me pain. Children delight in me, elders take fright. Cry and I weep, yawn and I sleep. Smile, and I shall grin.":
                ["mirror", "mirrors", "reflection", "reflections"]
        }

        self.riddle = random.choice(list(self._possible_riddles.keys()))
        self.answers = self._possible_riddles[self.riddle]

        self._display_initial_buttons()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_initial_embed(self):
        return Embed(title="Riddle Bird", description=f"Atop a tree, you're suddenly stopped by the cawing of a large bird, \"A one-word riddle I have for thee, respond wrong and I'll peck thee. Answer true and I will offer, from my most abundant coffer.\"")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(PlayButton())
        self.add_item(ContinueButton())

    def get_riddle_embed(self):
        self.clear_items()
        self.add_item(AnswerButton())

        return Embed(title="Riddle Bird", description=f"The bird caws again, presenting its riddle:\n\n\"{self.riddle}\"")

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