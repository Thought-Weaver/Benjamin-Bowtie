from __future__ import annotations

from math import ceil
from random import choice, random

import discord
import itertools
import jsonpickle

from dataclasses import dataclass
from discord.embeds import Embed
from discord.ext import commands
from enum import StrEnum
from features.expertise import ExpertiseClass    
from features.npcs.npc import NPC
from features.npcs.summons.waveform import Waveform
from features.npcs.summons.crab_servant import CrabServant
from features.player import Player
from features.shared.ability import Ability
from features.shared.constants import COMPANION_BATTLE_POINTS, DEX_DODGE_SCALE, LUCK_CRIT_DMG_BOOST, LUCK_CRIT_SCALE
from features.shared.effect import Effect, EffectType, ItemEffectCategory
from features.shared.enums import ClassTag, Summons
from features.shared.item import LOADED_ITEMS, WeaponStats
from features.shared.statuseffect import *

from typing import Dict, List, TYPE_CHECKING, Tuple
if TYPE_CHECKING:
    from features.dueling import Dueling
    from features.expertise import Expertise
    from features.shared.item import Item

# -----------------------------------------------------------------------------
# DUEL VIEW AND GUI
# -----------------------------------------------------------------------------

class Intent(StrEnum):
    Attack = "Attack"
    Ability = "Ability"
    Item = "Item"


class AttackActionButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Attack")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            view.set_intent(Intent.Attack)
            view.set_targets_remaining_based_on_weapon()
            response = view.show_targets()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class AbilityActionButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Ability")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            view.set_intent(Intent.Ability)
            response = view.show_abilities()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ItemActionButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Item")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            view.set_intent(Intent.Item)
            response = view.show_items()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class TargetButton(discord.ui.Button):
    def __init__(self, label: str, target: Player | NPC, index: int, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=label, row=row)
        self._target = target
        self._index = index

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            response = view.select_target(self._target, self._index)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ChooseItemButton(discord.ui.Button):
    def __init__(self, exact_item_index: int, item: Item, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_name_and_count()}", row=row, emoji=item.get_icon())
        
        self._exact_item_index = exact_item_index
        self._item = item

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            response = view.select_item(self._exact_item_index, self._item)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ChooseAbilityButton(discord.ui.Button):
    def __init__(self, ability_index: int, ability: Ability, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{ability.get_name()}", row=row, emoji=ability.get_icon())
        
        self._ability_index = ability_index
        self._ability = ability

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            response = view.select_ability(self._ability_index, self._ability)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class BackToActionSelectButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.red, label="Back", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            response = view.exit_to_action_select()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ConfirmAbilityButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.green, label=f"Choose", row=row)
        
    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            response = view.confirm_ability()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ConfirmItemButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.green, label=f"Choose", row=row)
        
    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            response = view.confirm_item()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ContinueToNextActionButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label=f"Continue")
        
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        if self.view is None:
            return
        
        view: DuelView = self.view
        cur_turn_user: discord.User | None = view.get_user_for_current_turn()
        last_player_turn_user: discord.User | None = view.get_last_player_turn_user()
        if interaction.user == last_player_turn_user or interaction.user == cur_turn_user:
            assert(interaction.message is not None)

            self.disabled = True
            await interaction.followup.edit_message(message_id=interaction.message.id, content=None, view=view)

            response = view.continue_turn()
            await interaction.followup.edit_message(message_id=interaction.message.id, content=None, embed=response, view=view)


class BackUsingIntentButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.red, label=f"Back", row=row)
        
    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            response = view.go_back_using_intent()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class DoActionOnTargetsButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.green, label=f"Finish", row=row)
        
    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            response = view.do_action_on_selected_targets(is_finished=True)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ConfirmTargetButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.green, label=f"Choose", row=row)
        
    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            response = view.confirm_target()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class DuelingNextButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.blurple, label="Next", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            response = view.next_page()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class DuelingPrevButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.blurple, label="Prev", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            response = view.prev_page()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class SkipButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.red, label="Skip")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            response = view.continue_turn(skip_turn=True)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ContinueButton(discord.ui.Button):
    def __init__(self, new_view: discord.ui.View, player_loss: bool):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

        self._new_view = new_view
        self._player_loss = player_loss

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        if self._player_loss:
            view: DuelView = self.view
            for player in view.get_players():
                player.get_dungeon_run().in_dungeon_run = False

        embed = self._new_view.get_initial_embed() # type: ignore
        await interaction.response.edit_message(content=None, embed=embed, view=self._new_view)


class ScrollButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Scroll")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            response = view.scroll()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class DuelView(discord.ui.View):
    # Using a data class instead of a tuple to make the code more readable
    @dataclass
    class DuelResult():
        game_won: bool
        winners: List[Player | NPC] | None

    def __init__(self, bot: commands.Bot, database: dict, guild_id: int, users: List[discord.User], allies: List[Player | NPC], enemies: List[Player | NPC], skip_init_updates: bool=False, companion_battle:bool=False, player_victory_post_view:discord.ui.View | None=None, player_loss_post_view:discord.ui.View | None=None):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users

        self._allies: List[Player | NPC] = allies
        for ally in self._allies:
            self.add_summons(ally.get_equipment().get_summons_enums(ally), self._allies)

        self._enemies: List[Player | NPC] = enemies
        for enemy in self._enemies:
            self.add_summons(enemy.get_equipment().get_summons_enums(enemy), self._enemies)

        self._turn_order: List[Player | NPC] = sorted(self._allies + self._enemies, key=lambda x: x.get_combined_attributes().dexterity, reverse=True)
        self._turn_index: int = 0
        self._last_player_turn_user: discord.User | None = next(self.get_user_from_player(entity) for entity in self._turn_order if isinstance(entity, Player)) if not companion_battle else None

        self._companion_battle: bool = companion_battle
        self._companion_abilities: Dict[str, Ability] = {}

        # These are both used during dungeons to trigger associated win and loss event screens
        self._player_victory_post_view: discord.ui.View | None = player_victory_post_view
        self._player_loss_post_view: discord.ui.View | None = player_loss_post_view

        self._intent: (Intent | None) = None
        self._selected_targets: List[Player | NPC] = []
        self._targets_remaining = 1
        self._selected_ability: (Ability | None) = None
        self._selected_ability_index: int = -1
        self._selected_item: (Item | None) = None
        self._selected_item_index: int = -1
        self._target_own_group: bool = False
        self._current_target: Player | NPC | None = None # For passing along to the confirmation
        self._current_target_index: int = -1
        self._selecting_targets: bool = False # For next/prev buttons
        self._npc_initial_embed: Embed | None = None

        # Internal stats
        self.turns_taken: int = 0

        self._page = 0
        self._NUM_PER_PAGE = 4
        self._scroll_index = 0

        self._additional_info_string_data = ""

        if not skip_init_updates:
            for entity in allies + enemies:
                entity.get_dueling().is_in_combat = True
                entity.get_dueling().armor = entity.get_equipment().get_total_reduced_armor(entity.get_expertise().level, entity.get_expertise().get_all_attributes() + entity.get_equipment().get_total_attribute_mods())
                # Make sure stats are correct.
                entity.get_expertise().update_stats(entity.get_combined_attributes())

                if isinstance(entity, Player):
                    companions = entity.get_companions()
                    if companions.current_companion is not None:
                        companion_ability = companions.companions[companions.current_companion].get_dueling_ability(effect_category=None)
                        
                        if isinstance(companion_ability, Ability):
                            self._companion_abilities[entity.get_id()] = companion_ability
                            entity.get_dueling().temp_abilities.append(companion_ability)

                    if entity.get_dungeon_run().in_dungeon_run and entity.get_dungeon_run().corruption > 0:
                        entity.get_dueling().status_effects.append(Corrupted(-1, entity.get_dungeon_run().corruption))

                for ability in entity.get_equipment().get_granted_abilities(entity):
                    entity.get_dueling().temp_abilities.append(ability)

            cur_entity: (Player | NPC) = self._turn_order[self._turn_index]
            if isinstance(cur_entity, Player) or self._companion_battle:
                self.show_actions()
            else:
                self._npc_initial_embed = self.take_npc_turn()

    def get_players(self):
        return [self._get_player(user.id) for user in self._users]
    
    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_user_from_player(self, player: Player | NPC):
        for user in self._users:
            if str(user.id) == player.get_id():
                return user
        return None

    def get_user_for_current_turn(self):
        cur_turn_entity = self._turn_order[self._turn_index]
        if isinstance(cur_turn_entity, Player) or self._companion_battle:
            return self.get_user_from_player(cur_turn_entity)
        return None
    
    def get_last_player_turn_user(self):
        return self._last_player_turn_user

    def get_name(self, entity: Player | NPC):
        if isinstance(entity, NPC):
            return entity.get_name()
        user = self.get_user_from_player(entity)
        return user.display_name if user is not None else "Player Name"

    def get_turn_index(self, entity: Player | NPC):
        for i, other_entity in enumerate(self._turn_order):
            if other_entity == entity:
                return i
        return -1

    def get_entities_by_ids(self, ids: List[str]):
        entities: List[Player | NPC] = []
        for entity_id in ids:
            for entity in self._turn_order:
                if entity.get_id() == entity_id:
                    entities.append(entity)
        return entities

    def add_summons(self, summons: List[Summons], entity_list: List[Player | NPC]):
        for summon in summons:
            if summon == Summons.Waveform:
                entity_list.append(Waveform())
            elif summon == Summons.CrabServant:
                entity_list.append(CrabServant())

    def get_initial_embed(self):
        if self._npc_initial_embed is not None:
            return self._npc_initial_embed
        else:
            return self.show_actions()

    def check_for_win(self) -> DuelResult:
        allies_alive: List[Player | NPC] = list(filter(lambda x: x.get_expertise().hp != 0, self._allies))
        enemies_alive: List[Player | NPC] = list(filter(lambda x: x.get_expertise().hp != 0, self._enemies))
        
        if len(allies_alive) == 0 and len(enemies_alive) == 0: # Tie, which may happen due to reflected damage
            return self.DuelResult(True, None)
        if len(enemies_alive) == 0:
            return self.DuelResult(True, self._allies)
        if len(allies_alive) == 0:
            return self.DuelResult(True, self._enemies)
        
        return self.DuelResult(False, None)

    def _reset_turn_variables(self):
        self._intent = None
        self._selected_targets = []
        self._targets_remaining = 1
        self._selected_ability = None
        self._selected_ability_index = -1
        self._selected_item = None
        self._selected_item_index = -1
        self._target_own_group = False
        self._current_target = None
        self._current_target_index = -1
        self._selecting_targets = False
        self._page = 0

    def set_next_turn(self, init_info_str: str=""):
        self.turns_taken += 1
        
        previous_entity: Player | NPC = self._turn_order[self._turn_index]
        
        prev_item_status_effects: List[str] = previous_entity.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnTurnEnd, previous_entity, previous_entity, 0, 0, True)
        
        self._additional_info_string_data = init_info_str

        for result_str in prev_item_status_effects:
            formatted_str = result_str.format(self.get_name(previous_entity))
            self._additional_info_string_data += formatted_str + "\n"
        
        for item in previous_entity.get_equipment().get_all_equipped_items():
            item_effects = item.get_item_effects()
            if item_effects is None:
                continue
            for item_effect in item_effects.on_turn_end:
                result_str = previous_entity.get_dueling().apply_on_turn_start_or_end_effects(item, item_effect, previous_entity, self.get_name(previous_entity), is_turn_start=False, source_str=item.get_full_name())
                if result_str != "":
                    self._additional_info_string_data += result_str + "\n"

        if isinstance(previous_entity, Player):
            companions = previous_entity.get_companions()
            companion_key = companions.current_companion
            if companion_key is not None:
                current_companion = companions.companions[companion_key]
                companion_effect = current_companion.get_dueling_ability(effect_category=ItemEffectCategory.OnTurnEnd)
                if isinstance(companion_effect, Effect):
                    result_str = previous_entity.get_dueling().apply_on_turn_start_or_end_effects(None, companion_effect, previous_entity, self.get_name(previous_entity), is_turn_start=False, source_str=current_companion.get_icon_and_name())
                    if result_str != "":
                        self._additional_info_string_data += result_str + "\n"

        self._turn_index = (self._turn_index + 1) % len(self._turn_order)
        while self._turn_order[self._turn_index].get_expertise().hp == 0:
            self._turn_index = (self._turn_index + 1) % len(self._turn_order)

        entity: Player | NPC = self._turn_order[self._turn_index]

        if isinstance(entity, Player):
            self._last_player_turn_user = self.get_user_from_player(entity)

        item_status_effects: List[str] = previous_entity.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnTurnStart, entity, entity, 0, 0, True)
        
        for result_str in item_status_effects:
            formatted_str = result_str.format(self.get_name(previous_entity))
            self._additional_info_string_data += formatted_str + "\n"

        for item in entity.get_equipment().get_all_equipped_items():
            item_effects = item.get_item_effects()
            if item_effects is None:
                continue
            for item_effect in item_effects.on_turn_start:
                result_str = entity.get_dueling().apply_on_turn_start_or_end_effects(item, item_effect, entity, self.get_name(entity), is_turn_start=True, source_str=item.get_full_name())
                if result_str != "":
                    self._additional_info_string_data += result_str + "\n"
        
        if isinstance(entity, Player):
            companions = entity.get_companions()
            companion_key = companions.current_companion
            if companion_key is not None:
                current_companion = companions.companions[companion_key]
                companion_effect = current_companion.get_dueling_ability(effect_category=ItemEffectCategory.OnTurnStart)
                if isinstance(companion_effect, Effect):
                    result_str = entity.get_dueling().apply_on_turn_start_or_end_effects(None, companion_effect, entity, self.get_name(entity), is_turn_start=True, source_str=current_companion.get_icon_and_name())
                    if result_str != "":
                        self._additional_info_string_data += result_str + "\n"
        
        start_percent_damage: int = 0
        start_damage: int = 0
        start_heals: int = 0
        start_armor_restore: int = 0
        max_should_skip_chance: float = 0
        heals_from_poison: bool = any(se.key == StatusEffectKey.PoisonHeals for se in entity.get_dueling().status_effects)
        max_sleeping_chance: float = 0

        max_armor: int = entity.get_equipment().get_total_reduced_armor(entity.get_expertise().level, entity.get_expertise().get_all_attributes() + entity.get_equipment().get_total_attribute_mods())
    
        for se in entity.get_dueling().status_effects:
            if se.turns_remaining > 0 or se.turns_remaining == -1:
                if se.key == StatusEffectKey.FixedDmgTick:
                    start_damage += int(se.value)
                if se.key == StatusEffectKey.Bleeding:
                    start_percent_damage += ceil(entity.get_expertise().max_hp * se.value)
                if se.key == StatusEffectKey.Poisoned:
                    if heals_from_poison:
                        start_heals += ceil(entity.get_expertise().max_hp * se.value)
                    else:
                        start_percent_damage += ceil(entity.get_expertise().max_hp * se.value)
                if se.key == StatusEffectKey.RegenerateHP:
                    start_heals += ceil(entity.get_expertise().max_hp * se.value)
                if se.key == StatusEffectKey.RegenerateArmor:
                    start_armor_restore += ceil(max_armor * se.value)
                # Only take the largest chance to skip the turn
                if se.key == StatusEffectKey.TurnSkipChance:
                    max_should_skip_chance = max(se.value, max_should_skip_chance)
                if se.key == StatusEffectKey.Sleeping:
                    max_sleeping_chance = max(se.value, max_sleeping_chance)
            
        # Fixed damage is taken directly, no reduction, but still goes through armor
        if start_damage > 0:
            entity.get_expertise().damage(start_damage, entity.get_dueling(), percent_reduct=0, ignore_armor=False)
            if self._additional_info_string_data != "":
                self._additional_info_string_data += "\n"
            self._additional_info_string_data += f"{self.get_name(entity)} took {start_damage} damage! "

        # Percent damage is taken directly, no reduction and ignoring armor
        if start_percent_damage > 0:
            entity.get_expertise().damage(start_percent_damage, entity.get_dueling(), percent_reduct=0, ignore_armor=True)
            if self._additional_info_string_data != "":
                self._additional_info_string_data += "\n"
            self._additional_info_string_data += f"{self.get_name(entity)} took {start_percent_damage} damage! "

        decaying_adjustment: float = 0
        for se in entity.get_dueling().status_effects:
            if se.key == StatusEffectKey.Decaying:
                decaying_adjustment += se.value

        if decaying_adjustment != 0:
            start_heals += ceil(start_heals * -decaying_adjustment)

        entity.get_expertise().heal(start_heals)
        if start_heals > 0:
            if self._additional_info_string_data != "":
                self._additional_info_string_data += "\n"
            self._additional_info_string_data += f"{self.get_name(entity)} had {start_heals} health restored! "
        elif start_heals < 0:
            if self._additional_info_string_data != "":
                self._additional_info_string_data += "\n"
            self._additional_info_string_data += f"{self.get_name(entity)} took {start_heals} damage due to Decaying! "

        if start_armor_restore != 0:
            pre_armor: int = entity.get_dueling().armor
            entity.get_dueling().armor = min(entity.get_dueling().armor + start_armor_restore, max_armor)
            armor_restore_diff: int = entity.get_dueling().armor - pre_armor
            if armor_restore_diff != 0:
                if self._additional_info_string_data != "":
                    self._additional_info_string_data += "\n"
                self._additional_info_string_data += f"{self.get_name(entity)} had {armor_restore_diff} armor restored! "

        turn_skipped: bool = False
        if random() < max_should_skip_chance:
            self._turn_index = (self._turn_index + 1) % len(self._turn_order)
            if self._additional_info_string_data != "":
                self._additional_info_string_data += "\n"
            self._additional_info_string_data += f"{self.get_name(entity)}'s turn was skipped!"
            # This is a special case to make sure that Faltering doesn't always skip the entity; if it triggers,
            # then it has to be decremented to avoid potentially skipping their turn forever
            entity.get_dueling().decrement_all_ability_cds()
            entity.get_dueling().decrement_statuses_time_remaining()
            entity.get_expertise().update_stats(entity.get_combined_attributes())

        if random() < max_sleeping_chance and not turn_skipped:
            self._turn_index = (self._turn_index + 1) % len(self._turn_order)
            if self._additional_info_string_data != "":
                self._additional_info_string_data += "\n"
            self._additional_info_string_data += f"{self.get_name(entity)} is Sleeping and their turn was skipped!"
            # This is a special case to make sure that Sleeping doesn't always skip the entity; if it triggers,
            # then it has to be decremented to avoid potentially skipping their turn forever
            entity.get_dueling().decrement_all_ability_cds()
            entity.get_dueling().decrement_statuses_time_remaining()
            entity.get_expertise().update_stats(entity.get_combined_attributes())

        duel_result = self.check_for_win()
        if duel_result.game_won:
            return duel_result

        # Continue to iterate if the fixed damage killed the current entity
        while self._turn_order[self._turn_index].get_expertise().hp == 0:
            self._turn_index = (self._turn_index + 1) % len(self._turn_order)

        self._reset_turn_variables()

        return duel_result

    def _is_ally(self, entity: Player | NPC):
        cur_turn_player = self._turn_order[self._turn_index]
        
        self_charmed: bool = any(se.key == StatusEffectKey.Charmed for se in cur_turn_player.get_dueling().status_effects)
        entity_charmed: bool = any(se.key == StatusEffectKey.Charmed for se in entity.get_dueling().status_effects)

        if cur_turn_player in self._allies and not self_charmed:
            return entity in self._allies if not entity_charmed else entity in self._enemies
        else:
            return entity in self._enemies if not entity_charmed else entity in self._allies

    def get_duel_info_str(self):
        info_str = "᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n"
        for i, entity in enumerate(self._turn_order):
            group_icon = ":handshake:" if self._is_ally(entity) else ":imp:"

            max_reduced_armor: int = entity.get_equipment().get_total_reduced_armor(entity.get_expertise().level, entity.get_expertise().get_all_attributes() + entity.get_equipment().get_total_attribute_mods())
            armor_str: str = f"\n{entity.get_dueling().get_armor_string(max_reduced_armor)}" if max_reduced_armor > 0 or entity.get_dueling().armor > 0 else ""

            stats_hidden: bool = any(se.key == StatusEffectKey.StatsHidden for se in entity.get_dueling().status_effects)
            all_stats_str: str = f"{entity.get_expertise().get_health_and_mana_string()}{armor_str}" if not stats_hidden else "HP: ???\nMana: ???\nArmor: ???"
            info_str += f"({i + 1}) **{self.get_name(entity)}** {group_icon} (Lvl. {entity.get_expertise().level})\n\n{all_stats_str}"
            if len(entity.get_dueling().status_effects) > 0:
                statuses_str = entity.get_dueling().get_statuses_string()
                if statuses_str != "":
                    info_str += f"\n\n{statuses_str}"
            info_str += "\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n"

        cur_player = self.get_user_for_current_turn()
        player_name = cur_player.display_name if cur_player is not None else "Someone"

        additional_info_str = f"\n\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\n{self._additional_info_string_data}" if self._additional_info_string_data != "" else ""
        return info_str + f"\n*It's {player_name}'s turn!*{additional_info_str}"

    def get_selected_entity_full_duel_info_str(self):
        if self._current_target is None:
            return ""

        name = self.get_name(self._current_target)
        expertise = self._current_target.get_expertise()
        dueling = self._current_target.get_dueling()
        equipment = self._current_target.get_equipment()

        max_reduced_armor: int = equipment.get_total_reduced_armor(expertise.level, expertise.get_all_attributes() + equipment.get_total_attribute_mods())
        armor_str = f"\n{dueling.get_armor_string(max_reduced_armor)}" if max_reduced_armor > 0 or dueling.armor > 0 else ""

        stats_hidden: bool = any(se.key == StatusEffectKey.StatsHidden for se in dueling.status_effects)
        all_stats_str: str = f"{expertise.get_health_and_mana_string()}{armor_str}" if not stats_hidden else "HP: ???\nMana: ???\nArmor: ???"
        duel_string = f"᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n({self._current_target_index + 1}) **{name}**\n\n{all_stats_str}"
        if len(dueling.status_effects) > 0:
            duel_string += f"\n\n{dueling.get_statuses_string()}"

        return f"{duel_string}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆"

    def get_victory_screen(self, duel_result: DuelResult):
        self.clear_items()

        if duel_result.winners is None:
            for entity in self._turn_order:
                entity.get_dueling().status_effects = []
                entity.get_dueling().is_in_combat = False
                entity.get_dueling().reset_ability_cds()

                entity.get_expertise().update_stats(entity.get_combined_attributes())
                entity.get_expertise().hp = entity.get_expertise().max_hp
                entity.get_expertise().mana = entity.get_expertise().max_mana
                
                if not self._companion_battle:
                    entity.get_stats().dueling.duels_fought += 1
                    entity.get_stats().dueling.duels_tied += 1
                else:
                    entity.get_stats().companions.companion_battles_fought += 1
                    entity.get_stats().companions.companion_battles_tied += 1

                entity.get_expertise().level_up_check()

            if self._player_loss_post_view is not None:
                self.add_item(ContinueButton(self._player_loss_post_view, True))

            return Embed(
                title="Victory for Both and Neither",
                description="A hard-fought battle resulting in a tie. Neither side emerges truly victorious and yet both have defeated their enemies."
            )
        
        losers = self._allies if duel_result.winners == self._enemies else self._enemies

        if self._companion_battle:
            winner_owner_players: List[Player] = [self._database[str(self._guild_id)].get("members", {}).get(npc.get_id(), None) for npc in duel_result.winners]
            winner_str: str = ""
            for player in winner_owner_players:
                player.get_dueling().is_in_combat = False
                companion_key = player.get_companions().current_companion
                if companion_key is not None:
                    current_companion = player.get_companions().companions[companion_key]

                    xp_gained: int = ceil(4 * current_companion.pet_battle_xp_gain)
                    final_xp: int = current_companion.add_xp(xp_gained)

                    current_companion.add_companion_points(COMPANION_BATTLE_POINTS)

                    winner_str += f"{current_companion.get_icon_and_name()} *(+{final_xp} xp)*\n"

                    player.get_stats().companions.companion_battles_fought += 1
                    player.get_stats().companions.companion_battles_won += 1

            loser_owner_players: List[Player] = [self._database[str(self._guild_id)].get("members", {}).get(npc.get_id(), None) for npc in losers]
            loser_str: str = ""
            for player in loser_owner_players:
                player.get_dueling().is_in_combat = False

                companion_key = player.get_companions().current_companion
                if companion_key is not None:
                    current_companion = player.get_companions().companions[companion_key]
                    
                    loser_xp_gained: int = ceil(2 * current_companion.pet_battle_xp_gain)
                    loser_final_xp: int = current_companion.add_xp(loser_xp_gained)

                    current_companion.add_companion_points(COMPANION_BATTLE_POINTS)

                    loser_str += f"{current_companion.get_icon_and_name()} *(+{loser_final_xp} xp)*\n"

                    player.get_stats().companions.companion_battles_fought += 1

            result_str: str = f"To those victorious:\n\n{winner_str}\nAnd to those who were vanquished:\n\n{loser_str}"
            return Embed(title="Companion Battle Complete", description=f"Your bonds have grown stronger and your companions have gained experience.\n\n{result_str}")

        for winner in duel_result.winners:
            winner.get_stats().dueling.duels_fought += 1
            winner.get_stats().dueling.duels_won += 1
            winner.get_dueling().temp_abilities = []
        for loser in losers:
            loser.get_stats().dueling.duels_fought += 1
            loser.get_dueling().temp_abilities = []

        if all(isinstance(entity, Player) for entity in self._turn_order):
            # This should only happen in a PvP duel
            winner_str = ""
            winner_xp = ceil(0.75 * sum(loser.get_expertise().level for loser in losers) / len(duel_result.winners))
            for winner in duel_result.winners:
                winner_expertise = winner.get_expertise()
                winner_dueling = winner.get_dueling()
                
                final_winner_xp = winner_expertise.add_xp_to_class(winner_xp, ExpertiseClass.Guardian, winner.get_equipment())
                
                winner_dueling.reset_ability_cds()
                winner_dueling.status_effects = []
                winner_dueling.is_in_combat = False

                winner_expertise.update_stats(winner.get_combined_attributes())
                winner_expertise.hp = winner_expertise.max_hp
                winner_expertise.mana = winner_expertise.max_mana

                winner_expertise.level_up_check()

                winner_str += f"{self.get_name(winner)} *(+{final_winner_xp} Guardian xp)*\n"

                companion_xp_str: str = ""
                if isinstance(winner, Player):
                    companion_key = winner.get_companions().current_companion
                    if companion_key is not None:
                        companion = winner.get_companions().companions[companion_key]
                        final_comp_xp: int = companion.add_xp(companion.duel_xp_gain)

                        companion_xp_str += f"{companion.get_icon_and_name()} *(+{final_comp_xp} xp)*\n"
                
                if companion_xp_str != "":
                    winner_str += f"{companion_xp_str}\n"

            loser_str = ""
            loser_xp = ceil(sum(winner.get_expertise().level for winner in duel_result.winners) / (4 * len(losers)))
            for loser in losers:
                loser_expertise = loser.get_expertise()
                loser_dueling = loser.get_dueling()
                
                final_loser_xp = loser_expertise.add_xp_to_class(loser_xp, ExpertiseClass.Guardian, loser.get_equipment())

                loser_dueling.reset_ability_cds()
                loser_dueling.status_effects = []
                loser_dueling.is_in_combat = False

                loser_expertise.update_stats(loser.get_combined_attributes())
                loser_expertise.hp = loser_expertise.max_hp
                loser_expertise.mana = loser_expertise.max_mana

                loser_expertise.level_up_check()

                loser_str += f"{self.get_name(loser)} *(+{final_loser_xp} Guardian xp)*\n"

                loser_companion_xp_str: str = ""
                if isinstance(loser, Player):
                    companion_key = loser.get_companions().current_companion
                    if companion_key is not None:
                        companion = loser.get_companions().companions[companion_key]
                        loser_final_comp_xp: int = companion.add_xp(companion.duel_xp_gain)

                        loser_companion_xp_str += f"{companion.get_icon_and_name()} *(+{loser_final_comp_xp} xp)*\n"
                
                if loser_companion_xp_str != "":
                    loser_str += f"{loser_companion_xp_str}\n"

            return Embed(title="Duel Finished", description=f"To those victorious:\n\n{winner_str}\nAnd to those who were vanquished:\n\n{loser_str}\nPractice for the journeys yet to come.")
        elif all(isinstance(entity, NPC) for entity in self._enemies):

            if duel_result.winners == self._allies:
                if self._player_victory_post_view is not None:
                    self.add_item(ContinueButton(self._player_victory_post_view, False))
            else:
                if self._player_loss_post_view is not None:
                    self.add_item(ContinueButton(self._player_loss_post_view, True))

            winner_str = ""
            winner_xp = ceil(0.15 * sum(loser.get_expertise().level for loser in losers) / len(duel_result.winners))
            for winner in duel_result.winners:
                if isinstance(winner, Player):
                    winner_expertise = winner.get_expertise()
                    winner_dueling = winner.get_dueling()
                    
                    final_winner_xp = winner_expertise.add_xp_to_class(winner_xp, ExpertiseClass.Guardian, winner.get_equipment())
                    
                    winner_dueling.reset_ability_cds()
                    winner_dueling.status_effects = []
                    winner_dueling.is_in_combat = False

                    winner_expertise.update_stats(winner.get_combined_attributes())

                    winner_expertise.level_up_check()

                    winner_str += f"{self.get_name(winner)} *(+{final_winner_xp} Guardian xp)*\n"

                    winner_companion_xp_str: str = ""
                    companion_key = winner.get_companions().current_companion
                    if companion_key is not None:
                        companion = winner.get_companions().companions[companion_key]
                        winner_final_comp_xp: int = companion.add_xp(companion.duel_xp_gain)

                        winner_companion_xp_str += f"{companion.get_icon_and_name()} *(+{winner_final_comp_xp} xp)*\n"
                
                    if winner_companion_xp_str != "":
                        winner_str += f"{winner_companion_xp_str}\n"
                else:
                    winner_expertise = winner.get_expertise()
                    winner_dueling = winner.get_dueling()
                    
                    winner_dueling.reset_ability_cds()
                    winner_dueling.status_effects = []
                    winner_dueling.is_in_combat = False

                    winner_expertise.update_stats(winner.get_combined_attributes())
                    winner_expertise.hp = winner_expertise.max_hp
                    winner_expertise.mana = winner_expertise.max_mana

            for loser in losers:
                if isinstance(loser, Player):
                    loser_expertise = loser.get_expertise()
                    loser_dueling = loser.get_dueling()
                    
                    loser_dueling.reset_ability_cds()
                    loser_dueling.status_effects = []
                    loser_dueling.is_in_combat = False

                    loser_expertise.update_stats(loser.get_combined_attributes())

                    loser_companion_xp_str: str = ""
                    companion_key = loser.get_companions().current_companion
                    if companion_key is not None:
                        companion = loser.get_companions().companions[companion_key]
                        loser_final_comp_xp: int = companion.add_xp(companion.duel_xp_gain)

                        loser_companion_xp_str += f"{companion.get_icon_and_name()} *(+{loser_final_comp_xp} xp)*\n"
                
                    if loser_companion_xp_str != "":
                        winner_str += f"{loser_companion_xp_str}\n"
                else:
                    loser_expertise = loser.get_expertise()
                    loser_dueling = loser.get_dueling()
                    
                    loser_dueling.reset_ability_cds()
                    loser_dueling.status_effects = []
                    loser_dueling.is_in_combat = False

                    loser_expertise.update_stats(loser.get_combined_attributes())
                    loser_expertise.hp = loser_expertise.max_hp
                    loser_expertise.mana = loser_expertise.max_mana
            
            if losers == self._enemies:
                winner_str += "\n"
                player_winners = list(filter(lambda x: isinstance(x, Player), duel_result.winners))
                for loser in losers:
                    assert(isinstance(loser, NPC))
                    for reward_key, probability in loser.get_dueling_rewards().items():
                        if random() < probability:
                            new_item = LOADED_ITEMS.get_new_item(reward_key)
                            item_winner = choice(player_winners)
                            item_winner.get_inventory().add_item(new_item)
                            winner_str += f"{self.get_name(item_winner)} received {new_item.get_full_name_and_count()}\n"

            if any(isinstance(entity, Player) for entity in duel_result.winners):
                return Embed(title="Duel Finished", description=f"You are victorious:\n\n{winner_str}")
            else:
                return Embed(title="Duel Finished", description=f"You have been vanquished!")
        else: # In a completely mixed duel

            if duel_result.winners == self._allies:
                if self._player_victory_post_view is not None:
                    self.add_item(ContinueButton(self._player_victory_post_view, False))
            else:
                if self._player_loss_post_view is not None:
                    self.add_item(ContinueButton(self._player_loss_post_view, True))
            
            winner_str = ""
            winner_xp = ceil(0.15 * sum(loser.get_expertise().level for loser in losers) / len(duel_result.winners))
            for winner in duel_result.winners:
                if isinstance(winner, Player):
                    winner_expertise = winner.get_expertise()
                    winner_dueling = winner.get_dueling()
                    
                    final_winner_xp = winner_expertise.add_xp_to_class(winner_xp, ExpertiseClass.Guardian, winner.get_equipment())
                    
                    winner_dueling.reset_ability_cds()
                    winner_dueling.status_effects = []
                    winner_dueling.is_in_combat = False

                    winner_expertise.update_stats(winner.get_combined_attributes())

                    winner_expertise.level_up_check()

                    winner_str += f"{self.get_name(winner)} *(+{final_winner_xp} Guardian xp)*\n"

                    winner_companion_xp_str: str = ""
                    companion_key = winner.get_companions().current_companion
                    if companion_key is not None:
                        companion = winner.get_companions().companions[companion_key]
                        winner_final_comp_xp: int = companion.add_xp(companion.duel_xp_gain)

                        winner_companion_xp_str += f"{companion.get_icon_and_name()} *(+{winner_final_comp_xp} xp)*\n"
                
                    if winner_companion_xp_str != "":
                        winner_str += f"{winner_companion_xp_str}\n"
                else:
                    winner_expertise = winner.get_expertise()
                    winner_dueling = winner.get_dueling()
                    
                    winner_dueling.reset_ability_cds()
                    winner_dueling.status_effects = []
                    winner_dueling.is_in_combat = False

                    winner_expertise.update_stats(winner.get_combined_attributes())
                    winner_expertise.hp = winner_expertise.max_hp
                    winner_expertise.mana = winner_expertise.max_mana

            loser_str = ""
            loser_xp = ceil(sum(winner.get_expertise().level for winner in duel_result.winners) / (4 * len(losers)))
            for loser in losers:
                if isinstance(loser, Player):
                    loser_expertise = loser.get_expertise()
                    loser_dueling = loser.get_dueling()
                    
                    final_loser_xp = loser_expertise.add_xp_to_class(loser_xp, ExpertiseClass.Guardian, loser.get_equipment())

                    loser_dueling.reset_ability_cds()
                    loser_dueling.status_effects = []
                    loser_dueling.is_in_combat = False

                    loser_expertise.update_stats(loser.get_combined_attributes())

                    loser_expertise.level_up_check()

                    loser_str += f"{self.get_name(loser)} *(+{final_loser_xp} Guardian xp)*\n"

                    companion_xp_str: str = ""
                    companion_key = loser.get_companions().current_companion
                    if companion_key is not None:
                        companion = loser.get_companions().companions[companion_key]
                        final_comp_xp: int = companion.add_xp(companion.duel_xp_gain)

                        companion_xp_str += f"{companion.get_icon_and_name()} *(+{final_comp_xp} xp)*\n"
                
                    if companion_xp_str != "":
                        loser_str += f"{companion_xp_str}\n"
                else:
                    loser_expertise = loser.get_expertise()
                    loser_dueling = loser.get_dueling()
                    
                    loser_dueling.reset_ability_cds()
                    loser_dueling.status_effects = []
                    loser_dueling.is_in_combat = False

                    loser_expertise.update_stats(loser.get_combined_attributes())
                    loser_expertise.hp = loser_expertise.max_hp
                    loser_expertise.mana = loser_expertise.max_mana

                    loser_expertise.level_up_check()

            return Embed(title="Duel Finished", description=f"To those victorious:\n\n{winner_str}\nAnd to those who were vanquished:\n\n{loser_str}")

    def show_actions(self):
        self.clear_items()

        entity: Player | NPC = self._turn_order[self._turn_index]
        restricted_to_items: bool = any(se.key == StatusEffectKey.RestrictedToItems for se in entity.get_dueling().status_effects)
        cannot_attack: bool = any(se.key == StatusEffectKey.CannotAttack for se in entity.get_dueling().status_effects)
        cannot_use_abilities: bool = any(se.key == StatusEffectKey.CannotUseAbilities for se in entity.get_dueling().status_effects)

        taunt_target: Player | NPC | None = None
        for se in entity.get_dueling().status_effects:
            if se.key == StatusEffectKey.Taunted:
                # TODO: Why not just check this instead of using keys? Is there
                # any risk associated with it? Arguably, it's nicer to potentially
                # have the enum moved to the new enums file and avoid import issues.
                assert(isinstance(se, Taunted))
                taunt_target = se.forced_to_attack
                break

        if not restricted_to_items:
            if not cannot_attack:
                self.add_item(AttackActionButton())
                if taunt_target is not None:
                    self._selecting_targets = False
                    self._intent = Intent.Attack
                    self._selected_targets = [taunt_target]
                    return self.do_action_on_selected_targets()
            else:
                if taunt_target is not None:
                    self.continue_turn(skip_turn=True)
            
            if not cannot_use_abilities:
                self.add_item(AbilityActionButton())
        else:
            if taunt_target is not None:
                self.continue_turn(skip_turn=True)

        self.add_item(ItemActionButton())
        self.add_item(SkipButton())

        self._reset_turn_variables()

        duel_info_str = self.get_duel_info_str()
        if len(duel_info_str) > 1000:
            self.add_item(ScrollButton())

        return Embed(title="Choose an Action", description=duel_info_str[self._scroll_index:])

    def scroll(self):
        duel_info_str = self.get_duel_info_str()
        self._scroll_index += 1000
        if self._scroll_index > len(duel_info_str):
            self._scroll_index = 0

        return Embed(title="Choose an Action", description=duel_info_str[self._scroll_index:])

    def set_intent(self, intent: Intent):
        self._intent = intent

    def filter_entity(self, entity: Player | NPC, entities: List[Player | NPC]):
        return [other for other in entities if other.get_id() != entity.get_id()]

    def show_targets(self, target_own_group: bool=False):
        self.clear_items()

        self._selecting_targets = True

        cur_turn_entity: Player = self._turn_order[self._turn_index] # type: ignore

        selected_target_names = "\n".join(list(map(lambda x: self.get_name(x), self._selected_targets)))
        selected_targets_str = f"Selected Targets:\n\n{selected_target_names}\n\n" if len(selected_target_names) > 0 else ""
        
        self._target_own_group = target_own_group and self._intent != Intent.Attack

        # This should only be called for a Player
        targets: List[Player | NPC] = []

        # In the special case of attacking with a weapon, display information about the weapon so the user is informed.
        main_hand_item = cur_turn_entity.get_equipment().get_item_in_slot(ClassTag.Equipment.MainHand)
        unarmed_strength_bonus = int(cur_turn_entity.get_combined_attributes().strength / 2)
        weapon_stats = WeaponStats(1 + unarmed_strength_bonus, 2 + unarmed_strength_bonus) if main_hand_item is None else main_hand_item.get_weapon_stats()
        description = "" if self._intent != Intent.Attack else f"{self.get_name(cur_turn_entity)} is attacking with {main_hand_item.get_full_name() if main_hand_item is not None else 'a good slap'} for {weapon_stats.get_range_str()}.\n\n"

        if self._current_target is not None:
            description += self.get_selected_entity_full_duel_info_str() + "\n\n"

        charmed: bool = any(se.key == StatusEffectKey.Charmed for se in cur_turn_entity.get_dueling().status_effects)
            
        if (cur_turn_entity in self._enemies and target_own_group) or (cur_turn_entity in self._allies and not target_own_group):
            targets = self.filter_entity(cur_turn_entity, self._enemies) if not charmed else self.filter_entity(cur_turn_entity, self._allies)
            target_str = "target" if self._targets_remaining == 1 else "targets"
            ally_or_op_str = "ally" if target_own_group else "opponent"
            description += f"{selected_targets_str}Choose an {ally_or_op_str}. {self._targets_remaining} {target_str} remaining."
        elif (cur_turn_entity in self._enemies and not target_own_group) or (cur_turn_entity in self._allies and target_own_group):
            targets = self.filter_entity(cur_turn_entity, self._allies) if not charmed else self.filter_entity(cur_turn_entity, self._enemies)
            target_str = "target" if self._targets_remaining == 1 else "targets"
            ally_or_op_str = "ally" if target_own_group else "opponent"
            description += f"{selected_targets_str}Choose an {ally_or_op_str}. {self._targets_remaining} {target_str} remaining."

        all_targets = targets[self._page * self._NUM_PER_PAGE:min(len(targets), (self._page + 1) * self._NUM_PER_PAGE)]
        filtered_targets = list(filter(lambda target: target.get_expertise().hp > 0, all_targets)) if not self._target_own_group else all_targets
        page_slots = sorted(filtered_targets, key=lambda target: self.get_turn_index(target))
        for i, target in enumerate(page_slots):
            turn_number: int = self.get_turn_index(target)
            self.add_item(TargetButton(f"({turn_number + 1}) {self.get_name(target)}", target, turn_number, i))

        if self._page != 0:
            self.add_item(DuelingPrevButton(min(4, len(page_slots))))
        if len(targets) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(DuelingNextButton(min(4, len(page_slots))))
        if self._current_target is not None and self._current_target_index != -1:
            self.add_item(ConfirmTargetButton(min(4, len(page_slots))))
        if len(self._selected_targets) > 0:
            # This handles the cases where you might not want/need to select the max number
            # of possible targets.
            self.add_item(DoActionOnTargetsButton(min(4, len(page_slots))))
        self.add_item(BackUsingIntentButton(min(4, len(page_slots))))

        return Embed(title="Choose a Target", description=description)

    def attack_selected_targets(self):
        attacker = self._turn_order[self._turn_index]
        attacker_name = self.get_name(attacker)
        attacker_attrs = attacker.get_combined_attributes()
        attacker_equipment = attacker.get_equipment()

        dmg_buff_effect_totals: Dict[EffectType, float] = attacker_equipment.get_dmg_buff_effect_totals(attacker)
        critical_hit_dmg_buff: float = min(max(dmg_buff_effect_totals[EffectType.CritDmgBuff] - dmg_buff_effect_totals[EffectType.CritDmgReduction], 1), 0)
        self_hp_dmg_buff: int = ceil(dmg_buff_effect_totals[EffectType.DmgBuffSelfMaxHealth] * attacker.get_expertise().max_hp) + ceil(dmg_buff_effect_totals[EffectType.DmgBuffSelfRemainingHealth] * attacker.get_expertise().hp)

        generating_value = 0
        tarnished_value = 0
        bonus_damage: int = 0
        bonus_percent_damage: float = 1 + dmg_buff_effect_totals[EffectType.DmgBuff]
        chance_status_effect: List[Tuple[StatusEffect, float]] = []
        for se in attacker.get_dueling().status_effects:
            if se.key == StatusEffectKey.Generating:
                generating_value = se.value
            elif se.key == StatusEffectKey.Tarnished:
                tarnished_value = se.value
            elif se.key == StatusEffectKey.BonusDamageOnAttack:
                bonus_damage += int(se.value)
            elif se.key == StatusEffectKey.DmgBuff:
                bonus_percent_damage += se.value
            elif se.key == StatusEffectKey.DmgDebuff:
                bonus_percent_damage -= se.value
            elif isinstance(se, AttackingChanceToApplyStatus):
                chance_status_effect.append((se.status_effect, se.value))
        cursed_coins_damage = 0

        main_hand_item = attacker_equipment.get_item_in_slot(ClassTag.Equipment.MainHand)
        level_req: int = main_hand_item.get_level_requirement() if main_hand_item is not None else 0
        # Base possible damage is [1, 2], basically fist fighting
        unarmed_strength_bonus = int(attacker_attrs.strength / 2)
        weapon_stats = WeaponStats(1 + unarmed_strength_bonus, 2 + unarmed_strength_bonus) if main_hand_item is None else main_hand_item.get_weapon_stats()
        item_effects = main_hand_item.get_item_effects() if main_hand_item is not None else None

        splash_dmg: int = 0
        splash_percent_dmg: float = 0
        piercing_dmg: int = 0
        piercing_percent_dmg: float = 0
        for item in attacker_equipment.get_all_equipped_items():
            other_item_effects = item.get_item_effects()
            if other_item_effects is not None:
                for item_effect in other_item_effects.permanent:
                    if not item_effect.meets_conditions(attacker, item):
                        continue

                    if item_effect.effect_type == EffectType.SplashDmg:
                        splash_dmg += int(item_effect.effect_value)
                    elif item_effect.effect_type == EffectType.SplashPercentMaxDmg and weapon_stats is not None:
                        splash_percent_dmg += ceil(weapon_stats.get_max_damage() * item_effect.effect_value)
                    elif item_effect.effect_type == EffectType.PiercingDmg:
                        piercing_dmg += int(item_effect.effect_value)
                    elif item_effect.effect_type == EffectType.PiercingPercentDmg:
                        piercing_percent_dmg = min(piercing_percent_dmg + item_effect.effect_value, 1)

        result_strs = [f"{attacker_name} attacked using {main_hand_item.get_full_name() if main_hand_item is not None else 'a good slap'}!\n"]
        for i, target in enumerate(self._selected_targets):
            target_expertise = target.get_expertise()
            target_equipment = target.get_equipment()
            target_dueling = target.get_dueling()
            target_attrs = target.get_combined_attributes()

            target_name = self.get_name(target)
            target_dodged = random() < target_attrs.dexterity * DEX_DODGE_SCALE
            
            if target_dodged:
                target.get_stats().dueling.attacks_dodged += 1
                result_strs.append(f"{target_name} dodged the attack")
                continue

            critical_hit_boost = LUCK_CRIT_DMG_BOOST if random() < attacker_attrs.luck * LUCK_CRIT_SCALE else 1

            if critical_hit_boost > 1:
                attacker.get_stats().dueling.critical_hit_successes += 1
 
            critical_hit_final = max(critical_hit_boost + critical_hit_dmg_buff, 1) if critical_hit_boost > 1 else 1 
            base_damage = weapon_stats.get_random_damage(attacker_attrs, item_effects, max(0, level_req - attacker.get_expertise().level))

            stacking_damage: float = 1
            poison_buff_applied: bool = False
            bleeding_buff_applied: bool = False
            for se in target_dueling.status_effects:
                if se.key == StatusEffectKey.StackingDamage:
                    assert(isinstance(se, StackingDamage))
                    if main_hand_item is not None and se.caster == attacker and se.source_str == main_hand_item.get_full_name():
                        stacking_damage += se.value
                elif se.key == StatusEffectKey.Poisoned and not poison_buff_applied:
                    bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffPoisoned]
                    poison_buff_applied = True
                elif se.key == StatusEffectKey.Bleeding and not bleeding_buff_applied:
                    bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffBleeding]
                    bleeding_buff_applied = True
            
            if target_dueling.is_legendary:
                bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffLegends]

            target_hp_dmg_buff: int = ceil(dmg_buff_effect_totals[EffectType.DmgBuffOtherMaxHealth] * target.get_expertise().max_hp) + ceil(dmg_buff_effect_totals[EffectType.DmgBuffOtherRemainingHealth] * target.get_expertise().hp)
            
            damage = ceil(base_damage * stacking_damage)
            damage = ceil(damage * critical_hit_final * bonus_percent_damage) 
            damage += bonus_damage + target_hp_dmg_buff + self_hp_dmg_buff

            final_piercing_dmg = piercing_dmg + ceil(piercing_percent_dmg * base_damage)
            damage = max(damage - final_piercing_dmg, 0)

            # Doing these after damage computation because the player doesn't get an indication the effect occurred
            # until the Continue screen, so it feels slightly more natural to have them not affect damage dealt. I
            # may reverse this decision later.
            result_strs += [s.format(target_name, attacker_name) for s in attacker.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnSuccessfulAttack, target, attacker, 0, 1, self._is_ally(target))]
            for se, chance in chance_status_effect:
                if random() < chance:
                    result_strs += target.get_dueling().add_status_effect_with_resist(se, target, 0).format(target_name)

            for item in attacker_equipment.get_all_equipped_items():
                other_item_effects = item.get_item_effects()
                if other_item_effects is None:
                    continue
                for item_effect in other_item_effects.on_successful_attack:
                    damage, result_str = attacker.get_dueling().apply_on_successful_attack_or_ability_effects(item, item_effect, attacker, target, 1, damage, item.get_full_name())
                    if result_str != "":
                        result_strs.append(result_str.format(attacker_name, target_name))

            if isinstance(attacker, Player):
                companions = attacker.get_companions()
                companion_key = companions.current_companion
                if companion_key is not None:
                    current_companion = companions.companions[companion_key]
                    companion_effect = current_companion.get_dueling_ability(effect_category=ItemEffectCategory.OnSuccessfulAttack)
                    if isinstance(companion_effect, Effect):
                        damage, result_str = attacker.get_dueling().apply_on_successful_attack_or_ability_effects(None, companion_effect, attacker, target, 1, damage, current_companion.get_icon_and_name())
                        if result_str != "":
                            result_strs.append(result_str.format(attacker_name, target_name))

            result_strs += [s.format(attacker_name, target_name) for s in target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnAttacked, attacker, target, 0, 1, self._is_ally(target))]

            for item in target_equipment.get_all_equipped_items():
                other_item_effects = item.get_item_effects()
                if other_item_effects is None:
                    continue
                for item_effect in other_item_effects.on_attacked:
                    damage, result_str = target.get_dueling().apply_on_attacked_or_damaged_effects(item, item_effect, target, attacker, 1, damage, item.get_full_name())
                    if result_str != "":
                        result_strs.append(result_str.format(attacker_name, target_name))

            if isinstance(attacker, Player):
                companions = attacker.get_companions()
                companion_key = companions.current_companion
                if companion_key is not None:
                    current_companion = companions.companions[companion_key]
                    companion_effect = current_companion.get_dueling_ability(effect_category=ItemEffectCategory.OnAttacked)
                    if isinstance(companion_effect, Effect):
                        damage, result_str = attacker.get_dueling().apply_on_attacked_or_damaged_effects(None, companion_effect, target, attacker, 1, damage, current_companion.get_icon_and_name())
                        if result_str != "":
                            result_strs.append(result_str.format(attacker_name, target_name))

            percent_dmg_reduct = target_dueling.get_total_percent_dmg_reduct(target.get_combined_req_met_effects())

            org_armor = target_dueling.armor
            actual_damage_dealt = target_expertise.damage(damage, target_dueling, percent_dmg_reduct, ignore_armor=False)
            piercing_damage_dealt = target_expertise.damage(final_piercing_dmg, target_dueling, percent_dmg_reduct, ignore_armor=True)

            if (actual_damage_dealt > 0 or piercing_damage_dealt > 0) and target.get_expertise().hp > 0:
                result_strs += [s.format(attacker_name, target_name) for s in target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnDamaged, attacker, target, 0, 1, self._is_ally(target))]
                for item in target_equipment.get_all_equipped_items():
                    other_item_effects = item.get_item_effects()
                    if other_item_effects is None:
                        continue
                    for item_effect in other_item_effects.on_damaged:
                        _, result_str = target.get_dueling().apply_on_attacked_or_damaged_effects(item, item_effect, target, attacker, 1, actual_damage_dealt, item.get_full_name())
                        if result_str != "":
                            result_strs.append(result_str.format(attacker_name, target_name))

                if isinstance(attacker, Player):
                    companions = attacker.get_companions()
                    companion_key = companions.current_companion
                    if companion_key is not None:
                        current_companion = companions.companions[companion_key]
                        companion_effect = current_companion.get_dueling_ability(effect_category=ItemEffectCategory.OnDamaged)
                        if isinstance(companion_effect, Effect):
                            damage, result_str = attacker.get_dueling().apply_on_attacked_or_damaged_effects(None, companion_effect, target, attacker, 1, damage, current_companion.get_icon_and_name())
                            if result_str != "":
                                result_strs.append(result_str.format(attacker_name, target_name))

            attacker.get_stats().dueling.damage_dealt += actual_damage_dealt + piercing_damage_dealt
            target.get_stats().dueling.damage_taken += actual_damage_dealt + piercing_damage_dealt
            target.get_stats().dueling.damage_blocked_or_reduced += damage - actual_damage_dealt + final_piercing_dmg - piercing_damage_dealt

            dmg_reflect: float = 0
            for se in target_dueling.status_effects:
                if se.key == StatusEffectKey.AttrBuffOnDamage:
                    assert(isinstance(se, AttrBuffOnDamage))
                    target_dueling.status_effects += list(map(lambda s: s.set_trigger_first_turn(target != attacker), se.on_being_hit_buffs))
                    result_strs.append(f"{target_name} gained {se.get_buffs_str()}")
                elif se.key == StatusEffectKey.DmgReflect:
                    dmg_reflect += se.value
            
            for effect in target.get_combined_req_met_effects().permanent:
                if effect.effect_type == EffectType.DmgReflect:
                    dmg_reflect += effect.effect_value

            if dmg_reflect > 0:
                reflected_damage: int = ceil(damage * dmg_reflect)
                attacker_dmg_reduct = attacker.get_dueling().get_total_percent_dmg_reduct(attacker.get_combined_req_met_effects())

                attacker_org_armor = attacker.get_dueling().armor
                actual_reflected_damage = attacker.get_expertise().damage(reflected_damage, attacker.get_dueling(), attacker_dmg_reduct, ignore_armor=False)
                attacker_cur_armor = attacker.get_dueling().armor
                
                attacker_dmg_reduct_str = f" ({abs(attacker_dmg_reduct) * 100}% {'Reduction' if attacker_dmg_reduct > 0 else 'Increase'})" if attacker_dmg_reduct != 0 else ""
                reflect_armor_str = f" ({attacker_cur_armor - attacker_org_armor} Armor)" if attacker_cur_armor - attacker_org_armor < 0 else ""

                result_strs.append(f"{target_name} reflected {actual_reflected_damage}{reflect_armor_str}{attacker_dmg_reduct_str} back to {attacker_name}")

            target.get_expertise().update_stats(target.get_combined_attributes())

            generating_string = ""
            if generating_value != 0:
                attacker.get_inventory().add_coins(int(generating_value))
                generating_string = f" and gained {generating_value} coins"

                if tarnished_value != 0:
                    cursed_coins_damage += ceil(tarnished_value * generating_value)
            
            critical_hit_str = "" if critical_hit_boost == 1 else " [Crit!]"
            percent_dmg_reduct_str = f" ({abs(percent_dmg_reduct) * 100}% {'Reduction' if percent_dmg_reduct > 0 else 'Increase'})" if percent_dmg_reduct != 0 else ""
            armor_str = f" ({target_dueling.armor - org_armor} Armor)" if target_dueling.armor - org_armor < 0 else ""
            piercing_str = f" ({piercing_damage_dealt} Piercing)" if piercing_damage_dealt > 0 else ""

            result_strs.append(f"{attacker_name} dealt {actual_damage_dealt}{piercing_str}{armor_str}{percent_dmg_reduct_str}{critical_hit_str} damage to {target_name}{generating_string}")
        
            attacker.get_stats().dueling.attacks_done += 1
        
        if cursed_coins_damage != 0:
            if attacker in self._enemies:
                for other in self._allies:
                    org_armor = other.get_dueling().armor
                    percent_dmg_reduct = other.get_dueling().get_total_percent_dmg_reduct(other.get_combined_req_met_effects())
                    actual_cc_damage = other.get_expertise().damage(cursed_coins_damage, other.get_dueling(), percent_dmg_reduct, ignore_armor=False)

                    armor_str = f" ({other.get_dueling().armor - org_armor} Armor)" if other.get_dueling().armor - org_armor < 0 else ""

                    attacker.get_stats().dueling.damage_dealt += actual_cc_damage
                    other.get_stats().dueling.damage_taken += actual_cc_damage

                    result_strs.append(f"{attacker_name} dealt {actual_cc_damage}{armor_str} damage to {self.get_name(other)} using Cursed Coins")
            elif attacker in self._allies:
                for other in self._enemies:
                    org_armor = other.get_dueling().armor
                    percent_dmg_reduct = other.get_dueling().get_total_percent_dmg_reduct(other.get_combined_req_met_effects())
                    actual_cc_damage = other.get_expertise().damage(cursed_coins_damage, other.get_dueling(), percent_dmg_reduct, ignore_armor=False)

                    armor_str = f" ({other.get_dueling().armor - org_armor} Armor)" if other.get_dueling().armor - org_armor < 0 else ""

                    attacker.get_stats().dueling.damage_dealt += actual_cc_damage
                    other.get_stats().dueling.damage_taken += actual_cc_damage

                    result_strs.append(f"{attacker_name} dealt {actual_cc_damage}{armor_str} damage to {self.get_name(other)} using Cursed Coins")

        if splash_dmg > 0 or splash_percent_dmg > 0:
            if attacker in self._enemies:
                for target in self._allies:
                    org_armor = target.get_dueling().armor
                    percent_dmg_reduct = target.get_dueling().get_total_percent_dmg_reduct(target.get_combined_req_met_effects())
                    damage_dealt = target.get_expertise().damage(splash_dmg + splash_percent_dmg, target.get_dueling(), percent_dmg_reduct, ignore_armor=False)

                    armor_str = f" ({target.get_dueling().armor - org_armor} Armor)" if target.get_dueling().armor - org_armor < 0 else ""

                    attacker.get_stats().dueling.damage_dealt += damage_dealt
                    target.get_stats().dueling.damage_taken += damage_dealt

                    result_strs.append(f"{attacker_name} dealt {damage_dealt}{armor_str} splash damage to {self.get_name(target)}")
            else:
                for target in self._enemies:
                    org_armor = target.get_dueling().armor
                    percent_dmg_reduct = target.get_dueling().get_total_percent_dmg_reduct(target.get_combined_req_met_effects())
                    damage_dealt = target.get_expertise().damage(splash_dmg + splash_percent_dmg, target.get_dueling(), percent_dmg_reduct, ignore_armor=False)

                    armor_str = f" ({target.get_dueling().armor - org_armor} Armor)" if target.get_dueling().armor - org_armor < 0 else ""

                    attacker.get_stats().dueling.damage_dealt += damage_dealt
                    target.get_stats().dueling.damage_taken += damage_dealt

                    result_strs.append(f"{attacker_name} dealt {damage_dealt}{armor_str} splash damage to {self.get_name(target)}")

        return "\n".join(result_strs)

    def use_ability_on_selected_targets(self):
        assert(self._selected_ability is not None)

        caster = self._turn_order[self._turn_index]

        # Avoid the player targeting and getting multiple triggers on enemies that are already dead -- this should
        # only be relevant for abilities that target all enemies or everyone, since the abilities that ask you to
        # select targets already filter out dead enemies
        if not self._selected_ability.get_target_own_group():
            self._selected_targets = list(filter(lambda entity: entity.get_expertise().hp > 0, self._selected_targets))

        names = [self.get_name(caster), *list(map(lambda x: self.get_name(x), self._selected_targets))]
        result_str = self._selected_ability.use_ability(caster, self._selected_targets)

        self._selected_ability.set_turn_after_lapsed(False)

        caster.get_stats().dueling.abilities_used += 1
        xp_str: str = ""
        if isinstance(caster, Player):
            xp_to_add: int = ceil(self._selected_ability.get_level_requirement() / 4)
            class_key: ExpertiseClass = self._selected_ability.get_class_key()
            final_xp = caster.get_expertise().add_xp_to_class(xp_to_add, class_key, caster.get_equipment())
            xp_str = f"\n\n*You gained {final_xp} {class_key} xp!*"

        return result_str.format(*names) + xp_str

    def use_item_on_selected_targets(self):
        assert(self._selected_item is not None)

        applicator = self._turn_order[self._turn_index]
        applicator_dueling = applicator.get_dueling()
        applicator_name = self.get_name(applicator)

        potion_effect_mod: float = 1.0
        if ClassTag.Consumable.Potion in self._selected_item.get_class_tags():
            for se in applicator.get_dueling().status_effects:
                if se.key == StatusEffectKey.PotionBuff:
                    potion_effect_mod += se.value
            for item in applicator.get_equipment().get_all_equipped_items():
                for item_effect in item.get_item_effects().permanent:
                    if item_effect.effect_type == EffectType.PotionMod:
                        potion_effect_mod += item_effect.effect_value

        result_strs = []
        for target in self._selected_targets:
            target_name = self.get_name(target)
            result_strs += [s.format(target_name, applicator_name) for s in target.get_dueling().apply_chance_status_effect_from_item(ItemEffectCategory.Permanent, self._selected_item, target, applicator, 0, 1, self._is_ally(target), potion_effect_mod)]
            item_effects = self._selected_item.get_item_effects()
            if item_effects is not None:
                for effect in item_effects.permanent:
                    result_str = applicator_dueling.apply_consumable_item_effect(self._selected_item, effect, applicator, target, potion_effect_mod)
                    result_strs.append(result_str.format(applicator_name, self.get_name(target)))

        applicator.get_inventory().remove_item(self._selected_item_index, 1)
        applicator.get_stats().dueling.items_used += 1
        
        return "\n".join(result_strs)

    def confirm_target(self):
        if self._current_target is None:
            return self.show_targets()

        selected_target_names = "\n".join(list(map(lambda x: self.get_name(x), self._selected_targets)))
        selected_targets_str = f"Current Targets:\n\n{selected_target_names}\n\n" if len(selected_target_names) > 0 else ""

        if self._current_target != self._turn_order[self._current_target_index]:
            return Embed(title="Choose a Target", description=f"{selected_targets_str}*Error: That target changed position in the turn order or something else terrible happened.*\n\n{self._targets_remaining} targets remaining.")
        
        if self._current_target in self._selected_targets:
            return Embed(title="Choose a Target", description=f"{selected_targets_str}You already selected that target. {self._targets_remaining} targets remaining.")
        
        entity = self._turn_order[self._turn_index]
        if any(isinstance(se, CannotTarget) and se.cant_target == entity for se in entity.get_dueling().status_effects):
            return Embed(title="Choose a Target", description=f"{selected_targets_str}You can't select that target due to being Convinced. {self._targets_remaining} targets remaining.")

        self._selected_targets.append(self._current_target)
        self._targets_remaining -= 1
        self._current_target = None

        return self.do_action_on_selected_targets()

    def do_action_on_selected_targets(self, is_finished=False):
        # I'm using a boolean for that case at the moment rather than setting self._targets_remaining to 0, just to
        # make a clear distinction about this case in the code.
        if self._targets_remaining <= 0 or is_finished:
            self._page = 0
            self.clear_items()
            self.add_item(ContinueToNextActionButton())

            catch_phrases = []
            result_str = ""
            if self._intent == Intent.Attack:
                catch_phrases = [
                    "Now, strike!",
                    "Yield to none!",
                    "Glory is yours!"
                ]
                result_str = self.attack_selected_targets()
            if self._intent == Intent.Ability:
                catch_phrases = [
                    "Behold true power!",
                    "Surge as they crumble!",
                    "Calamity unleashed!"
                ]
                result_str = self.use_ability_on_selected_targets()
            if self._intent == Intent.Item:
                catch_phrases = [
                    "A useful trinket!",
                    "The time is now!",
                    "A perfect purpose!"
                ]
                result_str = self.use_item_on_selected_targets()
            
            return Embed(title=choice(catch_phrases), description=result_str)
        self._page = 0
        self._selecting_targets = True
        return self.show_targets(self._target_own_group)

    def show_items(self, error_str: str | None=None):
        self._page = 0
        self._get_current_items_page_buttons()
        return self._get_current_page_info(error_str)

    def show_abilities(self, error_str: str | None=None):
        self._page = 0
        self._get_current_abilities_page_buttons()
        return self._get_current_page_info(error_str)

    def _get_current_items_page_buttons(self):
        self.clear_items()
        player: Player = self._turn_order[self._turn_index] # type: ignore
        inventory = player.get_inventory()
        inventory_slots = inventory.get_inventory_slots()

        filtered_indices = inventory.filter_inventory_slots([ClassTag.Consumable.UsableWithinDuels])
        filtered_items = [inventory_slots[i] for i in filtered_indices]

        page_slots = filtered_items[self._page * self._NUM_PER_PAGE:min(len(filtered_items), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            exact_item_index: int = filtered_indices[i + (self._page * self._NUM_PER_PAGE)]
            self.add_item(ChooseItemButton(exact_item_index, item, i))
        
        if self._page != 0:
            self.add_item(DuelingPrevButton(min(4, len(page_slots))))
        if len(filtered_items) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(DuelingNextButton(min(4, len(page_slots))))
        
        if self._selected_item is not None:
            self.add_item(ConfirmItemButton(min(4, len(page_slots))))
        self.add_item(BackToActionSelectButton(min(4, len(page_slots))))

    def _get_current_abilities_page_buttons(self):
        self.clear_items()
        player: Player = self._turn_order[self._turn_index] # type: ignore
        expertise: Expertise = player.get_expertise()
        dueling: Dueling = player.get_dueling()
        # Theoretically, this should only account for equipment/expertise, but if I add in an ability that reduces memory,
        # I'll want to make sure I'm using this combined attributes function.
        available_memory: int = max(0, player.get_combined_attributes().memory)
        combined_abilities = dueling.abilities[:available_memory] + dueling.temp_abilities

        page_slots = combined_abilities[self._page * self._NUM_PER_PAGE:min(len(combined_abilities), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, ability in enumerate(page_slots):
            self.add_item(ChooseAbilityButton(i + (self._page * self._NUM_PER_PAGE), ability, i))
        
        if self._page != 0:
            self.add_item(DuelingPrevButton(min(4, len(page_slots))))
        if len(combined_abilities) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(DuelingNextButton(min(4, len(page_slots))))

        sanguinated_active = any(se.key == StatusEffectKey.ManaToHP for se in dueling.status_effects)
        mana_cost_adjustment = 0
        for effect in player.get_combined_req_met_effects().permanent:
            if effect.effect_type == EffectType.AdjustedManaCosts:
                mana_cost_adjustment = max(mana_cost_adjustment + effect.effect_value, -1)

        if self._selected_ability is not None:
            if self._selected_ability.get_cur_cooldown() == 0:
                final_mana_cost = self._selected_ability.get_mana_cost() + int(self._selected_ability.get_mana_cost() * mana_cost_adjustment)
                if expertise.mana >= final_mana_cost or sanguinated_active:
                    self.add_item(ConfirmAbilityButton(min(4, len(page_slots))))
        self.add_item(BackToActionSelectButton(min(4, len(page_slots))))

    def exit_to_action_select(self):
        self._reset_turn_variables()
        return self.show_actions()

    def _get_current_page_info(self, error_str: str | None=None):
        player: Player = self._turn_order[self._turn_index]
        description = ""
        if self._intent == Intent.Item:
            description = "Selected item info will be displayed here."
            if self._selected_item is not None:
                description = f"᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{self._selected_item}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆"
        if self._intent == Intent.Ability:
            stats_hidden: bool = any(se.key == StatusEffectKey.StatsHidden for se in player.get_dueling().status_effects)
            stats_str: str = player.get_expertise().get_health_and_mana_string() if not stats_hidden else "HP: ???\nMana: ???"
            description = f"{stats_str}\nCoins: {player.get_inventory().get_coins_str()}\n\n"
            if self._selected_ability is not None:
                description += f"᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{self._selected_ability}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆"
            else:
                description += "Selected ability info will be displayed here."
        if error_str is not None:
            description += f"\n\n{error_str}"
        return Embed(title=f"Choose an {self._intent}", description=description)

    def next_page(self):
        self._page += 1
        if self._intent == Intent.Item:
            self._selected_item = None
            self._selected_item_index = -1
            self._get_current_items_page_buttons()
        if self._intent == Intent.Ability:
            self._selected_ability = None
            self._selected_ability_index = -1
            self._get_current_abilities_page_buttons()
        if self._selecting_targets:
            self._current_target = None
            self._current_target_index = -1
            return self.show_targets(self._target_own_group)
        return self._get_current_page_info()

    def prev_page(self):
        self._page = max(0, self._page - 1)
        if self._intent == Intent.Item:
            self._selected_item = None
            self._selected_item_index = -1
            self._get_current_items_page_buttons()
        if self._intent == Intent.Ability:
            self._selected_ability = None
            self._selected_ability_index = -1
            self._get_current_abilities_page_buttons()
        if self._selecting_targets:
            self._current_target = None
            self._current_target_index = -1
            return self.show_targets(self._target_own_group)
        return self._get_current_page_info()

    def select_item(self, exact_item_index: int, item: Item):
        self._selected_item_index = exact_item_index
        self._selected_item = item

        self._get_current_items_page_buttons()
        return self._get_current_page_info()
        
    def select_ability(self, ability_index: int, ability: Ability):
        self._selected_ability_index = ability_index
        self._selected_ability = ability

        self._get_current_abilities_page_buttons()
        return self._get_current_page_info()

    def confirm_item(self):
        if self._selected_item is None:
            return self.show_items("*Error: That item couldn't be selected.*")

        entity: Player | NPC = self._turn_order[self._turn_index]
        found_index = entity.get_inventory().item_exists(self._selected_item)
        if self._selected_item is not None and found_index == self._selected_item_index:
            consumable_stats = self._selected_item.get_consumable_stats()
            if consumable_stats is None:
                return self.show_items("*Error: That item doesn't have consumable stats.*")
            
            self._targets_remaining = consumable_stats.get_num_targets()
            target_own_group = consumable_stats.get_target_own_group()

            if self._targets_remaining == 0:
                self._selected_targets = [entity]
                return self.do_action_on_selected_targets()
            
            charmed: bool = any(se.key == StatusEffectKey.Charmed for se in entity.get_dueling().status_effects)
            
            if self._targets_remaining == -1:
                if (entity in self._enemies and target_own_group) or (entity in self._allies and not target_own_group):
                    if not charmed:
                        self._selected_targets = self._enemies
                    else:
                        self._selected_targets = self._allies

                    return self.do_action_on_selected_targets()
                elif (entity in self._enemies and not target_own_group) or (entity in self._allies and target_own_group):
                    if not charmed:
                        self._selected_targets = self._allies
                    else:
                        self._selected_targets = self._enemies

                    return self.do_action_on_selected_targets()

            if self._targets_remaining == -2:
                self._selected_targets = self._turn_order
                return self.do_action_on_selected_targets()

            self._page = 0
            self._selecting_targets = True
            return self.show_targets(target_own_group)
        return self.show_items("*Error: That item couldn't be selected.*")

    def confirm_ability(self):
        if self._selected_ability is None:
            return self.show_abilities("*Error: That item couldn't be selected.*")

        entity: Player | NPC = self._turn_order[self._turn_index]
        found_index = entity.get_dueling().ability_exists(self._selected_ability)
        if found_index == self._selected_ability_index:
            self._targets_remaining = self._selected_ability.get_num_targets()
            target_own_group = self._selected_ability.get_target_own_group()

            if self._targets_remaining == 0:
                self._selected_targets = [entity]
                return self.do_action_on_selected_targets()
            
            charmed: bool = any(se.key == StatusEffectKey.Charmed for se in entity.get_dueling().status_effects)
            
            if self._targets_remaining == -1:
                if (entity in self._enemies and target_own_group) or (entity in self._allies and not target_own_group):
                    if not charmed:
                        self._selected_targets = self._enemies
                    else:
                        self._selected_targets = self._allies

                    return self.do_action_on_selected_targets()
                elif (entity in self._enemies and not target_own_group) or (entity in self._allies and target_own_group):
                    if not charmed:
                        self._selected_targets = self._allies
                    else:
                        self._selected_targets = self._enemies

                    return self.do_action_on_selected_targets()

            if self._targets_remaining == -2:
                self._selected_targets = self._turn_order
                return self.do_action_on_selected_targets()

            self._page = 0
            self._selecting_targets = True
            return self.show_targets(target_own_group)
        return self.show_abilities("*Error: That ability couldn't be selected.*")

    def select_target(self, target: Player | NPC, index: int):
        self._current_target_index = index
        self._current_target = target

        return self.show_targets(self._target_own_group)
 
    def set_targets_remaining_based_on_weapon(self):
        cur_entity: Player | NPC = self._turn_order[self._turn_index]
        main_hand_item: Item | None = cur_entity.get_equipment().get_item_in_slot(ClassTag.Equipment.MainHand)
        
        if main_hand_item is None:
            self._targets_remaining = 1
        else:
            weapon_stats = main_hand_item.get_weapon_stats()
            if weapon_stats is None:
                self._targets_remaining = 1
            else:
                self._targets_remaining = weapon_stats.get_num_targets()

    def continue_turn(self, skip_turn=False):
        self._page = 0
        self._scroll_index = 0
        cur_entity: Player | NPC = self._turn_order[self._turn_index]

        # Check here before setting next turn, just in case
        duel_result = self.check_for_win()
        if duel_result.game_won:
            return self.get_victory_screen(duel_result)

        dueling: Dueling = cur_entity.get_dueling()
        dueling.actions_remaining = max(0, dueling.actions_remaining - 1)
        if dueling.actions_remaining == 0 or skip_turn:
            init_info_str: str = ""

            is_charmed = any(se.key == StatusEffectKey.Charmed for se in cur_entity.get_dueling().status_effects)
            if dueling.actions_remaining > 0 and skip_turn and is_charmed:
                damage = ceil(0.5 * cur_entity.get_expertise().max_hp)
                cur_entity.get_expertise().damage(damage, cur_entity.get_dueling(), 0, True)
                init_info_str += f"{self.get_name(cur_entity)} took {damage} damage for skipping their turn while Charmed!\n\n"

            # CDs and status effect time remaining decrement at the end of the turn,
            # so they actually last a turn
            dueling.decrement_all_ability_cds()
            dueling.decrement_statuses_time_remaining()
            cur_entity.get_expertise().update_stats(cur_entity.get_combined_attributes())
            duel_result = self.set_next_turn(init_info_str)
            if duel_result.game_won:
                return self.get_victory_screen(duel_result)
        
        next_entity: Player | NPC = self._turn_order[self._turn_index]
        if next_entity != cur_entity:
            next_entity_dueling: Dueling = next_entity.get_dueling()
            next_entity_dueling.actions_remaining = next_entity_dueling.init_actions_remaining
        
        cur_turn_user = self.get_user_for_current_turn()
        if isinstance(next_entity, Player) or (cur_turn_user is not None and next_entity.get_id() == str(cur_turn_user.id)):
            return self.show_actions()
        else:
            return self.take_npc_turn()

    def go_back_using_intent(self):
        self._page = 0
        self._selecting_targets = False
        if self._intent == Intent.Attack:
            return self.show_actions()
        if self._intent == Intent.Ability:
            self._selected_ability = None
            self._selected_ability_index = -1
            return self.show_abilities()
        if self._intent == Intent.Item:
            self._selected_item = None
            self._selected_item_index = -1
            return self.show_items()

    def take_npc_turn(self):
        cur_npc: NPC = self._turn_order[self._turn_index] # type: ignore
        npc_dueling: Dueling = cur_npc.get_dueling()
        npc_inventory = cur_npc.get_inventory()

        # Based on the chosen action, the vars below will be used to make the action for real
        optimal_fitness_score: float | None = None
        chosen_action: Intent | None = None

        selected_ability: Ability | None = None
        selected_ability_index: int = -1

        selected_item: Item | None = None
        selected_item_index: int = -1

        selected_targets: List[Player | NPC] = []

        def update_optimal_fitness(fitness_score: float, intent: Intent, ability: Ability | None, ability_index: int, item: Item | None, item_index: int, targets: List[Player | NPC]):
            nonlocal optimal_fitness_score, chosen_action, selected_ability, selected_ability_index, selected_item, selected_item_index, selected_targets

            if optimal_fitness_score is None or fitness_score > optimal_fitness_score:
                optimal_fitness_score = fitness_score
                chosen_action = intent
                
                selected_ability = ability
                selected_ability_index = ability_index

                selected_item = item
                selected_item_index = item_index

                selected_targets = targets

        def get_target_ids(targets: List[Player | NPC], cannot_target_ids: List[str], is_targeting_own_group: bool):
            # To allow healing abilities and buffs to target your own group, even if they're not alive, but not continue
            # to damage dead enemies, this conditionally filters based on whether the NPC is targeting its own group
            alive_targets = filter(lambda x: x.get_expertise().hp > 0, targets) if not is_targeting_own_group else targets
            target_ids = map(lambda x: x.get_id(), alive_targets)
            return list(filter(lambda x: x != "" and x not in cannot_target_ids, target_ids))

        restricted_to_items: bool = any(se.key == StatusEffectKey.RestrictedToItems for se in npc_dueling.status_effects)
        cannot_attack: bool = any(se.key == StatusEffectKey.CannotAttack for se in npc_dueling.status_effects)
        taunt_targets: List[Player | NPC] = [se.forced_to_attack for se in npc_dueling.status_effects if isinstance(se, Taunted)]

        cannot_use_abilities: bool = any(se.key == StatusEffectKey.CannotUseAbilities for se in npc_dueling.status_effects) or len(taunt_targets) > 0
        cannot_use_items: bool = len(taunt_targets) > 0

        charmed: bool = any(se.key == StatusEffectKey.Charmed for se in npc_dueling.status_effects)

        enemies = self._allies if ((cur_npc in self._enemies and not charmed) or (cur_npc in self._allies and charmed)) else self._enemies

        cannot_target_ids: List[str] = []
        for se in npc_dueling.status_effects:
            if se.key == StatusEffectKey.CannotTarget:
                assert(isinstance(se, CannotTarget))
                if se.cant_target in enemies:
                    cannot_target_ids.append(se.cant_target.get_id())

        if all(enemy.get_id() in cannot_target_ids for enemy in enemies):
            action_str = "skips their turn!"

            self.clear_items()
            self.add_item(ContinueToNextActionButton())

            additional_info_str = f"{self._additional_info_string_data}\n\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\n" if self._additional_info_string_data != "" else ""
            return Embed(title=f"{cur_npc.get_name()} {action_str}", description=f"{cur_npc.get_name()} had no available targets!\n\n{additional_info_str}")

        # Step 1: Try attacking all enemies
        if not restricted_to_items:
            if not cannot_attack:
                self.set_targets_remaining_based_on_weapon()

                if self._targets_remaining == 0:
                    # Who knows, maybe I'll make something that can attack itself.
                    dueling_copy: DuelView = self.create_copy()
                    dueling_copy._selected_targets = [dueling_copy._turn_order[dueling_copy._turn_index]]
                    dueling_copy.attack_selected_targets()

                    copy_cur_npc: NPC = dueling_copy.get_entities_by_ids([cur_npc.get_id()])[0] # type: ignore
                    dueling_copy_allies = dueling_copy._allies if copy_cur_npc in dueling_copy._allies else dueling_copy._enemies
                    dueling_copy_enemies = dueling_copy._enemies if copy_cur_npc in dueling_copy._allies else dueling_copy._allies
                    fitness_score = copy_cur_npc.get_fitness_for_persona(cur_npc, dueling_copy_allies, dueling_copy_enemies)

                    update_optimal_fitness(fitness_score, Intent.Attack, None, -1, None, -1, [cur_npc])
                elif self._targets_remaining < 0:
                    dueling_copy: DuelView = self.create_copy()

                    targets = []
                    if self._targets_remaining == -1:
                        targets = enemies
                    elif self._targets_remaining == -2:
                        targets = self._turn_order
                    
                    target_ids: List[str] = get_target_ids(list(targets), cannot_target_ids, False)

                    if len(target_ids) > 0:
                        dueling_copy._selected_targets = dueling_copy.get_entities_by_ids(target_ids)
                        dueling_copy.attack_selected_targets()

                        copy_cur_npc: NPC = dueling_copy.get_entities_by_ids([cur_npc.get_id()])[0] # type: ignore
                        dueling_copy_allies = dueling_copy._allies if copy_cur_npc in dueling_copy._allies else dueling_copy._enemies
                        dueling_copy_enemies = dueling_copy._enemies if copy_cur_npc in dueling_copy._allies else dueling_copy._allies
                        fitness_score = copy_cur_npc.get_fitness_for_persona(cur_npc, dueling_copy_allies, dueling_copy_enemies)
                        
                        update_optimal_fitness(fitness_score, Intent.Attack, None, -1, None, -1, enemies)
                else:
                    if len(taunt_targets) > 0:
                        targets = [choice(taunt_targets)]
                        dueling_copy: DuelView = self.create_copy()
                        target_ids: List[str] = get_target_ids(list(targets), cannot_target_ids, False)
                        dueling_copy._selected_targets = dueling_copy.get_entities_by_ids(target_ids)
                        dueling_copy.attack_selected_targets()

                        copy_cur_npc: NPC = dueling_copy.get_entities_by_ids([cur_npc.get_id()])[0] # type: ignore
                        dueling_copy_allies = dueling_copy._allies if copy_cur_npc in dueling_copy._allies else dueling_copy._enemies
                        dueling_copy_enemies = dueling_copy._enemies if copy_cur_npc in dueling_copy._allies else dueling_copy._allies
                        fitness_score = copy_cur_npc.get_fitness_for_persona(cur_npc, dueling_copy_allies, dueling_copy_enemies)

                        update_optimal_fitness(fitness_score, Intent.Attack, None, -1, None, -1, list(targets))
                    elif len(enemies) > 0:
                        combinations = list(itertools.combinations(enemies, min(self._targets_remaining, len(enemies))))
                        for targets in combinations:
                            dueling_copy: DuelView = self.create_copy()
                            
                            target_ids: List[str] = get_target_ids(list(targets), cannot_target_ids, False)
                            if len(target_ids) == 0:
                                continue

                            dueling_copy._selected_targets = dueling_copy.get_entities_by_ids(target_ids)
                            dueling_copy.attack_selected_targets()

                            copy_cur_npc: NPC = dueling_copy.get_entities_by_ids([cur_npc.get_id()])[0] # type: ignore
                            dueling_copy_allies = dueling_copy._allies if copy_cur_npc in dueling_copy._allies else dueling_copy._enemies
                            dueling_copy_enemies = dueling_copy._enemies if copy_cur_npc in dueling_copy._allies else dueling_copy._allies
                            fitness_score = copy_cur_npc.get_fitness_for_persona(cur_npc, dueling_copy_allies, dueling_copy_enemies)

                            update_optimal_fitness(fitness_score, Intent.Attack, None, -1, None, -1, list(targets))

            if not cannot_use_abilities:
                # Step 2: Try using all abilities
                for i, ability in enumerate(npc_dueling.abilities + npc_dueling.temp_abilities):
                    if cur_npc.get_expertise().mana < ability.get_mana_cost() or ability.get_cur_cooldown() != 0:
                        continue

                    # Special casing for the Underworld final boss, so it doesn't waste its main ability
                    if ability.get_name() == "Annihilation Beam":
                        can_use = any(se.key == StatusEffectKey.Marked and se.source_str == "\uD83D\uDD3B Ruby Eyes Begin to Glow" for en in self._enemies for se in en.get_dueling().status_effects)
                        if not can_use:
                            continue

                    self._targets_remaining = ability.get_num_targets()

                    if self._targets_remaining < 0:
                        dueling_copy: DuelView = self.create_copy()

                        copy_cur_npc: NPC = dueling_copy.get_entities_by_ids([cur_npc.get_id()])[0] # type: ignore
                        dueling_copy._selected_ability = (copy_cur_npc.get_dueling().abilities + copy_cur_npc.get_dueling().temp_abilities)[i]
                        dueling_copy._selected_ability_index = i

                        targets = []
                        target_own_group = dueling_copy._selected_ability.get_target_own_group()
                        if self._targets_remaining == -1:
                            if (cur_npc in self._enemies and target_own_group) or (cur_npc in self._allies and not target_own_group):
                                if not charmed:
                                    targets = self._enemies
                                else:
                                    targets = self._allies
                            elif (cur_npc in self._enemies and not target_own_group) or (cur_npc in self._allies and target_own_group):
                                if not charmed:
                                    targets = self._allies
                                else:
                                    targets = self._enemies
                        elif self._targets_remaining == -2:
                            targets = self._turn_order
                        
                        target_ids: List[str] = get_target_ids(list(targets), cannot_target_ids, target_own_group)

                        if len(target_ids) > 0:
                            dueling_copy._selected_targets = dueling_copy.get_entities_by_ids(target_ids)
                            dueling_copy.use_ability_on_selected_targets()

                            copy_cur_npc: NPC = dueling_copy.get_entities_by_ids([cur_npc.get_id()])[0] # type: ignore
                            dueling_copy_allies = dueling_copy._allies if copy_cur_npc in dueling_copy._allies else dueling_copy._enemies
                            dueling_copy_enemies = dueling_copy._enemies if copy_cur_npc in dueling_copy._allies else dueling_copy._allies
                            fitness_score = copy_cur_npc.get_fitness_for_persona(cur_npc, dueling_copy_allies, dueling_copy_enemies)

                            update_optimal_fitness(fitness_score, Intent.Ability, ability, i, None, -1, targets)
                    elif self._targets_remaining == 0:
                        dueling_copy: DuelView = self.create_copy()

                        copy_cur_npc: NPC = dueling_copy.get_entities_by_ids([cur_npc.get_id()])[0] # type: ignore
                        dueling_copy._selected_ability = (copy_cur_npc.get_dueling().abilities + copy_cur_npc.get_dueling().temp_abilities)[i]
                        dueling_copy._selected_ability_index = i

                        targets = [cur_npc]
                        target_ids: List[str] = get_target_ids(list(targets), cannot_target_ids, True)
                        dueling_copy._selected_targets = dueling_copy.get_entities_by_ids(target_ids)
                        dueling_copy.use_ability_on_selected_targets()

                        copy_cur_npc: NPC = dueling_copy.get_entities_by_ids([cur_npc.get_id()])[0] # type: ignore
                        dueling_copy_allies = dueling_copy._allies if copy_cur_npc in dueling_copy._allies else dueling_copy._enemies
                        dueling_copy_enemies = dueling_copy._enemies if copy_cur_npc in dueling_copy._allies else dueling_copy._allies
                        fitness_score = copy_cur_npc.get_fitness_for_persona(cur_npc, dueling_copy_allies, dueling_copy_enemies)

                        update_optimal_fitness(fitness_score, Intent.Ability, ability, i, None, -1, targets)
                    else:
                        targets = []
                        target_own_group = ability.get_target_own_group()
                        if (cur_npc in self._enemies and target_own_group) or (cur_npc in self._allies and not target_own_group):
                            if not charmed:
                                targets = self._enemies
                            else:
                                targets = self._allies
                        elif (cur_npc in self._enemies and not target_own_group) or (cur_npc in self._allies and target_own_group):
                            if not charmed:
                                targets = self._allies
                            else:
                                targets = self._enemies

                        if len(targets) > 0:
                            combinations = list(itertools.combinations(targets, min(self._targets_remaining, len(enemies))))
                            for targets in combinations:
                                dueling_copy: DuelView = self.create_copy()

                                copy_cur_npc: NPC = dueling_copy.get_entities_by_ids([cur_npc.get_id()])[0] # type: ignore
                                dueling_copy._selected_ability = (copy_cur_npc.get_dueling().abilities + copy_cur_npc.get_dueling().temp_abilities)[i]
                                dueling_copy._selected_ability_index = i

                                target_ids: List[str] = get_target_ids(list(targets), cannot_target_ids, target_own_group)
                                if len(target_ids) == 0:
                                    continue

                                dueling_copy._selected_targets = dueling_copy.get_entities_by_ids(target_ids)
                                dueling_copy.use_ability_on_selected_targets()

                                copy_cur_npc: NPC = dueling_copy.get_entities_by_ids([cur_npc.get_id()])[0] # type: ignore
                                dueling_copy_allies = dueling_copy._allies if copy_cur_npc in dueling_copy._allies else dueling_copy._enemies
                                dueling_copy_enemies = dueling_copy._enemies if copy_cur_npc in dueling_copy._allies else dueling_copy._allies
                                fitness_score = copy_cur_npc.get_fitness_for_persona(cur_npc, dueling_copy_allies, dueling_copy_enemies)

                                update_optimal_fitness(fitness_score, Intent.Ability, ability, i, None, -1, list(targets))

        if not cannot_use_items:
            # Step 3: Try using all items
            inventory_slots = npc_inventory.get_inventory_slots()
            filtered_indices = npc_inventory.filter_inventory_slots([ClassTag.Consumable.UsableWithinDuels])
            filtered_items = [inventory_slots[i] for i in filtered_indices]
            for i, item in enumerate(filtered_items):
                consumable_stats = item.get_consumable_stats()
                if consumable_stats is None:
                    continue
                
                self._targets_remaining = consumable_stats.get_num_targets()

                if self._targets_remaining < 0:
                    dueling_copy: DuelView = self.create_copy()

                    copy_cur_npc: NPC = dueling_copy.get_entities_by_ids([cur_npc.get_id()])[0] # type: ignore
                    dueling_copy._selected_item = copy_cur_npc.get_inventory().get_inventory_slots()[i]
                    dueling_copy._selected_item_index = i

                    targets = []
                    target_own_group = consumable_stats.get_target_own_group()
                    if self._targets_remaining == -1:
                        if (cur_npc in self._enemies and target_own_group) or (cur_npc in self._allies and not target_own_group):
                            if not charmed:
                                targets = self._enemies
                            else:
                                targets = self._allies
                        elif (cur_npc in self._enemies and not target_own_group) or (cur_npc in self._allies and target_own_group):
                            if not charmed:
                                targets = self._allies
                            else:
                                targets = self._enemies
                    elif self._targets_remaining == -2:
                        targets = self._turn_order
                        
                    target_ids: List[str] = get_target_ids(list(targets), cannot_target_ids, target_own_group)

                    if len(target_ids) > 0:
                        dueling_copy._selected_targets = dueling_copy.get_entities_by_ids(target_ids)
                        dueling_copy.use_item_on_selected_targets()

                        copy_cur_npc: NPC = dueling_copy.get_entities_by_ids([cur_npc.get_id()])[0] # type: ignore
                        dueling_copy_allies = dueling_copy._allies if copy_cur_npc in dueling_copy._allies else dueling_copy._enemies
                        dueling_copy_enemies = dueling_copy._enemies if copy_cur_npc in dueling_copy._allies else dueling_copy._allies
                        fitness_score = copy_cur_npc.get_fitness_for_persona(cur_npc, dueling_copy_allies, dueling_copy_enemies)

                        update_optimal_fitness(fitness_score, Intent.Item, None, -1, item, i, targets)
                elif self._targets_remaining == 0:
                    dueling_copy: DuelView = self.create_copy()

                    copy_cur_npc: NPC = dueling_copy.get_entities_by_ids([cur_npc.get_id()])[0] # type: ignore
                    dueling_copy._selected_item = copy_cur_npc.get_inventory().get_inventory_slots()[i]
                    dueling_copy._selected_item_index = i

                    targets = [cur_npc]
                    target_ids: List[str] = get_target_ids(list(targets), cannot_target_ids, True)
                    dueling_copy._selected_targets = dueling_copy.get_entities_by_ids(target_ids)
                    dueling_copy.use_item_on_selected_targets()

                    copy_cur_npc: NPC = dueling_copy.get_entities_by_ids([cur_npc.get_id()])[0] # type: ignore
                    dueling_copy_allies = dueling_copy._allies if copy_cur_npc in dueling_copy._allies else dueling_copy._enemies
                    dueling_copy_enemies = dueling_copy._enemies if copy_cur_npc in dueling_copy._allies else dueling_copy._allies
                    fitness_score = copy_cur_npc.get_fitness_for_persona(cur_npc, dueling_copy_allies, dueling_copy_enemies)

                    update_optimal_fitness(fitness_score, Intent.Item, None, -1, item, i, targets)
                else:
                    targets = []
                    target_own_group = consumable_stats.get_target_own_group()
                    if (cur_npc in self._enemies and target_own_group) or (cur_npc in self._allies and not target_own_group):
                        if not charmed:
                            targets = self._enemies
                        else:
                            targets = self._allies
                    elif (cur_npc in self._enemies and not target_own_group) or (cur_npc in self._allies and target_own_group):
                        if not charmed:
                            targets = self._allies
                        else:
                            targets = self._enemies

                    if len(targets) > 0:
                        combinations = list(itertools.combinations(enemies, min(self._targets_remaining, len(enemies))))
                        for targets in combinations:
                            dueling_copy: DuelView = self.create_copy()

                            copy_cur_npc: NPC = dueling_copy.get_entities_by_ids([cur_npc.get_id()])[0] # type: ignore
                            dueling_copy._selected_item = copy_cur_npc.get_inventory().get_inventory_slots()[i]
                            dueling_copy._selected_item_index = i

                            target_ids: List[str] = get_target_ids(list(targets), cannot_target_ids, target_own_group)
                            if len(target_ids) == 0:
                                continue

                            dueling_copy._selected_targets = dueling_copy.get_entities_by_ids(target_ids)
                            dueling_copy.use_item_on_selected_targets()

                            copy_cur_npc: NPC = dueling_copy.get_entities_by_ids([cur_npc.get_id()])[0] # type: ignore
                            dueling_copy_allies = dueling_copy._allies if copy_cur_npc in dueling_copy._allies else dueling_copy._enemies
                            dueling_copy_enemies = dueling_copy._enemies if copy_cur_npc in dueling_copy._allies else dueling_copy._allies
                            fitness_score = copy_cur_npc.get_fitness_for_persona(cur_npc, dueling_copy_allies, dueling_copy_enemies)
                            
                            update_optimal_fitness(fitness_score, Intent.Item, None, -1, item, i, list(targets))

        optimal_result_str: str = ""
        action_str: str = ""
        if chosen_action == Intent.Attack:
            action_str = "attacks!"

            self._selected_targets = selected_targets
            optimal_result_str = self.attack_selected_targets()
        elif chosen_action == Intent.Ability:
            action_str = "uses an ability!"
        
            self._selected_targets = selected_targets
            self._selected_ability = selected_ability
            self._selected_ability_index = selected_ability_index
            optimal_result_str = self.use_ability_on_selected_targets()
        elif chosen_action == Intent.Item:
            action_str = "uses an item!"

            self._selected_targets = selected_targets
            self._selected_item = selected_item
            self._selected_item_index = selected_item_index
            optimal_result_str = self.use_item_on_selected_targets()
        else:
            action_str = "skips their turn!"

        self.clear_items()
        self.add_item(ContinueToNextActionButton())

        additional_info_str = f"{self._additional_info_string_data}\n\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\n" if self._additional_info_string_data != "" else ""
        return Embed(title=f"{cur_npc.get_name()} {action_str}", description=f"{additional_info_str}{optimal_result_str}")

    def create_copy(self):
        copied_allies: List[Player | NPC] = jsonpickle.decode(jsonpickle.encode(self._allies, make_refs=False)) # type: ignore
        copied_enemies: List[Player | NPC] = jsonpickle.decode(jsonpickle.encode(self._enemies, make_refs=False)) # type: ignore

        duel_view: DuelView = DuelView(
            self._bot,
            self._database,
            self._guild_id,
            self._users,
            copied_allies,
            copied_enemies,
            skip_init_updates=True
        )

        duel_view._turn_index = self._turn_index

        return duel_view

# -----------------------------------------------------------------------------
# PvP DUEL VIEW AND GUI
# -----------------------------------------------------------------------------

class AcceptButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.green, label="Accept")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: PlayerVsPlayerOrNPCDuelView = self.view

        if interaction.user not in view.get_opponents() and len(view.get_non_npc_opponents()) > 0:
            await interaction.response.edit_message(content="Error: You can't accept this request!", view=view)
            return
        
        response: Embed = view.accept_request(interaction.user)
        if not view.all_accepted():
            await interaction.response.edit_message(embed=response, view=view, content=None)
        else:
            if view.any_in_duels_currently():
                await interaction.response.edit_message(embed=None, view=None, content="At least one person is already in a duel. This duel has been cancelled.")
                return
            
            users: List[discord.User] = [view.get_challenger(), *view.get_non_npc_opponents()]
            challenger_player: Player = view.get_challenger_player()
            opponents_players_and_npcs: List[Player | NPC] = view.get_opponents_players_and_npcs()
            
            duel_view: DuelView = DuelView(view.get_bot(), view.get_database(), view.get_guild_id(), users, [challenger_player], opponents_players_and_npcs)
            initial_info: Embed = duel_view.get_initial_embed()

            await interaction.response.edit_message(embed=initial_info, view=duel_view, content=None)


class DeclineButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.red, label="Decline")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: PlayerVsPlayerOrNPCDuelView = self.view

        if interaction.user not in view.get_opponents():
            await interaction.response.edit_message(content="Error: You can't decline this request!", view=view)
            return

        view.clear_items()
        await interaction.response.edit_message(content="The duel was declined.", view=view, embed=None)


class PlayerVsPlayerOrNPCDuelView(discord.ui.View):
    def __init__(self, bot: commands.Bot, database: dict, guild_id: int, challenger: discord.User, opponents: List[discord.User | NPC]):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._challenger = challenger
        self._opponents = opponents

        self._acceptances: List[discord.User] = []

        self.add_item(AcceptButton())
        self.add_item(DeclineButton())

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_non_npc_opponents(self) -> List[discord.User]:
        return list(filter(lambda x: isinstance(x, discord.User), self._opponents))

    def get_info_embed(self):
        not_accepted = list(filter(lambda x: x not in self._acceptances, self.get_non_npc_opponents()))
        not_accepted_names = "\n".join(list(map(lambda x: x.display_name, not_accepted)))
        acceptance_str = f"\n\n**Waiting on acceptances from:**\n\n{not_accepted_names}" if len(not_accepted_names) > 0 else ""

        npc_introduction_strs = []
        for opponent in self._opponents:
            if isinstance(opponent, NPC):
                if opponent.get_name() == "Yenna":
                    npc_introduction_strs.append("Yenna greets you in the dueling grounds, her robe billowing in the wind. \"I hope you've prepared for this moment. I won't be holding back.\"")
                elif opponent.get_name() == "Copperbroad":
                    npc_introduction_strs.append("Copperbroad stands at the ready with his trusty iron pan. \"Ah, aye love me a good rammy! Bring it on.\"")
                elif opponent.get_name() == "Abarra":
                    npc_introduction_strs.append("Abarra arrives at the dueling grounds in rather moderate gear, but a powerful greatsword by his side. \"Hm? Hm.\"")
                elif opponent.get_name() == "Mr. Bones":
                    npc_introduction_strs.append("The air itself seems to dim as shadows gather where Mr. Bones stands in the dueling grounds. The world fills with raspy laughter and a sense of dread as a bony, almost skeletal hand beckons you forth.")
                elif opponent.get_name() == "Viktor":
                    npc_introduction_strs.append("Viktor comes bounding into the dueling grounds, a wild look in his eye. You can't help but wonder what he's got flailing around in his hand. \"A KNIFE!\" he says, confirming your worst fear.")
                elif opponent.get_name() == "Galos":
                    npc_introduction_strs.append("Galos, as usual, is ready and practicing against the training dummy at the dueling grounds. As you approach, he looks towards you and smiles. \"Practice makes perfect. Here for a spar?\"")
        npc_intro_str = ("\n\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n" + "\n\n".join(npc_introduction_strs) + "\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆") if len(npc_introduction_strs) > 0 else ""

        return Embed(title="PvP Duel", description=(
            "Players will enter combat in turn order according to their Dexterity attribute. Each turn, you will choose an action to take: "
            "Attacking using their main hand weapon, using an ability, or using an item.\n\n"
            "The duel ends when all opponents have been reduced to 0 HP. Following the duel, all players will be restored to full HP and mana.\n\n"
            f"The duel will begin when all challenged players accept the invitation to duel.{npc_intro_str}{acceptance_str}"
        ))

    def accept_request(self, user: discord.User):
        if self._get_player(user.id).get_dueling().is_in_combat:
            self.clear_items()
            return Embed(
                title="PvP Duel Cancelled",
                description=f"{user.display_name} is already in a duel and can't accept this one!"
            )

        if user not in self._acceptances:
            self._acceptances.append(user)
        
        return self.get_info_embed()

    def all_accepted(self):
        return all(user in self._acceptances for user in self.get_non_npc_opponents())

    def any_in_duels_currently(self):
        return any(self._get_player(user.id).get_dueling().is_in_combat for user in [*self.get_non_npc_opponents(), self._challenger])

    def get_bot(self):
        return self._bot

    def get_database(self):
        return self._database

    def get_guild_id(self):
        return self._guild_id

    def get_challenger(self):
        return self._challenger

    def get_opponents(self):
        return self._opponents

    def get_challenger_player(self):
        return self._get_player(self._challenger.id)

    def get_opponents_players_and_npcs(self):
        return [(self._get_player(opponent.id) if isinstance(opponent, discord.User) else opponent) for opponent in self.get_opponents()]

# -----------------------------------------------------------------------------
# GROUP PvP DUEL VIEW AND GUI
# -----------------------------------------------------------------------------

class StartButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.green, label="Start")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: GroupPlayerVsPlayerDuelView = self.view

        if interaction.user.id != view.get_duel_starter().id:
            await interaction.response.edit_message(embed=view.get_info_embed(), content="Error: You can't start this duel!", view=view)
            return
        
        if not view.all_accepted():
            await interaction.response.edit_message(embed=view.get_info_embed(), view=view, content="All players choose a team before the duel can start.")
        elif len(view.get_team_1()) == 0 or len(view.get_team_2()) == 0:
            await interaction.response.edit_message(embed=view.get_info_embed(), view=view, content="At least one player must be on each team.")
        else:
            if view.any_in_duels_currently():
                await interaction.response.edit_message(embed=None, view=None, content="At least one person is already in a duel. This duel has been cancelled.")
                return

            duel_view: DuelView = DuelView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_team_1_players(), view.get_team_2_players())
            initial_info: Embed = duel_view.get_initial_embed()

            await interaction.response.edit_message(embed=initial_info, view=duel_view, content=None)


