from __future__ import annotations

from copy import deepcopy
from random import randint, random
from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Expertise, ExpertiseClass
from features.npcs.npc import NPC, NPCRoles
from features.shared.ability import ATidySumIII, BoundToGetLuckyIII, ContractBloodForBloodIII, ContractManaToBloodIII, ContractWealthForPowerIII, CursedCoinsIII, DeepPocketsIII, SecondWindIII, SilkspeakingI, UnseenRichesIII
from strenum import StrEnum

from typing import TYPE_CHECKING, Callable, List

from features.stats import Stats
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
        super().__init__("Mr. Bones", NPCRoles.KnucklebonesPatron)

        # Inventory Setup
        self._base_items = []
        self._base_coins = 100000

        self._inventory.add_coins(self._base_coins)
        for item in self._base_items:
            self._inventory.add_item(item)
        
        # Expertise Setup
        self._expertise.add_xp_to_class(1748260, ExpertiseClass.Merchant) # Level 100
        self._expertise.add_xp_to_class(20150, ExpertiseClass.Guardian) # Level 25
        
        self._expertise.points_to_spend = 0
        
        self._expertise.constitution = 35
        self._expertise.intelligence = 20
        self._expertise.dexterity = 10
        self._expertise.strength = 10
        self._expertise.luck = 40
        self._expertise.memory = 10

        # Equipment Setup
        # TODO: Add items when they've been created
        # self._equipment.equip_item_to_slot(ClassTag.Equipment.Ring, None)

        self._expertise.update_stats(self.get_combined_attributes())

        # Dueling Setup
        self._dueling.abilities = [
            BoundToGetLuckyIII(), SecondWindIII(), SilkspeakingI(),
            ContractWealthForPowerIII(), ATidySumIII(), CursedCoinsIII(),
            UnseenRichesIII(), ContractBloodForBloodIII(), DeepPocketsIII(),
            ContractManaToBloodIII()
        ]

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
                best_greedy_choice = randint(1, 3)
            
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

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        # TODO: Make each of these setup portions a private function in the class so I don't have
        # to duplicate everything between init and setstate. 
        self._name = state.get("_name", "Mr. Bones")
        self._role = state.get("_role", NPCRoles.KnucklebonesPatron)
        
        self._inventory: Inventory | None = state.get("_inventory")
        if self._inventory is None:
            self._inventory = Inventory()

            self._base_items = []
            self._base_coins = 100000

            self._inventory.add_coins(self._base_coins)
            for item in self._base_items:
                self._inventory.add_item(item)

        self._equipment: Equipment | None = state.get("_equipment")
        if self._equipment is None:
            self._equipment = Equipment()

        self._expertise: Expertise | None = state.get("_expertise")
        if self._expertise is None:
            self._expertise = Expertise()

            self._expertise.add_xp_to_class(96600, ExpertiseClass.Merchant) # Level 20
            self._expertise.add_xp_to_class(1600, ExpertiseClass.Guardian) # Level 5
            
            self._expertise.points_to_spend = 0
                
            self._expertise.constitution = 35
            self._expertise.intelligence = 20
            self._expertise.dexterity = 10
            self._expertise.strength = 10
            self._expertise.luck = 40
            self._expertise.memory = 10

            self._expertise.update_stats(self.get_combined_attributes())

        self._dueling: Dueling | None = state.get("_dueling")
        if self._dueling is None:
            self._dueling = Dueling()

            self._dueling.abilities = [
                BoundToGetLuckyIII(), SecondWindIII(), SilkspeakingI(),
                ContractWealthForPowerIII(), ATidySumIII(), CursedCoinsIII(),
                UnseenRichesIII(), ContractBloodForBloodIII(), DeepPocketsIII(),
                ContractManaToBloodIII()
            ]

        self._stats: Stats | None = state.get("_stats")
        if self._stats is None:
            self._stats = Stats()
