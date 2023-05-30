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
from features.shared.item import LOADED_ITEMS, ItemKey, WeaponStats
from features.shared.statuseffect import AttackingChanceToApplyStatus, DexDebuff, IntBuff, StrDebuff
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player
    from features.shared.ability import NegativeAbilityResult

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class WhirlwindOfBones(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF2A\uFE0F",
            name="Whirlwind of Bones",
            class_key=ExpertiseClass.Fisher,
            description="Summon a barrage of bones that damage all enemies for 80% of your weapon damage.",
            flavor_text="",
            mana_cost=15,
            cooldown=3,
            num_targets=-1,
            level_requirement=50,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        caster_equipment: Equipment = caster.get_equipment()
        caster_attrs = caster.get_combined_attributes()

        main_hand_item = caster_equipment.get_item_in_slot(ClassTag.Equipment.MainHand)
        level_req: int = main_hand_item.get_level_requirement() if main_hand_item is not None else 0
        
        unarmed_strength_bonus = int(caster_attrs.strength / 2)
        weapon_stats = WeaponStats(1 + unarmed_strength_bonus, 2 + unarmed_strength_bonus) if main_hand_item is None else main_hand_item.get_weapon_stats()
        item_effects = main_hand_item.get_item_effects() if main_hand_item is not None else None

        base_damage = weapon_stats.get_random_damage(caster_attrs, item_effects, max(0, level_req - caster.get_expertise().level))
        damage = ceil(base_damage * 0.8)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class VoidflameBurst(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD25",
            name="Voidflame Burst",
            class_key=ExpertiseClass.Fisher,
            description="Deal 4% of your current health to up to 2 enemies.",
            flavor_text="",
            mana_cost=25,
            cooldown=3,
            num_targets=2,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"

        damage = ceil(0.04 * caster.get_expertise().hp)
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class Inflame(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD25",
            name="Inflame",
            class_key=ExpertiseClass.Fisher,
            description="For 4 turns, gain +5 Intelligence for 3 turns whenever you attack",
            flavor_text="",
            mana_cost=5,
            cooldown=5,
            num_targets=0,
            level_requirement=20,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = AttackingChanceToApplyStatus(
            turns_remaining=4,
            value=1,
            source_str=self.get_icon_and_name(),
            status_effect=IntBuff(
                turns_remaining=3,
                value=5,
                source_str=self.get_icon_and_name()
            )
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class PiercingWail(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDDEF\uFE0F",
            name="Piercing Wail",
            class_key=ExpertiseClass.Fisher,
            description="Decrease all enemies' Strength and Dexterity by 10 for 3 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=-1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_debuff = DexDebuff(
            turns_remaining=3,
            value=-10,
            source_str=self.get_icon_and_name()
        )

        str_debuff = StrDebuff(
            turns_remaining=3,
            value=-10,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [dex_debuff, str_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# NPC CLASS
# -----------------------------------------------------------------------------

class WailingBones(NPC):
    def __init__(self, name_suffix: str=""):
        # Balance Simulation Results:
        # 30% chance of 4 player party (Lvl. 20-30) victory against 1

        super().__init__("Wailing Bones" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Mage, {
            ItemKey.Bones: 0.9,
            ItemKey.Bones: 0.7,
            ItemKey.Bones: 0.5,
            ItemKey.VoidseenBone: 0.8
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
        
        self._expertise.add_xp_to_class_until_level(230, ExpertiseClass.Fisher)
        self._expertise.constitution = 70
        self._expertise.strength = 60
        self._expertise.dexterity = 20
        self._expertise.intelligence = 50
        self._expertise.luck = 16
        self._expertise.memory = 4

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.ShamblersBones))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.OffHand, LOADED_ITEMS.get_new_item(ItemKey.ShamblersForm))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [WhirlwindOfBones(), VoidflameBurst(), Inflame(), PiercingWail()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Wailing Bones"
        self._role = NPCRoles.DungeonEnemy
        self._dueling_persona = NPCDuelingPersonas.Mage
        self._dueling_rewards = {
            ItemKey.Bones: 0.9,
            ItemKey.Bones: 0.7,
            ItemKey.Bones: 0.5,
            ItemKey.VoidseenBone: 0.8
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
