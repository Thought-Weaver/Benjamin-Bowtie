from discord.ext import commands

class Images(commands.Cog):
    def __init__(self, bot):
        self._bot = bot

    @commands.command(name="cat", help="")
    async def cat_handler(self, context):
        pass

    @commands.command(name="dog", help="")
    async def dog_handler(self, context):
        pass

    @commands.command(name="birb", help="")
    async def birb_handler(self, context):
        pass

    @commands.command(name="xkcd", help="")
    async def xkcd_handler(self, context):
        pass

    @commands.command(name="fractal", help="")
    async def fractal_handler(self, context):
        pass
