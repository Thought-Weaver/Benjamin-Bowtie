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
from features.shared.statuseffect import DexBuff, DmgReduction, DmgVulnerability, FixedDmgTick, TurnSkipChance
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player
    from features.shared.ability import NegativeAbilityResult

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class ScorchingTouch(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD25",
            name="Scorching Touch",
            class_key=ExpertiseClass.Merchant,
            description="Deal 200-250 damage and 100 damage per turn for the next 3 turns to an enemy.",
            flavor_text="",
            mana_cost=50,
            cooldown=3,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = FixedDmgTick(
            turns_remaining=3,
            value=100,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(200, 250), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class PlateInGold(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC51",
            name="Plate in Gold",
            class_key=ExpertiseClass.Merchant,
            description="Cover an enemy in liquid gold, adding 200 gold to their inventory, causing Faltering for 1 turn, dealing 75 damage every turn for 4 turns, and increasing the damage they take by 50% for 3 turns.",
            flavor_text="",
            mana_cost=40,
            cooldown=5,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        faltering_debuff = TurnSkipChance(
            turns_remaining=1,
            value=1,
            source_str=self.get_icon_and_name()
        )
        
        damage_tick = FixedDmgTick(
            turns_remaining=4,
            value=75,
            source_str=self.get_icon_and_name()
        )

        dmg_increase = DmgVulnerability(
            turns_remaining=3,
            value=0.5,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [faltering_debuff, damage_tick, dmg_increase])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        for i, result in enumerate(results):
            if not result.dodged:
                targets[i].get_inventory().add_coins(200)
                result_str += "\n{" + f"{i + 1}" + "} had 200 gold added to their inventory!"

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class AmorphousForm(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE99",
            name="Amorphous Form",
            class_key=ExpertiseClass.Merchant,
            description="Increase your Dex by 50 and gain 60% damage protection for 3 turns.",
            flavor_text="",
            mana_cost=30,
            cooldown=2,
            num_targets=0,
            level_requirement=20,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        protect_buff = DmgReduction(
            turns_remaining=3,
            value=0.6,
            source_str=self.get_icon_and_name()
        )

        dex_buff = DexBuff(
            turns_remaining=3,
            value=50,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [protect_buff, dex_buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# NPC CLASS
# -----------------------------------------------------------------------------

class MoltenGold(NPC):
    def __init__(self, name_suffix: str=""):
        # Balance Simulation Results:
        # 18% chance of 4 player party (Lvl. 80-90) victory against 1
        # Avg Number of Turns (per entity): 11

        super().__init__("Molten Gold" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Mage, {
            ItemKey.PileOfCoins: 0.7,
            ItemKey.PileOfCoins: 0.4,
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
        
        self._expertise.add_xp_to_class_until_level(330, ExpertiseClass.Merchant)
        self._expertise.constitution = 120
        self._expertise.strength = 0
        self._expertise.dexterity = 80
        self._expertise.intelligence = 100
        self._expertise.luck = 27
        self._expertise.memory = 3

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.MoltenGold))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [ScorchingTouch(), PlateInGold(), AmorphousForm()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Molten Gold"
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
