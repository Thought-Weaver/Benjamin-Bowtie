from __future__ import annotations

import discord
import random

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.companions.companion import VoidformedMimicCompanion
from features.expertise import Attribute
from features.npcs.npc import NPCDuelingPersonas
from features.shared.enums import CompanionKey
from features.shared.item import LOADED_ITEMS, ItemKey
from features.stories.ocean.combat.abyssal_plain.false_village_duel import FalseVillageDuelView
from features.stories.ocean.combat.npcs.clone import Clone
from features.stories.ocean.combat.npcs.faceless_husk import FacelessHusk
from features.views.dueling_view import DuelView

from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from features.npcs.npc import NPC
    from features.player import Player
    from features.stories.dungeon_run import DungeonRun

# -----------------------------------------------------------------------------
# DUEL VICTORY
# -----------------------------------------------------------------------------

class DuelVictoryContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: VictoryView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        next_view: FalseVillageDuelView = FalseVillageDuelView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = next_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=next_view, content=None)


class VictoryView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run

        self._display_initial_buttons()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_initial_embed(self):
        return Embed(title="Illusion Shattered", description="The terrifying eldritch copies of you begin to disintegrate and crumble as the final blow is dealt -- and against all odds, you've defeated the entities which held sway over the abyss of the sea. Their forms fall apart to merge with the sand below but the presence here only seems to grow stronger.")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(DuelVictoryContinueButton())

    def get_bot(self):
        return self._bot

    def get_users(self):
        return self._users

    def get_players(self):
        return [self._get_player(user.id) for user in self._users]

    def get_database(self):
        return self._database

    def get_guild_id(self):
        return self._guild_id
    
    def get_group_leader(self):
        return self._group_leader
    
    def get_dungeon_run(self):
        return self._dungeon_run

# -----------------------------------------------------------------------------
# CLONE DEFEAT VIEW
# -----------------------------------------------------------------------------

class CloneDefeatView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun, players_joined_willingly: List[Player]):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run
        self._players_joined_willingly = players_joined_willingly

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def _generate_run_info(self):
        info_str: str = (
            f"Rooms Explored: {self._dungeon_run.rooms_explored}\n\n"
            f"Combat Encounters: {self._dungeon_run.combat_encounters}\n"
            f"Treasure Rooms Found: {self._dungeon_run.treasure_rooms_encountered}\n"
            f"Shopkeeps Met: {self._dungeon_run.shopkeeps_encountered}\n"
            f"Events Encountered: {self._dungeon_run.events_encountered}\n\n"
            f"Rests Taken: {self._dungeon_run.rests_taken}\n"
            f"Bosses Defeated: {self._dungeon_run.bosses_defeated}"
        )
        return info_str

    def _update_player_stats(self):
        for user in self._users:
            player = self._get_player(user.id)
            ps = player.get_stats().dungeon_runs

            ps.ocean_rooms_explored += self._dungeon_run.rooms_explored
            ps.ocean_combat_encounters += self._dungeon_run.combat_encounters
            ps.ocean_treasure_rooms_encountered += self._dungeon_run.treasure_rooms_encountered
            ps.ocean_shopkeeps_encountered += self._dungeon_run.shopkeeps_encountered
            ps.ocean_events_encountered += self._dungeon_run.events_encountered
            ps.ocean_rests_taken += self._dungeon_run.rests_taken
            ps.ocean_bosses_defeated += self._dungeon_run.bosses_defeated
            ps.ocean_adventures_played += 1

    def get_initial_embed(self):
        post_run_info_str: str = self._generate_run_info()
        
        self._update_player_stats()

        for player in self._players_joined_willingly:
            companions = player.get_companions()
            if CompanionKey.VoidformedMimic not in companions.companions.keys():
                companions.companions[CompanionKey.VoidformedMimic] = VoidformedMimicCompanion()
                companions.companions[CompanionKey.VoidformedMimic].set_id(player.get_id())

                player.get_stats().companions.companions_found += 1
            
            player.get_inventory().add_item(LOADED_ITEMS.get_new_item(ItemKey.MarkOfCorruption))

        for user in self._users:
            player = self._get_player(user.id)
            player.get_dungeon_run().in_dungeon_run = False

        return Embed(title="From the Mirror", description=f"The cacophony of the chant grows louder and louder as the lights around you shift and dance madly. The throne is before you -- take it, take it! This is the world now, the screaming terror of those with sight of what is yet to come. Or is it already?\n\nSomething latches onto you, crawling up your leg like a misshapen, sloughing worm. Everything begins to fade as it grows and moves upwards towards your head. You collapse to the sand, the world spinning--\n\nThen suddenly there's a flash somewhere just beyond your vision. A bolt of lightning streaks through the water and pierces the figure by the throne, arcing across your party and the eldritch creatures attached to you. A hand grabs your own and pulls as your vision finally goes dark.\n\nThose who willingly chose to take the throne feel not all of it was destroyed by the attack. A new companion has been added to b!companions and a Mark of Corruption added to your inventory.\n\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\n{post_run_info_str}")

    def any_in_duels_currently(self):
        return any(self._get_player(user.id).get_dueling().is_in_combat for user in self._users)

    def get_bot(self):
        return self._bot

    def get_users(self):
        return self._users

    def get_database(self):
        return self._database

    def get_guild_id(self):
        return self._guild_id

    def get_group_leader(self):
        return self._group_leader

    def get_dungeon_run(self):
        return self._dungeon_run

