from __future__ import annotations

import random

from uuid import uuid4

from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Attribute, Expertise, ExpertiseClass
from features.inventory import Inventory
from features.npcs.npc import NPC, NPCDuelingPersonas, NPCRoles
from features.shared.ability import Ability
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, ItemKey
from features.shared.statuseffect import ConDebuff, DexDebuff, DmgBuff, IntDebuff, LckDebuff, StatusEffectKey, StrDebuff
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player
    from features.shared.ability import NegativeAbilityResult

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class SappingCold(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2744\uFE0F",
            name="Sapping Cold",
            class_key=ExpertiseClass.Guardian,
            description="Reduce the non-memory stats of all enemies by 15 for 3 turns.",
            flavor_text="",
            mana_cost=20,
            cooldown=3,
            num_targets=-1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        con_debuff = ConDebuff(
            turns_remaining=3,
            value=-15,
            source_str=self.get_icon_and_name()
        )
        str_debuff = StrDebuff(
            turns_remaining=3,
            value=-15,
            source_str=self.get_icon_and_name()
        )
        dex_debuff = DexDebuff(
            turns_remaining=3,
            value=-15,
            source_str=self.get_icon_and_name()
        )
        int_debuff = IntDebuff(
            turns_remaining=3,
            value=-15,
            source_str=self.get_icon_and_name()
        )
        lck_debuff = LckDebuff(
            turns_remaining=3,
            value=-15,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [con_debuff, str_debuff, dex_debuff, int_debuff, lck_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class SuddenWall(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEA8",
            name="Sudden Wall",
            class_key=ExpertiseClass.Guardian,
            description="Deal 140-145 damage to an enemy, doubled if they're Sleeping.",
            flavor_text="",
            mana_cost=30,
            cooldown=0,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        sleeping_bonus: int = 1 if any(se.key == StatusEffectKey.Sleeping for se in caster.get_dueling().status_effects) else 0
        damage: int = int((sleeping_bonus + 1) * random.randint(140, 145))

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class DeeperFog(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF2B\uFE0F",
            name="Deeper Fog",
            class_key=ExpertiseClass.Guardian,
            description="Increase your damage dealt by 100% for 3 turns.",
            flavor_text="",
            mana_cost=15,
            cooldown=5,
            num_targets=0,
            level_requirement=20,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = DmgBuff(
            turns_remaining=3,
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

# -----------------------------------------------------------------------------
# NPC CLASS
# -----------------------------------------------------------------------------

class ChokingFog(NPC):
    def __init__(self, name_suffix: str=""):
        # Balance Simulation Results:
        # ?% chance of 4 player party (Lvl. 60-70) victory against 1
        # Avg Number of Turns (per entity): ?

        super().__init__("Choking Fog" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Mage, {})

        self._setup_npc_params()

    def _setup_inventory(self):
        if self._inventory is None:
            self._inventory = Inventory()

    def _setup_xp(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()
        
        self._expertise.add_xp_to_class_until_level(240, ExpertiseClass.Guardian)
        self._expertise.constitution = 70
        self._expertise.strength = 0
        self._expertise.dexterity = 40
        self._expertise.intelligence = 100
        self._expertise.luck = 27
        self._expertise.memory = 3

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.EncroachingFog))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [SuddenWall(), SappingCold(), DeeperFog()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Choking Fog"
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
