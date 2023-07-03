from __future__ import annotations

from math import ceil
from uuid import uuid4

from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Attribute, Expertise, ExpertiseClass
from features.inventory import Inventory
from features.npcs.npc import NPC, NPCDuelingPersonas, NPCRoles
from features.shared.ability import Ability
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, ItemKey
from features.shared.statuseffect import ConBuff, DexBuff, StrBuff, TurnSkipChance
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player
    from features.shared.ability import NegativeAbilityResult

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class Slam(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA5",
            name="Slam",
            class_key=ExpertiseClass.Guardian,
            description="Deal 20-30 damage and cause Faltering on 1-2 enemies for 1 turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=2,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        
        debuff = TurnSkipChance(
            turns_remaining=1,
            value=1,
            source_str=self.get_icon_and_name()
        )

        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(20, 30), [debuff])

        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class Ram(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="Ram",
            class_key=ExpertiseClass.Guardian,
            description="Increase your Con, Dex, and Str by 4 for the rest of the duel.",
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
        con_buff = ConBuff(
            turns_remaining=-1,
            value=4,
            source_str=self.get_icon_and_name()
        )

        dex_buff = DexBuff(
            turns_remaining=-1,
            value=4,
            source_str=self.get_icon_and_name()
        )

        str_buff = StrBuff(
            turns_remaining=-1,
            value=4,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [con_buff, str_buff, dex_buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class Wham(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC1F",
            name="Wham",
            class_key=ExpertiseClass.Guardian,
            description="Deal damage an enemy equal to 16% of your remaining health.",
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
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        damage = ceil(caster.get_expertise().hp * 0.16)
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))

        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# NPC CLASS
# -----------------------------------------------------------------------------

class Titanfish(NPC):
    def __init__(self, name_suffix: str=""):
        # Balance Simulation Results:
        # 28% chance of 4 player party (Lvl. 30-40) victory against 1
        # Avg Number of Turns (per entity): 9

        super().__init__("Titanfish" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Bruiser, {
            ItemKey.Titanfish: 0.7
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
        
        self._expertise.add_xp_to_class_until_level(145, ExpertiseClass.Guardian)
        self._expertise.constitution = 90
        self._expertise.strength = 25
        self._expertise.dexterity = 0
        self._expertise.intelligence = 0
        self._expertise.luck = 7
        self._expertise.memory = 3

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.TitanicMaw))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.ChestArmor, LOADED_ITEMS.get_new_item(ItemKey.TitanfishForm))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [Slam(), Ram(), Wham()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Titanfish"
        self._role = NPCRoles.DungeonEnemy
        self._dueling_persona = NPCDuelingPersonas.Bruiser
        self._dueling_rewards = {
            ItemKey.Titanfish: 0.7
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
