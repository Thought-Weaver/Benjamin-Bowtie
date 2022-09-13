from __future__ import annotations

from features.equipment import Equipment
from features.expertise import Expertise
from features.stats import Stats
from features.inventory import Inventory
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from features.mail import Mail


class Player():
    def __init__(self):
        self._inventory: Inventory = Inventory()
        self._mailbox: List[Mail] = []
        self._stats: Stats = Stats()
        self._expertise: Expertise = Expertise()
        self._equipment: Equipment = Equipment()

    def get_inventory(self):
        return self._inventory

    def get_mailbox(self):
        return self._mailbox

    def get_stats(self):
        return self._stats

    def get_expertise(self):
        return self._expertise

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._inventory = state.get("_inventory", Inventory())
        self._mailbox = state.get("_mailbox", [])
        self._stats = state.get("_stats", Stats())
        self._expertise = state.get("_expertise", Expertise())
        self._equipment = state.get("_equipment", Equipment())
