from aenum import Enum, skip
from strenum import StrEnum

# Using aenum and @skip to create an Enum of StrEnums
# As a result, there can't be any top-level keys
class ClassTag(Enum):
    # Items that can be equipped
    @skip
    class Equipment(StrEnum):
        Equipment = "Equipment"
        Helmet = "Helmet"
        ChestArmor = "Chest_Armor"
        Gloves = "Gloves"
        Boots = "Boots"
        Amulet = "Amulet"
        Ring = "Ring"
        Leggings = "Leggings"
        MainHand = "Main_Hand"
        OffHand = "Off_Hand"
    
    # Weapon types that can be generated
    @skip
    class Weapon(StrEnum):
        Weapon = "Weapon"
        Dagger = "Dagger"
        Sword = "Sword"
        Greatsword = "Greatsword"
        Knuckles = "Knuckles"
        Spear = "Spear"
        Bow = "Bow"
        Staff = "Staff"
        Shield = "Shield"

    # Items that can be stacked and used for certain effects
    @skip
    class Consumable(StrEnum):
        Consumable = "Consumable"
        UsableOutsideDuels = "Usable_Outside_Duels"
        UsableWithinDuels = "Usable_Within_Duels"
        Potion = "Potion"
        Food = "Food"
        AbilityScroll = "Ability_Scroll"

    # Items that can be used as part of crafting consumables
    @skip
    class Ingredient(StrEnum):
        Ingredient = "Ingredient"
        Herb = "Herb"
        RawFish = "Raw_Fish" # Might be good to separate fish from other foods
        RawFood = "Raw_Food" # Like uncooked potatoes, meat, etc.
        Spice = "Spice" # Specifically for cooking
        PotionIngredient = "Potion_Ingredient"
        CraftingMaterial = "Crafting_Material"

    @skip
    class Creature(StrEnum):
        Creature = "Creature"
        Fish = "Fish"

    # Items that might might only be good for money.
    @skip
    class Valuable(StrEnum):
        Valuable = "Valuable"
        Gemstone = "Gemstone"

    @skip
    class Readable(StrEnum):
        Readable = "Readable"
        Scroll = "Scroll"

    @skip
    class Gardening(StrEnum):
        Gardening = "Gardening"
        Seed = "Seed"
        Soil = "Soil"
        GrowthAssist = "Growth_Assist"

    @skip
    class Misc(StrEnum):
        IsUnique = "Is_Unique"
        NeedsIdentification = "Needs_Identification"
        Junk = "Junk"


class HouseRoom(StrEnum):
    Unknown = "Unknown"
    Study = "Study"
    Alchemy = "Alchemy"
    Workshop = "Workshop"
    Kitchen = "Kitchen"
    Garden = "Garden"
    Storage = "Storage"
