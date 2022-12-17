from __future__ import annotations
from uuid import uuid4

from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Expertise, ExpertiseClass
from features.npcs.npc import NPC, NPCDuelingPersonas, NPCRoles
from features.shared.ability import BidedAttackIII, BoundToGetLuckyIII, PiercingStrikeIII, PressTheAdvantageI, SecondWindIII
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, ItemKey
from features.stats import Stats

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from features.inventory import Inventory

# -----------------------------------------------------------------------------
# NPC CLASS
# -----------------------------------------------------------------------------

class Galos(NPC):
    def __init__(self):
        super().__init__("Galos", NPCRoles.DuelingTrainer, NPCDuelingPersonas.Rogue, {})

        self._setup_npc_params()
            
    def _setup_inventory(self):
        if self._inventory is None:
            self._inventory = Inventory()

        items_to_add = []

        self._inventory.add_coins(300)
        for item in items_to_add:
            self._inventory.add_item(item)

    def _setup_xp(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._expertise.add_xp_to_class(600, ExpertiseClass.Alchemist, self._equipment) # Level 5
        self._expertise.add_xp_to_class(4000, ExpertiseClass.Merchant, self._equipment) # Level 15
        self._expertise.add_xp_to_class(29800, ExpertiseClass.Guardian, self._equipment) # Level 30
        
        self._expertise.points_to_spend = 0
        
        self._expertise.constitution = 20
        self._expertise.intelligence = 0
        self._expertise.dexterity = 20
        self._expertise.strength = 5
        self._expertise.luck = 0
        self._expertise.memory = 5

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.Helmet, LOADED_ITEMS.get_new_item(ItemKey.LeatherHelmet))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.Gloves, LOADED_ITEMS.get_new_item(ItemKey.LeatherGloves))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.ChestArmor, LOADED_ITEMS.get_new_item(ItemKey.LeatherJerkin))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.GalosRapier))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.Leggings, LOADED_ITEMS.get_new_item(ItemKey.LeatherLeggings))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.Boots, LOADED_ITEMS.get_new_item(ItemKey.LeatherBoots))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()

        self._dueling.abilities = [
            PressTheAdvantageI(), SecondWindIII(), PiercingStrikeIII(),
            BoundToGetLuckyIII(), BidedAttackIII()
        ]
    
    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Galos"
        self._role = NPCRoles.DuelingTrainer
        self._dueling_persona = NPCDuelingPersonas.Rogue
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
