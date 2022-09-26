from __future__ import annotations

import discord

from discord import Embed
from features.expertise import Expertise, ExpertiseClass
from features.shared.ability import ATidySumI, ATidySumII, ATidySumIII, Ability, BidedAttackI, BidedAttackII, BidedAttackIII, BoundToGetLuckyI, BoundToGetLuckyII, BoundToGetLuckyIII, ContractBloodForBloodI, ContractBloodForBloodII, ContractBloodForBloodIII, ContractManaToBloodI, ContractManaToBloodII, ContractManaToBloodIII, ContractWealthForPowerI, ContractWealthForPowerII, ContractWealthForPowerIII, CounterstrikeI, CounterstrikeII, CounterstrikeIII, CurseOfTheSeaI, CurseOfTheSeaII, CurseOfTheSeaIII, CursedCoinsI, CursedCoinsII, CursedCoinsIII, DeepPocketsI, DeepPocketsII, DeepPocketsIII, DrownInTheDeepI, DrownInTheDeepII, DrownInTheDeepIII, EvadeI, EvadeII, EvadeIII, HeavySlamI, HeavySlamII, HeavySlamIII, HighTideI, HighTideII, HighTideIII, HookI, HookII, HookIII, PiercingStrikeI, PiercingStrikeII, PiercingStrikeIII, PressTheAdvantageI, ScarArmorI, ScarArmorII, SeaSprayI, SeaSprayII, SeaSprayIII, SeaSprayIV, SeaSprayV, SecondWindI, SecondWindII, SecondWindIII, ShatteringStormI, ShatteringStormII, ShatteringStormIII, SilkspeakingI, TauntI, ThunderingTorrentI, ThunderingTorrentII, ThunderingTorrentIII, UnbreakingI, UnbreakingII, UnbreakingIII, UnseenRichesI, UnseenRichesII, UnseenRichesIII, WhirlpoolI, WhirlpoolII, WhirlpoolIII, WhirlwindI, WhirlwindII, WhirlwindIII, WrathOfTheWavesI, WrathOfTheWavesII, WrathOfTheWavesIII

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
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.green, label=f"Buy", row=row)
                
    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: TrainerView = self.view
        if interaction.user == view.get_user():
            response = view.purchase_ability()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class EnterEquipAbilitiesButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"Equip Abilities", row=row)
                
    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: TrainerView = self.view
        if interaction.user == view.get_user():
            new_view = EquipAbilitiesView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_user())
            await interaction.response.edit_message(content=None, embed=new_view.get_initial_info(), view=new_view)


