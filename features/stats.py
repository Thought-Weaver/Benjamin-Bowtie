from __future__ import annotations

import discord

from discord.embeds import Embed
from discord.ext import commands
from enum import StrEnum
from features.shared.nextbutton import NextButton
from features.shared.prevbutton import PrevButton


class StatCategory(StrEnum):
    Fish = "fish"
    Mail = "mail"
    Market = "market"
    Knucklebones = "knucklebones"
    WishingWell = "wishingwell"
    Dueling = "dueling"
    Garden = "garden"
    Crafting = "crafting"
    Companions = "companions"
    Adventures = "adventures"

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
            self.legendary_fish_caught: int = 0

        def get_name(self):
            return "Fish Stats"

        def get_stats_str(self):
            return (
                f"Common Items Caught: *{self.common_items_caught}*\n"
                f"Rare Items Caught: *{self.rare_items_caught}*\n\n"
                f"Common Fish Caught: *{self.common_fish_caught}*\n"
                f"Uncommon Fish Caught: *{self.uncommon_fish_caught}*\n"
                f"Rare Fish Caught: *{self.rare_fish_caught}*\n"
                f"Epic Fish Caught: *{self.epic_fish_caught}*\n"
                f"Legendary Fish Caught: *{self.legendary_fish_caught}*"
            )

        def __getstate__(self):
            return self.__dict__

        def __setstate__(self, state: dict):
            self.common_items_caught = state.get("common_items_caught", 0)
            self.rare_items_caught = state.get("rare_items_caught", 0)
            
            self.common_fish_caught = state.get("common_fish_caught", 0)
            self.uncommon_fish_caught = state.get("uncommon_fish_caught", 0)
            self.rare_fish_caught = state.get("rare_fish_caught", 0)
            self.epic_fish_caught = state.get("epic_fish_caught", 0)
            self.legendary_fish_caught = state.get("legendary_fish_caught", 0)

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
            return (
                f"Mail Sent: *{self.mail_sent}*\n"
                f"Mail Opened: *{self.mail_opened}*\n\n"
                f"Items Sent: *{self.items_sent}*\n"
                f"Coins Sent: *{self.coins_sent}*\n"
                f"Messages Sent: *{self.messages_sent}*\n\n"
                f"Items Received: *{self.items_received}*\n"
                f"Coins Received: *{self.coins_received}*\n"
                f"Messages Received: *{self.messages_received}*\n\n"
                f"Mail Sent to Self: *{self.mail_sent_to_self}*\n"
                f"Items Sent to Self: *{self.items_sent_to_self}*\n"
                f"Coins Sent to Self: *{self.coins_sent_to_self}*\n"
                f"Messages Sent to Self: *{self.messages_sent_to_self}*"
            )

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
            return (
                f"Items Sold: *{self.items_sold}*\n"
                f"Coins Made: *{self.coins_made}*"
            )

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

            self.npc_easy_games_won: int = 0
            self.npc_easy_games_tied: int = 0
            self.npc_easy_games_played: int = 0

            self.npc_medium_games_won: int = 0
            self.npc_medium_games_tied: int = 0
            self.npc_medium_games_played: int = 0

            self.npc_hard_games_won: int = 0
            self.npc_hard_games_tied: int = 0
            self.npc_hard_games_played: int = 0

            self.mr_bones_games_won: int = 0
            self.mr_bones_games_tied: int = 0
            self.mr_bones_games_played: int = 0

            self.coins_won: int = 0

        def get_name(self):
            return "Knucklebones Stats"

        def get_stats_str(self):
            return (
                f"PvP Games Played: *{self.games_played}*\n"
                f"PvP Games Won: *{self.games_won}*\n"
                f"PvP Games Tied: *{self.games_tied}*\n\n"

                f"NPC Easy Games Played: *{self.npc_easy_games_played}*\n"
                f"NPC Easy Games Won: *{self.npc_easy_games_won}*\n"
                f"NPC Easy Games Tied: *{self.npc_easy_games_tied}*\n\n"

                f"NPC Medium Games Played: *{self.npc_medium_games_played}*\n"
                f"NPC Medium Games Won: *{self.npc_medium_games_won}*\n"
                f"NPC Medium Games Tied: *{self.npc_medium_games_tied}*\n\n"

                f"NPC Hard Games Played: *{self.npc_hard_games_played}*\n"
                f"NPC Hard Games Won: *{self.npc_hard_games_won}*\n"
                f"NPC Hard Games Tied: *{self.npc_hard_games_tied}*\n\n"

                f"Mr. Bones Games Played: *{self.mr_bones_games_played}*\n"
                f"Mr. Bones Games Won: *{self.mr_bones_games_won}*\n"
                f"Mr. Bones Games Tied: *{self.mr_bones_games_tied}*\n\n"

                f"Coins Won: *{self.coins_won}*"
            )

        def __getstate__(self):
            return self.__dict__

        def __setstate__(self, state: dict):
            self.games_won = state.get("games_won", 0)
            self.games_tied = state.get("games_tied", 0)
            self.games_played = state.get("games_played", 0)
            self.coins_won = state.get("coins_won", 0)

            self.npc_easy_games_won = state.get("npc_easy_games_won", 0)
            self.npc_easy_games_tied = state.get("npc_easy_games_tied", 0)
            self.npc_easy_games_played = state.get("npc_easy_games_played", 0)

            self.npc_medium_games_won = state.get("npc_medium_games_won", 0)
            self.npc_medium_games_tied = state.get("npc_medium_games_tied", 0)
            self.npc_medium_games_played = state.get("npc_medium_games_played", 0)

            self.npc_hard_games_won = state.get("npc_hard_games_won", 0)
            self.npc_hard_games_tied = state.get("npc_hard_games_tied", 0)
            self.npc_hard_games_played = state.get("npc_hard_games_played", 0)

            self.mr_bones_games_won = state.get("mr_bones_games_won", 0)
            self.mr_bones_games_tied = state.get("mr_bones_games_tied", 0)
            self.mr_bones_games_played = state.get("mr_bones_games_played", 0)

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

    class DuelingStats():
        def __init__(self):
            self.duels_fought: int = 0
            self.duels_won: int = 0
            self.duels_tied: int = 0

            self.attacks_done: int = 0
            self.abilities_used: int = 0
            self.items_used: int = 0

            self.damage_dealt: int = 0
            self.damage_taken: int = 0
            self.damage_blocked_or_reduced: int = 0
            
            self.attacks_dodged: int = 0
            self.abilities_dodged: int = 0
            self.critical_hit_successes: int = 0

            self.alchemist_abilities_used: int = 0
            self.fisher_abilities_used: int = 0
            self.guardian_abilities_used: int = 0
            self.merchant_abilities_used: int = 0

        def get_name(self):
            return "Dueling Stats"

        def get_stats_str(self):
            return (
                f"Duels Fought: *{self.duels_fought}*\n"
                f"Duels Won: *{self.duels_won}*\n"
                f"Duels Tied: *{self.duels_tied}*\n\n"
                f"Attacks Done: *{self.attacks_done}*\n"
                f"Abilities Used: *{self.abilities_used}*\n"
                f"Items Used: *{self.items_used}*\n\n"
                f"Damage Dealt: *{self.damage_dealt}*\n"
                f"Damage Taken: *{self.damage_taken}*\n"
                f"Damage Blocked or Reduced: *{self.damage_blocked_or_reduced}*\n\n"
                f"Attacks Dodged: *{self.attacks_dodged}*\n"
                f"Abilities Dodged: *{self.abilities_dodged}*\n"
                f"Criticals Hit Successes: *{self.critical_hit_successes}*\n\n"
                f"Alchemist Abilities Used: *{self.alchemist_abilities_used}*\n"
                f"Fisher Abilities Used: *{self.fisher_abilities_used}*\n"
                f"Guardian Abilities Used: *{self.guardian_abilities_used}*\n"
                f"Merchant Abilities Used: *{self.merchant_abilities_used}*"
            )

        def __getstate__(self):
            return self.__dict__

        def __setstate__(self, state: dict):
            self.duels_fought = state.get("duels_fought", 0)
            self.duels_won = state.get("duels_won", 0)
            self.duels_tied = state.get("duels_tied", 0)
            self.attacks_done = state.get("attacks_done", 0)
            self.abilities_used = state.get("abilities_used", 0)
            self.items_used = state.get("items_used", 0)
            self.damage_dealt = state.get("damage_dealt", 0)
            self.damage_taken = state.get("damage_taken", 0)
            self.damage_blocked_or_reduced = state.get("damage_blocked_or_reduced", 0)
            self.attacks_dodged = state.get("attacks_dodged", 0)
            self.abilities_dodged = state.get("abilities_dodged", 0)
            self.critical_hit_successes = state.get("critical_hit_successes", 0)
            self.alchemist_abilities_used = state.get("alchemist_abilities_used", 0)
            self.fisher_abilities_used = state.get("fisher_abilities_used", 0)
            self.guardian_abilities_used = state.get("guardian_abilities_used", 0)
            self.merchant_abilities_used = state.get("merchant_abilities_used", 0)

    class GardenStats():
        def __init__(self):
            self.common_plants_harvested: int = 0
            self.uncommon_plants_harvested: int = 0
            self.rare_plants_harvested: int = 0
            self.epic_plants_harvested: int = 0
            self.legendary_plants_harvested: int = 0

            self.common_seeds_dropped: int = 0
            self.uncommon_seeds_dropped: int = 0
            self.rare_seeds_dropped: int = 0
            self.epic_seeds_dropped: int = 0
            self.legendary_seeds_dropped: int = 0

        def get_name(self):
            return "Garden Stats"

        def get_stats_str(self):
            return (
                f"Common Plants Harvested: *{self.common_plants_harvested}*\n"
                f"Uncommon Plants Harvested: *{self.uncommon_plants_harvested}*\n"
                f"Rare Plants Harvested: *{self.rare_plants_harvested}*\n"
                f"Epic Plants Harvested: *{self.epic_plants_harvested}*\n"
                f"Legendary Plants Harvested: *{self.legendary_plants_harvested}*\n\n"

                f"Common Seeds Dropped: *{self.common_seeds_dropped}*\n"
                f"Uncommon Seeds Harvested: *{self.uncommon_seeds_dropped}*\n"
                f"Rare Seeds Harvested: *{self.rare_seeds_dropped}*\n"
                f"Epic Seeds Harvested: *{self.epic_seeds_dropped}*\n"
                f"Legendary Seeds Harvested: *{self.legendary_seeds_dropped}*"
            )

        def __getstate__(self):
            return self.__dict__

        def __setstate__(self, state: dict):
            self.common_plants_harvested = state.get("common_plants_harvested", 0)
            self.uncommon_plants_harvested = state.get("uncommon_plants_harvested", 0)
            self.rare_plants_harvested = state.get("rare_plants_harvested", 0)
            self.epic_plants_harvested = state.get("epic_plants_harvested", 0)
            self.legendary_plants_harvested = state.get("legendary_plants_harvested", 0)

            self.common_seeds_dropped = state.get("common_seeds_dropped", 0)
            self.uncommon_seeds_dropped = state.get("uncommon_seeds_dropped", 0)
            self.rare_seeds_dropped = state.get("rare_seeds_dropped", 0)
            self.epic_seeds_dropped = state.get("epic_seeds_dropped", 0)
            self.legendary_seeds_dropped = state.get("legendary_seeds_dropped", 0)

    class CraftingStats():
        def __init__(self):
            self.patterns_discovered: int = 0
            self.common_items_crafted: int = 0
            self.uncommon_items_crafted: int = 0
            self.rare_items_crafted: int = 0
            self.epic_items_crafted: int = 0
            self.legendary_items_crafted: int = 0
            self.artifact_items_crafted: int = 0

            self.alchemy_recipes_discovered: int = 0
            self.common_items_alchemized: int = 0
            self.uncommon_items_alchemized: int = 0
            self.rare_items_alchemized: int = 0
            self.epic_items_alchemized: int = 0
            self.legendary_items_alchemized: int = 0
            self.artifact_items_alchemized: int = 0

            self.cooking_recipes_discovered: int = 0
            self.common_items_cooked: int = 0
            self.uncommon_items_cooked: int = 0
            self.rare_items_cooked: int = 0
            self.epic_items_cooked: int = 0
            self.legendary_items_cooked: int = 0
            self.artifact_items_cooked: int = 0

        def get_name(self):
            return "Crafting Stats"

        def get_stats_str(self):
            return (
                f"Patterns Discovered: *{self.patterns_discovered}*\n"
                f"Common Items Crafted: *{self.common_items_crafted}*\n"
                f"Uncommon Items Crafted: *{self.uncommon_items_crafted}*\n"
                f"Rare Items Crafted: *{self.rare_items_crafted}*\n"
                f"Epic Items Crafted: *{self.epic_items_crafted}*\n"
                f"Legendary Items Crafted: *{self.legendary_items_crafted}*\n"
                f"Artifact Items Crafted: *{self.artifact_items_crafted}*\n\n"

                f"Alchemy Recipes Discovered: *{self.alchemy_recipes_discovered}*\n"
                f"Common Items Alchemized: *{self.common_items_alchemized}*\n"
                f"Uncommon Items Alchemized: *{self.uncommon_items_alchemized}*\n"
                f"Rare Items Alchemized: *{self.rare_items_alchemized}*\n"
                f"Epic Items Alchemized: *{self.epic_items_alchemized}*\n"
                f"Legendary Items Alchemized: *{self.legendary_items_alchemized}*\n"
                f"Artifact Items Alchemized: *{self.artifact_items_alchemized}*\n\n"

                f"Cooking Recipes Discovered: *{self.cooking_recipes_discovered}*\n"
                f"Common Items Cooked: *{self.common_items_cooked}*\n"
                f"Uncommon Items Cooked: *{self.uncommon_items_cooked}*\n"
                f"Rare Items Cooked: *{self.rare_items_cooked}*\n"
                f"Epic Items Cooked: *{self.epic_items_cooked}*\n"
                f"Legendary Items Cooked: *{self.legendary_items_cooked}*\n"
                f"Artifact Items Cooked: *{self.artifact_items_cooked}*"
            )

        def __getstate__(self):
            return self.__dict__

        def __setstate__(self, state: dict):
            self.patterns_discovered = state.get("patterns_discovered", 0)
            self.common_items_crafted = state.get("common_items_crafted", 0)
            self.uncommon_items_crafted = state.get("uncommon_items_crafted", 0)
            self.rare_items_crafted = state.get("rare_items_crafted", 0)
            self.epic_items_crafted = state.get("epic_items_crafted", 0)
            self.legendary_items_crafted = state.get("legendary_items_crafted", 0)
            self.artifact_items_crafted = state.get("artifact_items_crafted", 0)

            self.alchemy_recipes_discovered = state.get("alchemy_recipes_discovered", 0)
            self.common_items_alchemized = state.get("common_items_alchemized", 0)
            self.uncommon_items_alchemized = state.get("uncommon_items_alchemized", 0)
            self.rare_items_alchemized = state.get("rare_items_alchemized", 0)
            self.epic_items_alchemized = state.get("epic_items_alchemized", 0)
            self.legendary_items_alchemized = state.get("legendary_items_alchemized", 0)
            self.artifact_items_alchemized = state.get("artifact_items_alchemized", 0)

            self.cooking_recipes_discovered = state.get("cooking_recipes_discovered", 0)
            self.common_items_cooked = state.get("common_items_cooked", 0)
            self.uncommon_items_cooked = state.get("uncommon_items_cooked", 0)
            self.rare_items_cooked = state.get("rare_items_cooked", 0)
            self.epic_items_cooked = state.get("epic_items_cooked", 0)
            self.legendary_items_cooked = state.get("legendary_items_cooked", 0)
            self.artifact_items_cooked = state.get("artifact_items_cooked", 0)

    class CompanionsStats():
        def __init__(self):
            self.companions_found: int = 0
            self.items_fed: int = 0
            self.names_given: int = 0
            self.bond_points_earned: int = 0

            self.companion_battles_fought: int = 0
            self.companion_battles_won: int = 0
            self.companion_battles_tied: int = 0

        def get_name(self):
            return "Companions Stats"

        def get_stats_str(self):
            return (
                f"Companions Found: *{self.companions_found}*\n"
                f"Items Fed: *{self.items_fed}*\n"
                f"Names Given: *{self.names_given}*\n"
                f"Bond Points Earned: *{self.bond_points_earned}*\n\n"

                f"Companion Battles Fought: *{self.companion_battles_fought}*\n"
                f"Companion Battles Won: *{self.companion_battles_won}*\n"
                f"Companion Battles Tied: *{self.companion_battles_tied}*\n"
            )

        def __getstate__(self):
            return self.__dict__

        def __setstate__(self, state: dict):
            self.companions_found = state.get("companions_found", 0)
            self.items_fed = state.get("items_fed", 0)
            self.names_given = state.get("names_given", 0)
            self.bond_points_earned = state.get("bond_points_earned", 0)

            self.companion_battles_fought = state.get("companion_battles_fought", 0)
            self.companion_battles_won = state.get("companion_battles_won", 0)
            self.companion_battles_tied = state.get("companion_battles_tied", 0)

    class DungeonRunStats():
        def __init__(self):
            self.forest_rooms_explored: int = 0
            self.forest_combat_encounters: int = 0
            self.forest_treasure_rooms_encountered: int = 0
            self.forest_shopkeeps_encountered: int = 0
            self.forest_events_encountered: int = 0
            self.forest_rests_taken: int = 0
            self.forest_bosses_defeated: int = 0
            self.forest_adventures_won: int = 0
            self.forest_adventures_played: int = 0

        def get_name(self):
            return "Adventure Stats"

        def get_stats_str(self):
            return (
                f"**Forest:**\n\n"
                f"Rooms Explored: *{self.forest_rooms_explored}*\n"
                f"Combat Encounters: *{self.forest_combat_encounters}*\n"
                f"Treasure Rooms Found: *{self.forest_treasure_rooms_encountered}*\n"
                f"Shopkeepers Met: *{self.forest_shopkeeps_encountered}*\n"
                f"Events Encountered: *{self.forest_events_encountered}*\n"
                f"Rests Taken: *{self.forest_rests_taken}*\n"
                f"Bosses Defeated: *{self.forest_bosses_defeated}*\n"
                f"Adventures Won: *{self.forest_adventures_won}*\n"
                f"Adventures Played: *{self.forest_adventures_played}*"
            )

        def __getstate__(self):
            return self.__dict__

        def __setstate__(self, state: dict):
            self.forest_rooms_explored = state.get("forest_rooms_explored", 0)
            self.forest_combat_encounters = state.get("forest_combat_encounters", 0)
            self.forest_treasure_rooms_encountered = state.get("forest_treasure_rooms_encountered", 0)
            self.forest_shopkeeps_encountered = state.get("forest_shopkeeps_encountered", 0)
            self.forest_events_encountered = state.get("forest_events_encountered", 0)
            self.forest_rests_taken = state.get("forest_rests_taken", 0)
            self.forest_bosses_defeated = state.get("forest_bosses_defeated", 0)
            self.forest_adventures_won = state.get("forest_adventures_won", 0)
            self.forest_adventures_played = state.get("forest_adventures_played", 0)

    def __init__(self):
        self.fish = self.FishStats()
        self.mail = self.MailStats()
        self.market = self.MarketStats()
        self.knucklebones = self.KnucklebonesStats()
        self.wishingwell = self.WishingWellStats()
        self.dueling = self.DuelingStats()
        self.garden = self.GardenStats()
        self.crafting = self.CraftingStats()
        self.companions = self.CompanionsStats()
        self.dungeon_runs = self.DungeonRunStats()

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
        if category == category.Dueling:
            return self.dueling
        if category == category.Garden:
            return self.garden
        if category == category.Crafting:
            return self.crafting
        if category == category.Companions:
            return self.companions
        if category == category.Adventures:
            return self.dungeon_runs

    def list(self):
        # Can simply change the order of this list if I want the pages
        # to be organized differently.
        return [self.fish, self.mail, self.market, self.knucklebones, self.wishingwell, self.dueling, self.garden, self.crafting, self.companions, self.dungeon_runs]

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.fish = state.get("fish", self.FishStats())
        self.mail = state.get("mail", self.MailStats())
        self.market = state.get("market", self.MarketStats())
        self.knucklebones = state.get("knucklebones", self.KnucklebonesStats())
        self.wishingwell = state.get("wishingwell", self.WishingWellStats())
        self.dueling = state.get("dueling", self.DuelingStats())
        self.garden = state.get("garden", self.GardenStats())
        self.crafting = state.get("crafting", self.CraftingStats())
        self.companions = state.get("companions", self.CompanionsStats())
        self.dungeon_runs = state.get("dungeon_runs", self.DungeonRunStats())


class StatView(discord.ui.View):
    def __init__(self, bot: commands.Bot, database: dict, guild_id: int, user: discord.User, display_user: discord.User, stat_category: StatCategory | None=None):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._user = user
        self._display_user = display_user
        self._stat_category = stat_category
        
        self._page = 0
        self._stats_list = Stats().list() # Should be in sync with the player's Stats.list() always

        if stat_category is None:
            self.add_item(PrevButton(0))
            self.add_item(NextButton(0))

    def get_current_page_info(self):
        player_stats: Stats = self._database[str(self._guild_id)]["members"][str(self._display_user.id)].get_stats()

        stat_class = None
        if self._stat_category is not None:
            stat_class = player_stats.category_to_class(self._stat_category)
        else:
            stat_class = player_stats.list()[self._page]

        title = f"{self._display_user.display_name}'s Stats"
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
