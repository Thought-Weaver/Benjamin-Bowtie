from __future__ import annotations

from features.companions.player_companions import PlayerCompanions
from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Expertise
from features.house.house import House
from features.stats import Stats
from features.inventory import Inventory

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.mail import Mail


class Player():
    def __init__(self, id: str):
        self._id = id

        self._inventory: Inventory = Inventory()
        self._mailbox: List[Mail] = []
        self._stats: Stats = Stats()
        self._expertise: Expertise = Expertise()
        self._equipment: Equipment = Equipment()
        self._dueling: Dueling = Dueling()
        self._house: House = House()
        self._companions: PlayerCompanions = PlayerCompanions(self.send_mail)
        self._in_dungeon_run: bool = False

    def get_id(self):
        return self._id
    
    def set_id(self, id: str):
        if self._id is None or self._id == "":
            self._id = id

    def get_combined_attributes(self):
        return self._expertise.get_all_attributes() + self._equipment.get_total_attribute_mods() + self._dueling.get_combined_attribute_mods()

    def get_inventory(self):
        return self._inventory

    def get_mailbox(self):
        return self._mailbox

    def send_mail(self, mail: Mail):
        self._mailbox.append(mail)

    def get_stats(self):
        return self._stats

    def get_expertise(self):
        return self._expertise

    def get_equipment(self):
        return self._equipment

    def get_dueling(self):
        return self._dueling

    def get_house(self):
        return self._house

    def get_companions(self):
        return self._companions
    
    def is_in_dungeon_run(self):
        return self._dungeon_run
    
    def set_is_in_dungeon_run(self, value: bool):
        self._in_dungeon_run = value

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", "")
        self._inventory = state.get("_inventory", Inventory())
        self._mailbox = state.get("_mailbox", [])
        self._stats = state.get("_stats", Stats())
        self._expertise = state.get("_expertise", Expertise())
        self._equipment = state.get("_equipment", Equipment())
        self._dueling = state.get("_dueling", Dueling())
        self._house = state.get("_house", House())
        self._companions = state.get("_companions", PlayerCompanions(self.send_mail))
        self._dungeon_run = state.get("_dungeon_run", None)
