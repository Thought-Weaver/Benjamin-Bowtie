from discord.ext import commands
from discord import Intents
from dotenv import load_dotenv

import logging
import os

# -----------------------------------------------------------------------------
# GLOBALS
# -----------------------------------------------------------------------------

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

class BenjaminBowtieBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or("b!"), intents=Intents().all())

    async def setup_hook(self):
        await self.load_extension("cogs.images")
        await self.load_extension("cogs.randomization")
        await self.load_extension("cogs.adventures")

bot = BenjaminBowtieBot()

# -----------------------------------------------------------------------------
# LOGGING
# -----------------------------------------------------------------------------

def setup_logger(name, log_file, level=logging.INFO):
    formatter = logging.Formatter('%(asctime)s: %(name)s: %(levelname)s: %(message)s')
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

ERROR_LOGGER = setup_logger("error_logger", "errors.log", logging.ERROR)
INFO_LOGGER = setup_logger("info_logger", "info.log")

# -----------------------------------------------------------------------------
# COMMAND HANDLERS
# -----------------------------------------------------------------------------

@bot.check
async def globally_block_dms(context):
    return context.guild is not None

@bot.event
async def on_command_error(context, error):
  if isinstance(error, commands.CommandOnCooldown):
    await context.send(f"This command is on cooldown. You can use it in {round(error.retry_after, 2)} seconds.")

# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    bot.run(TOKEN)
