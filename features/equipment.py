from __future__ import annotations

import discord
import features.shared.ability

from discord.embeds import Embed
from features.expertise import Expertise
from features.shared.attributes import Attributes
from features.shared.constants import ARMOR_OVERLEVELED_DEBUFF
from features.shared.effect import EffectType, ItemEffectCategory, ItemEffects
from features.shared.enums import ClassTag, Summons
from features.shared.item import Item
from features.shared.nextbutton import NextButton
from features.shared.prevbutton import PrevButton

from typing import TYPE_CHECKING, Dict, List
if TYPE_CHECKING:
    from bot import BenjaminBowtieBot
    from features.inventory import Inventory
    from features.npcs.npc import NPC
    from features.player import Player
    from features.shared.ability import Ability
    from features.shared.item import ArmorStats

# -----------------------------------------------------------------------------
# CLASSES
# -----------------------------------------------------------------------------

class Equipment():
    def __init__(self):
        self._helmet: Item | None = None
        self._amulet: Item | None = None
        self._chest_armor: Item | None = None
        self._gloves: Item | None = None
        self._ring: Item | None = None
        self._leggings: Item | None = None
        self._boots: Item | None = None
        self._main_hand: Item | None = None
        self._off_hand: Item | None = None

    def get_all_equipped_items(self) -> List[Item]:
        equipment = [
            self._helmet,
            self._amulet,
            self._chest_armor,
            self._gloves,
            self._ring,
            self._leggings,
            self._boots,
            self._main_hand,
            self._off_hand
        ]
        return list(filter(lambda item: item is not None, equipment))

    def get_all_equipment_dict(self) -> Dict[ClassTag.Equipment, Item | None]:
        return {
            ClassTag.Equipment.Helmet: self._helmet,
            ClassTag.Equipment.Amulet: self._amulet,
            ClassTag.Equipment.ChestArmor: self._chest_armor,
            ClassTag.Equipment.Gloves: self._gloves,
            ClassTag.Equipment.Ring: self._ring,
            ClassTag.Equipment.Leggings: self._leggings,
            ClassTag.Equipment.Boots: self._boots,
            ClassTag.Equipment.MainHand: self._main_hand,
            ClassTag.Equipment.OffHand: self._off_hand
        }

    def get_item_in_slot(self, slot: ClassTag.Equipment | None):
        if slot == ClassTag.Equipment.Helmet:
            return self._helmet
        if slot == ClassTag.Equipment.Amulet:
            return self._amulet
        if slot == ClassTag.Equipment.ChestArmor:
            return self._chest_armor
        if slot == ClassTag.Equipment.Gloves:
            return self._gloves
        if slot == ClassTag.Equipment.Ring:
            return self._ring
        if slot == ClassTag.Equipment.Leggings:
            return self._leggings
        if slot == ClassTag.Equipment.Boots:
            return self._boots
        if slot == ClassTag.Equipment.MainHand:
            return self._main_hand
        if slot == ClassTag.Equipment.OffHand:
            return self._off_hand
        return None

    def unequip_item_from_slot(self, slot: ClassTag.Equipment | None):
        if slot == ClassTag.Equipment.Helmet:
            item = self._helmet
            self._helmet = None
            return item
        if slot == ClassTag.Equipment.Amulet:
            item = self._amulet
            self._amulet = None
            return item
        if slot == ClassTag.Equipment.ChestArmor:
            item = self._chest_armor
            self._chest_armor = None
            return item
        if slot == ClassTag.Equipment.Gloves:
            item = self._gloves
            self._gloves = None
            return item
        if slot == ClassTag.Equipment.Ring:
            item = self._ring
            self._ring = None
            return item
        if slot == ClassTag.Equipment.Leggings:
            item = self._leggings
            self._leggings = None
            return item
        if slot == ClassTag.Equipment.Boots:
            item = self._boots
            self._boots = None
            return item
        if slot == ClassTag.Equipment.MainHand:
            item = self._main_hand
            self._main_hand = None
            return item
        if slot == ClassTag.Equipment.OffHand:
            item = self._off_hand
            self._off_hand = None
            return item
        return None

    def equip_item_to_slot(self, slot: ClassTag.Equipment | None, item: (Item | None)):
        prev_item = None
        if slot == ClassTag.Equipment.Helmet:
            prev_item = self._helmet
            self._helmet = item
        if slot == ClassTag.Equipment.Amulet:
            prev_item = self._amulet
            self._amulet = item
        if slot == ClassTag.Equipment.ChestArmor:
            prev_item = self._chest_armor
            self._chest_armor = item
        if slot == ClassTag.Equipment.Gloves:
            prev_item = self._gloves
            self._gloves = item
        if slot == ClassTag.Equipment.Ring:
            prev_item = self._ring
            self._ring = item
        if slot == ClassTag.Equipment.Leggings:
            prev_item = self._leggings
            self._leggings = item
        if slot == ClassTag.Equipment.Boots:
            prev_item = self._boots
            self._boots = item
        if slot == ClassTag.Equipment.MainHand:
            prev_item = self._main_hand
            self._main_hand = item
        if slot == ClassTag.Equipment.OffHand:
            prev_item = self._off_hand
            self._off_hand = item
        return prev_item

    def get_total_attribute_mods(self) -> Attributes:
        mods: Attributes = Attributes(0, 0, 0, 0, 0, 0)
        for item in self.get_all_equipped_items():
            item_effects = item.get_item_effects()
            mods += item_effects.get_permanent_attribute_mods()
        return mods

    def _get_total_armor(self):
        armor: int = 0
        for item in self.get_all_equipped_items():
            armor_stats: ArmorStats | None = item.get_armor_stats()
            if armor_stats is not None:
                armor += armor_stats.get_armor_amount()
        return armor

    def get_total_reduced_armor(self, level: int, attributes: Attributes):
        armor: int = 0
        for item in self.get_all_equipped_items():
            armor_stats: ArmorStats | None = item.get_armor_stats()
            if armor_stats is not None and item.meets_attr_requirements(attributes):
                reduce_to: float = max(0, 1.0 - (ARMOR_OVERLEVELED_DEBUFF * max(0, item.get_level_requirement() - level)))
                armor += int(armor_stats.get_armor_amount() * reduce_to)
        return armor

    def get_total_armor_str(self, level: int, attributes: Attributes):
        armor: int = self._get_total_armor()
        reduced_armor: int = self.get_total_reduced_armor(level, attributes)
        
        if armor != reduced_armor:
            return f"{armor} (-{armor - reduced_armor}) Armor"
        return f"{armor} Armor"

    def get_num_slots_unequipped(self):
        equipment = [
            self._helmet,
            self._amulet,
            self._chest_armor,
            self._gloves,
            self._ring,
            self._leggings,
            self._boots,
            self._main_hand,
            self._off_hand
        ]
        return len(list(filter(lambda item: item is None, equipment)))

    def get_combined_item_effects(self):
        equipped_items = self.get_all_equipped_items()
        result = None
        for item in equipped_items:
            item_effects = item.get_item_effects()
            if item_effects is not None:
                if result is None:
                    result = item_effects
                else:
                    result += item_effects

        return result

    def get_combined_item_effects_if_requirements_met(self, entity: Player | NPC):
        equipped_items = self.get_all_equipped_items()
        result = ItemEffects([], [], [], [], [], [], [], [])
        for item in equipped_items:
            item_effects = item.get_item_effects()
            if item_effects is not None:
                for category in ItemEffectCategory:
                    for item_effect in item_effects.get_effects_by_category(category):
                        if not item_effect.meets_conditions(entity, item):
                            continue
                        
                        result.add_effect_in_category(item_effect, category)

        return result

    def get_dmg_buff_effect_totals(self, entity: Player | NPC):
        result: Dict[EffectType, float] = {
            EffectType.DmgBuff: 0,
            EffectType.DmgBuffSelfMaxHealth: 0,
            EffectType.DmgBuffSelfRemainingHealth: 0,
            EffectType.DmgBuffOtherMaxHealth: 0,
            EffectType.DmgBuffOtherRemainingHealth: 0,
            EffectType.DmgBuffLegends: 0,
            EffectType.DmgBuffPoisoned: 0,
            EffectType.DmgBuffBleeding: 0,
            EffectType.CritDmgBuff: 0,
            EffectType.CritDmgReduction: 0
        }

        for item in self.get_all_equipped_items():
            item_effects = item.get_item_effects()
            if item_effects is not None:
                for item_effect in item_effects.permanent:
                    if not item_effect.meets_conditions(entity, item):
                        continue

                    if item_effect.effect_type in result.keys():
                        result[item_effect.effect_type] = result.get(item_effect.effect_type, 0) + item_effect.effect_value
        
        return result

    def get_granted_abilities(self, entity: Player | NPC):
        abilities: List[Ability] = []
        for item in self.get_all_equipped_items():
            item_effects = item.get_item_effects()
            if item_effects is not None:
                for item_effect in item_effects.permanent:
                    if not item_effect.meets_conditions(entity, item):
                        continue

                    if item_effect.effect_type == EffectType.GrantAbility:
                        if item_effect.granted_ability is not None:
                            ability = next(ability() for ability in features.shared.ability.ALL_ABILITIES if ability().get_name() == item_effect.granted_ability)
                            if ability is not None:
                                abilities.append(ability)
        return abilities
    
    def get_summons_enums(self, entity: Player | NPC):
        summons: List[Summons] = []
        for item in self.get_all_equipped_items():
            item_effects = item.get_item_effects()
            if item_effects is not None:
                for item_effect in item_effects.permanent:
                    if not item_effect.meets_conditions(entity, item):
                        continue

                    if item_effect.effect_type == EffectType.Summon and item_effect.summon is not None:
                        summons += [item_effect.summon for _ in range(int(item_effect.effect_value))]
        return summons

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._helmet = state.get("_helmet")
        self._amulet = state.get("_amulet")
        self._chest_armor = state.get("_chest_armor")
        self._gloves = state.get("_gloves")
        self._ring = state.get("_ring")
        self._leggings = state.get("_leggings")
        self._boots = state.get("_boots")
        self._main_hand = state.get("_main_hand")
        self._off_hand = state.get("_off_hand")


