import discord


# Could abstract into a generic button with some callback in the parent view?
class NextButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.blurple, label="Next", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        # TODO: Add type hint to this. Need to abstract view class with next/prev callbacks.
        view = self.view
        if interaction.user == view.get_user():
            response = view.next_page()
            await interaction.response.edit_message(content=None, embed=response, view=view)