# -----------------------------------------------------------------------------
# DUEL INTRO
# -----------------------------------------------------------------------------

class ContinueToDuelButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        await interaction.response.defer()
        assert(interaction.message is not None)

        view: CloneDuelView = self.view

        enemies = view.generate_enemies()

        victory_view: VictoryView = VictoryView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        defeat_view: CloneDefeatView = CloneDefeatView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run(), view.players_joined_willingly)
        duel_view: DuelView = DuelView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.players_resisted, enemies, player_victory_post_view=victory_view, player_loss_post_view=defeat_view)
        initial_info: Embed = duel_view.get_initial_embed()

        await interaction.followup.edit_message(message_id=interaction.message.id, embed=initial_info, view=duel_view, content=None)


class JoinButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Join")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        await interaction.response.defer()
        assert(interaction.message is not None)
        
        view: CloneDuelView = self.view

        result_embed: Embed = view.join(interaction.user)
        if len(view.get_users()) != len(view.players_joined_with_fail) + len(view.players_resisted) + len(view.players_joined_willingly):
            await interaction.followup.edit_message(message_id=interaction.message.id, embed=result_embed, view=view, content=None)
            return

        defeat_view: CloneDefeatView = CloneDefeatView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run(), view.players_joined_willingly)

        if len(view.get_users()) == len(view.players_joined_with_fail) + len(view.players_joined_willingly):
            # In the case where all the players joined the false village
            await interaction.followup.edit_message(message_id=interaction.message.id, embed=defeat_view.get_initial_embed(), view=defeat_view, content=None)
            return

        await interaction.followup.edit_message(message_id=interaction.message.id, embed=result_embed, view=view, content=None)


class ResistButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Resist")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        await interaction.response.defer()
        assert(interaction.message is not None)

        view: CloneDuelView = self.view

        result_embed: Embed = view.resist(interaction.user)
        if len(view.get_users()) != len(view.players_joined_with_fail) + len(view.players_resisted) + len(view.players_joined_willingly):
            await interaction.followup.edit_message(message_id=interaction.message.id, embed=result_embed, view=view, content=None)
            return

        defeat_view: CloneDefeatView = CloneDefeatView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run(), view.players_joined_willingly)

        if len(view.get_users()) == len(view.players_joined_with_fail) + len(view.players_joined_willingly):
            # In the case where all the players joined the false village
            await interaction.followup.edit_message(message_id=interaction.message.id, embed=defeat_view.get_initial_embed(), view=defeat_view, content=None)
            return

        await interaction.followup.edit_message(message_id=interaction.message.id, embed=result_embed, view=view, content=None)


class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: CloneDuelView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the duel.")
            return
        
        if view.any_in_duels_currently():
            await interaction.response.edit_message(content="At least one person is already in a duel. This duel has been cancelled.")
            return

        if view.times_pressed == 0:
            view.times_pressed = 1
            next_embed = view.get_second_page()
            await interaction.response.edit_message(embed=next_embed, view=view, content=None)
        else:
            next_embed = view.get_resist_or_join_page()
            await interaction.response.edit_message(embed=next_embed, view=view, content=None)


