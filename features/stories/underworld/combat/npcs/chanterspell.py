from __future__ import annotations

from uuid import uuid4

from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Expertise, ExpertiseClass
from features.inventory import Inventory
from features.npcs.npc import NPC, NPCDuelingPersonas, NPCRoles
from features.shared.ability import Ability
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, ItemKey
from features.shared.statuseffect import DmgReduction, RegenerateHP
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class CastIllusions(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC65",
            name="Cast Illusions",
            class_key=ExpertiseClass.Alchemist,
            description="Restore two allies to full health if they're dead.",
            flavor_text="",
            mana_cost=10,
            cooldown=1,
            num_targets=2,
            level_requirement=20,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"

        if all(target.get_expertise().hp == 0 for target in targets):
            results: List[str] = self._use_heal_ability(caster, targets, range(500, 500))
            result_str += "\n".join(results)

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ArcaneShield(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDEE1\uFE0F",
            name="Arcane Shield",
            class_key=ExpertiseClass.Alchemist,
            description="Gain 80% Protected for 3 turns.",
            flavor_text="",
            mana_cost=30,
            cooldown=7,
            num_targets=0,
            level_requirement=20,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = DmgReduction(
            turns_remaining=3,
            value=0.8,
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


class HummingRegeneration(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF44",
            name="Humming Regeneration",
            class_key=ExpertiseClass.Alchemist,
            description="Regenerate 25% of your max health every turn for 3 turns.",
            flavor_text="",
            mana_cost=10,
            cooldown=8,
            num_targets=0,
            level_requirement=20,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = RegenerateHP(
            turns_remaining=3,
            value=0.25,
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

class Chanterspell(NPC):
    def __init__(self, name_suffix: str=""):
        # Balance Simulation Results:
        # 21% chance of 4 player party (Lvl. 70-80) victory against 1 + 2 Volatile Illusions
        # Avg Number of Turns (per entity): 11

        super().__init__("Chanterspell" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Healer, {
            ItemKey.Chanterspell: 0.9
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
        
        self._expertise.add_xp_to_class_until_level(220, ExpertiseClass.Alchemist)
        self._expertise.constitution = 100
        self._expertise.strength = 0
        self._expertise.dexterity = 40
        self._expertise.intelligence = 50
        self._expertise.luck = 27
        self._expertise.memory = 3

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.ChantingSong))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [CastIllusions(), ArcaneShield(), HummingRegeneration()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Chanterspell"
        self._role = NPCRoles.DungeonEnemy
        self._dueling_persona = NPCDuelingPersonas.Healer
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
