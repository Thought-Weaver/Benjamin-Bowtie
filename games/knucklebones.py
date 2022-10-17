from __future__ import annotations

import discord

from random import choice, choices, randint
from discord.embeds import Embed
from discord.ext import commands

from typing import Dict, List, TYPE_CHECKING

from features.npcs.mrbones import Difficulty


if TYPE_CHECKING:
    from features.npcs.mrbones import MrBones
    from features.player import Player

class AcceptButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.green, label="Accept")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: Knucklebones = self.view

        if interaction.user.id != view.get_accepting_id():
            await interaction.response.edit_message(
                content="Error: You can't accept this request!",
                view=view
            )
            return
        
        content: str = view.setup_game()
        embed = Embed(description=content)
        await interaction.response.edit_message(
            embed=embed,
            view=view,
            content=None
        )


class DeclineButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.red, label="Decline")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: Knucklebones = self.view

        if interaction.user.id != view.get_accepting_id():
            await interaction.response.edit_message(
                content="Error: You can't decline this request!",
                view=view
            )
            return

        view.clear_items()
        await interaction.response.edit_message(
            content="The knucklebones game was declined.",
            view=view,
            embed=None
        )


class KnucklebonesButton(discord.ui.Button):
    def __init__(self, pos: int):
        emoji = ""
        if pos == 0:
            emoji = "1️⃣"
        if pos == 1:
            emoji = "2️⃣"
        if pos == 2:
            emoji = "3️⃣"
        
        super().__init__(style=discord.ButtonStyle.secondary, emoji=emoji)
        self._pos = pos

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: Knucklebones = self.view

        if interaction.user != view.get_current_turn_player():
            return

        content = view.place_roll(self._pos)
        embed = Embed(description=content)
        if content is not None:
            await interaction.response.edit_message(
                embed=embed,
                content=None,
                view=view
            )


