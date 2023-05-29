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
from features.shared.statuseffect import Bleeding, DexBuff, DexDebuff, LckBuff, StatusEffectKey
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
            description="Deal 30-35 damage with a 75% chance to cause Bleeding for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(30, 35))
        
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


class Dash(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="Dash",
            class_key=ExpertiseClass.Guardian,
            description="Increase your Dexterity and Luck by 50 for 4 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=0,
            level_requirement=20,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        lck_buff = LckBuff(
            turns_remaining=4,
            value=50,
            source_str=self.get_icon_and_name()
        )

        dex_buff = DexBuff(
            turns_remaining=4,
            value=50,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [lck_buff, dex_buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ScentForBlood(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE78",
            name="Scent for Blood",
            class_key=ExpertiseClass.Guardian,
            description="Decrease the Dexterity of all enemies with Bleeding by 15 for 3 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=1,
            num_targets=-1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_debuff = DexDebuff(
            turns_remaining=3,
            value=15,
            source_str=self.get_icon_and_name()
        )

        filtered_targets = [target for target in targets if any(se.key == StatusEffectKey.Bleeding for se in target.get_dueling().status_effects)]

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, filtered_targets, [dex_debuff])
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

class ShallowsShark(NPC):
    def __init__(self, name_suffix: str=""):
        # Balance Simulation Results:
        # 47% chance of 4 player party (Lvl. 30-40) victory against 2
        
        super().__init__("Shallows Shark" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Bruiser, {
            ItemKey.Shark: 0.85,
            ItemKey.IronSpear: 0.05
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
        
        self._expertise.add_xp_to_class_until_level(120, ExpertiseClass.Guardian)
        self._expertise.constitution = 40
        self._expertise.strength = 20
        self._expertise.dexterity = 20
        self._expertise.intelligence = 0
        self._expertise.luck = 37
        self._expertise.memory = 3

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.SharkTeeth))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.ChestArmor, LOADED_ITEMS.get_new_item(ItemKey.SharkScales))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [Dash(), SavageBite(), ScentForBlood()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Shallows Shark"
        self._role = NPCRoles.DungeonEnemy
        self._dueling_persona = NPCDuelingPersonas.Bruiser
        self._dueling_rewards = {
            ItemKey.Shark: 0.85,
            ItemKey.IronSpear: 0.05
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
