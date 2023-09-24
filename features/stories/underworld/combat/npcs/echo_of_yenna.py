from __future__ import annotations

from uuid import uuid4

from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Attribute, Expertise, ExpertiseClass
from features.inventory import Inventory
from features.npcs.npc import NPC, NPCDuelingPersonas, NPCRoles
from features.shared.ability import Ability
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, ItemKey
from features.shared.statuseffect import ConBuff, DamageSplit, LckBuff
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class FortifyingIncense(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE94",
            name="Fortifying Incense",
            class_key=ExpertiseClass.Alchemist,
            description="Restore 90-100 health to all allies and increase their Con by 10 for 5 turns.",
            flavor_text="",
            mana_cost=30,
            cooldown=3,
            num_targets=-1,
            level_requirement=20,
            target_own_group=True,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = ConBuff(
            turns_remaining=5,
            value=10,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_heal_and_effect_ability(caster, targets, range(90, 100), [buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class Fatebinding(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD2E",
            name="Fatebinding",
            class_key=ExpertiseClass.Alchemist,
            description="Link yourself to all allies, splitting the damage any of you take evenly between you for 4 turns.",
            flavor_text="",
            mana_cost=80,
            cooldown=9,
            num_targets=-1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = DamageSplit(
            turns_remaining=4,
            linked_targets=targets,
            value=1,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class FortunesFavor(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF40",
            name="Fortune's Favor",
            class_key=ExpertiseClass.Alchemist,
            description="Increase the Luck of all allies by 100 for 2 turns.",
            flavor_text="",
            mana_cost=20,
            cooldown=4,
            num_targets=0,
            level_requirement=20,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = LckBuff(
            turns_remaining=2,
            value=100,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# NPC CLASS
# -----------------------------------------------------------------------------

class EchoOfYenna(NPC):
    def __init__(self, name_suffix: str=""):
        # Balance Simulation Results:
        # ?% chance of 4 player party (Lvl. 80-90) victory against 1 + Asterius + Passerhawk
        # Avg Number of Turns (per entity): ?

        super().__init__("Echo of Yenna" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Mage, {
            ItemKey.StaffOfTheEyelessAlchemist: 0.01,
            ItemKey.RobeOfTheEyelessAlchemist: 0.01
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
        
        self._expertise.add_xp_to_class_until_level(300, ExpertiseClass.Alchemist)
        self._expertise.constitution = 100
        self._expertise.strength = 0
        self._expertise.dexterity = 60
        self._expertise.intelligence = 100
        self._expertise.luck = 37
        self._expertise.memory = 3

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.StaffOfTheEyelessAlchemist))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.ChestArmor, LOADED_ITEMS.get_new_item(ItemKey.RobeOfTheEyelessAlchemist))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [FortifyingIncense(), Fatebinding(), FortunesFavor()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Echo of Yenna"
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
