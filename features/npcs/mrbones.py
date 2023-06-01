from __future__ import annotations

from copy import deepcopy
from uuid import uuid4
from enum import StrEnum
from random import randint, random
from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Expertise, ExpertiseClass
from features.npcs.npc import NPC, NPCDuelingPersonas, NPCRoles
from features.shared.ability import ATidySumIII, BoundToGetLuckyIII, ContractBloodForBloodIII, ContractManaToBloodIII, ContractWealthForPowerIII, CursedCoinsIII, DeepPocketsIII, SecondWindIII, SilkspeakingI, UnseenRichesIII
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, ItemKey
from features.stats import Stats

from typing import TYPE_CHECKING, Callable, List
if TYPE_CHECKING:
    from features.inventory import Inventory

# -----------------------------------------------------------------------------
# ENUMS
# -----------------------------------------------------------------------------

class Difficulty(StrEnum):
    Easy = "Easy"
    Medium = "Medium"
    Hard = "Hard"
    MrBones = "MrBones"

# -----------------------------------------------------------------------------
# NPC CLASS
# -----------------------------------------------------------------------------

class MrBones(NPC):
    def __init__(self):
        # Balance Simulation Results:
        # 28% chance of 1 player party (Lvl. 120-130) victory against 1
        super().__init__("Mr. Bones", NPCRoles.KnucklebonesPatron, NPCDuelingPersonas.Mage, {})

        self._setup_npc_params()

    def _try_move(self, player_board: List[List[int]], npc_board: List[List[int]], pos: int, current_roll: int, compute_points_in_col: Callable[[List[List[int]], int], int], actual_move: bool):
        cur_player_board: List[List[int]] = deepcopy(player_board) if not actual_move else player_board
        cur_npc_board: List[List[int]] = deepcopy(npc_board) if not actual_move else npc_board

        can_place = False
        for i in range(3):
            if cur_npc_board[i][pos] == 0:
                cur_npc_board[i][pos] = current_roll
                can_place = True
                for j in range(3):
                    if cur_player_board[j][pos] == current_roll:
                        cur_player_board[j][pos] = 0
                break

        if not can_place:
            # One less than the minimum it could be, indicating the worst possible option
            return -163
        else:
            return compute_points_in_col(cur_npc_board, pos) - compute_points_in_col(cur_player_board, pos)

    def _try_move_with_lookahead(self, player_board: List[List[int]], npc_board: List[List[int]], current_roll: int, compute_points_in_col: Callable[[List[List[int]], int], int]):
        # The basis of this algorithm is to get the NPC to avoid always stacking and
        # instead play more conservatively when there's high risk. It does this by
        # doing the greedy algorithm, but simulating what would happen if the player
        # were to get the same roll and place it in the same column, trying to maximize
        # that board value.
        best_greedy_choice: int = 0
        best_greedy_choice_diff: int = -163
        best_placed_row: int = 0
        
        for pos in range(3):
            cur_player_board: List[List[int]] = deepcopy(player_board)
            cur_npc_board: List[List[int]] = deepcopy(npc_board)

            placed_row = -1
            for i in range(3):
                if cur_npc_board[i][pos] == 0:
                    cur_npc_board[i][pos] = current_roll
                    placed_row = i
                    for j in range(3):
                        if cur_player_board[j][pos] == current_roll:
                            cur_player_board[j][pos] = 0
                    break

            if placed_row == -1:
                continue
            else:
                if cur_player_board[placed_row][pos] == 0:
                    cur_player_board[placed_row][pos] = current_roll
                    for j in range(3):
                        if cur_npc_board[j][pos] == current_roll:
                            cur_npc_board[j][pos] = 0
            
            total = compute_points_in_col(cur_npc_board, pos) - compute_points_in_col(cur_player_board, pos)
            if total > best_greedy_choice_diff:
                best_greedy_choice = pos
                best_greedy_choice_diff = total
                best_placed_row = placed_row

        npc_board[best_placed_row][best_greedy_choice] = current_roll
        for j in range(3):
            if player_board[j][best_greedy_choice] == current_roll:
                player_board[j][best_greedy_choice] = 0

        return best_greedy_choice
                
    def make_move(self, player_board: List[List[int]], npc_board: List[List[int]], difficulty: Difficulty, compute_points_in_col: Callable[[List[List[int]], int], int], current_roll: int, npc_name: str) -> str:
        if difficulty == Difficulty.Easy:
            best_greedy_choice = 0
            best_greedy_choice_diff = -163
            for i in range(3):
                result = self._try_move(player_board, npc_board, i, current_roll, compute_points_in_col, False)
                if result > best_greedy_choice_diff:
                    best_greedy_choice = i
                    best_greedy_choice_diff = result
            
            if random() <= 0.75:
                best_greedy_choice = randint(0, 2)
            
            self._try_move(player_board, npc_board, best_greedy_choice, current_roll, compute_points_in_col, True)
            return f"{npc_name} has placed their {current_roll} in column {best_greedy_choice + 1}!"
        elif difficulty == Difficulty.Medium:
            best_greedy_choice = 0
            best_greedy_choice_diff = -163
            for i in range(3):
                result = self._try_move(player_board, npc_board, i, current_roll, compute_points_in_col, False)
                if result > best_greedy_choice_diff:
                    best_greedy_choice = i
                    best_greedy_choice_diff = result
            
            self._try_move(player_board, npc_board, best_greedy_choice, current_roll, compute_points_in_col, True)
            return f"{npc_name} has placed their {current_roll} in column {best_greedy_choice + 1}!"
        elif difficulty == Difficulty.Hard:
            best_greedy_choice = self._try_move_with_lookahead(player_board, npc_board, current_roll, compute_points_in_col)
            return f"{npc_name} has placed their {current_roll} in column {best_greedy_choice + 1}!"

        return f"{npc_name} has skipped their turn."

    def _setup_inventory(self):
        if self._inventory is None:
            self._inventory = Inventory()
        
        items_to_add = []

        self._inventory.add_coins(100000)
        for item in items_to_add:
            self._inventory.add_item(item)

    def _setup_xp(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._expertise.add_xp_to_class(1748260, ExpertiseClass.Merchant, self._equipment) # Level 100
        self._expertise.add_xp_to_class(20150, ExpertiseClass.Guardian, self._equipment) # Level 25
        
        self._expertise.points_to_spend = 0
        
        self._expertise.constitution = 35
        self._expertise.intelligence = 25
        self._expertise.dexterity = 10
        self._expertise.strength = 5
        self._expertise.luck = 40
        self._expertise.memory = 10

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()
        
        self._equipment.equip_item_to_slot(ClassTag.Equipment.Ring, LOADED_ITEMS.get_new_item(ItemKey.MrBonesRing))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()

        self._dueling.abilities = [
            BoundToGetLuckyIII(), SecondWindIII(), SilkspeakingI(),
            ContractWealthForPowerIII(), ATidySumIII(), CursedCoinsIII(),
            UnseenRichesIII(), ContractBloodForBloodIII(), DeepPocketsIII(),
            ContractManaToBloodIII()
        ]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Mr. Bones"
        self._role = NPCRoles.KnucklebonesPatron
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
