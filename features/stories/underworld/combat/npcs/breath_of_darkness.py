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
from features.shared.statuseffect import ConDebuff, StatusEffectKey
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player
    from features.shared.ability import NegativeAbilityResult

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class ForceBackwards(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD19",
            name="Force Backwards",
            class_key=ExpertiseClass.Guardian,
            description="Duplicates a random fixed damage tick on all enemies.",
            flavor_text="",
            mana_cost=10,
            cooldown=2,
            num_targets=-1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        for target in targets:
            fixed_dmg_ticks = [se for se in target.get_dueling().status_effects if se.key == StatusEffectKey.FixedDmgTick]
            if len(fixed_dmg_ticks) > 0:
                rand_tick = random.choice(fixed_dmg_ticks)
                target.get_dueling().status_effects.append(rand_tick)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\nA random fixed damage tick has been duplicated on each enemy!"

        self.remove_mana_and_set_cd(caster)

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class PuncturingDebris(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEA8",
            name="Puncturing Debris",
            class_key=ExpertiseClass.Guardian,
            description="Bits of debris go flying at all enemies, dealing 30-35 damage.",
            flavor_text="",
            mana_cost=15,
            cooldown=2,
            num_targets=-1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(30, 35))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class SensationOfWeakness(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDD40",
            name="Sensation of Weakness",
            class_key=ExpertiseClass.Guardian,
            description="Decrease all enemies' Con by 5 for the rest of the duel.",
            flavor_text="",
            mana_cost=20,
            cooldown=4,
            num_targets=-1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = ConDebuff(
            turns_remaining=-1,
            value=-5,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [debuff])
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

class BreathOfDarkness(NPC):
    def __init__(self, name_suffix: str=""):
        # Balance Simulation Results:
        # 11% chance of 4 player party (Lvl. 60-70) victory against 1
        # Avg Number of Turns (per entity): 9

        super().__init__("Breath of Darkness" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Mage, {})

        self._setup_npc_params()

    def _setup_inventory(self):
        if self._inventory is None:
            self._inventory = Inventory()

    def _setup_xp(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()
        
        self._expertise.add_xp_to_class_until_level(250, ExpertiseClass.Alchemist)
        self._expertise.constitution = 100
        self._expertise.strength = 40
        self._expertise.dexterity = 40
        self._expertise.intelligence = 60
        self._expertise.luck = 7
        self._expertise.memory = 3

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.BuffetingWinds))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [SensationOfWeakness(), PuncturingDebris(), ForceBackwards()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Breath of Darkness"
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
