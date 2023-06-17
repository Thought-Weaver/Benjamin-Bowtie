from __future__ import annotations

import logging
import random
import time

from bot import ERROR_LOGGER
from features.companions.player_companions import PlayerCompanions
from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Expertise
from features.house.house import House
from features.inventory import Inventory
from features.mail import Mail
from features.settings import Settings
from features.shared.effect import Effect, ItemEffects
from features.shared.enums import CompanionTier
from features.shared.item import LOADED_ITEMS
from features.stats import Stats
from features.stories.player_dungeon_run import PlayerDungeonRun

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from bot import BenjaminBowtieBot

class Player():
    def __init__(self, id: str):
        self._id = id

        self._inventory: Inventory = Inventory()
        self._mailbox: List[Mail] = []
        self._stats: Stats = Stats()
        self._expertise: Expertise = Expertise()
        self._equipment: Equipment = Equipment()
        self._dueling: Dueling = Dueling()
        self._house: House = House()
        self._companions: PlayerCompanions = PlayerCompanions()
        self._dungeon_run: PlayerDungeonRun = PlayerDungeonRun()
        self._settings: Settings = Settings()

    async def tick(self, bot: BenjaminBowtieBot):
        self._house.tick()
        self._companions.tick()

        for key in self._companions.companions.keys():
            if self._companions.companions[key].get_tier() == CompanionTier.Best:
                companion = self._companions.companions[key]

                # 5% chance per tick means roughly an item a day
                if random.random() < 0.05:
                    item_key = random.choice(companion.get_best_tier_items())
                    item = LOADED_ITEMS.get_new_item(item_key)
                    
                    time_str: str = str(time.time()).split(".")[0]
                    mail: Mail = Mail(companion.get_name(), item, 0, f"{companion.get_icon_and_name()} found this and brought it to you!", time_str, -1)
                    
                    await self.send_mail(mail, bot)

                if not companion.talisman_given:
                    talisman = LOADED_ITEMS.get_new_item(companion.talisman)

                    mail = Mail(companion.get_name(), talisman, 0, f"{companion.get_icon_and_name()} has given this to you as a symbol of your incredible bond!", str(time.time()).split(".")[0], -1)
                    await self.send_mail(mail, bot)
                    
                    companion.talisman_given = True

        if self._settings.mature_plant_notifications:
            plants_just_matured = self._house.get_plants_just_matured()
            if len(plants_just_matured) > 0:
                try:
                    plants_str: str = "\n".join(list(map(lambda plant: plant.get_full_name(), plants_just_matured)))
                    user = await bot.fetch_user(int(self._id))
                    await user.send(f"The following plants have matured in your garden:\n\n{plants_str}")
                except Exception as e:
                    ERROR_LOGGER.log(logging.ERROR, f"Failed to send plant notification to user: {e}")

    def get_id(self):
        return self._id
    
    def set_id(self, id: str):
        if self._id is None or self._id == "":
            self._id = id

    def get_combined_attributes(self):
        return self._expertise.get_all_attributes() + self._equipment.get_total_attribute_mods() + self._dueling.get_combined_attribute_mods()

    def get_non_status_combined_attributes(self):
        return self._expertise.get_all_attributes() + self._equipment.get_total_attribute_mods()

    def get_combined_req_met_effects(self):
        combined_effects = ItemEffects([], [], [], [], [], [], [], [])
        
        equipment_effects = self._equipment.get_combined_item_effects_if_requirements_met(self)
        if equipment_effects is not None:
            combined_effects += equipment_effects

        if self._companions.current_companion is not None:
            current_companion = self._companions.companions[self._companions.current_companion]
            companion_dueling_ability = current_companion.get_dueling_ability(effect_category=None)
            effect_category = current_companion.get_ability_effect_category()
            if effect_category is not None and isinstance(companion_dueling_ability, Effect):
                combined_effects.add_effect_in_category(companion_dueling_ability, effect_category)
        
        return combined_effects

    def get_inventory(self):
        return self._inventory

    def get_mailbox(self):
        return self._mailbox

    async def send_mail(self, mail: Mail, bot: BenjaminBowtieBot):
        self._mailbox.append(mail)

        if self._settings.mail_notifications:
            try:
                user = await bot.fetch_user(int(self._id))
                await user.send(f"You have new mail from {mail.get_sender_name()}!")
            except Exception as e:
                ERROR_LOGGER.log(logging.ERROR, f"Failed to send mail notification to user: {e}")

    def get_stats(self):
        return self._stats

    def get_expertise(self):
        return self._expertise

    def get_equipment(self):
        return self._equipment

    def get_dueling(self):
        return self._dueling

    def get_house(self):
        return self._house

    def get_companions(self):
        return self._companions
    
    def get_dungeon_run(self):
        return self._dungeon_run
    
    def get_settings(self):
        return self._settings

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", "")
        self._inventory = state.get("_inventory", Inventory())
        self._mailbox = state.get("_mailbox", [])
        self._stats = state.get("_stats", Stats())
        self._expertise = state.get("_expertise", Expertise())
        self._equipment = state.get("_equipment", Equipment())
        self._dueling = state.get("_dueling", Dueling())
        self._house = state.get("_house", House())
        self._companions = state.get("_companions", PlayerCompanions())
        self._dungeon_run = state.get("_dungeon_run", PlayerDungeonRun())
        self._settings = state.get("_settings", Settings())
