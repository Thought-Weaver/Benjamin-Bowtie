import discord

from discord.embeds import Embed
from discord.ext import commands
from strenum import LowercaseStrEnum
from features.shared.nextbutton import NextButton
from features.shared.prevbutton import PrevButton


class StatCategory(LowercaseStrEnum):
    Fish = "fish"
    Mail = "mail"
    Market = "market"
    Knucklebones = "knucklebones"
    WishingWell = "wishingwell"

# Based on the command names; the user will do b!stats [name] or omit the name
# and get all of them at once. I'm using a class to help with deserializing the
# object and having some type safety -- a strange thing to say in Python, I
# know.
class Stats():
    # Using subclasses because these should never be instantiated by anything
    # other than Stats.
    class FishStats():
        def __init__(self):
            self.common_items_caught: int = 0
            self.rare_items_caught: int = 0

            self.common_fish_caught: int = 0
            self.uncommon_fish_caught: int = 0
            self.rare_fish_caught: int = 0
            self.epic_fish_caught: int = 0

        def get_name(self):
            return "Fish Stats"

        def get_stats_str(self):
            return f"Common Items Caught: *{self.common_items_caught}*\n" \
            f"Rare Items Caught: *{self.rare_items_caught}*\n\n" \
            f"Common Fish Caught: *{self.common_fish_caught}*\n" \
            f"Uncommon Fish Caught: *{self.uncommon_fish_caught}*\n" \
            f"Rare Fish Caught: *{self.rare_fish_caught}*\n" \
            f"Epic Fish Caught: *{self.epic_fish_caught}*"

        def __getstate__(self):
            return self.__dict__

        def __setstate__(self, state: dict):
            self.common_items_caught = state.get("common_items_caught", 0)
            self.rare_items_caught = state.get("rare_items_caught", 0)
            self.common_fish_caught = state.get("common_fish_caught", 0)
            self.uncommon_fish_caught = state.get("uncommon_fish_caught", 0)
            self.rare_fish_caught = state.get("rare_fish_caught", 0)
            self.epic_fish_caught = state.get("epic_fish_caught", 0)

    class MailStats():
        def __init__(self):
            self.mail_sent: int = 0
            self.mail_opened: int = 0
            self.items_sent: int = 0
            self.coins_sent: int = 0
            self.messages_sent: int = 0

            self.items_received: int = 0
            self.coins_received: int = 0
            self.messages_received: int = 0

            self.mail_sent_to_self: int = 0
            self.items_sent_to_self: int = 0
            self.coins_sent_to_self: int = 0
            self.messages_sent_to_self: int = 0

        def get_name(self):
            return "Mail Stats"

        def get_stats_str(self):
            return f"Mail Sent: *{self.mail_sent}*\n" \
            f"Mail Opened: *{self.mail_opened}*\n\n" \
            f"Items Sent: *{self.items_sent}*\n" \
            f"Coins Sent: *{self.coins_sent}*\n" \
            f"Messages Sent: *{self.messages_sent}*\n\n" \
            f"Items Received: *{self.items_received}*\n" \
            f"Coins Received: *{self.coins_received}*\n" \
            f"Messages Received: *{self.messages_received}*\n\n" \
            f"Mail Sent to Self: *{self.mail_sent_to_self}*\n" \
            f"Items Sent to Self: *{self.items_sent_to_self}*\n" \
            f"Coins Sent to Self: *{self.coins_sent_to_self}*\n" \
            f"Messages Sent to Self: *{self.messages_sent_to_self}*"

        def __getstate__(self):
            return self.__dict__

        def __setstate__(self, state: dict):
            self.mail_sent = state.get("mail_sent", 0)
            self.mail_opened = state.get("mail_opened", 0)
            self.items_sent = state.get("items_sent", 0)
            self.coins_sent = state.get("coins_sent", 0)
            self.messages_sent = state.get("messages_sent", 0)
            self.items_received = state.get("items_received", 0)
            self.coins_received = state.get("coins_received", 0)
            self.messages_received = state.get("messages_received", 0)
            self.mail_sent_to_self = state.get("mail_sent_to_self", 0)
            self.items_sent_to_self = state.get("items_sent_to_self", 0)
            self.coins_sent_to_self = state.get("coins_sent_to_self", 0)
            self.messages_sent_to_self = state.get("messages_sent_to_self", 0)

    class MarketStats():
        def __init__(self):
            self.items_sold: int = 0
            self.coins_made: int = 0

        def get_name(self):
            return "Market Stats"

        def get_stats_str(self):
            return f"Items Sold: *{self.items_sold}*\n" \
            f"Coins Made: *{self.coins_made}*"

        def __getstate__(self):
            return self.__dict__

        def __setstate__(self, state: dict):
            self.items_sold = state.get("items_sold", 0)
            self.coins_made = state.get("coins_made", 0)

    class KnucklebonesStats():
        def __init__(self):
            self.games_won: int = 0
            self.games_tied: int = 0
            self.games_played: int = 0
            self.coins_won: int = 0

        def get_name(self):
            return "Knucklebones Stats"

        def get_stats_str(self):
            return f"Games Played: *{self.games_played}*\n" \
            f"Games Won: *{self.games_won}*\n" \
            f"Games Tied: *{self.games_tied}*\n" \
            f"Coins Won: *{self.coins_won}*"

        def __getstate__(self):
            return self.__dict__

        def __setstate__(self, state: dict):
            self.games_won = state.get("games_won", 0)
            self.games_tied = state.get("games_tied", 0)
            self.games_played = state.get("games_played", 0)
            self.coins_won = state.get("coins_won", 0)

    class WishingWellStats():
        def __init__(self):
            self.coins_tossed: int = 0
            self.coins_received: int = 0
            self.items_received: int = 0
            self.something_stirs: int = 0

        def get_name(self):
            return "Wishing Well Stats"

        def get_stats_str(self):
            stats_str = f"Coins Tossed: *{self.coins_tossed}*"
            if self.coins_received != 0:
                stats_str += f"\n||Coins Received||: *{self.coins_received}*"
            if self.items_received != 0:
                stats_str += f"\n||Items Received||: *{self.items_received}*"
            if self.something_stirs != 0:
                stats_str += f"\n||Something Stirs||: *{self.something_stirs}*"
            return stats_str

        def __getstate__(self):
            return self.__dict__

        def __setstate__(self, state: dict):
            self.coins_tossed = state.get("coins_tossed", 0)
            self.coins_received = state.get("coins_received", 0)
            self.items_received = state.get("items_received", 0)
            self.something_stirs = state.get("something_stirs", 0)

    def __init__(self):
        self.fish = self.FishStats()
        self.mail = self.MailStats()
        self.market = self.MarketStats()
        self.knucklebones = self.KnucklebonesStats()
        self.wishingwell = self.WishingWellStats()

    def category_to_class(self, category: StatCategory):
        if category == category.Fish:
            return self.fish
        if category == category.Mail:
            return self.mail
        if category == category.Market:
            return self.market
        if category == category.Knucklebones:
            return self.knucklebones
        if category == category.WishingWell:
            return self.wishingwell

    def list(self):
        # Can simply change the order of this list if I want the pages
        # to be organized differently.
        return [self.fish, self.mail, self.market, self.knucklebones, self.wishingwell]

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.fish = state.get("fish", self.FishStats())
        self.mail = state.get("mail", self.MailStats())
        self.market = state.get("market", self.MarketStats())
        self.knucklebones = state.get("knucklebones", self.KnucklebonesStats())
        self.wishingwell = state.get("wishingwell", self.WishingWellStats())


