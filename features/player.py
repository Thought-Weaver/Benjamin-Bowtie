from __future__ import annotations

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

    def get_inventory(self):
        return self._inventory

    def get_mailbox(self):
        return self._mailbox

    def get_stats(self):
        return self._stats

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._inventory = state.get("_inventory", Inventory())
        self._mailbox = state.get("_mailbox", [])
        self._stats = state.get("_stats", Stats())
