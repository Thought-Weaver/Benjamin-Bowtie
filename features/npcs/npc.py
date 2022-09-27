from __future__ import annotations

from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Expertise
from features.inventory import Inventory
from features.stats import Stats


class NPC():
    def __init__(self, name: str):
        self._name = name

        self._inventory: Inventory = Inventory()
        self._stats: Stats = Stats()
        self._expertise: Expertise = Expertise()
        self._equipment: Equipment = Equipment()
        self._dueling: Dueling = Dueling()

    def get_combined_attributes(self):
        return self._expertise.get_all_attributes() + (self._equipment.get_total_buffs() + self._dueling.get_combined_attribute_mods())

    def get_name(self):
        return self._name

    def get_inventory(self):
        return self._inventory

    def get_expertise(self):
        return self._expertise

    def get_equipment(self):
        return self._equipment

    def get_dueling(self):
        return self._dueling

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._inventory = state.get("_inventory", Inventory())
        self._expertise = state.get("_expertise", Expertise())
        self._equipment = state.get("_equipment", Equipment())
        self._dueling = state.get("_dueling", Dueling())
