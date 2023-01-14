from pstats import Stats
from uuid import uuid4
from features.companions.abilities import MightOfTheVoidI, MightOfTheVoidII, MightOfTheVoidIII, MightOfTheVoidIV, MightOfTheVoidV, RecklessBiteI, RecklessBiteII, RecklessBiteIII, RecklessBiteIV, RecklessBiteV, TheDarkBarkI, TheDarkBarkII, TheDarkBarkIII, TheDarkBarkIV, TheDarkBarkV
from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Expertise
from features.inventory import Inventory
from features.npcs.npc import NPC, NPCDuelingPersonas, NPCRoles
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, ItemKey


class VoidseenPup(NPC):
    def __init__(self, companion_level: int):
        super().__init__("Voidseen Pup", NPCRoles.Companion, NPCDuelingPersonas.Mage, {})

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
        
        self._expertise.constitution = self._companion_level // 2
        self._expertise.strength = self._companion_level
        self._expertise.dexterity = self._companion_level // 2
        self._expertise.intelligence = self._companion_level // 3
        self._expertise.luck = 2 * self._companion_level
        self._expertise.memory = self._companion_level // 5

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.VoidBite))

        self._expertise.update_stats(self.get_combined_attributes())

    def get_abilities_for_level(self):
        if self._companion_level <= 50:
            return [MightOfTheVoidV, RecklessBiteV, TheDarkBarkV]
        elif self._companion_level <= 45:
            return [MightOfTheVoidV, RecklessBiteV, TheDarkBarkIV]
        elif self._companion_level <= 40:
            return [MightOfTheVoidIV, RecklessBiteIV, TheDarkBarkIV]
        elif self._companion_level <= 35:
            return [MightOfTheVoidIV, RecklessBiteIII, TheDarkBarkIV]
        elif self._companion_level <= 30:
            return [MightOfTheVoidIV, RecklessBiteIII, TheDarkBarkIII]
        elif self._companion_level <= 25:
            return [MightOfTheVoidIII, RecklessBiteIII, TheDarkBarkIII]
        elif self._companion_level <= 20:
            return [MightOfTheVoidIII, RecklessBiteII, TheDarkBarkII]
        elif self._companion_level <= 15:
            return [MightOfTheVoidII, RecklessBiteII, TheDarkBarkI]
        elif self._companion_level <= 10:
            return [MightOfTheVoidII, RecklessBiteI]
        elif self._companion_level <= 5:
            return [MightOfTheVoidI]

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = []

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Voidseen Pup"
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
