from discord.ext import commands

class Music(commands.Cog):
    def __init__(self, bot):
        self._bot = bot
        self._song_queue = []
        self._current_song = None

    @commands.command(name="play", help="")
    async def play_handler(self, context):
        pass

    @commands.command(name="lyrics", help="")
    async def lyrics_handler(self, context):
        pass

    @commands.command(name="nowplaying", help="")
    async def nowplaying_handler(self, context):
        pass

    @commands.command(name="showqueue", help="")
    async def showqueue_handler(self, context):
        pass

    @commands.command(name="remove", help="")
    async def remove_handler(self, context):
        pass

    @commands.command(name="pause", help="")
    async def pause_handler(self, context):
        pass

    @commands.command(name="resume", help="")
    async def resume_handler(self, context):
        pass

    @commands.command(name="search", help="")
    async def search_handler(self, context):
        pass

    @commands.command(name="seek", help="")
    async def seek_handler(self, context):
        pass

    @commands.command(name="shuffle", help="")
    async def shuffle_handler(self, context):
        pass

    @commands.command(name="skip", help="")
    async def skip_handler(self, context):
        pass

    @commands.command(name="stop", help="")
    async def stop_handler(self, context):
        pass

    @commands.command(name="volume", help="")
    async def volume_handler(self, context):
        pass