from __future__ import annotations

import discord

from discord import Embed
from features.dueling import ChooseAbilityButton
from features.expertise import ExpertiseClass
from features.shared.ability import Ability, CurseOfTheSeaI, CurseOfTheSeaII, CurseOfTheSeaIII, DrownInTheDeepI, DrownInTheDeepII, DrownInTheDeepIII, HighTideI, HighTideII, HighTideIII, HookI, HookII, HookIII, SeaSprayI, SeaSprayII, SeaSprayIII, SeaSprayIV, SeaSprayV, ShatteringStormI, ShatteringStormII, ShatteringStormIII, ThunderingTorrentI, ThunderingTorrentII, ThunderingTorrentIII, WhirlpoolI, WhirlpoolII, WhirlpoolIII, WrathOfTheWavesI, WrathOfTheWavesII, WrathOfTheWavesIII

from typing import TYPE_CHECKING, List
from features.shared.nextbutton import NextButton

from features.shared.prevbutton import PrevButton
if TYPE_CHECKING:
    from bot import BenjaminBowtieBot
    from features.player import Player

# -----------------------------------------------------------------------------
# TRAINER VIEW GUI
# -----------------------------------------------------------------------------

class FisherTrainerButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"Sea Shrine", row=row)
        
    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: TrainerView = self.view
        if interaction.user == view.get_user():
            response = view.visit_sea_shrine()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class MerchantTrainerButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"Tavern", row=row)
        
    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: TrainerView = self.view
        if interaction.user == view.get_user():
            response = view.visit_tavern()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class GuardianTrainerButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"Dueling Grounds", row=row)
        
    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: TrainerView = self.view
        if interaction.user == view.get_user():
            response = view.visit_dueling_grounds()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class SelectAbilityButton(discord.ui.Button):
    def __init__(self, ability: Ability, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=ability.get_name(), row=row, emoji=ability.get_icon())

        self._ability = ability
        
    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: TrainerView = self.view
        if interaction.user == view.get_user():
            response = view.select_ability(self._ability)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ConfirmPurchaseButton(discord.ui.Button):
    def __init__(self, ability: Ability, row: int):
        super().__init__(style=discord.ButtonStyle.green, label=f"Buy", row=row)
        
        self._ability = ability
        
    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: TrainerView = self.view
        if interaction.user == view.get_user():
            response = view.purchase_ability(self._ability)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class MarketExitButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.red, label="Exit", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: TrainerView = self.view
        if interaction.user == view.get_user():
            response = view.exit_to_main_menu()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class TrainerView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, user: discord.User):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._user = user

        self._page = 0
        self._current_class = ExpertiseClass.Unknown

        self._NUM_PER_PAGE = 4

        self._fisher_abilities: List[List[Ability]] = [
            [SeaSprayI, SeaSprayII, SeaSprayIII, SeaSprayIV, SeaSprayV]
            [CurseOfTheSeaI, CurseOfTheSeaII, CurseOfTheSeaIII]
            [HookI, HookII, HookIII]
            [WrathOfTheWavesI, WrathOfTheWavesII, WrathOfTheWavesIII]
            [HighTideI, HighTideII, HighTideIII]
            [ThunderingTorrentI, ThunderingTorrentII, ThunderingTorrentIII]
            [DrownInTheDeepI, DrownInTheDeepII, DrownInTheDeepIII]
            [WhirlpoolI, WhirlpoolII, WhirlpoolIII]
            [ShatteringStormI, ShatteringStormII, ShatteringStormIII]
        ]

        self._display_initial_buttons()

    def _get_player(self) -> Player:
        return self._database[str(self._guild_id)]["members"][str(self._user.id)]

    def get_initial_info(self):
        return Embed(title="Trainers", description="Who would you like to visit?")

    def get_embed_for_class(self):
        if self._current_class == ExpertiseClass.Fisher:
            return Embed(title="Sea Shrine", description=(
                "An ancient edifice of mottled, grey stone stands before you, seaweed-like vines creeping around the time-worn rock at the edge of the bluff. "
                "The jagged outcropping is marked by a diamond-shaped hole towards the top and some engraved inscription too old to be interpreted. "
                "At the base of the shrine is a wooden bowl and a small selection of candles that seem to be well-tended."
            ))
        if self._current_class == ExpertiseClass.Guardian:
            return Embed(title="Dueling Grounds", description=(
                ""
            ))
        if self._current_class == ExpertiseClass.Merchant:
            return Embed(title="The Dragon and Anchor Tavern", description=(
                ""
            ))
        return Embed(title="Where are you?", description="In the midst of knowing where you were, suddenly now there is a bleak unknown, a pale that sparks fear and awe.")

    def get_available_abilities(self, player: Player, all_abilities: List[List[Ability]]):
        player_abilities: List[Ability] = player.get_dueling().abilities
        available_abilities: List[Ability] = []
        # TODO: Could optimize this significantly?
        for ability_group in all_abilities:
            result: Ability | None = ability_group[0]()
            for i, ability_class in enumerate(ability_group):
                if any(isinstance(ability, ability_class) for ability in player_abilities):
                    if i == len(ability_class) - 1:
                        result = None
                    else:
                        result = ability_group[i + 1]()
                    break
            if result is not None:
                available_abilities.append(result)
        return available_abilities

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(FisherTrainerButton(0))
        self.add_item(GuardianTrainerButton(1))
        self.add_item(MerchantTrainerButton(2))

    def _get_current_page_buttons(self):
        self.clear_items()
        player: Player = self._get_player()

        available_abilities = []
        if self._current_class == ExpertiseClass.Fisher:
            available_abilities = self._fisher_abilities
        if self._current_class == ExpertiseClass.Guardian:
            available_abilities = self._guardian_abilities
        if self._current_class == ExpertiseClass.Merchant:
            available_abilities = self._merchant_abilities
        all_slots = self.get_available_abilities(player, available_abilities)

        page_slots = all_slots[self._page * self._NUM_PER_PAGE:min(len(all_slots), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            self.add_item(ChooseAbilityButton(i, item))
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(all_slots) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        self.add_item(ConfirmPurchaseButton(min(4, len(page_slots))))
        self.add_item(MarketExitButton(min(4, len(page_slots))))

    def next_page(self):
        self._page += 1
        self._get_current_page_buttons()

        return self.get_embed_for_class()

    def prev_page(self):
        self._page = max(0, self._page - 1)
        self._get_current_page_buttons()

        return self.get_embed_for_class()

    def visit_sea_shrine(self):
        self._current_class = ExpertiseClass.Fisher

    def visit_tavern(self):
        self._current_class = ExpertiseClass.Merchant

    def visit_dueling_grounds(self):
        self._current_class = ExpertiseClass.Guardian

    def select_ability(self, ability: Ability):
        pass

    def purchase_ability(self, ability: Ability):
        pass

    def exit_to_main_menu(self):
        self._display_initial_buttons()
        return self.get_initial_info()

    def get_user(self):
        return self._user
