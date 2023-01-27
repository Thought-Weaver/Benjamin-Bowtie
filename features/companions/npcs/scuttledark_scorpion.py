from typing import List
from uuid import uuid4
from features.companions.abilities import GraspingClawsI, GraspingClawsII, GraspingClawsIII, GraspingClawsIV, GraspingClawsV, IntoTheShadowsI, IntoTheShadowsII, IntoTheShadowsIII, IntoTheShadowsIV, IntoTheShadowsV, PowerfulPierceI, PowerfulPierceII, PowerfulPierceIII, PowerfulPierceIV, PowerfulPierceV
from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Expertise
from features.inventory import Inventory
from features.shared.ability import Ability
from features.npcs.npc import NPC, NPCDuelingPersonas, NPCRoles
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, ItemKey
from features.stats import Stats


class ScuttledarkScorpion(NPC):
    def __init__(self, companion_level: int):
        super().__init__("Scuttledark Scorpion", NPCRoles.Companion, NPCDuelingPersonas.Mage, {})

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
        
        self._expertise.constitution = min(self._companion_level // 2, 50)
        self._expertise.strength = self._companion_level
        self._expertise.dexterity = self._companion_level // 4
        self._expertise.intelligence = min(self._companion_level // 2, 40)
        self._expertise.luck = self._companion_level // 4
        self._expertise.memory = self._companion_level // 5

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.ScorpionClaws))

        self._expertise.update_stats(self.get_combined_attributes())
    
    def get_abilities_for_level(self) -> List[Ability]:
        if self._companion_level >= 50:
            return [PowerfulPierceV(), IntoTheShadowsV(), GraspingClawsV()]
        elif self._companion_level >= 45:
            return [PowerfulPierceV(), IntoTheShadowsV(), GraspingClawsIV()]
        elif self._companion_level >= 40:
            return [PowerfulPierceIV(), IntoTheShadowsIV(), GraspingClawsIV()]
        elif self._companion_level >= 35:
            return [PowerfulPierceIV(), IntoTheShadowsIII(), GraspingClawsIV()]
        elif self._companion_level >= 30:
            return [PowerfulPierceIV(), IntoTheShadowsIII(), GraspingClawsIII()]
        elif self._companion_level >= 25:
            return [PowerfulPierceIII(), IntoTheShadowsIII(), GraspingClawsIII()]
        elif self._companion_level >= 20:
            return [PowerfulPierceIII(), IntoTheShadowsII(), GraspingClawsII()]
        elif self._companion_level >= 15:
            return [PowerfulPierceII(), IntoTheShadowsII(), GraspingClawsI()]
        elif self._companion_level >= 10:
            return [PowerfulPierceII(), IntoTheShadowsI()]
        elif self._companion_level >= 5:
            return [PowerfulPierceI()]
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
        self._name = "Scuttledark Scorpion"
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
