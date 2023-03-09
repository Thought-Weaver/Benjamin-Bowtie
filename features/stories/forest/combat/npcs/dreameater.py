from __future__ import annotations

from math import ceil
from uuid import uuid4

from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Attribute, Expertise, ExpertiseClass
from features.inventory import Inventory
from features.npcs.npc import NPC, NPCDuelingPersonas, NPCRoles
from features.shared.ability import Ability
from features.shared.constants import STR_DMG_SCALE
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, ItemKey, WeaponStats
from features.shared.statuseffect import DexBuff, DexDebuff, DmgReduction, StrBuff, StrDebuff, TurnSkipChance
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player
    from features.shared.ability import NegativeAbilityResult

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class Siphon(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD73",
            name="Siphon",
            class_key=ExpertiseClass.Fisher,
            description="Reduce a target's Dexterity and Strength by 2 and increase your own by the same amount for the rest of the duel.",
            flavor_text="",
            mana_cost=5,
            cooldown=1,
            num_targets=1,
            level_requirement=100,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = []

        dex_debuff = DexDebuff(
            turns_remaining=-1,
            value=-2,
            source_str=self.get_icon_and_name()
        )

        str_debuff = StrDebuff(
            turns_remaining=-1,
            value=-2,
            source_str=self.get_icon_and_name()
        )

        results += self._use_negative_status_effect_ability(caster, targets, [dex_debuff, str_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        dex_buff = DexBuff(
            turns_remaining=-1,
            value=2,
            source_str=self.get_icon_and_name()
        )

        str_buff = StrBuff(
            turns_remaining=-1,
            value=2,
            source_str=self.get_icon_and_name()
        )

        buff_result = self._use_positive_status_effect_ability(caster, [caster], [dex_buff, str_buff])
        buff_result = [s.replace("{1}", "{0}") for s in buff_result]
        result_str += "\n" + "\n".join(buff_result)

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class SharedSuffering(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC65",
            name="Shared Suffering",
            class_key=ExpertiseClass.Fisher,
            description="Reduce all enemies' health to the percent of the lowest health enemy.",
            flavor_text="",
            mana_cost=0,
            cooldown=8,
            num_targets=-1,
            level_requirement=100,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = []

        lowest_percent = min([entity.get_expertise().hp / entity.get_expertise().max_hp for entity in targets])

        for target in targets:
            damage = max(0, target.get_expertise().hp - int(lowest_percent * target.get_expertise().max_hp))
            target_result = self._use_damage_ability(caster, [target], range(damage, damage))
            results += target_result

        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class Formless(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="Formless",
            class_key=ExpertiseClass.Fisher,
            description="Gain +5 Dexterity for the rest of the duel.",
            flavor_text="",
            mana_cost=10,
            cooldown=3,
            num_targets=0,
            level_requirement=100,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=-1,
            value=5,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class Rending(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA5",
            name="Rending",
            class_key=ExpertiseClass.Fisher,
            description="Deal damage to all enemies equal to 10% max health of the enemy with the lowest max health.",
            flavor_text="",
            mana_cost=25,
            cooldown=5,
            num_targets=-1,
            level_requirement=100,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"

        damage = int(0.1 * min([entity.get_expertise().max_hp for entity in targets]))

        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class Deterioration(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCAB",
            name="Deterioration",
            class_key=ExpertiseClass.Fisher,
            description="Deal damage to all enemies equal to twice the number of status effects they have.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=-1,
            level_requirement=100,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = []

        for target in targets:
            damage = int(2 * len(target.get_dueling().status_effects))
            target_result = self._use_damage_ability(caster, [target], range(damage, damage))
            results += target_result

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

class Dreameater(NPC):
    def __init__(self):
        super().__init__("Dreameater", NPCRoles.DungeonEnemy, NPCDuelingPersonas.Mage, {
            ItemKey.MemoryOfVictory: 1
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
        
        self._expertise.add_xp_to_class_until_level(100, ExpertiseClass.Fisher)
        self._expertise.constitution = 40
        self._expertise.strength = 0
        self._expertise.dexterity = 10
        self._expertise.intelligence = 35
        self._expertise.luck = 10
        self._expertise.memory = 5

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.DreameatersGrasp))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [Siphon(), SharedSuffering(), Formless(), Rending(), Deterioration()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Dreameater"
        self._role = NPCRoles.DungeonEnemy
        self._dueling_persona = NPCDuelingPersonas.Mage
        self._dueling_rewards = {
            ItemKey.MemoryOfVictory: 1
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
