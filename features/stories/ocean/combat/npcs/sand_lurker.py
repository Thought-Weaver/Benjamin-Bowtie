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
from features.shared.statuseffect import DexBuff, LckBuff
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player
    from features.shared.ability import NegativeAbilityResult

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class Burrow(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD73\uFE0F",
            name="Burrow",
            class_key=ExpertiseClass.Guardian,
            description="Increase your Dex by 150 for 3 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=6,
            num_targets=0,
            level_requirement=20,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=3,
            value=150,
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


class LurkerStrike(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDD88",
            name="Lurker Strike",
            class_key=ExpertiseClass.Guardian,
            description="Deal damage equal to 2x your total Dexterity to an enemy.",
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
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        damage = int(2 * caster.get_combined_attributes().dexterity)
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class SurpriseAttack(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2757",
            name="Surprise Attack",
            class_key=ExpertiseClass.Guardian,
            description="Increase your Luck by 100 for 3 turns and deal 40-45 damage to a single target.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n" + "{0} is now Lucky\n"
        
        lck_buff = LckBuff(
            turns_remaining=3,
            value=100,
            source_str=self.get_icon_and_name()
        )
        caster.get_dueling().status_effects.append(lck_buff)
        
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(40, 45))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# NPC CLASS
# -----------------------------------------------------------------------------

class SandLurker(NPC):
    def __init__(self, name_suffix: str=""):
        # Balance Simulation Results:
        # 42% chance of 4 player party (Lvl. 40-50) victory against 1
        # Avg Number of Turns (per entity): 13

        super().__init__("Sand Lurker" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Mage, {
            ItemKey.SandLurkerTeeth: 0.8,
            ItemKey.SandLurker: 0.4
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
        
        self._expertise.add_xp_to_class_until_level(180, ExpertiseClass.Guardian)
        self._expertise.constitution = 100
        self._expertise.strength = 0
        self._expertise.dexterity = 20
        self._expertise.intelligence = 0
        self._expertise.luck = 38
        self._expertise.memory = 2

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.LurkerTeeth))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.ChestArmor, LOADED_ITEMS.get_new_item(ItemKey.LurkerForm))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [Burrow(), LurkerStrike(), SurpriseAttack()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Sand Lurker"
        self._role = NPCRoles.DungeonEnemy
        self._dueling_persona = NPCDuelingPersonas.Bruiser
        self._dueling_rewards = {
            ItemKey.SandLurkerTeeth: 0.8,
            ItemKey.SandLurker: 0.4
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
