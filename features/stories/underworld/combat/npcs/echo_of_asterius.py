from __future__ import annotations

from uuid import uuid4

from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Attribute, Expertise, ExpertiseClass
from features.inventory import Inventory
from features.npcs.npc import NPC, NPCDuelingPersonas, NPCRoles
from features.shared.ability import Ability, NegativeAbilityResult
from features.shared.constants import BLEED_PERCENT_HP
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, ItemKey
from features.shared.statuseffect import Bleeding, ConBuff, DexBuff, StrBuff
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class SweepingStrike(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2694\uFE0F",
            name="Sweeping Strike",
            class_key=ExpertiseClass.Guardian,
            description="Deal 120-130 damage to all enemies and cause Bleeding for 4 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=-1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = Bleeding(
            turns_remaining=4,
            value=BLEED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(90, 100), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class HeroicDash(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="Heroic Dash",
            class_key=ExpertiseClass.Guardian,
            description="Increase your Dex, Str, and Con by 25 for 4 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=8,
            num_targets=0,
            level_requirement=20,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=4,
            value=25,
            source_str=self.get_icon_and_name()
        )

        str_buff = StrBuff(
            turns_remaining=4,
            value=25,
            source_str=self.get_icon_and_name()
        )

        con_buff = ConBuff(
            turns_remaining=4,
            value=25,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff, str_buff, con_buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class AllIn(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA5",
            name="All In",
            class_key=ExpertiseClass.Guardian,
            description="Deal damage to an enemy equal to your combined stats.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage: int = sum(attr for attr in caster.get_combined_attributes().to_lst())

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}, dealing damage proportional to his combined stats!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
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

class EchoOfAsterius(NPC):
    def __init__(self, name_suffix: str=""):
        # Balance Simulation Results:
        # ?% chance of 4 player party (Lvl. 80-90) victory against 1 + Yenna + Passerhawk
        # Avg Number of Turns (per entity): ?

        super().__init__("Echo of Asterius" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Bruiser, {
            ItemKey.CuirassOfTheEyelessGuardian: 0.01,
            ItemKey.SwordOfTheEyelessGuardian: 0.01
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
        
        self._expertise.add_xp_to_class_until_level(300, ExpertiseClass.Guardian)
        self._expertise.constitution = 150
        self._expertise.strength = 50
        self._expertise.dexterity = 50
        self._expertise.intelligence = 0
        self._expertise.luck = 47
        self._expertise.memory = 3

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.SwordOfTheEyelessGuardian))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.ChestArmor, LOADED_ITEMS.get_new_item(ItemKey.CuirassOfTheEyelessGuardian))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [SweepingStrike(), HeroicDash(), AllIn()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Echo of Asterius"
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
