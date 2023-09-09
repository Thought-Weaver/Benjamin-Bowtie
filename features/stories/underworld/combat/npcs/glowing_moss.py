from __future__ import annotations

import random

from uuid import uuid4

from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Expertise, ExpertiseClass
from features.inventory import Inventory
from features.npcs.npc import NPC, NPCDuelingPersonas, NPCRoles
from features.shared.ability import Ability
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, ItemKey
from features.shared.statuseffect import AttackingChanceToApplyStatus, CannotUseAbilities, DexDebuff, IntDebuff, StatusEffectKey, StrDebuff
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player
    from features.shared.ability import NegativeAbilityResult

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class SlumberSap(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA4",
            name="Slumber Sap",
            class_key=ExpertiseClass.Alchemist,
            description="Steal 90% of an enemy's max health if they're Sleeping.",
            flavor_text="",
            mana_cost=20,
            cooldown=0,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"

        is_sleeping: bool = any(se.key == StatusEffectKey.Sleeping for se in targets[0].get_dueling().status_effects)
        damage: int = int(0.9 * targets[0].get_expertise().max_hp) if is_sleeping else 0

        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        heal_results: List[str] = self._use_heal_ability(caster, [caster], range(damage, damage))

        result_str += "\n".join(list(map(lambda x: x.target_str, results)))
        result_str += "\n"
        result_str += "\n".join([s.replace("{1}", "{0}") for s in heal_results])

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class Luminesce(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2600\uFE0F",
            name="Luminesce",
            class_key=ExpertiseClass.Alchemist,
            description="Give all enemies a status effect for 5 turns that reduces their Str, Dex, and Int by 25 for 5 turns whenever they attack.",
            flavor_text="",
            mana_cost=10,
            cooldown=3,
            num_targets=-1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        str_debuff = AttackingChanceToApplyStatus(
            turns_remaining=5,
            value=1,
            status_effect=StrDebuff(
                turns_remaining=5,
                value=-25,
                source_str=self.get_icon_and_name()
            ),
            source_str=self.get_icon_and_name()
        )

        dex_debuff = AttackingChanceToApplyStatus(
            turns_remaining=5,
            value=1,
            status_effect=DexDebuff(
                turns_remaining=5,
                value=-25,
                source_str=self.get_icon_and_name()
            ),
            source_str=self.get_icon_and_name()
        )

        int_debuff = AttackingChanceToApplyStatus(
            turns_remaining=5,
            value=1,
            status_effect=IntDebuff(
                turns_remaining=5,
                value=-25,
                source_str=self.get_icon_and_name()
            ),
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [str_debuff, dex_debuff, int_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ConfusingPattern(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF87",
            name="Confusing Pattern",
            class_key=ExpertiseClass.Alchemist,
            description="Cause Enfeebled on all enemies for 3 turns.",
            flavor_text="",
            mana_cost=30,
            cooldown=6,
            num_targets=-1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = CannotUseAbilities(
            turns_remaining=3,
            value=1,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# NPC CLASS
# -----------------------------------------------------------------------------

class GlowingMoss(NPC):
    def __init__(self, name_suffix: str=""):
        # Balance Simulation Results:
        # 47% chance of 4 player party (Lvl. 70-80) victory against 1
        # Avg Number of Turns (per entity): 13

        super().__init__("Glowing Moss" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Mage, {})

        self._setup_npc_params()

    def _setup_inventory(self):
        if self._inventory is None:
            self._inventory = Inventory()

    def _setup_xp(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()
        
        self._expertise.add_xp_to_class_until_level(320, ExpertiseClass.Alchemist)
        self._expertise.constitution = 60
        self._expertise.strength = 0
        self._expertise.dexterity = 70
        self._expertise.intelligence = 120
        self._expertise.luck = 67
        self._expertise.memory = 3

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.ShimmeringLight))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [SlumberSap(), Luminesce(), ConfusingPattern()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Glowing Moss"
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