class Team1Button(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Team 1")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: GroupPlayerVsPlayerDuelView = self.view

        if interaction.user not in view.get_users():
            await interaction.response.edit_message(embed=view.get_info_embed(), content="Error: You can't accept this request!", view=view)
            return
        
        response: Embed = view.add_to_team_1(interaction.user)
        await interaction.response.edit_message(embed=response, view=view, content=None)


class Team2Button(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Team 2")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: GroupPlayerVsPlayerDuelView = self.view

        if interaction.user not in view.get_users():
            await interaction.response.edit_message(embed=view.get_info_embed(), content="Error: You can't accept this request!", view=view)
            return
        
        response: Embed = view.add_to_team_2(interaction.user)
        await interaction.response.edit_message(embed=response, view=view, content=None)


class GroupPlayerVsPlayerDuelView(discord.ui.View):
    def __init__(self, bot: commands.Bot, database: dict, guild_id: int, users: List[discord.User]):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._duel_starter = users[0]

        self._team_1: List[discord.User] = []
        self._team_2: List[discord.User] = []

        self.add_item(Team1Button())
        self.add_item(Team2Button())
        self.add_item(StartButton())

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_info_embed(self):
        team_1_names = "\n".join(list(map(lambda x: x.display_name, self._team_1)))
        team_2_names = "\n".join(list(map(lambda x: x.display_name, self._team_2)))
        return Embed(title="Group PvP Duel", description=(
            "Players will enter combat in turn order according to their Dexterity attribute. Each turn, you will choose an action to take: "
            "Attacking using their main hand weapon, using an ability, or using an item.\n\n"
            "The duel ends when all opponents have been reduced to 0 HP. Following the duel, all players will be restored to full HP and mana.\n\n"
            f"The duel will begin when all players have selected a team and at least 1 person is on each team.\n\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n**Team 1:**\n\n{team_1_names}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n**Team 2:**\n\n{team_2_names}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆"
        ))

    def add_to_team_1(self, user: discord.User):
        if self._get_player(user.id).get_dueling().is_in_combat:
            self.clear_items()
            return Embed(
                title="PvP Duel Cancelled",
                description=f"{user.display_name} is already in a duel and can't accept this one!"
            )

        if user in self._team_2:
            self._team_2.remove(user)
        if user not in self._team_1:
            self._team_1.append(user)
        
        return self.get_info_embed()

    def add_to_team_2(self, user: discord.User):
        if self._get_player(user.id).get_dueling().is_in_combat:
            self.clear_items()
            return Embed(
                title="PvP Duel Cancelled",
                description=f"{user.display_name} is already in a duel and can't accept this one!"
            )

        if user in self._team_1:
            self._team_1.remove(user)
        if user not in self._team_2:
            self._team_2.append(user)
        
        return self.get_info_embed()

    def all_accepted(self):
        return all(user in self._team_1 or user in self._team_2 for user in self._users)

    def any_in_duels_currently(self):
        return any(self._get_player(user.id).get_dueling().is_in_combat for user in self._users)

    def get_team_1_players(self):
        return [self._get_player(user.id) for user in self._team_1]

    def get_team_2_players(self):
        return [self._get_player(user.id) for user in self._team_2]
    
    def get_bot(self):
        return self._bot

    def get_database(self):
        return self._database

    def get_guild_id(self):
        return self._guild_id

    def get_team_1(self):
        return self._team_1

    def get_team_2(self):
        return self._team_2

    def get_users(self):
        return self._users

    def get_duel_starter(self):
        return self._duel_starter

# -----------------------------------------------------------------------------
# COMPANION BATTLE VIEW AND GUI
# -----------------------------------------------------------------------------

class StartCompanionBattleButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.green, label="Start")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: CompanionBattleView = self.view

        if interaction.user.id != view.get_duel_starter().id:
            await interaction.response.edit_message(embed=view.get_info_embed(), content="Error: You can't start this companion battle!", view=view)
            return
        
        if not view.all_accepted():
            await interaction.response.edit_message(embed=view.get_info_embed(), view=view, content="All players choose a team before the companion battle can start.")
        elif len(view.get_team_1()) == 0 or len(view.get_team_2()) == 0:
            await interaction.response.edit_message(embed=view.get_info_embed(), view=view, content="At least one player must be on each team.")
        else:
            if view.any_in_duels_currently():
                await interaction.response.edit_message(embed=None, view=None, content="At least one person is already in a duel or companion battle. This duel has been cancelled.")
                return

            view.set_players_in_combat()

            duel_view: DuelView = DuelView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_team_1_players(), view.get_team_2_players(), companion_battle=True)
            initial_info: Embed = duel_view.get_initial_embed()

            await interaction.response.edit_message(embed=initial_info, view=duel_view, content=None)


