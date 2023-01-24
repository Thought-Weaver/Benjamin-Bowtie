from uuid import uuid4
from typing import List
from features.companions.abilities import InnervateI, InnervateII, InnervateIII, InnervateIV, InnervateV, MesmerizeI, MesmerizeII, MesmerizeIII, MesmerizeIV, MesmerizeV, WingbeatI, WingbeatII, WingbeatIII, WingbeatIV, WingbeatV
from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Expertise
from features.inventory import Inventory
from features.npcs.npc import NPC, NPCDuelingPersonas, NPCRoles
from features.shared.ability import Ability
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, ItemKey
from features.stats import Stats


class BlueFlitterwingButterfly(NPC):
    def __init__(self, companion_level: int):
        super().__init__("Blue Flitterwing Butterfly", NPCRoles.Companion, NPCDuelingPersonas.Mage, {})

        self._companion_level = companion_level

        self._setup_npc_params()

    def _setup_inventory(self):
        if self._inventory is None:
            self._inventory = Inventory()

    def _setup_xp(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()
        
        self._expertise.constitution = self._companion_level // 4
        self._expertise.strength = self._companion_level // 5
        self._expertise.dexterity = self._companion_level // 2
        self._expertise.intelligence = self._companion_level
        self._expertise.luck = self._companion_level // 2
        self._expertise.memory = self._companion_level // 5

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.ButterflyWings))

        self._expertise.update_stats(self.get_combined_attributes())

    def get_abilities_for_level(self) -> List[Ability]:
        if self._companion_level >= 50:
            return [MesmerizeV(), InnervateV(), WingbeatV()]
        elif self._companion_level >= 45:
            return [MesmerizeV(), InnervateV(), WingbeatIV()]
        elif self._companion_level >= 40:
            return [MesmerizeIV(), InnervateIV(), WingbeatIV()]
        elif self._companion_level >= 35:
            return [MesmerizeIV(), InnervateIII(), WingbeatIV()]
        elif self._companion_level >= 30:
            return [MesmerizeIV(), InnervateIII(), WingbeatIII()]
        elif self._companion_level >= 25:
            return [MesmerizeIII(), InnervateIII(), WingbeatIII()]
        elif self._companion_level >= 20:
            return [MesmerizeIII(), InnervateII(), WingbeatII()]
        elif self._companion_level >= 15:
            return [MesmerizeII(), InnervateII(), WingbeatI()]
        elif self._companion_level >= 10:
            return [MesmerizeII(), InnervateI()]
        elif self._companion_level >= 5:
            return [MesmerizeI()]
        return []

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = self.get_abilities_for_level()

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Blue Flitterwing Butterfly"
        self._role = NPCRoles.Companion
        self._dueling_persona = NPCDuelingPersonas.Mage
        self._dueling_rewards = {}
        
        self._inventory: Inventory | None = state.get("_inventory")
        if self._inventory is None:
            self._inventory = Inventory()
            self._setup_inventory()

        self._equipment: Equipment | None = state.get("_equipment")
        if self._equipment is None:
            self._equipment = Equipment()
            self._setup_equipment()

        self._expertise: Expertise | None = state.get("_expertise")
        if self._expertise is None:
            self._expertise = Expertise()
            self._setup_xp()

        self._dueling: Dueling | None = state.get("_dueling")
        if self._dueling is None:
            self._dueling = Dueling()
            self._setup_abilities()

        self._stats: Stats | None = state.get("_stats")
        if self._stats is None:
            self._stats = Stats()
