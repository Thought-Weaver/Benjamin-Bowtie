from __future__ import annotations

from uuid import uuid4

from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import  Expertise, ExpertiseClass
from features.inventory import Inventory
from features.npcs.npc import NPC, NPCDuelingPersonas, NPCRoles
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, ItemKey
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.shared.ability import Ability

# -----------------------------------------------------------------------------
# NPC CLASS
# -----------------------------------------------------------------------------

class Clone(NPC):
    def __init__(self, name: str, org_expertise: Expertise, org_equipment: Equipment, org_abilities: List[Ability], persona: NPCDuelingPersonas):
        super().__init__(name, NPCRoles.DungeonEnemy, persona, {})

        self._org_expertise = org_expertise
        self._org_equipment = org_equipment
        self._org_abilities = org_abilities

        self._setup_npc_params()

    def _setup_inventory(self):
        if self._inventory is None:
            self._inventory = Inventory()

    def _setup_xp(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()
        
        self._expertise.add_xp_to_class_until_level(500, ExpertiseClass.Guardian)
        self._expertise.constitution = self._org_expertise.constitution * 3
        self._expertise.strength = self._org_expertise.strength * 3
        self._expertise.dexterity = self._org_expertise.dexterity * 3
        self._expertise.intelligence = self._org_expertise.intelligence * 3
        self._expertise.luck = self._org_expertise.luck * 3
        self._expertise.memory = self._org_expertise.memory

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        helmet = self._org_equipment.get_item_in_slot(ClassTag.Equipment.Helmet)
        if helmet is not None:
            self._equipment.equip_item_to_slot(ClassTag.Equipment.Helmet, LOADED_ITEMS.get_new_item(helmet.get_key()))
        
        gloves = self._org_equipment.get_item_in_slot(ClassTag.Equipment.Gloves)
        if gloves is not None:
            self._equipment.equip_item_to_slot(ClassTag.Equipment.Gloves, LOADED_ITEMS.get_new_item(gloves.get_key()))
        
        chest_armor = self._org_equipment.get_item_in_slot(ClassTag.Equipment.ChestArmor)
        if chest_armor is not None:
            self._equipment.equip_item_to_slot(ClassTag.Equipment.ChestArmor, LOADED_ITEMS.get_new_item(chest_armor.get_key()))
        
        main_hand = self._org_equipment.get_item_in_slot(ClassTag.Equipment.MainHand)
        if main_hand is not None:
            self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(main_hand.get_key()))

        off_hand = self._org_equipment.get_item_in_slot(ClassTag.Equipment.OffHand)
        if off_hand is not None:
            self._equipment.equip_item_to_slot(ClassTag.Equipment.OffHand, LOADED_ITEMS.get_new_item(off_hand.get_key()))

        leggings = self._org_equipment.get_item_in_slot(ClassTag.Equipment.Leggings)
        if leggings is not None:
            self._equipment.equip_item_to_slot(ClassTag.Equipment.Leggings, LOADED_ITEMS.get_new_item(leggings.get_key()))
        
        boots = self._org_equipment.get_item_in_slot(ClassTag.Equipment.Boots)
        if boots is not None:
            self._equipment.equip_item_to_slot(ClassTag.Equipment.Boots, LOADED_ITEMS.get_new_item(boots.get_key()))

        amulet = self._org_equipment.get_item_in_slot(ClassTag.Equipment.Amulet)
        if amulet is not None:
            self._equipment.equip_item_to_slot(ClassTag.Equipment.Amulet, LOADED_ITEMS.get_new_item(amulet.get_key()))

        ring = self._org_equipment.get_item_in_slot(ClassTag.Equipment.Ring)
        if ring is not None:
            self._equipment.equip_item_to_slot(ClassTag.Equipment.Ring, LOADED_ITEMS.get_new_item(ring.get_key()))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        for ability in self._org_abilities:
            # Clones don't have items, so this strictly hinders them
            if ability.get_name() != "Quick Access I":
                self._dueling.abilities.append(ability.__class__()) # type: ignore

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Clone"
        self._role = NPCRoles.DungeonEnemy
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