class CompanionBattleView(discord.ui.View):
    def __init__(self, bot: commands.Bot, database: dict, guild_id: int, users: List[discord.User]):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._duel_starter = users[0]

        self._team_1: List[discord.User] = []
        self._team_2: List[discord.User] = []

        self.add_item(Team1Button())
        self.add_item(Team2Button())
        self.add_item(StartCompanionBattleButton())

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_info_embed(self):
        team_1_names = "\n".join(list(map(lambda x: x.display_name, self._team_1)))
        team_2_names = "\n".join(list(map(lambda x: x.display_name, self._team_2)))
        return Embed(title="Companion Battle", description=(
            "Companions will enter combat in turn order according to their Dexterity attribute. Each turn, you will choose an action to take: "
            "Attacking using their main hand weapon, using an ability, or using an item.\n\n"
            "The duel ends when all opponents have been reduced to 0 HP. Following the duel, all players will be restored to full HP and mana.\n\n"
            f"The companion battle will begin when all players have selected a team and at least 1 person is on each team.\n\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n**Team 1:**\n\n{team_1_names}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n**Team 2:**\n\n{team_2_names}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆"
        ))

    def add_to_team_1(self, user: discord.User):
        if self._get_player(user.id).get_dueling().is_in_combat:
            self.clear_items()
            return Embed(
                title="Companion Battle Cancelled",
                description=f"{user.display_name} is in a duel or companion battle and can't accept this one!"
            )

        if user in self._team_2:
            self._team_2.remove(user)
        if user not in self._team_1:
            self._team_1.append(user)
        
        return self.get_info_embed()

    def add_to_team_2(self, user: discord.User):
        if self._get_player(user.id).get_dueling().is_in_combat:
            self.clear_items()
            return Embed(
                title="Companion Battle Cancelled",
                description=f"{user.display_name} is already in a duel and can't accept this one!"
            )

        if user in self._team_1:
            self._team_1.remove(user)
        if user not in self._team_2:
            self._team_2.append(user)
        
        return self.get_info_embed()

    def all_accepted(self):
        return all(user in self._team_1 or user in self._team_2 for user in self._users)

    def any_in_duels_currently(self):
        return any(self._get_player(user.id).get_dueling().is_in_combat for user in self._users)

    def get_team_1_players(self):
        team_1: List[NPC] = []

        for user in self._team_1:
            player = self._get_player(user.id)
            companions = player.get_companions()
            companion_key = companions.current_companion
            if companion_key is not None:
                team_1.append(companions.companions[companion_key].get_pet_battle_entity())
        
        return team_1

    def get_team_2_players(self):
        team_2: List[NPC] = []

        for user in self._team_2:
            player = self._get_player(user.id)
            companions = player.get_companions()
            companion_key = companions.current_companion
            if companion_key is not None:
                team_2.append(companions.companions[companion_key].get_pet_battle_entity())
        
        return team_2
    
    def get_bot(self):
        return self._bot

    def get_database(self):
        return self._database

    def get_guild_id(self):
        return self._guild_id

    def get_team_1(self):
        return self._team_1

    def get_team_2(self):
        return self._team_2

    def get_users(self):
        return self._users

    def get_duel_starter(self):
        return self._duel_starter

    def set_players_in_combat(self):
        for user in self._users:
            player = self._get_player(user.id)
            player.get_dueling().is_in_combat = True
