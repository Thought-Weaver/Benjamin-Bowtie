import random

from uuid import uuid4

from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Attribute, Expertise, ExpertiseClass
from features.inventory import Inventory
from features.npcs.npc import NPC, NPCDuelingPersonas, NPCRoles
from features.shared.ability import Ability, BidedAttackIII, SecondWindIII
from features.shared.constants import BLEED_PERCENT_HP
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, ItemKey
from features.shared.statuseffect import Bleeding, TurnSkipChance
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player
    from features.shared.ability import NegativeAbilityResult

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class Gore(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE78",
            name="Gore",
            class_key=ExpertiseClass.Guardian,
            description="Deal 10-15 damage with a 75% chance to cause Bleeding for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(5, 6))
        
        bleed = Bleeding(
            turns_remaining=2,
            value=BLEED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged and random.random() < 0.75:
                se_str = targets[i].get_dueling().add_status_effect_with_resist(bleed, targets[i], i + 1)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
                results[i].target_str += f" and {se_str}"
                
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class Charge(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD31",
            name="Charge",
            class_key=ExpertiseClass.Guardian,
            description="Deal 5-10 damage and cause Faltering with a 50% chance for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = TurnSkipChance(
            turns_remaining=2,
            value=0.5,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(5, 6), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# NPC CLASS
# -----------------------------------------------------------------------------

class WildBoar(NPC):
    def __init__(self):
        super().__init__("Wild Boar", NPCRoles.DungeonEnemy, NPCDuelingPersonas.Bruiser, {
            ItemKey.Bones: 0.85,
            ItemKey.RawBoarMeat: 1,
            ItemKey.IronDagger: 0.1,
            ItemKey.IronSpear: 0.05
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
        
        self._expertise.constitution = 11
        self._expertise.strength = 5
        self._expertise.dexterity = 5
        self._expertise.intelligence = 0
        self._expertise.luck = 0
        self._expertise.memory = 4

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.BoarTusks))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [Gore(), BidedAttackIII(), SecondWindIII(), Charge()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Wild Boar"
        self._role = NPCRoles.Companion
        self._dueling_persona = NPCDuelingPersonas.Bruiser
        self._dueling_rewards = {
            ItemKey.Bones: 0.85,
            ItemKey.RawBoarMeat: 1,
            ItemKey.IronDagger: 0.1,
            ItemKey.IronSpear: 0.05
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
