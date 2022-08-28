from random import choice, randint
from discord.ext import commands
import discord

class AcceptButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.green, label="Accept")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: Knucklebones = self.view

        if interaction.user != view.get_player_2():
            await interaction.response.edit_message(
                content="Error: You can't accept this request!",
                view=view
            )
            return
        
        content: str = view.setup_game()
        embed = discord.embeds.Embed(description=content)
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

        if interaction.user != view.get_player_2():
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
        
        super().__init__(style=discord.ButtonStyle.secondary, label="Column", emoji=emoji)
        self._pos = pos

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: Knucklebones = self.view

        if interaction.user != view.get_current_turn_player():
            return

        content = view.place_roll(self._pos)
        embed = discord.embeds.Embed(description=content)
        if content is not None:
            await interaction.response.edit_message(
                embed=embed,
                content=None,
                view=view
            )


class Knucklebones(discord.ui.View):
    def __init__(self, bot: commands.Bot, database: dict, guild_id: int, player_1: discord.User, player_2: discord.User, bet: int):
        super().__init__()

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._player_1 = player_1
        self._player_2 = player_2
        self._current_roll = 0
        self._bet = 0

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

    def _dice_value_to_char(self, value):
        if value == 1:
            return "⚀"
        if value == 2:
            return "⚁"
        if value == 3:
            return "⚂"
        if value == 4:
            return "⚃"
        if value == 5:
            return "⚄"
        if value == 6:
            return "⚅"
        return "⬜"

    def _compute_points_in_col(self, board: list[list[int]], col_num: int):
        counts = {}
        for i in range(3):
            counts[board[i][col_num]] = counts.get(board[i][col_num], 0) + 1
        return sum([num * count for num, count in counts.items()])

    def _get_game_state_string(self):
        content = self._player_1.display_name + "\n\n"
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

        content += "\n\n" + self._player_2.display_name + "\n\n"
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
        return f"It's {self._turn.display_name}'s turn! They rolled a {str(self._current_roll)}."

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

    def setup_game(self):
        self.clear_items()
        for pos in range(3):
            self.add_item(KnucklebonesButton(pos))
        self._current_roll = randint(1, 6)
        return self._get_game_state_string() + "\n\n" + self._get_current_turn_string()

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
            if winner is not None:
                if self._bet > 0:
                    amount_won = 0
                    if winner == self._player_1:
                        coins = self._database[self._guild_id]["members"][self._player_2.id].get_inventory().get_coins()
                        amount_won = min(coins, self._bet)
                        self._database[self._guild_id]["members"][self._player_2.id].get_inventory().remove_coins(amount_won)
                        self._database[self._guild_id]["members"][self._player_1.id].get_inventory().add_coins(amount_won)
                    if winner == self._player_2:
                        coins = self._database[self._guild_id]["members"][self._player_1.id].get_inventory().get_coins()
                        amount_won = min(coins, self._bet)
                        self._database[self._guild_id]["members"][self._player_1.id].get_inventory().remove_coins(amount_won)
                        self._database[self._guild_id]["members"][self._player_2.id].get_inventory().add_coins(amount_won)
                    return self._get_game_state_string() + f"\n\n{winner.display_name} has won the game and {amount_won} coins!"
                else:
                    return self._get_game_state_string() + f"\n\n{winner.display_name} has won the game!"
            return self._get_game_state_string() + "\n\nIt's a tie! No one wins any coins."

        self._current_roll = randint(1, 6)
        self._turn = self._player_1 if self._turn == self._player_2 else self._player_2
        return self._get_game_state_string()

    def get_player_2(self):
        return self._player_2

    def get_current_turn_player(self):
        return self._turn
