from __future__ import annotations

import logging
import os

from discord.ext import commands
from discord import Intents
from dotenv import load_dotenv

# -----------------------------------------------------------------------------
# GLOBALS
# -----------------------------------------------------------------------------

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
VERSION_NUMBER = "20230121" # Just for tracking releases

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
    dt_fmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter("[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style='{')
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

ERROR_LOGGER = setup_logger("discord", "errors.log", logging.ERROR)
INFO_LOGGER = setup_logger("discord", "info.log")

# -----------------------------------------------------------------------------
# COMMAND HANDLERS
# -----------------------------------------------------------------------------

@bot.check
async def globally_block_dms(context: commands.Context):
    return context.guild is not None

@bot.event
async def on_command_error(context: commands.Context, error):
  if isinstance(error, commands.CommandOnCooldown):
    await context.send(f"This command is on cooldown. You can use it in {round(error.retry_after, 2)} seconds.")

# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    bot.run(TOKEN, log_handler=None)
