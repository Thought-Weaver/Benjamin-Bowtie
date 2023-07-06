from __future__ import annotations

from uuid import uuid4

from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Attribute, Expertise, ExpertiseClass
from features.inventory import Inventory
from features.npcs.npc import NPC, NPCDuelingPersonas, NPCRoles
from features.player import Player
from features.shared.ability import Ability
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, ItemKey
from features.shared.statuseffect import Charmed, ConDebuff, DexDebuff, IntDebuff, StrDebuff
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.shared.ability import NegativeAbilityResult

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class HorrifyingMaw(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDDB7",
            name="Horrifying Maw",
            class_key=ExpertiseClass.Fisher,
            description="Deal 90-100 damage to an enemy and decrease their Con by 5 for the rest of the duel.",
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

        debuff = ConDebuff(
            turns_remaining=-1,
            value=5,
            source_str=self.get_icon_and_name()
        )

        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(90, 100), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class GazeIntoTheBulb(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA1",
            name="Gaze Into the Bulb",
            class_key=ExpertiseClass.Fisher,
            description="Charm an enemy for 4 turns.",
            flavor_text="",
            mana_cost=20,
            cooldown=7,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = Charmed(
            turns_remaining=4,
            value=1,
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


class DontLook(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC41\uFE0F",
            name="Don't Look",
            class_key=ExpertiseClass.Fisher,
            description="Decrease the Str, Dex, and Int of all enemies by 10 for the rest of the duel.",
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
        str_debuff = StrDebuff(
            turns_remaining=-1,
            value=-10,
            source_str=self.get_icon_and_name()
        )

        dex_debuff = DexDebuff(
            turns_remaining=-1,
            value=-10,
            source_str=self.get_icon_and_name()
        )

        int_debuff = IntDebuff(
            turns_remaining=-1,
            value=-10,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [str_debuff, dex_debuff, int_debuff])
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

class VoidseenAngler(NPC):
    def __init__(self, name_suffix: str=""):
        # Balance Simulation Results:
        # 25% chance of 4 player party (Lvl. 50-60) victory against 1
        # Avg Number of Turns (per entity): 13

        super().__init__("Voidseen Angler" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Mage, {
            ItemKey.AnglerTeeth: 0.6,
            ItemKey.AnglerBulb: 0.1
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
        
        self._expertise.add_xp_to_class_until_level(400, ExpertiseClass.Fisher)
        self._expertise.constitution = 200
        self._expertise.strength = 60
        self._expertise.dexterity = 20
        self._expertise.intelligence = 60
        self._expertise.luck = 57
        self._expertise.memory = 3

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.AnglerMaw))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [GazeIntoTheBulb(), HorrifyingMaw(), DontLook()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Voidseen Angler"
        self._role = NPCRoles.DungeonEnemy
        self._dueling_persona = NPCDuelingPersonas.Mage
        self._dueling_rewards = {
            ItemKey.AnglerTeeth: 0.6,
            ItemKey.AnglerBulb: 0.1
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
