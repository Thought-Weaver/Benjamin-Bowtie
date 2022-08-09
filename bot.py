from discord.ext import commands
from dotenv import load_dotenv

import logging
import os

from music import Music
from randomization import Randomization
from images import Images

# -----------------------------------------------------------------------------
# GLOBALS
# -----------------------------------------------------------------------------

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix="b!")

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

# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    # Register the cogs
    bot.add_cog(Music(bot))
    bot.add_cog(Randomization(bot))
    bot.add_cog(Images(bot))

    # Run the bot
    bot.run(TOKEN)