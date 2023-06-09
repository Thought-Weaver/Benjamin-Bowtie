from __future__ import annotations

import random

from uuid import uuid4

from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Attribute, Expertise, ExpertiseClass
from features.inventory import Inventory
from features.npcs.npc import NPC, NPCDuelingPersonas, NPCRoles
from features.shared.ability import Ability
from features.shared.constants import BLEED_PERCENT_HP
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, ItemKey
from features.shared.statuseffect import Bleeding, DexBuff, DmgBuff, DmgDebuff, StrBuff
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player
    from features.shared.ability import NegativeAbilityResult

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class SavageBite(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE78",
            name="Savage Bite",
            class_key=ExpertiseClass.Guardian,
            description="Deal 25-30 damage with a 75% chance to cause Bleeding for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(25, 30))
        
        bleed = Bleeding(
            turns_remaining=2,
            value=BLEED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged and random.random() < 0.75:
                se_str = targets[i].get_dueling().add_status_effect_with_resist(bleed, targets[i], i + 1)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
                results[i].target_str += f" and {se_str}"
                
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class PackTactics(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC3A",
            name="Pack Tactics",
            class_key=ExpertiseClass.Guardian,
            description="All allies gain a 15% damage bonus, +8 Strength, and +5 Dexterity for 3 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=1,
            num_targets=-1,
            level_requirement=20,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dmg_buff = DmgBuff(
            turns_remaining=3,
            value=0.15,
            source_str=self.get_icon_and_name()
        )

        str_buff = StrBuff(
            turns_remaining=3,
            value=8,
            source_str=self.get_icon_and_name()
        )

        dex_buff = DexBuff(
            turns_remaining=3,
            value=5,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dmg_buff, str_buff, dex_buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class Snarl(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDDEF\uFE0F",
            name="Snarl",
            class_key=ExpertiseClass.Guardian,
            description="Decrease the damage all enemies deal by 25% for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=-1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dmg_debuff = DmgDebuff(
            turns_remaining=2,
            value=0.25,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [dmg_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# NPC CLASS
# -----------------------------------------------------------------------------

class StarvingDireWolf(NPC):
    def __init__(self, name_suffix: str=""):
        # Balance Simulation Results:
        # 20% chance of 4 player party (Lvl. 20-30) victory against 2

        super().__init__("Starving Dire Wolf" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Bruiser, {
            ItemKey.Bones: 0.85,
            ItemKey.Bones: 0.6,
            ItemKey.RawWolfMeat: 0.4
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
        
        self._expertise.add_xp_to_class_until_level(110, ExpertiseClass.Guardian)
        self._expertise.constitution = 55
        self._expertise.strength = 25
        self._expertise.dexterity = 10
        self._expertise.intelligence = 0
        self._expertise.luck = 17
        self._expertise.memory = 3

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.DireWolfCanines))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [PackTactics(), SavageBite(), Snarl()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Starving Dire Wolf"
        self._role = NPCRoles.DungeonEnemy
        self._dueling_persona = NPCDuelingPersonas.Bruiser
        self._dueling_rewards = {
            ItemKey.Bones: 0.85,
            ItemKey.Bones: 0.6,
            ItemKey.RawWolfMeat: 0.9
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
