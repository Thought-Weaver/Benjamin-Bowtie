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
from features.shared.statuseffect import CannotAttack, CannotUseAbilities, DmgReduction
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player
    from features.shared.ability import NegativeAbilityResult

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class TentacleGrasp(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEB1",
            name="Tentacle Grasp",
            class_key=ExpertiseClass.Merchant,
            description="Latch onto an enemy, causing them to be Atrophied and Enfeebled for 3 turns.",
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
        attack_debuff = CannotAttack(
            turns_remaining=3,
            value=1,
            source_str=self.get_icon_and_name()
        )

        ability_debuff = CannotUseAbilities(
            turns_remaining=3,
            value=1,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [attack_debuff, ability_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class SpewCoins(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE99",
            name="Spew Coins",
            class_key=ExpertiseClass.Merchant,
            description="Launch coins at an enemy, adding 100 coins to their inventory and dealing 150 damage.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(150, 150))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        for i, result in enumerate(results):
            if not result.dodged:
                targets[i].get_inventory().add_coins(100)
                result_str += "\n{" + f"{i + 1}" + "} had 100 gold added to their inventory!"

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class HardenCarapace(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDEE1\uFE0F",
            name="Harden Carapace",
            class_key=ExpertiseClass.Merchant,
            description="Grant yourself 75% damage resistance for 3 turns and restore 200 armor.",
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
        protect_buff = DmgReduction(
            turns_remaining=3,
            value=0.75,
            source_str=self.get_icon_and_name()
        )

        max_armor: int = caster.get_equipment().get_total_reduced_armor(caster.get_expertise().level, caster.get_non_status_combined_attributes())
        armor_to_restore: int = 200
        org_armor = caster.get_dueling().armor
        caster.get_dueling().armor = max(max_armor, org_armor + armor_to_restore)
        post_armor = caster.get_dueling().armor

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [protect_buff])
        
        result_str += "\n".join(results)
        result_str += "\n{0} restored " + f"{post_armor - org_armor} armor"

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# NPC CLASS
# -----------------------------------------------------------------------------

class WaylaidChest(NPC):
    def __init__(self, name_suffix: str=""):
        # Balance Simulation Results:
        # 46% chance of 4 player party (Lvl. 80-90) victory against 1
        # Avg Number of Turns (per entity): 12

        super().__init__("Waylaid Chest" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Bruiser, {})

        self._setup_npc_params()

    def _setup_inventory(self):
        if self._inventory is None:
            self._inventory = Inventory()

    def _setup_xp(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()
        
        self._expertise.add_xp_to_class_until_level(340, ExpertiseClass.Merchant)
        self._expertise.constitution = 140
        self._expertise.strength = 100
        self._expertise.dexterity = 30
        self._expertise.intelligence = 0
        self._expertise.luck = 67
        self._expertise.memory = 3

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.ChestTentacles))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [SpewCoins(), HardenCarapace(), TentacleGrasp()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Waylaid Chest"
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
