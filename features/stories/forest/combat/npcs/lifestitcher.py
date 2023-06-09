from __future__ import annotations

from uuid import uuid4

from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Expertise, ExpertiseClass
from features.inventory import Inventory
from features.npcs.npc import NPC, NPCDuelingPersonas, NPCRoles
from features.shared.ability import CleanseI, IncenseII, IncenseIII, RegenerationI, RegenerationII, SmokescreenI
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, ItemKey
from features.stats import Stats

# -----------------------------------------------------------------------------
# NPC CLASS
# -----------------------------------------------------------------------------

class Lifestitcher(NPC):
    def __init__(self, name_suffix: str=""):
        super().__init__("Lifestitcher" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Healer, {
            ItemKey.WrathbarkStaff: 0.3,
            ItemKey.LesserManaPotion: 0.1,
            ItemKey.PileOfCoins: 0.1,
            ItemKey.AFewCoins: 0.5,
        })

        self._setup_npc_params()

    def _setup_inventory(self):
        if self._inventory is None:
            self._inventory = Inventory()

    def _setup_xp(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()
        
        self._expertise.add_xp_to_class_until_level(80, ExpertiseClass.Fisher)
        self._expertise.constitution = 30
        self._expertise.strength = 0
        self._expertise.dexterity = 16
        self._expertise.intelligence = 30
        self._expertise.luck = 0
        self._expertise.memory = 4

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.BoneStaffOfHealing))

        self._equipment.equip_item_to_slot(ClassTag.Equipment.Helmet, LOADED_ITEMS.get_new_item(ItemKey.AmberiteHelmet))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.Gloves, LOADED_ITEMS.get_new_item(ItemKey.AmberiteGauntlets))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.ChestArmor, LOADED_ITEMS.get_new_item(ItemKey.AmberiteCuirass))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.Leggings, LOADED_ITEMS.get_new_item(ItemKey.AmberiteLeggings))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.Boots, LOADED_ITEMS.get_new_item(ItemKey.AmberiteGreaves))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [IncenseIII(), CleanseI(), SmokescreenI(), RegenerationII()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Mystic"
        self._role = NPCRoles.DungeonEnemy
        self._dueling_persona = NPCDuelingPersonas.Healer
        self._dueling_rewards = {
            ItemKey.WrathbarkStaff: 0.6,
            ItemKey.LesserManaPotion: 0.2,
            ItemKey.PileOfCoins: 0.4,
            ItemKey.AFewCoins: 1,
        }
        
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
