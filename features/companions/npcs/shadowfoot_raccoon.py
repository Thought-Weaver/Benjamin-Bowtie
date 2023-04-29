from typing import List
from uuid import uuid4
from features.companions.abilities import IntoTheShadowsI, IntoTheShadowsII, IntoTheShadowsIII, IntoTheShadowsIV, IntoTheShadowsV, LuckyPawsI, LuckyPawsII, LuckyPawsIII, LuckyPawsIV, LuckyPawsV, StrikeFromBehindI, StrikeFromBehindII, StrikeFromBehindIII, StrikeFromBehindIV, StrikeFromBehindV
from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Expertise, ExpertiseClass
from features.inventory import Inventory
from features.shared.ability import Ability
from features.npcs.npc import NPC, NPCDuelingPersonas, NPCRoles
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, ItemKey
from features.stats import Stats


class ShadowfootRaccoon(NPC):
    def __init__(self, companion_level: int, name: str):
        super().__init__(name, NPCRoles.Companion, NPCDuelingPersonas.Mage, {})

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
        self._expertise.strength = self._companion_level // 4
        self._expertise.dexterity = self._companion_level
        self._expertise.intelligence = min(self._companion_level // 2, 40)
        self._expertise.luck = self._companion_level
        self._expertise.memory = self._companion_level // 5

        self._expertise.add_xp_to_class_until_level(self._companion_level, ExpertiseClass.Merchant)

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.RaccoonClaws))

        self._expertise.update_stats(self.get_combined_attributes())

    def get_abilities_for_level(self) -> List[Ability]:
        if self._companion_level >= 50:
            return [StrikeFromBehindV(), LuckyPawsV(), IntoTheShadowsV()]
        elif self._companion_level >= 45:
            return [StrikeFromBehindV(), LuckyPawsV(), IntoTheShadowsIV()]
        elif self._companion_level >= 40:
            return [StrikeFromBehindIV(), LuckyPawsIV(), IntoTheShadowsIV()]
        elif self._companion_level >= 35:
            return [StrikeFromBehindIV(), LuckyPawsIII(), IntoTheShadowsIV()]
        elif self._companion_level >= 30:
            return [StrikeFromBehindIV(), LuckyPawsIII(), IntoTheShadowsIII()]
        elif self._companion_level >= 25:
            return [StrikeFromBehindIII(), LuckyPawsIII(), IntoTheShadowsIII()]
        elif self._companion_level >= 20:
            return [StrikeFromBehindIII(), LuckyPawsII(), IntoTheShadowsII()]
        elif self._companion_level >= 15:
            return [StrikeFromBehindII(), LuckyPawsII(), IntoTheShadowsI()]
        elif self._companion_level >= 10:
            return [StrikeFromBehindII(), LuckyPawsI()]
        elif self._companion_level >= 5:
            return [StrikeFromBehindI()]
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
        self._name = "Shadowfoot Raccoon"
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
