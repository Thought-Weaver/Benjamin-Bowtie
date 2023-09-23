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
from features.shared.statuseffect import DmgReduction, TurnSkipChance
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player
    from features.shared.ability import NegativeAbilityResult

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class Bolster(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDEE1\uFE0F",
            name="Bolster",
            class_key=ExpertiseClass.Guardian,
            description="Restore and increase the max armor of all allies by 200.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=-1,
            level_requirement=20,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        for target in targets:
            target.get_dueling().armor += 150

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}, restoring 150 armor to all allies and increasing their max armor by 150!\n\n"

        self.remove_mana_and_set_cd(caster)

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class Protect(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD30",
            name="Protect",
            class_key=ExpertiseClass.Guardian,
            description="Grants an ally 100% damage protection for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=6,
            num_targets=1,
            level_requirement=20,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = DmgReduction(
            turns_remaining=2,
            value=1,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class Bash(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCAB",
            name="Bash",
            class_key=ExpertiseClass.Guardian,
            description="Cause Faltering on an enemy for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=5,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = TurnSkipChance(
            turns_remaining=2,
            value=1,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

# -----------------------------------------------------------------------------
# NPC CLASS
# -----------------------------------------------------------------------------

class DefendingTombGuardian(NPC):
    def __init__(self, name_suffix: str=""):
        # Balance Simulation Results:
        # 13% chance of 4 player party (Lvl. 80-90) victory against 1 + Assailing Tomb Guardian
        # Avg Number of Turns (per entity): 22

        super().__init__("Defending Tomb Guardian" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Bruiser, {})

        self._setup_npc_params()

    def _setup_inventory(self):
        if self._inventory is None:
            self._inventory = Inventory()

    def _setup_xp(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()
        
        self._expertise.add_xp_to_class_until_level(200, ExpertiseClass.Guardian)
        self._expertise.constitution = 130
        self._expertise.strength = 40
        self._expertise.dexterity = 0
        self._expertise.intelligence = 0
        self._expertise.luck = 27
        self._expertise.memory = 3

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.StoneMace))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.ChestArmor, LOADED_ITEMS.get_new_item(ItemKey.StoneForm))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [Bolster(), Protect(), Bash()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Assailing Tomb Guardian"
        self._role = NPCRoles.DungeonEnemy
        self._dueling_persona = NPCDuelingPersonas.Bruiser
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
