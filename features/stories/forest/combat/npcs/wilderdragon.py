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
from features.shared.statuseffect import POSITIVE_STATUS_EFFECTS_ON_SELF, FixedDmgTick, TurnSkipChance
from features.stats import Stats

from typing import List, TYPE_CHECKING, Set
if TYPE_CHECKING:
    from features.player import Player
    from features.shared.ability import NegativeAbilityResult

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class VoidBreath(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF0C",
            name="Void Breath",
            class_key=ExpertiseClass.Guardian,
            description="Deal 70-100 damage to all enemies.",
            flavor_text="",
            mana_cost=100,
            cooldown=8,
            num_targets=-2,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"

        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(70, 100))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class TailSlam(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA5",
            name="Tail Slam",
            class_key=ExpertiseClass.Guardian,
            description="Deal 30-40 damage to up to 2 enemies and cause Faltering with a 50% chance for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=2,
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
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(30, 40), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class Consume(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD25",
            name="Consume",
            class_key=ExpertiseClass.Guardian,
            description="Cause Faltering with a 100% chance on an enemy for 2 turns and cause a fixed damage tick of 10 per turn for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=1,
            level_requirement=0,
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

        dmg_tick = FixedDmgTick(
            turns_remaining=2,
            value=10,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [debuff, dmg_tick])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class Boneweaving(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC80",
            name="Boneweaving",
            class_key=ExpertiseClass.Guardian,
            description="Restore and increase your max armor by 100.",
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
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"

        caster.get_dueling().armor += 100

        result_str += "{0} gained 100 armor and increased their max armor by 100."

        mana_and_cd_str: str | None = self.remove_mana_and_set_cd(caster)
        if mana_and_cd_str is not None:
            result_str += mana_and_cd_str

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class TerrifyingRoar(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDDEF\uFE0F",
            name="Terrifying Roar",
            class_key=ExpertiseClass.Guardian,
            description="Remove all positive status effects from all enemies.",
            flavor_text="",
            mana_cost=150,
            cooldown=10,
            num_targets=-1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"

        target_result_strs: List[str] = []
        for i, target in enumerate(targets):
            removed_se_strs: Set[str] = set()
            for se_key in POSITIVE_STATUS_EFFECTS_ON_SELF:
                for se in target.get_dueling().status_effects:
                    if se.key == se_key:
                        removed_se_strs.add(se.key)
                target.get_dueling().status_effects = list(filter(lambda se: se.key != se_key, target.get_dueling().status_effects))
            
            if len(removed_se_strs) > 0:
                final_str: str = ", ".join(removed_se_strs)
                target_result_strs.append("{" + f"{i + 1}" + "} had " + f"{final_str} removed")

        result_str += "\n\n".join(target_result_strs)

        mana_and_cd_str: str | None = self.remove_mana_and_set_cd(caster)
        if mana_and_cd_str is not None:
            result_str += mana_and_cd_str

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# NPC CLASS
# -----------------------------------------------------------------------------

class Wilderdragon(NPC):
    def __init__(self, name_suffix: str=""):
        super().__init__("Wilderdragon" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Mage, {})

        self._setup_npc_params()

    def _setup_inventory(self):
        if self._inventory is None:
            self._inventory = Inventory()

    def _setup_xp(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()
        
        self._expertise.add_xp_to_class_until_level(1500, ExpertiseClass.Guardian)
        self._expertise.constitution = 450
        self._expertise.strength = 100
        self._expertise.dexterity = 0
        self._expertise.intelligence = 350
        self._expertise.luck = 25
        self._expertise.memory = 5

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
        
        self._dueling.abilities = [VoidBreath(), TailSlam(), Consume(), Boneweaving(), TerrifyingRoar()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Wilderdragon"
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
