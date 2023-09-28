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
from features.shared.statuseffect import CannotAttack, CannotUseAbilities, ConBuff, ConDebuff, DexBuff, DexDebuff, DmgReduction, IntBuff, IntDebuff, LckBuff, LckDebuff, StatusEffectKey, StrBuff, StrDebuff
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player
    from features.shared.ability import NegativeAbilityResult

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class ConfusingPaths(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2753",
            name="Confusing Paths",
            class_key=ExpertiseClass.Alchemist,
            description="Swap the stats of two enemies for for the rest of the duel.",
            flavor_text="",
            mana_cost=30,
            cooldown=8,
            num_targets=2,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        if len(targets) < 2:
            return "{0}" + f" was unable to use {self.get_icon_and_name()}!"

        first_target = targets[0]
        second_target = targets[1]

        con_debuff_1 = ConDebuff(
            turns_remaining=-1,
            value=-first_target.get_expertise().constitution,
            source_str=self.get_icon_and_name()
        )
        str_debuff_1 = StrDebuff(
            turns_remaining=-1,
            value=-first_target.get_expertise().strength,
            source_str=self.get_icon_and_name()
        )
        dex_debuff_1 = DexDebuff(
            turns_remaining=-1,
            value=-first_target.get_expertise().dexterity,
            source_str=self.get_icon_and_name()
        )
        int_debuff_1 = IntDebuff(
            turns_remaining=-1,
            value=-first_target.get_expertise().intelligence,
            source_str=self.get_icon_and_name()
        )
        lck_debuff_1 = LckDebuff(
            turns_remaining=-1,
            value=-first_target.get_expertise().luck,
            source_str=self.get_icon_and_name()
        )
        
        con_debuff_2 = ConDebuff(
            turns_remaining=-1,
            value=-second_target.get_expertise().constitution,
            source_str=self.get_icon_and_name()
        )
        str_debuff_2 = StrDebuff(
            turns_remaining=-1,
            value=-second_target.get_expertise().strength,
            source_str=self.get_icon_and_name()
        )
        dex_debuff_2 = DexDebuff(
            turns_remaining=-1,
            value=-second_target.get_expertise().dexterity,
            source_str=self.get_icon_and_name()
        )
        int_debuff_2 = IntDebuff(
            turns_remaining=-1,
            value=-second_target.get_expertise().intelligence,
            source_str=self.get_icon_and_name()
        )
        lck_debuff_2 = LckDebuff(
            turns_remaining=-1,
            value=-second_target.get_expertise().luck,
            source_str=self.get_icon_and_name()
        )

        con_buff_1 = ConBuff(
            turns_remaining=-1,
            value=first_target.get_expertise().constitution,
            source_str=self.get_icon_and_name()
        )
        str_buff_1 = StrBuff(
            turns_remaining=-1,
            value=first_target.get_expertise().strength,
            source_str=self.get_icon_and_name()
        )
        dex_buff_1 = DexBuff(
            turns_remaining=-1,
            value=first_target.get_expertise().dexterity,
            source_str=self.get_icon_and_name()
        )
        int_buff_1 = IntBuff(
            turns_remaining=-1,
            value=first_target.get_expertise().intelligence,
            source_str=self.get_icon_and_name()
        )
        lck_buff_1 = LckBuff(
            turns_remaining=-1,
            value=second_target.get_expertise().luck,
            source_str=self.get_icon_and_name()
        )

        con_buff_2 = ConBuff(
            turns_remaining=-1,
            value=second_target.get_expertise().constitution,
            source_str=self.get_icon_and_name()
        )
        str_buff_2 = StrBuff(
            turns_remaining=-1,
            value=second_target.get_expertise().strength,
            source_str=self.get_icon_and_name()
        )
        dex_buff_2 = DexBuff(
            turns_remaining=-1,
            value=second_target.get_expertise().dexterity,
            source_str=self.get_icon_and_name()
        )
        int_buff_2 = IntBuff(
            turns_remaining=-1,
            value=second_target.get_expertise().intelligence,
            source_str=self.get_icon_and_name()
        )
        lck_buff_2 = LckBuff(
            turns_remaining=-1,
            value=second_target.get_expertise().luck,
            source_str=self.get_icon_and_name()
        )

        first_target.get_dueling().status_effects += [
            con_debuff_1, str_debuff_1, dex_debuff_1, int_debuff_1, lck_debuff_1,
            con_buff_2, str_buff_2, dex_buff_2, int_buff_2, lck_buff_2
        ]
        second_target.get_dueling().status_effects += [
            con_debuff_2, str_debuff_2, dex_debuff_2, int_debuff_2, lck_debuff_2,
            con_buff_1, str_buff_1, dex_buff_1, int_buff_1, lck_buff_1
        ]

        first_target.get_expertise().update_stats(first_target.get_combined_attributes())
        second_target.get_expertise().update_stats(second_target.get_combined_attributes())

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n" + "{1} and {2} have had their stats swapped!"

        self.remove_mana_and_set_cd(caster)

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class DarkerAndDarker(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF11",
            name="Darker and Darker",
            class_key=ExpertiseClass.Alchemist,
            description="Set Atrophied and Enfeebled on all enemies for 3 turns.",
            flavor_text="",
            mana_cost=20,
            cooldown=5,
            num_targets=-1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        atrophied_debuff = CannotAttack(
            turns_remaining=3,
            value=1,
            source_str=self.get_icon_and_name()
        )

        enfeebled_debuff = CannotUseAbilities(
            turns_remaining=3,
            value=1,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [atrophied_debuff, enfeebled_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class NowhereToTurn(Ability):
    def __init__(self):
        super().__init__(
            icon="\u21AA\uFE0F",
            name="Nowhere to Turn",
            class_key=ExpertiseClass.Alchemist,
            description="Deal damage to an enemy equal to 50x the number of status effects they have.",
            flavor_text="",
            mana_cost=10,
            cooldown=0,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength, Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage = int(50 * len(targets[0].get_dueling().status_effects))

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}, dealing damage based on the number of status effects" + " {1} has!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# NPC CLASS
# -----------------------------------------------------------------------------

class WindingTunnels(NPC):
    def __init__(self, name_suffix: str=""):
        # Balance Simulation Results:
        # 61% chance of 4 player party (Lvl. 60-70) victory against 1
        # Avg Number of Turns (per entity): 10

        super().__init__("Winding Tunnels" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Mage, {
            ItemKey.PileOfCoins: 0.7,
            ItemKey.BagOfCoins: 0.1,
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
        
        self._expertise.add_xp_to_class_until_level(200, ExpertiseClass.Alchemist)
        self._expertise.constitution = 110
        self._expertise.strength = 30
        self._expertise.dexterity = 0
        self._expertise.intelligence = 40
        self._expertise.luck = 17
        self._expertise.memory = 3

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.BranchingPaths))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [ConfusingPaths(), DarkerAndDarker(), NowhereToTurn()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Winding Tunnels"
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
