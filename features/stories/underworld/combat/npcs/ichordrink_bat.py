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
from features.shared.statuseffect import DexBuff, IntDebuff, StrDebuff
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player
    from features.shared.ability import NegativeAbilityResult

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class Screech(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDD87",
            name="Screech",
            class_key=ExpertiseClass.Guardian,
            description="Create a devastating noise that decreases the Str and Int of all enemies by 30 for 3 turns.",
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
            turns_remaining=3,
            value=-30,
            source_str=self.get_icon_and_name()
        )

        int_debuff = IntDebuff(
            turns_remaining=3,
            value=-30,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [str_debuff, int_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class Siphon(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE78",
            name="Siphon",
            class_key=ExpertiseClass.Guardian,
            description="Drink deeply and steal 40% of an enemy's max health.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"

        damage = int(0.4 * targets[0].get_expertise().max_hp)

        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        heal_results: List[str] = self._use_heal_ability(caster, [caster], range(damage, damage))

        result_str += "\n".join(list(map(lambda x: x.target_str, results)))
        result_str += "\n"
        result_str += "\n".join([s.replace("{1}", "{0}") for s in heal_results])

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class Dive(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="Dive",
            class_key=ExpertiseClass.Guardian,
            description="Move swiftly and increase your Dex by 100 for 2 turns.",
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
        buff = DexBuff(
            turns_remaining=2,
            value=100,
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

class IchordrinkBat(NPC):
    def __init__(self, name_suffix: str=""):
        # Balance Simulation Results:
        # 51% chance of 4 player party (Lvl. 60-70) victory against 2
        # Avg Number of Turns (per entity): 23

        super().__init__("Ichordrink Bat" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Mage, {
            ItemKey.BlendedIchor: 0.9,
            ItemKey.BlendedIchor: 0.5
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
        
        self._expertise.add_xp_to_class_until_level(150, ExpertiseClass.Guardian)
        self._expertise.constitution = 90
        self._expertise.strength = 0
        self._expertise.dexterity = 40
        self._expertise.intelligence = 0
        self._expertise.luck = 17
        self._expertise.memory = 3

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.IchordrinkFangs))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.ChestArmor, LOADED_ITEMS.get_new_item(ItemKey.BatForm))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [Siphon(), Dive(), Screech()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Ichordrink Bat"
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