class ExitTrainerButton(discord.ui.Button):
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

        self._page: int = 0
        self._current_ability: Ability | None = None
        self._current_class: ExpertiseClass = ExpertiseClass.Unknown

        self._NUM_PER_PAGE = 4

        self._fisher_abilities: List[List[Ability]] = [
            [SeaSprayI, SeaSprayII, SeaSprayIII, SeaSprayIV, SeaSprayV],
            [CurseOfTheSeaI, CurseOfTheSeaII, CurseOfTheSeaIII],
            [HookI, HookII, HookIII],
            [WrathOfTheWavesI, WrathOfTheWavesII, WrathOfTheWavesIII],
            [HighTideI, HighTideII, HighTideIII],
            [ThunderingTorrentI, ThunderingTorrentII, ThunderingTorrentIII],
            [DrownInTheDeepI, DrownInTheDeepII, DrownInTheDeepIII],
            [WhirlpoolI, WhirlpoolII, WhirlpoolIII],
            [ShatteringStormI, ShatteringStormII, ShatteringStormIII],
        ]

        self._guardian_abilities: List[List[Ability]] = [
            [WhirlwindI, WhirlwindII, WhirlwindIII],
            [SecondWindI, SecondWindII, SecondWindIII],
            [ScarArmorI, ScarArmorII],
            [UnbreakingI, UnbreakingII, UnbreakingIII],
            [CounterstrikeI, CounterstrikeII, CounterstrikeIII],
            [BidedAttackI, BidedAttackII, BidedAttackIII],
            [TauntI],
            [PiercingStrikeI, PiercingStrikeII, PiercingStrikeIII],
            [PressTheAdvantageI],
            [EvadeI, EvadeII, EvadeIII],
            [HeavySlamI, HeavySlamII, HeavySlamIII]
        ]

        self._merchant_abilities: List[List[Ability]] = [
            [ContractWealthForPowerI, ContractWealthForPowerII, ContractWealthForPowerIII],
            [BoundToGetLuckyI, BoundToGetLuckyII, BoundToGetLuckyIII],
            [SilkspeakingI],
            [ATidySumI, ATidySumII, ATidySumIII],
            [CursedCoinsI, CursedCoinsII, CursedCoinsIII],
            [UnseenRichesI, UnseenRichesII, UnseenRichesIII],
            [ContractManaToBloodI, ContractManaToBloodII, ContractManaToBloodIII],
            [ContractBloodForBloodI, ContractBloodForBloodII, ContractBloodForBloodIII],
            [DeepPocketsI, DeepPocketsII, DeepPocketsIII]
        ]

        self._display_initial_buttons()

    def _get_player(self) -> Player:
        return self._database[str(self._guild_id)]["members"][str(self._user.id)]

    def get_initial_info(self):
        return Embed(title="Trainers", description="Where would you like to visit?")

    def get_initial_embed_for_class(self):
        if self._current_class == ExpertiseClass.Fisher:
            return Embed(title="Sea Shrine", description=(
                "An ancient edifice of speckled, grey stone stands before you, seaweed-like vines creeping around the time-worn rock at the edge of the bluff. "
                "The jagged outcropping is marked by a diamond-shaped hole towards the top and some engraved inscription too old to be interpreted.\n\n"
                "At the base of the shrine is a wooden bowl and a small selection of candles that seem to be well-tended."
            ))
        if self._current_class == ExpertiseClass.Guardian:
            return Embed(title="Dueling Grounds", description=(
                "At a grassy clearing just outside the village, a circle of wooden posts loosely held together with a length of rope between them marks the officially recognized dueling grounds.\n\n"
                "An elderly gentleman wearing an elegant black and gold doublet waits on a stool, sharpening one weapon after another meticulously with a whetstone. Galos, a well-recognized figure around town and a practiced fighter, looks up as you approach."
            ))
        if self._current_class == ExpertiseClass.Merchant:
            return Embed(title="The Crown & Anchor Tavern", description=(
                "The warm glow of the large, wooden tavern near the center of the village is always an inviting presence. In the evenings, people gather for knucklebones, good conversation with friends, and excellent food. "
                "Quinan stands behind the bar polishing a tankard, an eye always looking around at the tables to see where she's needed.\n\n"
                "As you approach, she greets you with a wide smile and leans against the countertop, \"Good to see you. What can I get you today?\""
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
                    if i == len(ability_group) - 1:
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
        self.add_item(EnterEquipAbilitiesButton(3))

    def _get_page_info(self, purchased_ability: Ability | None=None):
        player: Player = self._get_player()

        description = ""
        if purchased_ability is not None:
            description = f"Acquired {purchased_ability.get_icon_and_name()}! You can equip it from the main menu."
        else:
            if self._current_ability is not None:
                description = f"──────────\n{self._current_ability}\nCost to Buy: {self._current_ability.get_purchase_cost()}\n──────────\n\n"
            description += f"You have {player.get_inventory().get_coins_str()}.\n\nChoose an ability to learn more."

        if self._current_class == ExpertiseClass.Fisher:
            return Embed(title="Sea Shrine", description=description)
        if self._current_class == ExpertiseClass.Guardian:
            return Embed(title="Dueling Grounds", description=description)
        if self._current_class == ExpertiseClass.Merchant:
            return Embed(title="The Crown & Anchor Tavern", description=description)
        return Embed(title="Where are you?", description="In the midst of knowing where you were, suddenly now there is a bleak unknown, a pale that sparks fear and awe.")

    def _get_current_page_buttons(self):
        self.clear_items()
        player: Player = self._get_player()
        player_expertise: Expertise = player.get_expertise()
        available_coins: int = player.get_inventory().get_coins()

        available_abilities = []
        if self._current_class == ExpertiseClass.Fisher:
            available_abilities = self._fisher_abilities
        if self._current_class == ExpertiseClass.Guardian:
            available_abilities = self._guardian_abilities
        if self._current_class == ExpertiseClass.Merchant:
            available_abilities = self._merchant_abilities
        all_slots = self.get_available_abilities(player, available_abilities)

        page_slots = all_slots[self._page * self._NUM_PER_PAGE:min(len(all_slots), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, ability in enumerate(page_slots):
            self.add_item(SelectAbilityButton(ability, i))
        
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(all_slots) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        
        if self._current_ability is not None:
            if available_coins >= self._current_ability.get_purchase_cost():
                current_class_level: int = player_expertise.get_level_for_class(self._current_ability.get_class_key())
                if current_class_level >= self._current_ability.get_level_requirement():
                    self.add_item(ConfirmPurchaseButton(min(4, len(page_slots))))
        
        self.add_item(ExitTrainerButton(min(4, len(page_slots))))

    def next_page(self):
        self._page += 1
        self._get_current_page_buttons()
        return self._get_page_info()

    def prev_page(self):
        self._page = max(0, self._page - 1)
        self._get_current_page_buttons()
        return self._get_page_info()

    def visit_sea_shrine(self):
        self._current_ability = None
        self._current_class = ExpertiseClass.Fisher
        self._page = 0
        self._get_current_page_buttons()
        return self.get_initial_embed_for_class()

    def visit_tavern(self):
        self._current_ability = None
        self._current_class = ExpertiseClass.Merchant
        self._page = 0
        self._get_current_page_buttons()
        return self.get_initial_embed_for_class()

    def visit_dueling_grounds(self):
        self._current_ability = None
        self._current_class = ExpertiseClass.Guardian
        self._page = 0
        self._get_current_page_buttons()
        return self.get_initial_embed_for_class()

    def select_ability(self, ability: Ability):
        self._current_ability = ability
        self._get_current_page_buttons()
        return self._get_page_info()

    def purchase_ability(self):
        if self._current_ability is not None:
            player: Player = self._get_player()
            ability: Ability = self._current_ability

            player.get_inventory().remove_coins(ability.get_purchase_cost())
            player.get_dueling().available_abilities.append(ability)

            self._current_ability = None

            return self._get_page_info(ability)
        return self._get_page_info()

    def exit_to_main_menu(self):
        self._display_initial_buttons()
        return self.get_initial_info()

    def get_bot(self):
        return self._bot

    def get_database(self):
        return self._database
    
    def get_guild_id(self):
        return self._guild_id

    def get_user(self):
        return self._user


class EnterEquipModeButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label=f"Equip", row=0)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: EquipAbilitiesView = self.view
        if interaction.user == view.get_user():
            response = view.enter_equip_mode()

            await interaction.response.edit_message(content=None, view=view, embed=response)


class EnterUnequipModeButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label=f"Unequip", row=0)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: EquipAbilitiesView = self.view
        if interaction.user == view.get_user():
            response = view.enter_unequip_mode()

            await interaction.response.edit_message(content=None, view=view, embed=response)


class EquipAbilityButton(discord.ui.Button):
    def __init__(self, row: int, ability: Ability):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{ability.get_name()}", row=row, emoji=ability.get_icon())
        
        self._ability = ability

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: EquipAbilitiesView = self.view
        if interaction.user == view.get_user():
            response = view.equip_ability(self._ability)

            await interaction.response.edit_message(content=None, view=view, embed=response)


class UnequipAbilityButton(discord.ui.Button):
    def __init__(self, ability_index: int, ability: Ability, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{ability.get_name()}", row=row, emoji=ability.get_icon())
        
        self._ability_index = ability_index
        self._ability = ability

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: EquipAbilitiesView = self.view
        if interaction.user == view.get_user():
            response = view.unequip_ability(self._ability, self._ability_index)

            await interaction.response.edit_message(content=None, view=view, embed=response)


class BackButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.red, label="Exit", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: EquipAbilitiesView = self.view
        if interaction.user == view.get_user():
            response = view.exit_to_main_menu()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ExitToTrainersButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.red, label="Exit", row=0)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: EquipAbilitiesView = self.view
        if interaction.user == view.get_user():
            new_view = TrainerView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_user())
            await interaction.response.edit_message(content=None, embed=new_view.get_initial_info(), view=new_view)


class EquipAbilitiesView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, user: discord.User):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._user = user

        self._page: int = 0
        # The alternative is unequipping, in which case this is True
        self._equipping: bool = False

        self._NUM_PER_PAGE = 4

        self._display_initial_buttons()

    def _get_player(self) -> Player:
        return self._database[str(self._guild_id)]["members"][str(self._user.id)]

    def get_initial_info(self):
        return Embed(title="Abilities", description="You can equip or unequip abilities (based on your Memory stat) via the buttons below.")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(EnterEquipModeButton())
        self.add_item(EnterUnequipModeButton())
        self.add_item(ExitToTrainersButton())

    def _get_equip_page_buttons(self, ability_just_equipped: Ability | None=None):
        self.clear_items()

        player: Player = self._get_player()
        all_slots = [ability for ability in player.get_dueling().available_abilities if ability not in player.get_dueling().abilities]

        page_slots = all_slots[self._page * self._NUM_PER_PAGE:min(len(all_slots), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, ability in enumerate(page_slots):
            self.add_item(EquipAbilityButton(i, ability))
        
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(all_slots) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))

        self.add_item(BackButton(min(4, len(page_slots))))

        ability_strs = []
        for i in range(self._NUM_PER_PAGE):
            if i > len(page_slots) - 1:
                ability_strs.append("")
            else:
                ability_strs.append(f"──────────\n{page_slots[i]}\n──────────")
        just_equipped_str = f"\n\n{ability_just_equipped.get_icon_and_name()} equipped!" if ability_just_equipped is not None else ""

        description = (
            "{0}    {1}\n"
            "{2}    {3}"
        ).format(*ability_strs) + just_equipped_str

        return Embed(title="Equip an Ability", description=description)

    def _get_unequip_page_buttons(self, ability_just_unequipped: Ability | None=None):
        self.clear_items()

        player: Player = self._get_player()
        all_slots = player.get_dueling().abilities

        page_slots = all_slots[self._page * self._NUM_PER_PAGE:min(len(all_slots), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, ability in enumerate(page_slots):
            self.add_item(UnequipAbilityButton(i + (self._page * self._NUM_PER_PAGE), ability, i))
        
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(all_slots) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        
        self.add_item(BackButton(min(4, len(page_slots))))

        just_equipped_str = f"\n\n{ability_just_unequipped.get_icon_and_name()} unequipped!" if ability_just_unequipped is not None else ""

        return Embed(title="Unequip an Ability", description="Choose an ability to unequip." + just_equipped_str)

    def next_page(self):
        self._page += 1
        if self._equipping:
            return self._get_equip_page_buttons()
        return self._get_unequip_page_buttons()

    def prev_page(self):
        self._page = max(0, self._page - 1)
        if self._equipping:
            return self._get_equip_page_buttons()
        return self._get_unequip_page_buttons()

    def enter_equip_mode(self):
        self._page = 0
        self._equipping = True
        return self._get_equip_page_buttons()

    def enter_unequip_mode(self):
        self._page = 0
        self._equipping = False
        return self._get_unequip_page_buttons()

    def exit_to_main_menu(self):
        self._display_initial_buttons()
        return self.get_initial_info()

    def equip_ability(self, ability: Ability):
        player: Player = self._get_player()
        player.get_dueling().abilities.append(ability)
        return self._get_equip_page_buttons(ability)

    def unequip_ability(self, ability: Ability, ability_index: int):
        player: Player = self._get_player()
        if isinstance(player.get_dueling().abilities[ability_index], ability.__class__):
            player.get_dueling().abilities.pop(ability_index)
            return self._get_unequip_page_buttons(ability)
        return self._get_unequip_page_buttons(None)

    def get_bot(self):
        return self._bot

    def get_database(self):
        return self._database
    
    def get_guild_id(self):
        return self._guild_id

    def get_user(self):
        return self._user
