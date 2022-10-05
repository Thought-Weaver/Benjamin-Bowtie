from __future__ import annotations

import discord

from features.expertise import ExpertiseClass
from features.npcs.npc import NPC, NPCRoles
from features.shared.item import ClassTag

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot import BenjaminBowtieBot

# -----------------------------------------------------------------------------
# NPC VIEW
# -----------------------------------------------------------------------------

class YennaView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, user: discord.User):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._user = user
        self._yenna = database[str(guild_id)]["npcs"][NPCRoles.FortuneTeller]

# -----------------------------------------------------------------------------
# NPC CLASS
# -----------------------------------------------------------------------------

class Yenna(NPC):
    def __init__(self):
        super().__init__("Yenna", NPCRoles.FortuneTeller)

        # Inventory Setup
        self._restock_items = []
        self._restock_coins = 5000

        self._inventory.add_coins(self._restock_coins)
        for item in self._restock_items:
            self._inventory.add_item(item)
        
        # Expertise Setup
        # TODO: When Alchemy is implemented, add XP to that class to get to Level 50
        self._expertise.add_xp_to_class(96600, ExpertiseClass.Merchant) # Level 20
        self._expertise.add_xp_to_class(1600, ExpertiseClass.Guardian) # Level 5
        
        self._expertise.points_to_spend = 0
        
        self._expertise.constitution = 10
        self._expertise.intelligence = 30
        self._expertise.dexterity = 10
        self._expertise.strength = 5
        self._expertise.luck = 10
        self._expertise.memory = 10

        self._expertise.update_stats()

        # Equipment Setup
        # TODO: Add items when they've been created
        self._equipment.equip_item_to_slot(ClassTag.Equipment.Ring, None)

        # Dueling Setup
        # TODO: Add abilities when Alchemist abilities are implemented
        self._dueling.abilities = []

        # Story Variables
        self._last_to_identify_scroll = None
