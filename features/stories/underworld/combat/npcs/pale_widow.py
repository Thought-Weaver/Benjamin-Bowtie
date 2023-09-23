from __future__ import annotations

from uuid import uuid4

from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Attribute, Expertise, ExpertiseClass
from features.inventory import Inventory
from features.npcs.npc import NPC, NPCDuelingPersonas, NPCRoles
from features.shared.ability import Ability
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, ItemKey
from features.shared.statuseffect import DmgReduction, StatusEffectKey
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player
    from features.shared.ability import NegativeAbilityResult

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class AccumulatingVenom(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2620\uFE0F",
            name="Accumulating Venom",
            class_key=ExpertiseClass.Alchemist,
            description="Double the time remaining on all enemy Poisoned status effects.",
            flavor_text="",
            mana_cost=20,
            cooldown=1,
            num_targets=-1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        for target in targets:
            for se in target.get_dueling().status_effects:
                if se.key == StatusEffectKey.Poisoned:
                    se.turns_remaining *= 2

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\nThe time remaining on all enemy Poisoned statuses has been doubled."

        self.remove_mana_and_set_cd(caster)

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class CripplingToxin(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD77\uFE0F",
            name="Crippling Toxin",
            class_key=ExpertiseClass.Alchemist,
            description="Strike with your fangs, dealing damage to an enemy equal to 10x the total time remaining on their Poisoned stacks.",
            flavor_text="",
            mana_cost=0,
            cooldown=0,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage: int = 10 * sum(se.turns_remaining for se in targets[0].get_dueling().status_effects if se.key == StatusEffectKey.Poisoned)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}, dealing damage proportional to the stacks of Poisoned on " + "{1}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class GhostlyMovement(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="Ghostly Movement",
            class_key=ExpertiseClass.Alchemist,
            description="Shift in and out of the shadows, increasing your damage resistance by 40% for 3 turns.",
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
        buff = DmgReduction(
            turns_remaining=3,
            value=0.4,
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

class PaleWidow(NPC):
    def __init__(self, name_suffix: str=""):
        # Balance Simulation Results:
        # 31% chance of 4 player party (Lvl. 60-70) victory against 2
        # Avg Number of Turns (per entity): 9

        super().__init__("Pale Widow" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Mage, {})

        self._setup_npc_params()

    def _setup_inventory(self):
        if self._inventory is None:
            self._inventory = Inventory()

    def _setup_xp(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()
        
        self._expertise.add_xp_to_class_until_level(140, ExpertiseClass.Alchemist)
        self._expertise.constitution = 50
        self._expertise.strength = 0
        self._expertise.dexterity = 30
        self._expertise.intelligence = 40
        self._expertise.luck = 17
        self._expertise.memory = 3

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.PaleWidowMandibles))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [AccumulatingVenom(), CripplingToxin(), GhostlyMovement()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Pale Widow"
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
