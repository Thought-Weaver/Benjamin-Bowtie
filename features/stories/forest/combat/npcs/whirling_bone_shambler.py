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
from features.shared.statuseffect import CannotAttack, CannotUseAbilities, DmgVulnerability, Undying
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player
    from features.shared.ability import NegativeAbilityResult

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class TerrifyingCage(Ability):
    def __init__(self):
        super().__init__(
            icon="\u26D3\uFE0F",
            name="Terrifying Cage",
            class_key=ExpertiseClass.Fisher,
            description="Cause Enfeebled and Atrophied on an enemy for 2 turns.",
            flavor_text="",
            mana_cost=20,
            cooldown=3,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"

        cannot_attack_debuff = CannotAttack(
            turns_remaining=2,
            value=1,
            source_str=self.get_icon_and_name()
        )

        cannot_use_abilities_debuff = CannotUseAbilities(
            turns_remaining=2,
            value=1,
            source_str=self.get_icon_and_name()
        )

        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [cannot_attack_debuff, cannot_use_abilities_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class DeathWish(Ability):
    def __init__(self):
        super().__init__(
            icon="\u26B0\uFE0F",
            name="Death Wish",
            class_key=ExpertiseClass.Fisher,
            description="Cause 1% damage vulnerability for each % of HP missing from the target for 2 turns.",
            flavor_text="",
            mana_cost=30,
            cooldown=3,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"

        debuff = DmgVulnerability(
            turns_remaining=2,
            value=0.01 * targets[0].get_expertise().hp / targets[0].get_expertise().max_hp,
            source_str=self.get_icon_and_name()
        )

        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class UndeadResolve(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC80",
            name="Undead Resolve",
            class_key=ExpertiseClass.Fisher,
            description="Gain Undying for 2 turns.",
            flavor_text="",
            mana_cost=50,
            cooldown=8,
            num_targets=0,
            level_requirement=20,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = Undying(
            turns_remaining=2,
            value=1,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# NPC CLASS
# -----------------------------------------------------------------------------

class WhirlingBoneShambler(NPC):
    def __init__(self, name_suffix: str=""):
        super().__init__("Whirling Bone Shambler" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Specialist, {})

        self._setup_npc_params()

    def _setup_inventory(self):
        if self._inventory is None:
            self._inventory = Inventory()

    def _setup_xp(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()
        
        self._expertise.add_xp_to_class_until_level(300, ExpertiseClass.Fisher)
        self._expertise.constitution = 150
        self._expertise.strength = 0
        self._expertise.dexterity = 30
        self._expertise.intelligence = 100
        self._expertise.luck = 20
        self._expertise.memory = 3

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.ShamblersBones))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.OffHand, LOADED_ITEMS.get_new_item(ItemKey.ShamblersForm))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [TerrifyingCage(), DeathWish(), UndeadResolve()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Whirling Bone Shambler"
        self._role = NPCRoles.DungeonEnemy
        self._dueling_persona = NPCDuelingPersonas.Specialist
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
