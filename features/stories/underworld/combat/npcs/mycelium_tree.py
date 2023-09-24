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
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player
    from features.shared.ability import NegativeAbilityResult

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class ManaBurn(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD25",
            name="Mana Burn",
            class_key=ExpertiseClass.Alchemist,
            description="Deal damage to an enemy equal to 125% of their current mana.",
            flavor_text="",
            mana_cost=100,
            cooldown=0,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage: int = int(1.25 * targets[0].get_expertise().mana)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}, dealing damage based on " + "{1}'s current mana!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class Wildspell(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2728",
            name="Wildspell",
            class_key=ExpertiseClass.Alchemist,
            description="Choose an enemy. Cast three random abilities they have that cost mana.",
            flavor_text="",
            mana_cost=0,
            cooldown=0,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}, casting three random abilities that use mana from " + "{1}'s abilities!\n\n"

        mana_based_abilities = [ability for ability in targets[0].get_dueling().abilities if ability.get_mana_cost() > 0]
        if len(mana_based_abilities) > 0:
            abilities = random.choices(mana_based_abilities, k=3)
            for ability in abilities:
                if ability.get_target_own_group():
                    result_self_str = ability.use_ability(caster, [caster])
                    if "{1}" in result_self_str:
                        result_self_str = result_self_str.replace("{1}", "{0}")
                        result_str += result_self_str + "\n\n"
                else:
                    result_str += ability.use_ability(caster, targets) + "\n\n"

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class UnstableReplenishment(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF00",
            name="Unstable Replenishment",
            class_key=ExpertiseClass.Alchemist,
            description="Restore 90% of your mana and deal the amount restored as damage to all enemies.",
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
        mana_to_restore: int = int(0.9 * caster.get_expertise().max_mana)
        org_mana = caster.get_expertise().mana
        caster.get_expertise().restore_mana(mana_to_restore)
        damage = caster.get_expertise().mana - org_mana

        result_str: str = "{0}" + f" used {self.get_icon_and_name()} and restored {damage} mana!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
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

class MyceliumTree(NPC):
    def __init__(self, name_suffix: str=""):
        # Balance Simulation Results:
        # 44% chance of 4 player party (Lvl. 70-80) victory against 1
        # Avg Number of Turns (per entity): 10

        super().__init__("Mycelium Tree" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Mage, {
            ItemKey.ManaSaturatedRoot: 0.7,
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
        
        self._expertise.add_xp_to_class_until_level(350, ExpertiseClass.Alchemist)
        self._expertise.constitution = 150
        self._expertise.strength = 0
        self._expertise.dexterity = 0
        self._expertise.intelligence = 140
        self._expertise.luck = 57
        self._expertise.memory = 3

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.MyceliumTendrils))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [ManaBurn(), Wildspell(), UnstableReplenishment()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Mycelium Tree"
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
