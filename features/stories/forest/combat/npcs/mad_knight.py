from __future__ import annotations

from uuid import uuid4

from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Attribute, Expertise, ExpertiseClass
from features.inventory import Inventory
from features.npcs.npc import NPC, NPCDuelingPersonas, NPCRoles
from features.shared.ability import Ability, SecondWindII, WhirlwindII
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, ItemKey
from features.shared.statuseffect import DexDebuff, IntDebuff, StrDebuff
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player
    from features.shared.ability import NegativeAbilityResult

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class WildStrike(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2694\uFE0F",
            name="Wild Strike",
            class_key=ExpertiseClass.Guardian,
            description="Recklessly attack an enemy, dealing 20-30 damage to it and yourself.",
            flavor_text="",
            mana_cost=5,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"

        damage = range(20, 30)
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, damage)

        self_damage_result: List[NegativeAbilityResult] = self._use_damage_ability(caster, [caster], damage)
        self_damage_result_str: str = self_damage_result[0].target_str.replace("{1}", "{0}")

        result_str += "\n".join(list(map(lambda x: x.target_str, results)))
        result_str += f"\n{self_damage_result_str}"

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        # This is a bit of a hack to ignore the state being passed in and
        # use the defaults in init since no state vars are ever needed.
        self.__init__() # type: ignore


class MaddeningScream(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDDEF\uFE0F",
            name="Maddening Scream",
            class_key=ExpertiseClass.Guardian,
            description="Decrease all enemies' Strength, Intelligence, and Dexterity by 5 for 3 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=1,
            num_targets=-1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        int_debuff = IntDebuff(
            turns_remaining=3,
            value=-5,
            source_str=self.get_icon_and_name()
        )

        str_debuff = StrDebuff(
            turns_remaining=3,
            value=-5,
            source_str=self.get_icon_and_name()
        )

        dex_debuff = DexDebuff(
            turns_remaining=3,
            value=-5,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [int_debuff, str_debuff, dex_debuff])
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

class MadKnight(NPC):
    def __init__(self, name_suffix: str=""):
        super().__init__("Mad Knight" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Bruiser, {
            ItemKey.IronGreatsword: 0.3,
            ItemKey.LesserHealthPotion: 0.1,
            ItemKey.Leather: 0.4,
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
        
        self._expertise.add_xp_to_class_until_level(80, ExpertiseClass.Guardian)
        self._expertise.constitution = 40
        self._expertise.strength = 30
        self._expertise.dexterity = 0
        self._expertise.intelligence = 0
        self._expertise.luck = 6
        self._expertise.memory = 4

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.CleaverOfReverberation))

        self._equipment.equip_item_to_slot(ClassTag.Equipment.Helmet, LOADED_ITEMS.get_new_item(ItemKey.AmberitePlateHelmet))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.Gloves, LOADED_ITEMS.get_new_item(ItemKey.AmberitePlateGauntlets))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.ChestArmor, LOADED_ITEMS.get_new_item(ItemKey.AmberitePlateCuirass))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.Leggings, LOADED_ITEMS.get_new_item(ItemKey.AmberitePlateLeggings))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.Boots, LOADED_ITEMS.get_new_item(ItemKey.AmberitePlateGreaves))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [SecondWindII(), WildStrike(), MaddeningScream(), WhirlwindII()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Mad Knight"
        self._role = NPCRoles.DungeonEnemy
        self._dueling_persona = NPCDuelingPersonas.Bruiser
        self._dueling_rewards = {
            ItemKey.IronGreatsword: 0.6,
            ItemKey.LesserHealthPotion: 0.2,
            ItemKey.Leather: 0.8,
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
