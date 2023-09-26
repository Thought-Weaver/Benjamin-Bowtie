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
from features.shared.statuseffect import DexBuff, DmgBuff, DmgReduction, FixedDmgTick, StrBuff
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player
    from features.shared.ability import NegativeAbilityResult

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class EchoingStrike(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2694\uFE0F",
            name="Echoing Strike",
            class_key=ExpertiseClass.Guardian,
            description="Deal 3x your max weapon damage to an enemy and that again every turn for 3 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=1,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        main_hand_item = caster.get_equipment().get_item_in_slot(ClassTag.Equipment.MainHand)
        damage: int = 1 if main_hand_item is None else (3 * main_hand_item.get_weapon_stats().get_max_damage()) # type: ignore

        debuff = FixedDmgTick(
            turns_remaining=3,
            value=damage,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(damage, damage), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class WarriorsCommand(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDD3A",
            name="Warrior's Command",
            class_key=ExpertiseClass.Guardian,
            description="Remember your duty, increasing your damage by 50% for 3 turns, as well as increasing your Str and Dex by 25 for 3 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=5,
            num_targets=0,
            level_requirement=20,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dmg_buff = DmgBuff(
            turns_remaining=3,
            value=0.5,
            source_str=self.get_icon_and_name()
        )

        str_buff = StrBuff(
            turns_remaining=3,
            value=25,
            source_str=self.get_icon_and_name()
        )

        dex_buff = DexBuff(
            turns_remaining=3,
            value=25,
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


class PhaseShift(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF2B\uFE0F",
            name="Phase Shift",
            class_key=ExpertiseClass.Guardian,
            description="Fade into the mist, increasing your Dex by 50 and granting you 75% damage protection for 3 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=7,
            num_targets=0,
            level_requirement=20,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        protection_buff = DmgReduction(
            turns_remaining=3,
            value=0.75,
            source_str=self.get_icon_and_name()
        )

        dex_buff = DexBuff(
            turns_remaining=3,
            value=50,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [protection_buff, dex_buff])
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

class TimelostEcho(NPC):
    def __init__(self, name_suffix: str=""):
        # Balance Simulation Results:
        # 18% chance of 4 player party (Lvl. 80-90) victory against 1
        # Avg Number of Turns (per entity): 15

        super().__init__("Timelost Echo" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Bruiser, {
            ItemKey.MemoryOfAWarrior: 0.9,
            ItemKey.SpectralSword: 0.01
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
        
        self._expertise.add_xp_to_class_until_level(350, ExpertiseClass.Guardian)
        self._expertise.constitution = 150
        self._expertise.strength = 80
        self._expertise.dexterity = 70
        self._expertise.intelligence = 0
        self._expertise.luck = 47
        self._expertise.memory = 3

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.SpectralSword))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [EchoingStrike(), WarriorsCommand(), PhaseShift()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Timelost Echo"
        self._role = NPCRoles.DungeonEnemy
        self._dueling_persona = NPCDuelingPersonas.Bruiser
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
