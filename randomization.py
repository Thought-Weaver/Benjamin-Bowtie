from discord.ext import commands
from random import randint, choice
import re

class Randomization(commands.Cog):
    def __init__(self, bot):
        self._bot = bot
        self._roll_pattern = re.compile(r"[0-9]+d[0-9]+", re.IGNORECASE)

    @commands.command(name="coinflip", help="Returns heads or tails at random.")
    async def coinflip_handler(self, context):
        await context.send("It's heads!" if randint(0, 1) == 0 else "It's tails!")

    @commands.command(name="roll", help="Rolls ndm (such as 4d6) dice.", usage="ndm")
    async def roll_handler(self, context, arg):
        is_matched = arg is not None and self._roll_pattern.match(arg)
        if is_matched:
            n, m = arg.split("d")
            result = [randint(1, int(m)) for _ in range(int(n))]
            await context.send(f"Result: {result}\nTotal: {sum(result)}")
        else:
            await context.send("Usage: b!roll ndm -- Example: b!roll 4d6")

    @commands.command(name="choose", help="Chooses an item in a list.", usage="item1 item2 ...")
    async def choose_handler(self, context, *args):
        if args is None or len(args) == 0:
            await context.send("Usage: b!choose item1 item2 ...")
        else:
            result = choice(args)
            await context.send(f"Result: {result}")
