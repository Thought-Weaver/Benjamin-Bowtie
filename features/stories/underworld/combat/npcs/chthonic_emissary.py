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
from features.shared.statuseffect import NEGATIVE_STATUS_EFFECTS, Bleeding, DmgBuff, DmgDebuff, DmgReduction, DmgReflect, DmgVulnerability, FixedDmgTick, Generating, LckBuff, Marked, RegenerateHP, StatusEffectKey, Tarnished, TurnSkipChance, Undying
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class RubyEyesBeginToGlow(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD3B",
            name="Ruby Eyes Begin to Glow",
            class_key=ExpertiseClass.Merchant,
            description="Mark all enemies, reduce their damage dealt by 40%, and set 25% Vulnerable on them for 3 turns.",
            flavor_text="",
            mana_cost=40,
            cooldown=6,
            num_targets=-1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        marked = Marked(
            turns_remaining=3,
            value=1,
            caster=caster,
            source_str=self.get_icon_and_name()
        )

        dmg_debuff = DmgDebuff(
            turns_remaining=3,
            value=0.4,
            source_str=self.get_icon_and_name()
        )

        dmg_vuln = DmgVulnerability(
            turns_remaining=3,
            value=0.25,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [marked, dmg_debuff, dmg_vuln])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class AnnihilationBeam(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2604\uFE0F",
            name="Annihilation Beam",
            class_key=ExpertiseClass.Merchant,
            description="Deal 2000 damage to all enemies who are marked by Ruby Eyes Begin to Glow.",
            flavor_text="",
            mana_cost=500,
            cooldown=8,
            num_targets=-1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        filtered_targets: List[Player | NPC] = [target for target in targets if any(se.key == StatusEffectKey.Marked and se.source_str == "\uD83D\uDD3B Ruby Eyes Begin to Glow" for se in target.get_dueling().status_effects)]

        if len(filtered_targets) == 0:
            self.remove_mana_and_set_cd(caster)
            return "{0}" + f" failed to use {self.get_icon_and_name()}!\n\n"

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, filtered_targets, range(2000, 2000))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class BreakShackle(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD17",
            name="Break Shackle",
            class_key=ExpertiseClass.Merchant,
            description="Destroy 300 of your armor, but gain 5% damage resistance for the rest of the duel. If you lack the armor, this does nothing.",
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
        org_armor: int = caster.get_dueling().armor
        if org_armor < 300:
            return "{0}" + f" failed to use {self.get_icon_and_name()}!"

        caster.get_dueling().armor -= 300

        buff = DmgReduction(
            turns_remaining=-1,
            value=0.05,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}, destroying 300 of its armor!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class GoldToIchor(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE78",
            name="Gold to Ichor",
            class_key=ExpertiseClass.Merchant,
            description="Steal 100 gold from every enemy and restore that much health.",
            flavor_text="",
            mana_cost=40,
            cooldown=6,
            num_targets=-1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        heal_amount: int = 0
        for target in targets:
            coins_to_remove: int = min(100, target.get_inventory().get_coins())
            target.get_inventory().remove_coins(coins_to_remove)
            heal_amount += coins_to_remove

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}, converting 100 gold from every enemy into ichor!\n\n"
        results: List[str] = self._use_heal_ability(caster, [caster], range(heal_amount, heal_amount))
        result_str += "\n".join([s.replace("{1}", "{0}") for s in results])

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class InvocationOfAvarice(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE99",
            name="Invocation of Avarice",
            class_key=ExpertiseClass.Merchant,
            description="Grant yourself 200% Tarnished and 50 Generating for 5 turns.",
            flavor_text="",
            mana_cost=50,
            cooldown=10,
            num_targets=0,
            level_requirement=20,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        tarnished = Tarnished(
            turns_remaining=5,
            value=2,
            source_str=self.get_icon_and_name()
        )

        generating = Generating(
            turns_remaining=5,
            value=50,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [tarnished, generating])
        result_str += "\n".join(results)

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class Eternal(Ability):
    def __init__(self):
        super().__init__(
            icon="\u267E\uFE0F",
            name="Eternal",
            class_key=ExpertiseClass.Merchant,
            description="If you're below 10% HP, become Undying for 2 turns and regenerate 5% of your max health every turn for 2 turns.",
            flavor_text="",
            mana_cost=100,
            cooldown=15,
            num_targets=0,
            level_requirement=20,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        if caster.get_expertise().hp < int(0.1 * caster.get_expertise().max_hp):
            return "{0}" + f" failed to use {self.get_icon_and_name()}!\n\n"

        undying = Undying(
            turns_remaining=2,
            value=1,
            source_str=self.get_icon_and_name()
        )

        regenerating = RegenerateHP(
            turns_remaining=2,
            value=0.05,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [undying, regenerating])
        result_str += "\n".join(results)

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class GiveInToGreed(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCB0",
            name="Give in to Greed",
            class_key=ExpertiseClass.Merchant,
            description="Set a fixed damage tick on an enemy equal to 2x their total Luck for 3 turns.",
            flavor_text="",
            mana_cost=30,
            cooldown=2,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = FixedDmgTick(
            turns_remaining=3,
            value=2 * targets[0].get_combined_attributes().luck,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class InvocationOfLapis(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC8E",
            name="Invocation of Lapis",
            class_key=ExpertiseClass.Merchant,
            description="Restore all of your mana and remove all negative status effects from yourself.",
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
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}, restored all of its mana, and removed all negative status effects from itself!"

        caster.get_expertise().restore_mana(caster.get_expertise().max_mana)
        caster.get_dueling().status_effects = [se for se in caster.get_dueling().status_effects if se.key not in NEGATIVE_STATUS_EFFECTS]

        self.remove_mana_and_set_cd(caster)

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class InvocationOfJade(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE99",
            name="Invocation of Jade",
            class_key=ExpertiseClass.Merchant,
            description="Increase your Luck by 200 for 5 turns.",
            flavor_text="",
            mana_cost=70,
            cooldown=12,
            num_targets=0,
            level_requirement=20,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = LckBuff(
            turns_remaining=5,
            value=200,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class InvocationOfOnyx(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE99",
            name="Invocation of Onyx",
            class_key=ExpertiseClass.Merchant,
            description="Grant yourself 75% damage reflection for 4 turns.",
            flavor_text="",
            mana_cost=100,
            cooldown=10,
            num_targets=0,
            level_requirement=20,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = DmgReflect(
            turns_remaining=4,
            value=0.75,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class InvocationOfRuby(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE99",
            name="Invocation of Ruby",
            class_key=ExpertiseClass.Merchant,
            description="Restore 10% of your max health.",
            flavor_text="",
            mana_cost=100,
            cooldown=15,
            num_targets=0,
            level_requirement=20,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = RegenerateHP(
            turns_remaining=1,
            value=0.1,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class InvocationOfSapphire(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE99",
            name="Invocation of Sapphire",
            class_key=ExpertiseClass.Merchant,
            description="Cause Faltering on all enemies for 2 turns.",
            flavor_text="",
            mana_cost=70,
            cooldown=11,
            num_targets=-1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = TurnSkipChance(
            turns_remaining=2,
            value=1,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class InvocationOfTanzanite(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE99",
            name="Invocation of Tanzanite",
            class_key=ExpertiseClass.Merchant,
            description="Deal 80% of an enemy's max health as damage to them.",
            flavor_text="",
            mana_cost=30,
            cooldown=4,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage: int = int(0.8 * targets[0].get_expertise().max_hp)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class InvocationOfBloodstone(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE99",
            name="Invocation of Bloodstone",
            class_key=ExpertiseClass.Merchant,
            description="Deal 140-150 damage to all enemies and cause Bleeding for 5 turns.",
            flavor_text="",
            mana_cost=60,
            cooldown=7,
            num_targets=-1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        bleeding = Bleeding(
            turns_remaining=5,
            value=BLEED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(140, 150), [bleeding])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class InvocationOfDiamond(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE99",
            name="Invocation of Diamond",
            class_key=ExpertiseClass.Merchant,
            description="Grant yourself 35% damage resistance and a 35% damage buff for 4 turns.",
            flavor_text="",
            mana_cost=150,
            cooldown=9,
            num_targets=0,
            level_requirement=20,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dmg_buff = DmgBuff(
            turns_remaining=4,
            value=0.35,
            source_str=self.get_icon_and_name()
        )

        dmg_resist = DmgReduction(
            turns_remaining=4,
            value=0.35,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dmg_buff, dmg_resist])
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

class ChthonicEmissary(NPC):
    def __init__(self, num_stirred: int, name_suffix: str=""):
        # Balance Simulation Results:
        #
        # --- Number of Times Stirred: 0 ---
        # 4% chance of 4 player party (Lvl. 90-100) victory against 1
        # Avg Number of Turns (per entity): 12
        #
        # --- Number of Times Stirred: 10 ---
        # 4% chance of 4 player party (Lvl. 90-100) victory against 1
        # Avg Number of Turns (per entity): 12
        #
        # --- Number of Times Stirred: 20 ---
        # 3% chance of 4 player party (Lvl. 90-100) victory against 1
        # Avg Number of Turns (per entity): 10
        #
        # --- Number of Times Stirred: 30 ---
        # 2% chance of 4 player party (Lvl. 90-100) victory against 1
        # Avg Number of Turns (per entity): 10
        #
        # --- Number of Times Stirred: 40 ---
        # 3% chance of 4 player party (Lvl. 90-100) victory against 1
        # Avg Number of Turns (per entity): 12
        #
        # --- Number of Times Stirred: 50 ---
        # 6% chance of 4 player party (Lvl. 90-100) victory against 1
        # Avg Number of Turns (per entity): 16
        #
        # --- Number of Times Stirred: 60 ---
        # 7% chance of 4 player party (Lvl. 90-100) victory against 1
        # Avg Number of Turns (per entity): 15
        #
        # --- Number of Times Stirred: 70 ---
        # 5% chance of 4 player party (Lvl. 90-100) victory against 1
        # Avg Number of Turns (per entity): 13
        #
        # --- Number of Times Stirred: 80 ---
        # 7% chance of 4 player party (Lvl. 90-100) victory against 1
        # Avg Number of Turns (per entity): 14
        #
        # --- Number of Times Stirred: 90 ---
        # 5% chance of 4 player party (Lvl. 90-100) victory against 1
        # Avg Number of Turns (per entity): 15
        #
        # --- Number of Times Stirred: 100 ---
        # 5% chance of 4 player party (Lvl. 90-100) victory against 1
        # Avg Number of Turns (per entity): 14
        #
        # --- Number of Times Stirred: 110 ---
        # 1% chance of 4 player party (Lvl. 90-100) victory against 1
        # Avg Number of Turns (per entity): 11
        #
        # --- Number of Times Stirred: 120 ---
        # 1% chance of 4 player party (Lvl. 90-100) victory against 1
        # Avg Number of Turns (per entity): 11

        super().__init__("Chthonic Emissary" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Mage, {})

        self._setup_npc_params(num_stirred)

    def _setup_inventory(self):
        if self._inventory is None:
            self._inventory = Inventory()

    def _setup_xp(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()
        
        self._expertise.add_xp_to_class_until_level(1500, ExpertiseClass.Merchant)
        self._expertise.constitution = 350
        self._expertise.strength = 800
        self._expertise.dexterity = 50
        self._expertise.intelligence = 200
        self._expertise.luck = 97
        self._expertise.memory = 3

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.ChthonicClaws))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.ChestArmor, LOADED_ITEMS.get_new_item(ItemKey.ChthonicRobe))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self, num_stirred: int):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [RubyEyesBeginToGlow(), AnnihilationBeam(), BreakShackle()]
        if num_stirred >= 10:
            self._dueling.abilities.append(GoldToIchor())
        if num_stirred >= 20:
            self._dueling.abilities.append(InvocationOfAvarice())
        if num_stirred >= 30:
            self._dueling.abilities.append(Eternal())
        if num_stirred >= 40:
            self._dueling.abilities.append(GiveInToGreed())
        if num_stirred >= 50:
            self._dueling.abilities.append(InvocationOfLapis())
        if num_stirred >= 60:
            self._dueling.abilities.append(InvocationOfJade())
        if num_stirred >= 70:
            self._dueling.abilities.append(InvocationOfOnyx())
        if num_stirred >= 80:
            self._dueling.abilities.append(InvocationOfRuby())
        if num_stirred >= 90:
            self._dueling.abilities.append(InvocationOfSapphire())
        if num_stirred >= 100:
            self._dueling.abilities.append(InvocationOfTanzanite())
        if num_stirred >= 110:
            self._dueling.abilities.append(InvocationOfBloodstone())
        if num_stirred >= 120:
            self._dueling.abilities.append(InvocationOfDiamond())

    def _setup_npc_params(self, num_stirred: int):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities(num_stirred)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Chthonic Emissary"
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
            self._setup_abilities(0)

        self._stats: Stats | None = state.get("_stats")
        if self._stats is None:
            self._stats = Stats()
