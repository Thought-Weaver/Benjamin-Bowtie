from math import ceil
from uuid import uuid4

from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Attribute, Expertise, ExpertiseClass
from features.inventory import Inventory
from features.npcs.npc import NPC, NPCDuelingPersonas, NPCRoles
from features.shared.ability import Ability
from features.shared.constants import STR_DMG_SCALE
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, ItemKey, WeaponStats
from features.shared.statuseffect import DmgReduction, TurnSkipChance
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player
    from features.shared.ability import NegativeAbilityResult

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class BearDown(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="Bear Down",
            class_key=ExpertiseClass.Guardian,
            description="Gain 75% resistance to all damage until your next turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=50,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_buff = DmgReduction(
            turns_remaining=1,
            value=0.75,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class Swipe(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF2A\uFE0F",
            name="Swipe",
            class_key=ExpertiseClass.Guardian,
            description="Swipe with your claws, dealing 200% of your weapon damage to all enemies.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=-1,
            level_requirement=50,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength]
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
        damage = ceil(base_damage * 2)
        damage += min(ceil(damage * STR_DMG_SCALE * max(caster_attrs.strength, 0)), damage)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class Roar(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDDEF\uFE0F",
            name="Roar",
            class_key=ExpertiseClass.Guardian,
            description="Roar at all enemies and cause Faltering for 2 turns with a 25% chance of skipping their turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=1,
            num_targets=-1,
            level_requirement=50,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        falter = TurnSkipChance(
            turns_remaining=2,
            value=0.25,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [falter])
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

class DeepwoodBear(NPC):
    def __init__(self):
        super().__init__("Deepwood Bear", NPCRoles.DungeonEnemy, NPCDuelingPersonas.Bruiser, {
            ItemKey.Bones: 0.85,
            ItemKey.IronSword: 0.1,
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
        
        self.level = 70
        self._expertise.constitution = 45
        self._expertise.strength = 22
        self._expertise.dexterity = 0
        self._expertise.intelligence = 0
        self._expertise.luck = 0
        self._expertise.memory = 3

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.WildBoarTusks))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [BearDown(), Swipe(), Roar()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Deepwood Bear"
        self._role = NPCRoles.DungeonEnemy
        self._dueling_persona = NPCDuelingPersonas.Bruiser
        self._dueling_rewards = {
            ItemKey.Bones: 0.85,
            ItemKey.IronSword: 0.1,
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