class StatView(discord.ui.View):
    def __init__(self, bot: commands.Bot, database: dict, guild_id: int, user: discord.User, stat_category: StatCategory=None):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._user = user
        self._stat_category = stat_category
        self._page = 0
        self._stats_list = Stats().list() # Should be in sync with the player's Stats.list() always

        if stat_category is None:
            self.add_item(PrevButton(0))
            self.add_item(NextButton(0))

    def get_current_page_info(self):
        player_stats: Stats = self._database[str(self._guild_id)]["members"][str(self._user.id)].get_stats()

        stat_class = None
        if self._stat_category is not None:
            stat_class = player_stats.category_to_class(self._stat_category)
        else:
            stat_class = player_stats.list()[self._page]

        title = f"{self._user.display_name}'s Stats"
        page_str = f"*({self._page + 1}/{len(self._stats_list)})*" if self._stat_category is None else ""
        description = f"**{stat_class.get_name()}**\n\n{stat_class.get_stats_str()}\n\n{page_str}"
        return Embed(title=title, description=description)

    def next_page(self):
        self._page = (self._page + 1) % len(self._stats_list)
        return self.get_current_page_info()

    def prev_page(self):
        self._page = (self._page - 1) % len(self._stats_list)
        return self.get_current_page_info()

    def get_user(self):
        return self._user
