import discord


class PrevButton(discord.ui.Button):
    def __init__(self, row: int, block_button: bool=False):
        super().__init__(style=discord.ButtonStyle.blurple, label="Prev", row=row)
        self.disabled = block_button

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        # TODO: Add type hint to this. Need to abstract view class with next/prev callbacks.
        view = self.view
        if interaction.user == view.get_user():
            response = view.prev_page()
            await interaction.response.edit_message(content=None, embed=response, view=view)
