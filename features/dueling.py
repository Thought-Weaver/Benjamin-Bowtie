from __future__ import annotations

import discord

from discord.embeds import Embed
from discord.ext import commands

from typing import Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from features.player import Player
    from features.shared.ability import Ability, StatusEffect


class Dueling():
    def __init__(self):
        self.abilities: List[Ability] = []

        # Temporary variables maintained for duels
        # They're stored here to make it easier to check if a Player/NPC
        # is currently in a duel
        self.is_in_combat: bool = False
        self.status_effects: List[StatusEffect] = []
    
    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.abilities = state.get("abilities", [])

        self.is_in_combat = False
        self.status_effects = []


class Duel(discord.ui.View):
    def __init__(self, bot: commands.Bot, database: dict, guild_id: int, users: List[discord.User], allies: List[Player], enemies: List[Player]):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._allies = allies
        self._enemies = enemies
        self._turn_order = (allies + enemies).sort(key=lambda x: x.get_expertise().dexterity)
        self._turn_index = 0