class Knucklebones(discord.ui.View):
    def __init__(self, bot: commands.Bot, database: dict, guild_id: int, player_1: Player, player_2: Player | MrBones, player_1_display_name: str, player_2_display_name: str, accepting_id: int, bet: int, use_luck: bool, difficulty: Difficulty):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._player_1 = player_1
        self._player_1_display_name = player_1_display_name
        self._player_2 = player_2
        self._player_2_display_name = player_2_display_name
        self._current_roll = 0
        self._bet = bet
        self._use_luck = use_luck
        self._accepting_id = accepting_id
        self._difficulty = difficulty

        self._turn = choice([self._player_1, self._player_2])

        self._player_1_board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]
        self._player_2_board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]

        self.add_item(AcceptButton())
        self.add_item(DeclineButton())

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def _dice_value_to_char(self, value):
        if value == 1:
            return "1️⃣" # "⚀"
        if value == 2:
            return "2️⃣" # "⚁"
        if value == 3:
            return "3️⃣" # "⚂"
        if value == 4:
            return "4️⃣" # "⚃"
        if value == 5:
            return "5️⃣" # "⚄"
        if value == 6:
            return "6️⃣" # "⚅"
        return "⬜" # "⬚"

    def _compute_points_in_col(self, board: List[List[int]], col_num: int):
        counts: Dict[int, int] = {}
        for i in range(3):
            counts[board[i][col_num]] = counts.get(board[i][col_num], 0) + 1
        return sum([num * count * count for num, count in counts.items()])

    def _get_game_state_string(self):
        content = f"**{self._player_1_display_name}**\n\n"
        for i in range(3):
            for j in range(3):
                value: int = self._player_1_board[i][j]
                content += self._dice_value_to_char(value)
            content += "\n"
        p1_total = 0
        for i in range(3):
            col_val = self._compute_points_in_col(self._player_1_board, i)
            p1_total += col_val
            content += f"{str(col_val)} "
        content += f"= {p1_total}"

        content += f"\n\n**{self._player_2_display_name}**\n\n"
        for i in range(3):
            for j in range(3):
                value: int = self._player_2_board[i][j]
                content += self._dice_value_to_char(value)
            content += "\n"
        p2_total = 0
        for i in range(3):
            col_val = self._compute_points_in_col(self._player_2_board, i)
            p2_total += col_val
            content += f"{str(col_val)} "
        content += f"= {p2_total}"
        
        return content

    def _get_current_turn_string(self):
        cur_display_name = self._player_1_display_name if self._turn == self._player_1 else self._player_2_display_name
        base_result = f"It's {cur_display_name}'s turn! They rolled a {str(self._current_roll)}."
        if isinstance(Player, self._turn):
            return f"{base_result} Choose a column to place it in:"
        else:
            return f"{base_result} {cur_display_name} is thinking...\n\n"

    def _check_game_complete(self):
        p1_all_nonzero = True
        p2_all_nonzero = True
        for i in range(3):
            for j in range(3):
                if self._player_1_board[i][j] == 0:
                    p1_all_nonzero = False
                if self._player_2_board[i][j] == 0:
                    p2_all_nonzero = False
        return p1_all_nonzero or p2_all_nonzero

    def _get_winner(self):
        player_1_total = 0
        player_2_total = 0
        for j in range(3):
            player_1_total += self._compute_points_in_col(self._player_1_board, j)
            player_2_total += self._compute_points_in_col(self._player_2_board, j)
        if player_1_total > player_2_total:
            return self._player_1
        if player_2_total > player_1_total:
            return self._player_2
        return None

    def _roll(self):
        if self._use_luck:
            player_luck: int = self._turn.get_expertise().luck
            equipment_luck: int = self._turn.get_equipment().get_total_buffs().lck_buff
            total_luck: int = player_luck + equipment_luck
            self._current_roll = choices(
                [1, 2, 3, 4, 5, 6], k=1, 
                weights=[
                    1/6 - 0.001 * total_luck,
                    1/6 - 0.001 * total_luck,
                    1/6 - 0.001 * total_luck,
                    1/6 + 0.001 * total_luck,
                    1/6 + 0.001 * total_luck,
                    1/6 + 0.001 * total_luck
                ]
            )[0]
        else:
            self._current_roll = randint(1, 6)

    def setup_game(self):
        self.clear_items()
        if isinstance(Player, self._turn):
            for pos in range(3):
                self.add_item(KnucklebonesButton(pos))
        
        self._roll()
        return self._get_game_state_string() + "\n\n" + self._get_current_turn_string()

    def _update_stats(self, winner: Player, amount_won=0, is_tied=False):
        player_1_stats = self._player_1.get_stats()
        player_2_stats = self._player_2.get_stats()
        winner_stats = winner.get_stats()

        player_1_stats.knucklebones.games_played += 1
        player_2_stats.knucklebones.games_played += 1

        if is_tied:
            player_1_stats.knucklebones.games_tied += 1
            player_2_stats.knucklebones.games_tied += 1
            return
        
        winner_stats.knucklebones.games_won += 1

        if amount_won > 0:
            winner_stats.knucklebones.coins_won += amount_won

    def place_roll(self, pos: int):
        can_place = False
        for i in range(3):
            if self._turn == self._player_1:
                if self._player_1_board[i][pos] == 0:
                    self._player_1_board[i][pos] = self._current_roll
                    can_place = True
                    for j in range(3):
                        if self._player_2_board[j][pos] == self._current_roll:
                            self._player_2_board[j][pos] = 0
                    break
            if self._turn == self._player_2:
                if self._player_2_board[i][pos] == 0:
                    self._player_2_board[i][pos] = self._current_roll
                    can_place = True
                    for j in range(3):
                        if self._player_1_board[j][pos] == self._current_roll:
                            self._player_1_board[j][pos] = 0
                    break
        
        if not can_place:
            return None

        if self._check_game_complete():
            self.clear_items()
            winner = self._get_winner()
            winner_display_name = self._player_1_display_name if winner == self._player_1 else self._player_2_display_name
            if winner is not None:
                winner_player: Player = self._get_player(winner.id)
                player_1: Player = self._get_player(self._player_1.id)
                player_2: Player = self._get_player(self._player_2.id)
                
                if self._bet > 0:
                    amount_won = 0
                    player_1_inv = player_1.get_inventory()
                    player_2_inv = player_2.get_inventory()
                    if winner == self._player_1:
                        coins = player_2_inv.get_coins()
                        amount_won = min(coins, self._bet)
                        player_2_inv.remove_coins(amount_won)
                        player_1_inv.add_coins(amount_won)
                    if winner == self._player_2:
                        coins = player_1_inv.get_coins()
                        amount_won = min(coins, self._bet)
                        player_1_inv.remove_coins(amount_won)
                        player_2_inv.add_coins(amount_won)
                    
                    self._update_stats(winner_player, amount_won)
                    return self._get_game_state_string() + f"\n\n{winner_display_name} has won the game and {amount_won} coins!"
                else:
                    self._update_stats(winner_player)
                    return self._get_game_state_string() + f"\n\n{winner_display_name} has won the game!"

            self._update_stats(winner_player, is_tied=True)
            return self._get_game_state_string() + "\n\nIt's a tie! No one wins any coins."

        self._roll()
        self._turn = self._player_1 if self._turn == self._player_2 else self._player_2

        npc_move_turn_str = ""
        pre_npc_move_board = ""
        if isinstance(MrBones, self._turn):
            pre_npc_move_board = self._get_game_state_string() + "\n\n" + self._get_current_turn_string() + "\n────────────────────\n\n"
            npc_move_turn_str = self._turn.make_move(self._player_1_board, self._player_2_board, self._difficulty, self._compute_points_in_col, self._current_roll, self._player_2_display_name) + "\n\n"
            self._roll()
            self._turn = self._player_1 if self._turn == self._player_2 else self._player_2

        return pre_npc_move_board + self._get_game_state_string() + "\n\n" + npc_move_turn_str + self._get_current_turn_string()

    def get_current_turn_player(self):
        return self._turn
        
    def get_accepting_id(self):
        return self._accepting_id
