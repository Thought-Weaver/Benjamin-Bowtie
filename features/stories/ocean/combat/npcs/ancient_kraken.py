from __future__ import annotations

from math import ceil

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
from features.shared.statuseffect import DmgDebuff, FixedDmgTick, TurnSkipChance
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player
    from features.shared.ability import NegativeAbilityResult

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class Grapple(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDD91",
            name="Grapple",
            class_key=ExpertiseClass.Fisher,
            description="Grapple 1-2 enemies, Faltering them for 3 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=6,
            num_targets=2,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        turn_skip_chance = TurnSkipChance(
            turns_remaining=3,
            value=1,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [turn_skip_chance])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class DevastatingCurrent(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEE7",
            name="Devastating Current",
            class_key=ExpertiseClass.Fisher,
            description="Deal 90-95 damage to an enemy and 50% of the base damage again next turn.",
            flavor_text="",
            mana_cost=25,
            cooldown=3,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"

        damage = random.randint(90, 95)
        debuff = FixedDmgTick(
            turns_remaining=1,
            value=ceil(0.5 * damage),
            source_str=self.get_icon_and_name()
        )

        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(damage, damage), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class Behold(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF0C",
            name="Behold",
            class_key=ExpertiseClass.Fisher,
            description="Decrease the damage all enemies deal by 25% for 4 turns.",
            flavor_text="",
            mana_cost=40,
            cooldown=8,
            num_targets=-1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = DmgDebuff(
            turns_remaining=4,
            value=0.25,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# NPC CLASS
# -----------------------------------------------------------------------------

class AncientKraken(NPC):
    def __init__(self, name_suffix: str=""):
        # Balance Simulation Results:
        # 38% chance of 4 player party (Lvl. 50-60) victory against 1
        # 25% and 11 turns for new item adjustments
        # Avg Number of Turns (per entity): 12

        super().__init__("Ancient Kraken" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Mage, {
            ItemKey.Squid: 0.9,
            ItemKey.Squid: 0.7,
            ItemKey.Squid: 0.5,
            ItemKey.Squid: 0.3,
            ItemKey.Squid: 0.1,
            ItemKey.KrakenEye: 0.1
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
        
        self._expertise.add_xp_to_class_until_level(380, ExpertiseClass.Fisher)
        self._expertise.constitution = 180
        self._expertise.strength = 0
        self._expertise.dexterity = 20
        self._expertise.intelligence = 130
        self._expertise.luck = 47
        self._expertise.memory = 3

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.AncientKrakenTentacles))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.ChestArmor, LOADED_ITEMS.get_new_item(ItemKey.AncientKrakenForm))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [Behold(), Grapple(), DevastatingCurrent()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Ancient Kraken"
        self._role = NPCRoles.DungeonEnemy
        self._dueling_persona = NPCDuelingPersonas.Mage
        self._dueling_rewards = {
            ItemKey.Squid: 0.9,
            ItemKey.Squid: 0.7,
            ItemKey.Squid: 0.5,
            ItemKey.Squid: 0.3,
            ItemKey.Squid: 0.1,
            ItemKey.KrakenEye: 0.1
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
