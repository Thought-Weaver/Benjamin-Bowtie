from __future__ import annotations

import discord
import random

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.player import Player
from features.stories.dungeon_run import DungeonRun, RoomSelectionView

from typing import List, Set


class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: VoiceOfTheSeaView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        room_selection_view: RoomSelectionView = RoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class ListenButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Red")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: VoiceOfTheSeaView = self.view
        if interaction.user.id not in view.players_decided:
            response = view.listen(interaction.user.id, interaction.user.display_name)
            await interaction.response.edit_message(content=None, embed=response, view=view)

            if interaction.user.id in view.players_listened:
                message = random.choice([
                    "The dream is the sky and the sky is the dream. It wasn't here before. Come deeper and let us understand.",
                    "Do you fear the chthonic thing? The flames were meant to free the world. They are gone now, until the next time.",
                    "The houses are new. The last one seeks the answers. Where did you come from? Green and blue and black and purple.",
                    "Blank. Awaken. They can go if they wish. The throne is meant for all. The entrance will be built."
                ])
                await interaction.user.send(message)


class ResistButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Resist")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: VoiceOfTheSeaView = self.view
        if interaction.user.id not in view.players_decided:
            response = view.resist(interaction.user.id, interaction.user.display_name)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class VoiceOfTheSeaView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run

        self.players_decided: Set[int] = set()
        self.players_listened: Set[int] = set()
        self.result_str: str = ""
        
        self._display_initial_buttons()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_initial_embed(self):
        return Embed(title="Voice of the Sea", description=f"Walking through the coral forest, along the golden sands of this region of the ocean, there's a sound suddenly echoing through the water. At first, it doesn't make sense -- it sounds like the common tongue, but the words are nonsense. Still, you feel an allure to listen more closely. What is it trying to say?\n\n{len(self.players_decided)}/{len(self._users)} have made a choice")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(ListenButton())
        self.add_item(ResistButton())

    def listen(self, user_id: int, name: str):
        player = self._get_player(user_id)
        player.get_dungeon_run().corruption += 5

        self.result_str += f"{name} listened more closely\n"
        self.players_listened.add(user_id)
        self.players_decided.add(user_id)

        if len(self.players_decided) == len(self._users):
            self.clear_items()
            self.add_item(ContinueButton())

            return Embed(title="An Alluring Whisper", description=f"The voice called to each of you...\n\n{self.result_str}")
        else:
            return self.get_initial_embed()

    def resist(self, user_id: int, name: str):
        player = self._get_player(user_id)
        resists: bool = random.random() < 0.05 * player.get_dungeon_run().corruption

        if not resists:
            return self.listen(user_id, name)
        else:
            self.result_str += f"{name} resisted the influence of the echoing voice\n"
            self.players_decided.add(user_id)

            if len(self.players_decided) == len(self._users):
                self.clear_items()
                self.add_item(ContinueButton())
            
                return Embed(title="An Alluring Whisper", description=f"The voice called to each of you...\n\n{self.result_str}")
            else:
                return self.get_initial_embed()

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