import discord

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.player import Player

from typing import List

# -----------------------------------------------------------------------------
# WILD BOAR DUEL INTRO
# -----------------------------------------------------------------------------

class WildBoarDuelView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User]):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        
        self._display_initial_buttons()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_initial_embed(self):
        return Embed(title="", description="")

    def _display_initial_buttons(self):
        self.clear_items()

    def get_bot(self):
        return self._bot

    def get_users(self):
        return self._users

    def get_database(self):
        return self._database

    def get_guild_id(self):
        return self._guild_id