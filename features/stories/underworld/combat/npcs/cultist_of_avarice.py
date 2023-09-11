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
from features.shared.statuseffect import CannotAttack, CannotUseAbilities, DmgReduction, Generating, StatusEffectKey, Tarnished
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player
    from features.shared.ability import NegativeAbilityResult

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class HailTheEmissary(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDE4C",
            name="Hail the Emissary",
            class_key=ExpertiseClass.Merchant,
            description="Grant all allies 100% Tarnished and 100 Generating for 3 turns.",
            flavor_text="",
            mana_cost=40,
            cooldown=3,
            num_targets=-1,
            level_requirement=20,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        tarnished_buff = Tarnished(
            turns_remaining=3,
            value=1,
            source_str=self.get_icon_and_name()
        )

        generating_buff = Generating(
            turns_remaining=3,
            value=100,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [tarnished_buff, generating_buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class MustHaveMore(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE99",
            name="Must Have More",
            class_key=ExpertiseClass.Merchant,
            description="Steal 10% of an enemy's coins.",
            flavor_text="",
            mana_cost=20,
            cooldown=4,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n"

        for i, target in enumerate(targets):
            coins: int = int(0.1 * target.get_inventory().get_coins())
            target.get_inventory().remove_coins(coins)
            result_str += "\n{" + f"{i + 1}" + "} had " + f"{coins} stolen!"

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class RitualOfBlood(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE78",
            name="Ritual of Blood",
            class_key=ExpertiseClass.Merchant,
            description="Deal 100 piercing damage to yourself and generate 300 coins.",
            flavor_text="",
            mana_cost=20,
            cooldown=5,
            num_targets=0,
            level_requirement=20,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        caster.get_expertise().damage(100, caster.get_dueling(), 0, True)

        coins_to_add: int = 300
        caster.get_inventory().add_coins(coins_to_add)

        tarnished_value = 0
        for se in caster.get_dueling().status_effects:
            if se.key == StatusEffectKey.Tarnished:
                tarnished_value = se.value
        
        cursed_coins_damage = 0
        if tarnished_value != 0:
            cursed_coins_damage += int(tarnished_value * coins_to_add)

        result_str = "{0}" + f" used {self.get_icon_and_name()}!\n\n" + "{0}" + f" gained {coins_to_add} coins."

        if cursed_coins_damage != 0:
            for i, target in enumerate(targets):
                org_armor = target.get_dueling().armor
                percent_dmg_reduct = target.get_dueling().get_total_percent_dmg_reduct(target.get_combined_req_met_effects())
                actual_cc_damage = target.get_expertise().damage(cursed_coins_damage, target.get_dueling(), percent_dmg_reduct, ignore_armor=False)

                armor_str = f" ({target.get_dueling().armor - org_armor} Armor)" if target.get_dueling().armor - org_armor < 0 else ""

                caster.get_stats().dueling.damage_dealt += actual_cc_damage
                target.get_stats().dueling.damage_taken += actual_cc_damage

                result_str += "\n{0}" + f" dealt {actual_cc_damage}{armor_str} damage to " + "{" + f"{i + 1}" + "} using Cursed Coins"

        mana_and_cd_str = self.remove_mana_and_set_cd(caster)
        if mana_and_cd_str is not None:
            result_str += "\n" + mana_and_cd_str
        
        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# NPC CLASS
# -----------------------------------------------------------------------------

class CultistOfAvarice(NPC):
    def __init__(self, name_suffix: str=""):
        # Balance Simulation Results:
        # 8% chance of 4 player party (Lvl. 80-90) victory against 3
        # Avg Number of Turns (per entity): 8

        super().__init__("Cultist of Avarice" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Mage, {})

        self._setup_npc_params()

    def _setup_inventory(self):
        if self._inventory is None:
            self._inventory = Inventory()

    def _setup_xp(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()
        
        self._expertise.add_xp_to_class_until_level(200, ExpertiseClass.Merchant)
        self._expertise.constitution = 90
        self._expertise.strength = 0
        self._expertise.dexterity = 40
        self._expertise.intelligence = 40
        self._expertise.luck = 27
        self._expertise.memory = 3

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.RitualDagger))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [HailTheEmissary(), MustHaveMore(), RitualOfBlood()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Cultist of Avarice"
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