class CloneDuelView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run

        self.times_pressed: int = 0

        self.players_joined_willingly: List[Player] = []
        self.players_joined_with_fail: List[Player] = []
        self.resisted_names: List[str] = []
        self.players_resisted: List[Player] = []
        
        self._display_initial_buttons()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_initial_embed(self):
        return Embed(title="The Outskirts", description="Venturing on across the endless waste of sand and stone, you soon come to the outskirts of the false village. The lights you saw before cast an eerie pallor across the entire scene: The structures here are warped and appear like dilapidated homes and stores. You can even see some kind of tent a ways from where you stand and a pier -- though it makes no sense for one to exist underwater.\n\nEverything is malformed, as if created by some twisted sense of reality, and the very materials used to construct them are wrong: They seem to be some amalgam of kelp, broken shells, the carapaces of crustaceans, driftwood, and worse. Their windows emit a radiance like the lights above you, which seem to be growing out of the buildings like anglerfish stalks; inside, you can't see anything except shadows that seem to move even though your party stands still.\n\nSomething here whispers in your mind with an otherworldly sentience -- perhaps not malevolent, but clearly unable to understand you or those like you. It's at this moment, the building begins to shift and undulate, rearranging itself into a slightly different form, though no less flawed.")

    def get_second_page(self):
        return Embed(title="Somewhere Familiar", description="As you continue past what could only be described as a warped tavern, you begin to reach the center of this imitation. Fragments of voices seem to call out to you from each place you pass, repeating in an uneasy chorus: \"You walk on chains with your eyes. Push the fingers through the surface into the void...\"\n\nHere, at the heart of the village, stands a mound of conches, scuttling crabs all incorrectly formed, and smothering stranglekelp. It looks almost as though it's been shaped into a grand seat. A throne. From it, something detaches, stretches, and reforms into something that looks oddly like paper. It floats away from the village outwards into the darkness of the plan.\n\nKneeling before the throne is a husk -- not unlike those you encountered before reaching the village. As you get closer, it begins to move, turning to face you all. The voice that emerges from somewhere, despite a nonexistent mouth, is guttural but cordial, \"You have come at last. The throne is yours, Fisher King. Join us. JOIN US.\"")

    def get_resist_or_join_page(self):
        self.clear_items()

        if len(self.get_users()) == len(self.players_joined_with_fail) + len(self.players_resisted) + len(self.players_joined_willingly):
            self.add_item(ContinueToDuelButton())
            return Embed(title="All Will Be Us", description="With an otherworldly noise, the creature before you screams in fury and dismay at those who resisted the call of this place and the throne they have prepared. From the building facsimiles, globs of sand, seaweed, and exoskeleton begin to form into multiple new beings that rush at you with mostly blank expressions.\n\nThose faces which aren't empty seem familiar -- far too familiar.")
        
        self.add_item(JoinButton())
        self.add_item(ResistButton())

        resist_chance_strs = []
        for user in self._users:
            corruption = self._get_player(user.id).get_dungeon_run().corruption
            chance_resist = int(100 * (1 - corruption * 0.02))
            resist_chance_strs.append(f"{user.display_name} has {corruption} stacks of Corruption and a {chance_resist}% chance to resist")
        resistance_str = "\n".join(resist_chance_strs)

        return Embed(title="Decide", description=f"It's time to make your choice:\n\n{resistance_str}\n\n{len(self.players_joined_willingly + self.players_joined_with_fail)}/{len(self._users)} wish to take the throne\n{len(self.players_resisted)}/{len(self._users)} resisted the call of the sea")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(ContinueButton())

    def join(self, user: discord.User):
        player: Player = self._get_player(user.id)
        combined = self.players_joined_willingly + self.players_joined_with_fail + self.players_resisted
        if player not in combined:
            self.players_joined_willingly.append(player)
        return self.get_resist_or_join_page()

    def resist(self, user: discord.User):
        player: Player = self._get_player(user.id)
        combined = self.players_joined_willingly + self.players_joined_with_fail + self.players_resisted
        if player not in combined:
            if random.random() < 0.02 * player.get_dungeon_run().corruption:
                self.players_joined_with_fail.append(player)
            else:
                self.resisted_names.append(user.display_name)
                self.players_resisted.append(player)
        return self.get_resist_or_join_page()

    def generate_enemies(self):
        enemies: List[Player | NPC] = self.players_joined_willingly + self.players_joined_with_fail # type: ignore
        for name, player in zip(self.resisted_names, self.players_resisted):
            persona = NPCDuelingPersonas.Unknown
            
            combined_attrs = player.get_expertise().get_all_attributes() + player.get_equipment().get_total_attribute_mods()
            attr_dict = {
                Attribute.Strength: combined_attrs.strength,
                Attribute.Dexterity: combined_attrs.dexterity,
                Attribute.Intelligence: combined_attrs.intelligence,
                Attribute.Luck: combined_attrs.luck
            }
            
            max_attr_key = max(attr_dict, key=attr_dict.get) # type: ignore
            if max_attr_key == Attribute.Strength:
                persona = NPCDuelingPersonas.Bruiser
            elif max_attr_key == Attribute.Dexterity:
                persona = NPCDuelingPersonas.Rogue
            elif max_attr_key == Attribute.Intelligence:
                persona = NPCDuelingPersonas.Mage
            elif max_attr_key == Attribute.Luck:
                persona = NPCDuelingPersonas.Mage
            
            enemy = Clone(name + "?", player.get_expertise(), player.get_equipment(), player.get_dueling().abilities, persona)
            enemies.append(enemy)

        while len(enemies) < 3:
            fh = FacelessHusk()
            enemy = Clone("Faceless Husk", fh.get_expertise(), fh.get_equipment(), fh.get_dueling().abilities, fh._dueling_persona)
            enemies.append(enemy)

        return enemies

    def any_in_duels_currently(self):
        return any(self._get_player(user.id).get_dueling().is_in_combat for user in self._users)

    def get_bot(self):
        return self._bot

    def get_users(self):
        return self._users

    def get_players(self):
        return [self._get_player(user.id) for user in self._users]

    def get_database(self):
        return self._database

    def get_guild_id(self):
        return self._guild_id
    
    def get_group_leader(self):
        return self._group_leader
    
    def get_dungeon_run(self):
        return self._dungeon_run