class ItemEquipButton(discord.ui.Button):
    def __init__(self, exact_item_index: int, item: Item, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_name_and_count()}", row=row, emoji=item.get_icon())
        
        self._exact_item_index = exact_item_index

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: EquipmentView = self.view
        if interaction.user == view.get_user():
            response = view.equip_item(self._exact_item_index)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class SelectSlotButton(discord.ui.Button):
    def __init__(self, label: str, slot: ClassTag.Equipment, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=label, row=row)
        
        self._slot = slot

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: EquipmentView = self.view
        if interaction.user == view.get_user():
            response = view.display_item_in_slot(self._slot)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class UnequipButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.blurple, label="Unequip", row=row)
        
    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: EquipmentView = self.view
        if interaction.user == view.get_user():
            response = view.unequip_item()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class SelectSlotExitButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.red, label="Exit", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: EquipmentView = self.view
        if interaction.user == view.get_user():
            response = view.exit_to_main_menu()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class EquipmentView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, user: discord.User, show_with_buttons: bool):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._user = user
        self._show_with_buttons = show_with_buttons

        self._page = 0
        self._cur_equip_slot: ClassTag.Equipment | None = None

        self._NUM_PER_PAGE = 4

        if show_with_buttons:
            self._display_slot_select_buttons()

    def get_player(self) -> Player:
        return self._database[str(self._guild_id)]["members"][str(self._user.id)]

    def get_str_for_slot(self, slot: ClassTag.Equipment | None):
        if slot == ClassTag.Equipment.ChestArmor:
            return "Chest Armor"
        if slot == ClassTag.Equipment.MainHand:
            return "Main Hand"
        if slot == ClassTag.Equipment.OffHand:
            return "Off Hand"
        return slot or "Unknown"

    def enter_equip_for_slot(self):
        self._get_current_page_buttons()

        player: Player = self.get_player()
        equipped_item: (Item | None) = player.get_equipment().get_item_in_slot(self._cur_equip_slot)

        description = ""
        if equipped_item is not None:
            description += f"᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{equipped_item}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\n"
        description += "Choose an item from your inventory to equip."

        return Embed(
            title=f"Equip to {self.get_str_for_slot(self._cur_equip_slot)}",
            description=description
        )

    def equip_item(self, exact_item_index: int):
        player: Player = self.get_player()
        inventory: Inventory = player.get_inventory()
        equipment: Equipment = player.get_equipment()
        expertise: Expertise = player.get_expertise()

        # Need to check that the item still exists since there are async operations
        # that can happen with different views.
        embed = Embed(
            title=f"Equip to {self.get_str_for_slot(self._cur_equip_slot)}",
            description="*Error: Could not equip that item.*\n\nChoose an item from your inventory to equip."
        )
        # The "exact_item_index" here is the index of the item with respect to the entire
        # inventory. This is used instead of an adjusted index here because the items are
        # filtered when displayed to the user, so adjusting based on page size wouldn't work.
        item = inventory.get_inventory_slots()[exact_item_index]
        found_index = inventory.item_exists(item)
        if found_index == exact_item_index and self._cur_equip_slot in item.get_class_tags():
            if item.meets_attr_requirements(expertise.get_all_attributes() + equipment.get_total_attribute_mods()):
                item = inventory.remove_item(exact_item_index, 1)
                prev_item = equipment.equip_item_to_slot(self._cur_equip_slot, item)

                if prev_item is not None:
                    inventory.add_item(prev_item)

                unequipped_items_strs: List[str] = []
                # Equipping an item that modifies attributes can trigger a chain effect (notably in the case of a negative modifier)
                # where items need to be unequipped since they no longer meet attribute requirements.
                if item is not None and item.get_item_effects() is not None and item.get_item_effects().get_permanent_attribute_mods().any_nonzero():
                    last_unequipped_items_len: int = -1
                    while len(unequipped_items_strs) != last_unequipped_items_len:
                        last_unequipped_items_len = len(unequipped_items_strs)
                        cur_attrs = expertise.get_all_attributes() + equipment.get_total_attribute_mods()
                        for slot in ClassTag.Equipment:
                            next_item: Item | None = equipment.get_item_in_slot(slot)
                            if next_item is not None and not next_item.meets_attr_requirements(cur_attrs):
                                equipment.unequip_item_from_slot(slot)
                                inventory.add_item(next_item)
                                unequipped_items_strs.append(next_item.get_full_name())
                                expertise.update_stats(player.get_combined_attributes())
                unequipped_items_str: str = "" if len(unequipped_items_strs) == 0 else ("\n\n" + ", ".join(unequipped_items_strs) + " unequipped due to attribute requirements changing! ")
                
                embed = Embed(
                    title=f"Equip to {self.get_str_for_slot(self._cur_equip_slot)}",
                    description=f"᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{item}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\nEquipped! You can choose a different item from your inventory to equip or exit.{unequipped_items_str}"
                )
                expertise.update_stats(player.get_combined_attributes())
            else:
                embed = Embed(
                    title=f"Equip to {self.get_str_for_slot(self._cur_equip_slot)}",
                    description="*Error: You don't meet the attribute requirements for that item!*\n\nChoose an item from your inventory to equip."
                )
        
        self._get_current_page_buttons()
        return embed

    def unequip_item(self):
        player: Player = self.get_player()
        equipment: Equipment = player.get_equipment()
        inventory: Inventory = player.get_inventory()
        expertise: Expertise = player.get_expertise()

        equipped_item: (Item | None) = equipment.unequip_item_from_slot(self._cur_equip_slot)
        inventory.add_item(equipped_item)

        unequipped_items_strs: List[str] = []
        # Unequipping an item that modifies attributes can trigger a chain effect where
        # other items need to be unequipped since they no longer meet attribute requirements.
        if equipped_item is not None and equipped_item.get_item_effects() is not None and equipped_item.get_item_effects().get_permanent_attribute_mods().any_nonzero():
            last_unequipped_items_len: int = -1
            while len(unequipped_items_strs) != last_unequipped_items_len:
                last_unequipped_items_len = len(unequipped_items_strs)
                cur_attrs = expertise.get_all_attributes() + equipment.get_total_attribute_mods()
                for slot in ClassTag.Equipment:
                    item: Item | None = equipment.get_item_in_slot(slot)
                    if item is not None and not item.meets_attr_requirements(cur_attrs):
                        equipment.unequip_item_from_slot(slot)
                        inventory.add_item(item)
                        unequipped_items_strs.append(item.get_full_name())
                        expertise.update_stats(player.get_combined_attributes())
        unequipped_items_str: str = "" if len(unequipped_items_strs) == 0 else ("\n\n" + ", ".join(unequipped_items_strs) + " unequipped due to attribute requirements changing! ")

        expertise.update_stats(player.get_combined_attributes())

        self._get_current_page_buttons()

        if equipped_item is not None:
            return Embed(
                title=f"Equip to {self.get_str_for_slot(self._cur_equip_slot)}",
                description = f"{equipped_item.get_full_name()} unequipped!{unequipped_items_str}\n\nNone equipped. Choose an item from your inventory to equip."
            )
        else:
            return Embed(
                title=f"Equip to {self.get_str_for_slot(self._cur_equip_slot)}",
                description = "None equipped. Choose an item from your inventory to equip."
            )

    def display_item_in_slot(self, slot: ClassTag.Equipment):
        self._cur_equip_slot = slot
        return self.enter_equip_for_slot()

    def _display_slot_select_buttons(self):
        self.clear_items()
        self.add_item(SelectSlotButton("Helmet", ClassTag.Equipment.Helmet, 0))
        self.add_item(SelectSlotButton("Amulet", ClassTag.Equipment.Amulet, 0))
        self.add_item(SelectSlotButton("Gloves", ClassTag.Equipment.Gloves, 1))
        self.add_item(SelectSlotButton("Chest Armor", ClassTag.Equipment.ChestArmor, 1))
        self.add_item(SelectSlotButton("Ring", ClassTag.Equipment.Ring, 1))
        self.add_item(SelectSlotButton("Leggings", ClassTag.Equipment.Leggings, 2))
        self.add_item(SelectSlotButton("Boots", ClassTag.Equipment.Boots, 2))
        self.add_item(SelectSlotButton("Main Hand", ClassTag.Equipment.MainHand, 3))
        self.add_item(SelectSlotButton("Off Hand", ClassTag.Equipment.OffHand, 3))

    def _get_current_page_buttons(self):
        self.clear_items()
        player: Player = self.get_player()
        inventory = player.get_inventory()
        inventory_slots = inventory.get_inventory_slots()

        filtered_indices = inventory.filter_inventory_slots([self._cur_equip_slot])
        filtered_items = [inventory_slots[i] for i in filtered_indices]

        page_slots = filtered_items[self._page * self._NUM_PER_PAGE:min(len(filtered_items), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            exact_item_index: int = filtered_indices[i + (self._page * self._NUM_PER_PAGE)]
            self.add_item(ItemEquipButton(exact_item_index, item, i))
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(filtered_items) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        
        equipped_item: (Item | None) = player.get_equipment().get_item_in_slot(self._cur_equip_slot)
        if equipped_item is not None:
            self.add_item(UnequipButton(min(4, len(page_slots))))
        self.add_item(SelectSlotExitButton(min(4, len(page_slots))))

    def get_full_equipment_str(self):
        player_equipment: Equipment = self.get_player().get_equipment()
        base_none_equipped_str: str = "᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\nNone Equipped\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆"

        helmet = player_equipment.get_item_in_slot(ClassTag.Equipment.Helmet)
        gloves = player_equipment.get_item_in_slot(ClassTag.Equipment.Gloves)
        amulet = player_equipment.get_item_in_slot(ClassTag.Equipment.Amulet)
        ring = player_equipment.get_item_in_slot(ClassTag.Equipment.Ring)
        chest_armor = player_equipment.get_item_in_slot(ClassTag.Equipment.ChestArmor)
        main_hand = player_equipment.get_item_in_slot(ClassTag.Equipment.MainHand)
        off_hand = player_equipment.get_item_in_slot(ClassTag.Equipment.OffHand)
        leggings = player_equipment.get_item_in_slot(ClassTag.Equipment.Leggings)
        boots = player_equipment.get_item_in_slot(ClassTag.Equipment.Boots)

        equipment_strs = [
            f"**Helmet:**\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{str(helmet)}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆" if helmet is not None else "**Helmet:**\n" + base_none_equipped_str,
            f"**Gloves:**\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{str(gloves)}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆" if gloves is not None else "**Gloves:**\n" + base_none_equipped_str,
            f"**Amulet:**\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{str(amulet)}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆" if amulet is not None else "**Amulet:**\n" + base_none_equipped_str,
            f"**Ring:**\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{str(ring)}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆" if ring is not None else "**Ring:**\n" + base_none_equipped_str,
            f"**Chest Armor:**\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{str(chest_armor)}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆" if chest_armor is not None else "**Chest Armor:**\n" + base_none_equipped_str,
            f"**Main Hand:**\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{str(main_hand)}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆" if main_hand is not None else "**Main Hand:**\n" + base_none_equipped_str,
            f"**Off Hand:**\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{str(off_hand)}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆" if off_hand is not None else "**Off Hand:**\n" + base_none_equipped_str,
            f"**Leggings:**\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{str(leggings)}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆" if leggings is not None else "**Leggings:**\n" + base_none_equipped_str,
            f"**Boots:**\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{str(boots)}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆" if boots is not None else "**Boots:**\n" + base_none_equipped_str
        ]

        return "\n\n".join(equipment_strs)

    def get_initial_info(self):
        click_to_see_str = "\n\nChoose a slot to see currently equipped item and equip another or unequip it." if self._show_with_buttons else ""
        return Embed(
            title=f"{self._user.display_name}'s Equipment",
            description=f"{self.get_full_equipment_str()}{click_to_see_str}"
        )

    def exit_to_main_menu(self):
        self._cur_equip_slot = None
        self._display_slot_select_buttons()
        return self.get_initial_info()

    def _get_current_equip_page_info(self):
        player: Player = self.get_player()
        equipped_item: (Item | None) = player.get_equipment().get_item_in_slot(self._cur_equip_slot)

        if equipped_item is not None:
            return Embed(
                title=f"Equip to {self.get_str_for_slot(self._cur_equip_slot)}",
                description=f"᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{equipped_item}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\nChoose an item from your inventory to equip."
            )
        else:
            return Embed(
                title=f"Equip to {self.get_str_for_slot(self._cur_equip_slot)}",
                description=f"None equipped. Choose an item from your inventory to equip."
            )
        
    def next_page(self):
        self._page += 1
        self._get_current_page_buttons()
        return self._get_current_equip_page_info()

    def prev_page(self):
        self._page = max(0, self._page - 1)
        self._get_current_page_buttons()
        return self._get_current_equip_page_info()

    def get_user(self):
        return self._user
