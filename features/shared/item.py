from __future__ import annotations

import json

from aenum import Enum
from random import randint
from strenum import StrEnum

from features.shared.constants import DEX_DMG_SCALE, WEAPON_OVERLEVELED_DEBUFF
from features.shared.effect import ConditionType, EffectType, ItemEffects
from features.shared.enums import ClassTag
from types import MappingProxyType

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from features.shared.attributes import Attributes

# -----------------------------------------------------------------------------
# ENUMS
# -----------------------------------------------------------------------------

class Rarity(StrEnum):
    Unknown = "Unknown"
    Common = "Common"
    Uncommon = "Uncommon"
    Rare = "Rare"
    Epic = "Epic"
    Legendary = "Legendary"
    Artifact = "Artifact"

    def __lt__(self, rarity: Rarity) -> bool:
        ordering = [Rarity.Common, Rarity.Uncommon, Rarity.Rare, Rarity.Epic, Rarity.Legendary, Rarity.Artifact, Rarity.Unknown]
        return ordering.index(self) < ordering.index(rarity)

    def __gt__(self, rarity: Rarity) -> bool:
        ordering = [Rarity.Common, Rarity.Uncommon, Rarity.Rare, Rarity.Epic, Rarity.Legendary, Rarity.Artifact, Rarity.Unknown]
        return ordering.index(self) > ordering.index(rarity)

    def __leq__(self, rarity: Rarity) -> bool:
        ordering = [Rarity.Common, Rarity.Uncommon, Rarity.Rare, Rarity.Epic, Rarity.Legendary, Rarity.Artifact, Rarity.Unknown]
        return ordering.index(self) <= ordering.index(rarity)

    def __geq__(self, rarity: Rarity) -> bool:
        ordering = [Rarity.Common, Rarity.Uncommon, Rarity.Rare, Rarity.Epic, Rarity.Legendary, Rarity.Artifact, Rarity.Unknown]
        return ordering.index(self) >= ordering.index(rarity)


class StateTag(Enum):
    pass


class ItemKey(StrEnum):
    # Fishing Results
    AncientVase = "items/valuable/ancient_vase"
    ClumpOfLeaves = "items/misc/junk/clump_of_leaves"
    Conch = "items/misc/junk/conch"
    Crab = "items/creature/fish/crab"
    FishMaybe = "items/creature/fish/fish_maybe"
    Lobster = "items/creature/fish/lobster"
    Minnow = "items/creature/fish/minnow"
    MysteriousScroll = "items/readable/scroll/mysterious_scroll"
    Oyster = "items/creature/fish/oyster"
    Pufferfish = "items/creature/fish/pufferfish"
    Roughy = "items/creature/fish/roughy"
    Shark = "items/creature/fish/shark"
    Shrimp = "items/creature/fish/shrimp"
    Squid = "items/creature/fish/squid"
    TatteredBoot = "items/misc/junk/tattered_boot"

    # Sunless Set
    SunlessSteps = "items/equipment/boots/sunless_steps"
    SunlessHeart = "items/equipment/chest_armor/sunless_heart"
    SunlessGrip = "items/equipment/gloves/sunless_grip"
    SunlessMind = "items/equipment/helmet/sunless_mind"
    SunlessStride = "items/equipment/leggings/sunless_stride"
    SunlessWill = "items/equipment/ring/sunless_will"
    SunlessChains = "items/equipment/amulet/sunless_chains"

    # Food
    Bread = "items/consumable/food/bread"
    CookedMinnow = "items/consumable/food/cooked_minnow"
    CookedRoughy = "items/consumable/food/cooked_roughy"
    Dumpling = "items/consumable/food/dumpling"
    FishCake = "items/consumable/food/fish_cake"
    FriedShrimp = "items/consumable/food/fried_shrimp"
    MushroomSalad = "items/consumable/food/mushroom_salad"
    MushroomStew = "items/consumable/food/mushroom_stew"
    VegetableFritter = "items/consumable/food/vegetable_fritter"

    # Potions
    AtrophyPotion = "items/consumable/potions/atrophy_potion"
    CharmPotion = "items/consumable/potions/charm_potion"
    CleansingPotion = "items/consumable/potions/cleansing_potion"
    ConstitutionPotion = "items/consumable/potions/constitution_potion"
    DexterityPotion = "items/consumable/potions/dexterity_potion"
    EnfeeblingPotion = "items/consumable/potions/enfeebling_potion"
    ExplosivePotion = "items/consumable/potions/explosive_potion"
    FearPotion = "items/consumable/potions/fear_potion"
    FortitudePotion = "items/consumable/potions/fortitude_potion"
    GreaterAtrophyPotion = "items/consumable/potions/greater_atrophy_potion"
    GreaterCharmPotion = "items/consumable/potions/greater_charm_potion"
    GreaterConstitutionPotion = "items/consumable/potions/greater_constitution_potion"
    GreaterDexterityPotion = "items/consumable/potions/greater_dexterity_potion"
    GreaterEnfeeblingPotion = "items/consumable/potions/greater_enfeebling_potion"
    GreaterExplosivePotion = "items/consumable/potions/greater_explosive_potion"
    GreaterFearPotion = "items/consumable/potions/greater_fear_potion"
    GreaterHealthPotion = "items/consumable/potions/greater_health_potion"
    GreaterIntelligencePotion = "items/consumable/potions/greater_intelligence_potion"
    GreaterManaPotion = "items/consumable/potions/greater_mana_potion"
    GreaterPoison = "items/consumable/potions/greater_poison"
    GreaterPotionOfDeathResist = "items/consumable/potions/greater_potion_of_death_resist"
    GreaterPotionOfDecay = "items/consumable/potions/greater_potion_of_decay"
    GreaterSleepingDraught = "items/consumable/potions/greater_sleeping_draught"
    GreaterSmokebomb = "items/consumable/potions/greater_smokebomb"
    GreaterStrengthPotion = "items/consumable/potions/greater_strength_potion"
    HealthPotion = "items/consumable/potions/health_potion"
    IntelligencePotion = "items/consumable/potions/intelligence_potion"
    LesserAtrophyPotion = "items/consumable/potions/lesser_atrophy_potion"
    LesserCharmPotion = "items/consumable/potions/lesser_charm_potion"
    LesserConstitutionPotion = "items/consumable/potions/lesser_constitution_potion"
    LesserDexterityPotion = "items/consumable/potions/lesser_dexterity_potion"
    LesserEnfeeblingPotion = "items/consumable/potions/lesser_enfeebling_potion"
    LesserExplosivePotion = "items/consumable/potions/lesser_explosive_potion"
    LesserFearPotion = "items/consumable/potions/lesser_fear_potion"
    LesserHealthPotion = "items/consumable/potions/lesser_health_potion"
    LesserIntelligencePotion = "items/consumable/potions/lesser_intelligence_potion"
    LesserManaPotion = "items/consumable/potions/lesser_mana_potion"
    LesserPoison = "items/consumable/potions/lesser_poison"
    LesserPotionOfDeathResist = "items/consumable/potions/lesser_potion_of_death_resist"
    LesserPotionOfDecay = "items/consumable/potions/lesser_potion_of_decay"
    LesserSleepingDraught = "items/consumable/potions/lesser_sleeping_draught"
    LesserSmokebomb = "items/consumable/potions/lesser_smokebomb"
    LesserStrengthPotion = "items/consumable/potions/lesser_strength_potion"
    LuckPotion = "items/consumable/potions/luck_potion"
    ManaPotion = "items/consumable/potions/mana_potion"
    Poison = "items/consumable/potions/poison"
    PotionOfDeathResist = "items/consumable/potions/potion_of_death_resist"
    PotionOfDecay = "items/consumable/potions/potion_of_decay"
    SappingPotion = "items/consumable/potions/sapping_potion"
    SleepingDraught = "items/consumable/potions/sleeping_draught"
    Smokebomb = "items/consumable/potions/smokebomb"
    StrengthPotion = "items/consumable/potions/strength_potion"
    SuperiorAtrophyPotion = "items/consumable/potions/superior_atrophy_potion"
    SuperiorConstitutionPotion = "items/consumable/potions/superior_constitution_potion"
    SuperiorDexterityPotion = "items/consumable/potions/superior_dexterity_potion"
    SuperiorExplosivePotion = "items/consumable/potions/superior_explosive_potion"
    SuperiorHealthPotion = "items/consumable/potions/superior_health_potion"
    SuperiorIntelligencePotion = "items/consumable/potions/superior_intelligence_potion"
    SuperiorManaPotion = "items/consumable/potions/superior_mana_potion"
    SuperiorPoison = "items/consumable/potions/superior_poison"
    SuperiorPotionOfDecay = "items/consumable/potions/superior_potion_of_decay"
    SuperiorSleepingDraught = "items/consumable/potions/superior_sleeping_draught"
    SuperiorSmokebomb = "items/consumable/potions/superior_smokebomb"
    SuperiorStrengthPotion = "items/consumable/potions/superior_strength_potion"

    # Alchemy Supplies
    CrystalVial = "items/ingredient/alchemy_supplies/crystal_vial"

    # Herbs
    AntlerCoral = "items/ingredient/herbs/antler_coral"
    Asptongue = "items/ingredient/herbs/asptongue"
    BandedCoral = "items/ingredient/herbs/banded_coral"
    BlazeCluster = "items/ingredient/herbs/blaze_cluster"
    Bloodcrown = "items/ingredient/herbs/bloodcrown"
    Bramblefrond = "items/ingredient/herbs/bramblefrond"
    DawnsGlory = "items/ingredient/herbs/dawns_glory"
    DragonsTeeth = "items/ingredient/herbs/dragons_teeth"
    DreamMaker = "items/ingredient/herbs/dream_maker"
    Fissureleaf = "items/ingredient/herbs/fissureleaf"
    FoolsDelight = "items/ingredient/herbs/fools_delight"
    ForgottenTears = "items/ingredient/herbs/forgotten_tears"
    Frostwort = "items/ingredient/herbs/frostwort"
    GoldenClover = "items/ingredient/herbs/golden_clover"
    Graspleaf = "items/ingredient/herbs/graspleaf"
    GraveMoss = "items/ingredient/herbs/grave_moss"
    Hushvine = "items/ingredient/herbs/hushvine"
    Lichbloom = "items/ingredient/herbs/lichbloom"
    Lithewood = "items/ingredient/herbs/lithewood"
    MagesBane = "items/ingredient/herbs/mages_bane"
    Manabloom = "items/ingredient/herbs/manabloom"
    Meddlespread = "items/ingredient/herbs/meddlespread"
    Razorgrass = "items/ingredient/herbs/razorgrass"
    Riverblossom = "items/ingredient/herbs/riverblossom"
    Rotstalk = "items/ingredient/herbs/rotstalk"
    Seaclover = "items/ingredient/herbs/seaclover"
    Shellflower = "items/ingredient/herbs/shellflower"
    Shellplate = "items/ingredient/herbs/shellplate"
    Shelterfoil = "items/ingredient/herbs/shelterfoil"
    Shiverroot = "items/ingredient/herbs/shiverroot"
    SingingCoral = "items/ingredient/herbs/singing_coral"
    SirensKiss = "items/ingredient/herbs/sirens_kiss"
    Snowdew = "items/ingredient/herbs/snowdew"
    SpeckledCap = "items/ingredient/herbs/speckled_cap"
    SpidersGrove = "items/ingredient/herbs/spiders_grove"
    Stranglekelp = "items/ingredient/herbs/stranglekelp"
    Sungrain = "items/ingredient/herbs/sungrain"
    Wanderweed = "items/ingredient/herbs/wanderweed"
    Witherheart = "items/ingredient/herbs/witherheart"
    Wrathbark = "items/ingredient/herbs/wrathbark"

    # Seeds
    AsptongueSeed = "items/gardening/seed/asptongue_seed"
    BlazeClusterSpores = "items/gardening/seed/blaze_cluster_spores"
    BloodcrownSpores = "items/gardening/seed/bloodcrown_spores"
    BramblefrondSeed = "items/gardening/seed/bramblefrond_seed"
    DawnsGlorySeed = "items/gardening/seed/dawns_glory_seed"
    DragonsTeethSeed = "items/gardening/seed/dragons_teeth_seed"
    DreamMakerSeed = "items/gardening/seed/dream_maker_seed"
    FissureleafSeed = "items/gardening/seed/fissureleaf_seed"
    FoolsDelightSpores = "items/gardening/seed/fools_delight_spores"
    ForgottenTearsSeed = "items/gardening/seed/forgotten_tears_seed"
    FrostwortSeed = "items/gardening/seed/frostwort_seed"
    GoldenCloverSeed = "items/gardening/seed/golden_clover_seed"
    GraspleafSeed = "items/gardening/seed/graspleaf_seed"
    GraveMossSpores = "items/gardening/seed/grave_moss_spores"
    HushvineSeed = "items/gardening/seed/hushvine_seed"
    LichbloomSeed = "items/gardening/seed/lichbloom_seed"
    MagesBaneSeed = "items/gardening/seed/mages_bane_seed"
    ManabloomSeed = "items/gardening/seed/manabloom_seed"
    MeddlespreadSpores = "items/gardening/seed/meddlespread_spores"
    RazorgrassSeed = "items/gardening/seed/razorgrass_seed"
    RiverblossomSeed = "items/gardening/seed/riverblossom_seed"
    RotstalkSeed = "items/gardening/seed/rotstalk_seed"
    SeacloverSeed = "items/gardening/seed/seaclover_seed"
    ShellflowerSeed = "items/gardening/seed/shellflower_seed"
    ShelterfoilSeed = "items/gardening/seed/shelterfoil_seed"
    ShiverrootSeed = "items/gardening/seed/shiverroot_seed"
    SirensKissSeed = "items/gardening/seed/sirens_kiss_seed"
    SnowdewSeed = "items/gardening/seed/snowdew_seed"
    SpeckledCapSpores = "items/gardening/seed/speckled_cap_spores"
    SpidersGroveSpores = "items/gardening/seed/spiders_grove_spores"
    SungrainSeed = "items/gardening/seed/sungrain_seed"
    WanderweedSeed = "items/gardening/seed/wanderweed_seed"
    WitherheartSeed = "items/gardening/seed/witherheart_seed"

    # Gemstones
    Agate = "items/valuable/gemstone/agate"
    Amethyst = "items/valuable/gemstone/amethyst"
    Bloodstone = "items/valuable/gemstone/bloodstone"
    CrackedAgate = "items/valuable/gemstone/cracked_agate"
    CrackedAmethyst = "items/valuable/gemstone/cracked_amethyst"
    CrackedBloodstone = "items/valuable/gemstone/cracked_bloodstone"
    CrackedDiamond = "items/valuable/gemstone/cracked_diamond"
    CrackedEmerald = "items/valuable/gemstone/cracked_emerald"
    CrackedJade = "items/valuable/gemstone/cracked_jade"
    CrackedLapis = "items/valuable/gemstone/cracked_lapis"
    CrackedMalachite = "items/valuable/gemstone/cracked_malachite"
    CrackedMoonstone = "items/valuable/gemstone/cracked_moonstone"
    CrackedOnyx = "items/valuable/gemstone/cracked_onyx"
    CrackedOpal = "items/valuable/gemstone/cracked_opal"
    CrackedPeridot = "items/valuable/gemstone/cracked_peridot"
    CrackedQuartz = "items/valuable/gemstone/cracked_quartz"
    CrackedRuby = "items/valuable/gemstone/cracked_ruby"
    CrackedSapphire = "items/valuable/gemstone/cracked_sapphire"
    CrackedSunstone = "items/valuable/gemstone/cracked_sunstone"
    CrackedTanzanite = "items/valuable/gemstone/cracked_tanzanite"
    CrackedTopaz = "items/valuable/gemstone/cracked_topaz"
    CrackedTurquoise = "items/valuable/gemstone/cracked_turquoise"
    CrackedZircon = "items/valuable/gemstone/cracked_zircon"
    Diamond = "items/valuable/gemstone/diamond"
    Emerald = "items/valuable/gemstone/emerald"
    FlawlessAgate = "items/valuable/gemstone/flawless_agate"
    FlawlessAmethyst = "items/valuable/gemstone/flawless_amethyst"
    FlawlessBloodstone = "items/valuable/gemstone/flawless_bloodstone"
    FlawlessDiamond = "items/valuable/gemstone/flawless_diamond"
    FlawlessEmerald = "items/valuable/gemstone/flawless_emerald"
    FlawlessJade = "items/valuable/gemstone/flawless_jade"
    FlawlessLapis = "items/valuable/gemstone/flawless_lapis"
    FlawlessMalachite = "items/valuable/gemstone/flawless_malachite"
    FlawlessMoonstone = "items/valuable/gemstone/flawless_moonstone"
    FlawlessOnyx = "items/valuable/gemstone/flawless_onyx"
    FlawlessOpal = "items/valuable/gemstone/flawless_opal"
    FlawlessPeridot = "items/valuable/gemstone/flawless_peridot"
    FlawlessQuartz = "items/valuable/gemstone/flawless_quartz"
    FlawlessRuby = "items/valuable/gemstone/flawless_ruby"
    FlawlessSapphire = "items/valuable/gemstone/flawless_sapphire"
    FlawlessSunstone = "items/valuable/gemstone/flawless_sunstone"
    FlawlessTanzanite = "items/valuable/gemstone/flawless_tanzanite"
    FlawlessTopaz = "items/valuable/gemstone/flawless_topaz"
    FlawlessTurquoise = "items/valuable/gemstone/flawless_turquoise"
    FlawlessZircon = "items/valuable/gemstone/flawless_zircon"
    Jade = "items/valuable/gemstone/jade"
    Lapis = "items/valuable/gemstone/lapis"
    Malachite = "items/valuable/gemstone/malachite"
    Moonstone = "items/valuable/gemstone/moonstone"
    Onyx = "items/valuable/gemstone/onyx"
    Opal = "items/valuable/gemstone/opal"
    Peridot = "items/valuable/gemstone/peridot"
    Quartz = "items/valuable/gemstone/quartz"
    Ruby = "items/valuable/gemstone/ruby"
    Sapphire = "items/valuable/gemstone/sapphire"
    Sunstone = "items/valuable/gemstone/sunstone"
    Tanzanite = "items/valuable/gemstone/tanzanite"
    Topaz = "items/valuable/gemstone/topaz"
    Turquoise = "items/valuable/gemstone/turquoise"
    Zircon = "items/valuable/gemstone/zircon"

    # Equipment
    
    # Amulet
    CopperNecklace = "items/equipment/amulet/copper_necklace"
    GoldNecklace = "items/equipment/amulet/gold_necklace"
    SilverNecklace = "items/equipment/amulet/silver_necklace"

    # Boots
    AmberiteGreaves = "items/equipment/boots/amberite_greaves"
    AmberitePlateGreaves = "items/equipment/boots/amberite_plate_greaves"
    IronGreaves = "items/equipment/boots/iron_greaves"
    IronPlateGreaves = "items/equipment/boots/iron_plate_greaves"
    LeatherBoots = "items/equipment/boots/leather_boots"
    MothsilkBoots = "items/equipment/boots/mothsilk_boots"
    MythrilGreaves = "items/equipment/boots/mythril_greaves"
    MythrilPlateGreaves = "items/equipment/boots/mythril_plate_greaves"
    OrichalcumGreaves = "items/equipment/boots/orichalcum_greaves"
    OrichalcumPlateGreaves = "items/equipment/boots/orichalcum_plate_greaves"
    SilverGreaves = "items/equipment/boots/silver_greaves"
    SilverPlateGreaves = "items/equipment/boots/silver_plate_greaves"
    SpidersilkBoots = "items/equipment/boots/spidersilk_boots"

    # Chest Armor
    AmberiteCuirass = "items/equipment/chest_armor/amberite_cuirass"
    AmberitePlateCuirass = "items/equipment/chest_armor/amberite_plate_cuirass"
    IronCuirass = "items/equipment/chest_armor/iron_cuirass"
    IronPlateCuirass = "items/equipment/chest_armor/iron_plate_cuirass"
    LeatherJerkin = "items/equipment/chest_armor/leather_jerkin"
    MothsilkRobe = "items/equipment/chest_armor/mothsilk_robe"
    MythrilCuirass = "items/equipment/chest_armor/mythril_cuirass"
    MythrilPlateCuirass = "items/equipment/chest_armor/mythril_plate_cuirass"
    OrichalcumCuirass = "items/equipment/chest_armor/orichalcum_cuirass"
    OrichalcumPlateCuirass = "items/equipment/chest_armor/orichalcum_plate_cuirass"
    RobeOfTheEyelessSeer = "items/equipment/chest_armor/robe_of_the_eyeless_seer"
    SilverCuirass = "items/equipment/chest_armor/silver_cuirass"
    SilverPlateCuirass = "items/equipment/chest_armor/silver_plate_cuirass"
    SpidersilkRobe = "items/equipment/chest_armor/spidersilk_robe"

    # Gloves
    AmberiteGauntlets = "items/equipment/gloves/amberite_gauntlets"
    AmberitePlateGauntlets = "items/equipment/gloves/amberite_plate_gauntlets"
    IronGauntlets = "items/equipment/gloves/iron_gauntlets"
    IronPlateGauntlets = "items/equipment/gloves/iron_plate_gauntlets"
    LeatherGloves = "items/equipment/gloves/leather_gloves"
    MothsilkGloves = "items/equipment/gloves/mothsilk_gloves"
    MythrilGauntlets = "items/equipment/gloves/mythril_gauntlets"
    MythrilPlateGauntlets = "items/equipment/gloves/mythril_plate_gauntlets"
    OrichalcumGauntlets = "items/equipment/gloves/orichalcum_gauntlets"
    OrichalcumPlateGauntlets = "items/equipment/gloves/orichalcum_plate_gauntlets"
    SilverGauntlets = "items/equipment/gloves/silver_gauntlets"
    SilverPlateGauntlets = "items/equipment/gloves/silver_plate_gauntlets"
    SpidersilkGloves = "items/equipment/gloves/spidersilk_gloves"

    # Helmet
    AmberiteHelmet = "items/equipment/helmet/amberite_helmet"
    AmberitePlateHelmet = "items/equipment/helmet/amberite_plate_helmet"
    IronHelmet = "items/equipment/helmet/iron_helmet"
    IronPlateHelmet = "items/equipment/helmet/iron_plate_helmet"
    LeatherHelmet = "items/equipment/helmet/leather_helmet"
    MothsilkCowl = "items/equipment/helmet/mothsilk_cowl"
    MythrilHelmet = "items/equipment/helmet/mythril_helmet"
    MythrilPlateHelmet = "items/equipment/helmet/mythril_plate_helmet"
    OrichalcumHelmet = "items/equipment/helmet/orichalcum_helmet"
    OrichalcumPlateHelmet = "items/equipment/helmet/orichalcum_plate_helmet"
    SilverHelmet = "items/equipment/helmet/silver_helmet"
    SilverPlateHelmet = "items/equipment/helmet/silver_plate_helmet"
    SpidersilkCowl = "items/equipment/helmet/spidersilk_cowl"

    # Leggings
    AmberiteLeggings = "items/equipment/leggings/amberite_leggings"
    AmberitePlateLeggings = "items/equipment/leggings/amberite_plate_leggings"
    IronLeggings = "items/equipment/leggings/iron_leggings"
    IronPlateLeggings = "items/equipment/leggings/iron_plate_leggings"
    LeatherLeggings = "items/equipment/leggings/leather_leggings"
    MythrilLeggings = "items/equipment/leggings/mythril_leggings"
    MythrilPlateLeggings = "items/equipment/leggings/mythril_plate_leggings"
    OrichalcumLeggings = "items/equipment/leggings/orichalcum_leggings"
    OrichalcumPlateLeggings = "items/equipment/leggings/orichalcum_plate_leggings"
    SilverLeggings = "items/equipment/leggings/silver_leggings"
    SilverPlateLeggings = "items/equipment/leggings/silver_plate_leggings"

    # Offhand
    DeckOfFate = "items/equipment/offhand/deck_of_fate"
    WoodenBuckler = "items/equipment/offhand/wooden_buckler"

    # Rings
    BandOfGreaterRestoration = "items/equipment/ring/band_of_greater_restoration"
    CopperRing = "items/equipment/ring/copper_ring"
    GoldRing = "items/equipment/ring/gold_ring"
    MrBonesRing = "items/equipment/ring/mr_bones_ring"
    SilverRing = "items/equipment/ring/silver_ring"

    # Gardening
    Ash = "items/gardening/soil/ash"
    Clay = "items/gardening/soil/clay"
    Compost = "items/gardening/soil/compost"
    Dirt = "items/gardening/soil/dirt"
    Loam = "items/gardening/soil/loam"
    Pebbles = "items/gardening/soil/pebbles"

    # Materials
    AmberiteIngot = "items/ingredient/materials/amberite_ingot"
    AmberiteOre = "items/ingredient/materials/amberite_ore"
    CopperIngot = "items/ingredient/materials/copper_ingot"
    CopperOre = "items/ingredient/materials/copper_ore"
    GoldIngot = "items/ingredient/materials/gold_ingot"
    GoldOre = "items/ingredient/materials/gold_ore"
    IronIngot = "items/ingredient/materials/iron_ingot"
    IronOre = "items/ingredient/materials/iron_ore"
    JewelersKit = "items/ingredient/materials/jewelers_kit"
    Leather = "items/ingredient/materials/leather"
    LeatherScraps = "items/ingredient/materials/leather_scraps"
    MothsilkBolt = "items/ingredient/materials/mothsilk_bolt"
    Mothsilk = "items/ingredient/materials/mothsilk"
    MythrilIngot = "items/ingredient/materials/mythril_ingot"
    MythrilOre = "items/ingredient/materials/mythril_ore"
    OrichalcumIngot = "items/ingredient/materials/orichalcum_ingot"
    OrichalcumOre = "items/ingredient/materials/orichalcum_ore"
    SilverIngot = "items/ingredient/materials/silver_ingot"
    SilverOre = "items/ingredient/materials/silver_ore"
    SpidersilkBolt = "items/ingredient/materials/spidersilk_bolt"
    Spidersilk = "items/ingredient/materials/spidersilk"
    ThickLeather = "items/ingredient/materials/thick_leather"
    VoidseenIngot = "items/ingredient/materials/voidseen_ingot"
    VoidseenOre = "items/ingredient/materials/voidseen_ore"
    Whetstone = "items/ingredient/materials/whetstone"

    # Weapons

    # Daggers
    IronDagger = "items/weapon/dagger/iron_dagger"

    # Greatswords
    AbarrasGreatsword = "items/weapon/greatsword/abarras_greatsword"
    IronGreatsword = "items/weapon/greatsword/iron_greatsword"

    # Knuckles
    IronKnuckles = "items/weapon/knuckles/iron_knuckles"
    
    # Spears
    IronSpear = "items/weapon/spear/iron_spear"
    
    # Staves
    LithewoodStaff = "items/weapon/staff/lithewood_staff"
    WrathbarkStaff = "items/weapon/staff/wrathbark_staff"
    YennasStaff = "items/weapon/staff/yennas_staff"

    # Swords
    IronSword = "items/weapon/sword/iron_sword"
    GalosRapier = "items/weapon/sword/galos_rapier"

    # Misc Weapons
    CopperbroadsFryingPan = "items/weapon/misc/copperbroads_frying_pan"

    # Misc
    CursedStone = "items/equipment/offhand/cursed_stone"
    GoldenKnucklebone = "items/equipment/offhand/golden_knucklebone"
    PurifiedHeart = "items/equipment/offhand/purified_heart"

# -----------------------------------------------------------------------------
# CLASSES
# -----------------------------------------------------------------------------

class ArmorStats():
    def __init__(self, armor_amount=0):
        self._armor_amount = armor_amount

    def get_armor_amount(self):
        return self._armor_amount

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._armor_amount = state.get("armor_amount", 0)


class WeaponStats():
    def __init__(self, min_damage=0, max_damage=0, num_targets=1):
        self._min_damage = min_damage
        self._max_damage = max_damage
        self._num_targets = num_targets
    
    def get_range_str(self):
        return f"{self._min_damage}-{self._max_damage} base damage"

    def get_num_targets_str(self):
        if self._num_targets == 1:
            return ""
        return f"({self._num_targets} targets)"

    def get_random_damage(self, attacker_attrs: Attributes, item_effects: ItemEffects | None, level_diff: int):
        base_damage: int = randint(self._min_damage, self._max_damage)
        buffed_damage: int = base_damage

        # This only applies to the main hand item; there should only be one instance of a damage boost per
        # attribute, so we can just use the value from the first matching one.
        if item_effects is not None:
            dex_damage_boost: float = 0
            int_damage_boost: float = 0
            lck_damage_boost: float = 0

            for effect in item_effects.permanent:
                if effect.effect_type == EffectType.DmgBuffFromDex:
                    dex_damage_boost = effect.effect_value
                elif effect.effect_type == EffectType.DmgBuffFromInt:
                    int_damage_boost = effect.effect_value
                elif effect.effect_type == EffectType.DmgBuffFromLck:
                    lck_damage_boost = effect.effect_value

            buffed_damage += min(int(base_damage * dex_damage_boost * max(attacker_attrs.dexterity, 0)), base_damage)
            buffed_damage += min(int(base_damage * int_damage_boost * max(attacker_attrs.intelligence, 0)), base_damage)
            buffed_damage += min(int(base_damage * lck_damage_boost * max(attacker_attrs.luck, 0)), base_damage)

        reduce_to: float = max(0, 1.0 - (WEAPON_OVERLEVELED_DEBUFF * max(0, level_diff)))
        return int(buffed_damage * reduce_to)

    def get_max_damage(self):
        return self._max_damage

    def get_num_targets(self):
        return self._num_targets

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._min_damage = state.get("min_damage", 0)
        self._max_damage = state.get("max_damage", 0)
        self._num_targets = state.get("num_targets", 1)


class ConsumableStats():
    def __init__(self, num_targets: int=0, target_own_group: bool=True):
        self._num_targets = num_targets
        self._target_own_group = target_own_group

    def get_num_targets(self):
        return self._num_targets

    def get_target_own_group(self):
        return self._target_own_group

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._num_targets = state.get("num_targets", 0)
        self._target_own_group = state.get("target_own_group", True)


class Item():
    def __init__(self, key: ItemKey, icon: str, name: str, value: int, rarity: Rarity, description: str, flavor_text:str, class_tags: List[ClassTag], state_tags: List[StateTag]=[], count=1, level_requirement=0, item_effects: ItemEffects | None=None, altering_item_keys: List[ItemKey]=[], armor_stats: ArmorStats | None=None, weapon_stats: WeaponStats | None=None, consumable_stats: ConsumableStats | None=None):
        self._key: ItemKey = key
        self._icon: str = icon
        self._name: str = name
        self._value: int = value
        self._rarity: Rarity = rarity
        self._description: str = description
        self._flavor_text: str = flavor_text
        self._class_tags: List[ClassTag] = class_tags
        self._state_tags: List[StateTag] = state_tags
        self._count: int = count
        self._level_requirement: int = level_requirement
        self._item_effects: ItemEffects | None = item_effects
        self._altering_item_keys: List[ItemKey] = altering_item_keys

        self._armor_stats: ArmorStats | None = armor_stats
        self._weapon_stats: WeaponStats | None = weapon_stats
        self._consumable_stats: ConsumableStats | None = consumable_stats

    @staticmethod
    def load_from_state(item_data: dict):
        armor_data = item_data.get("armor_stats")
        armor_stats = None
        if armor_data is not None:
            armor_stats = ArmorStats()
            armor_stats.__setstate__(armor_data)
        
        weapon_data = item_data.get("weapon_stats")
        weapon_stats = None
        if weapon_data is not None:
            weapon_stats = WeaponStats()
            weapon_stats.__setstate__(weapon_data)

        consumable_data = item_data.get("consumable_stats")
        consumable_stats = None
        if consumable_data is not None:
            consumable_stats = ConsumableStats()
            consumable_stats.__setstate__(consumable_data)

        item_effects_data = item_data.get("item_effects")
        item_effects = None
        if item_effects_data is not None:
            item_effects = ItemEffects()
            item_effects.__setstate__(item_effects_data)
        
        return Item(
            item_data.get("key", ""),
            item_data.get("icon", ""),
            item_data.get("name", ""),
            item_data.get("value", 0),
            item_data.get("rarity", Rarity.Unknown),
            item_data.get("description", ""),
            item_data.get("flavor_text", ""),
            item_data.get("class_tags", []),
            item_data.get("state_tags", []),
            item_data.get("count", 1),
            item_data.get("level_requirement", 0),
            item_effects,
            item_data.get("altering_item_keys", []),
            armor_stats,
            weapon_stats,
            consumable_stats
        )

    def remove_amount(self, amount: int):
        if amount <= self._count:
            result = Item(
                self._key,
                self._icon,
                self._name,
                self._value,
                self._rarity,
                self._description,
                self._flavor_text,
                self._class_tags,
                self._state_tags[:],
                amount,
                self._level_requirement,
                self._item_effects,
                self._altering_item_keys[:],
                self._armor_stats,
                self._weapon_stats,
                self._consumable_stats)
            self._count -= amount
            return result
        return None

    def add_amount(self, amount: int):
        self._count += amount

    def get_name(self) -> str:
        return self._name

    def get_full_name(self) -> str:
        return f"{self._icon} {self._name}"

    def get_name_and_count(self) -> str:
        if self._count > 1:
            return f"{self._name} ({self._count})"
        return f"{self._name}"

    def get_full_name_and_count(self) -> str:
        if self._count > 1:
            return f"{self._icon} {self._name} ({self._count})"
        return f"{self._icon} {self._name}"

    def get_value(self) -> int:
        sockted_item_keys = list(filter(lambda x: x != "", self._altering_item_keys))
        value = self._value
        for item_key in sockted_item_keys:
            value += int(LOADED_ITEMS.get_item_state(item_key)["value"])
        return value

    def get_value_str(self) -> str:
        if self.get_value() == 1:
            return "1 coin"
        return f"{self.get_value()} coins"

    def get_count(self) -> int:
        return self._count

    def get_icon(self) -> str:
        return self._icon

    def get_rarity(self) -> Rarity:
        return self._rarity

    def get_description(self) -> str:
        return self._description
    
    def get_flavor_text(self) -> str:
        return self._flavor_text

    def get_class_tags(self) -> List[ClassTag]:
        return self._class_tags

    def get_state_tags(self) -> List[StateTag]:
        return self._state_tags

    def set_state_tags(self, new_tags: List[StateTag]) -> None:
        self._state_tags = new_tags

    def get_key(self) -> ItemKey:
        return self._key

    def get_level_requirement(self) -> int:
        return self._level_requirement

    def get_item_effects(self) -> ItemEffects:
        # Start with this item's base effects
        combined_effects = self._item_effects if self._item_effects is not None else ItemEffects()

        # Add in everything from items that are altering it
        for item_key in self._altering_item_keys:
            if item_key != "":
                item_effects_data = LOADED_ITEMS.get_item_state(item_key).get("item_effects")
                item_effects = None
                if item_effects_data is not None:
                    item_effects = ItemEffects()
                    item_effects.__setstate__(item_effects_data)
                
                if item_effects is not None:
                    combined_effects += item_effects

        return combined_effects

    def get_altering_item_keys(self) -> List[ItemKey]:
        return self._altering_item_keys

    def get_armor_stats(self) -> (ArmorStats | None):
        return self._armor_stats

    def get_weapon_stats(self) -> (WeaponStats | None):
        return self._weapon_stats

    def get_consumable_stats(self) -> (ConsumableStats | None):
        return self._consumable_stats

    def set_altering_item_keys(self, keys: List[ItemKey]) -> None:
        self._altering_item_keys = keys

    def get_str_for_slot(self, slot: ClassTag.Equipment):
        if slot == ClassTag.Equipment.ChestArmor:
            return "Chest Armor"
        if slot == ClassTag.Equipment.MainHand:
            return "Main Hand"
        if slot == ClassTag.Equipment.OffHand:
            return "Off Hand"
        return slot

    def __str__(self):
        display_string = f"**{self.get_full_name_and_count()}**\n*{self._rarity} Item*" + (" / *Unique*" if ClassTag.Misc.IsUnique in self._class_tags else "")
        
        has_any_stats: bool = False

        if ClassTag.Equipment.Equipment in self._class_tags:
            equipment_tags = []
            possible_tags = set(item.value for item in ClassTag.Equipment if item != ClassTag.Equipment.Equipment)
            for class_tag in self._class_tags:
                if class_tag in possible_tags:
                    mapped_str = self.get_str_for_slot(class_tag)
                    equipment_tags.append(f"*{mapped_str}*")
            display_string += " / " + ", ".join(equipment_tags)

        display_string += "\n\n"

        if ClassTag.Misc.NeedsIdentification in self._class_tags:
            display_string += "???\n\n*Needs Identification*"
        
        if self._armor_stats is not None:
            has_any_stats = True
            display_string += f"{self._armor_stats.get_armor_amount()} Armor\n"

        if self._weapon_stats is not None:
            has_any_stats = True
            display_string += f"{self._weapon_stats.get_range_str()} {self._weapon_stats.get_num_targets_str()}\n"

        if self._consumable_stats is not None:
            has_any_stats = True
            target_str: str = ""
            if self._consumable_stats._num_targets == -1:
                target_str = "Targets All\n"
            if self._consumable_stats._num_targets == 0:
                target_str = "Targets Self\n"
            if self._consumable_stats._num_targets == 1:
                target_str = "1 Target\n"
            if self._consumable_stats._num_targets > 1:
                target_str = f"1-{self._consumable_stats._num_targets} Targets\n"
            display_string += target_str

        if self._item_effects is not None:
            item_effects_str = str(self._item_effects)
            # There are some cases where I'd rather use a custom description
            if item_effects_str != "":
                has_any_stats = True
                display_string += f"{self._item_effects}\n"

        if has_any_stats:
            display_string += "\n"

        if len(self._altering_item_keys) > 0:
            for altering_item_key in self._altering_item_keys:
                if altering_item_key == "":
                    display_string += f"Empty Socket\n"
                else:
                    item = LOADED_ITEMS.get_new_item(altering_item_key)
                    condition_type = ConditionType.IsItemArmor
                    if ClassTag.Equipment.MainHand in self.get_class_tags() or ClassTag.Equipment.OffHand in self.get_class_tags():
                        condition_type = ConditionType.IsItemInHand
                    item_effects = item.get_item_effects()
                    active_item_effects_str = f"{item_effects.get_socket_str(condition_type)}" if item_effects is not None else ""
                    display_string += f"{item.get_full_name()}\n{active_item_effects_str}"
            display_string += "\n"

        if self._description != "":
            display_string += f"{self._description}\n\n"
        if self._flavor_text != "":
            display_string += f"*{self._flavor_text}*\n\n"
        
        display_string += f"Value: *{self.get_value()}* each\n"
        display_string += f"Level Requirement: {self._level_requirement}"
        
        return display_string

    def __eq__(self, obj) -> bool:
        if not isinstance(obj, Item):
            return False
        
        if (ClassTag.Misc.IsUnique in self.get_state_tags() or
            ClassTag.Misc.IsUnique in obj.get_state_tags()):
            return False

        return (self._key == obj.get_key() and 
                self._state_tags == obj.get_state_tags() and
                self._altering_item_keys == obj.get_altering_item_keys())

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        # TODO: This handles the case where I've deleted an item JSON or the key
        # doesn't exist, but it should ideally somehow make this None instead of an Item,
        # though an Item with everything default will work too because it should
        # be cleaned up by the inventory automatically. I'll need to figure that out
        # at some point in the future. Custom param that indicates deletion and have
        # Inventory do it?
        if state.get("_key", "") not in LOADED_ITEMS.get_all_keys():
            return
        
        base_data = LOADED_ITEMS.get_item_state(state["_key"])

        # Always replace these values; the base data overrides them.
        self._key = base_data.get("key", "")
        self._icon = base_data.get("icon", "")
        self._name = base_data.get("name", "")
        self._value = base_data.get("value", 0)
        self._rarity = base_data.get("rarity", Rarity.Unknown)
        self._description = base_data.get("description", "")
        self._flavor_text = base_data.get("flavor_text", "")
        self._level_requirement = base_data.get("level_requirement", 0)
        self._class_tags = base_data.get("class_tags", [])

        armor_data = base_data.get("armor_stats")
        if armor_data is not None:
            self._armor_stats = ArmorStats()
            self._armor_stats.__setstate__(armor_data)
        else:
            self._armor_stats = None
        
        weapon_data = base_data.get("weapon_stats")
        if weapon_data is not None:
            self._weapon_stats = WeaponStats()
            self._weapon_stats.__setstate__(weapon_data)
        else:
            self._weapon_stats = None

        consumable_data = base_data.get("consumable_stats")
        if consumable_data is not None:
            self._consumable_stats = ConsumableStats()
            self._consumable_stats.__setstate__(consumable_data)
        else:
            self._consumable_stats = None

        item_effects_data = base_data.get("item_effects")
        if item_effects_data is not None:
            self._item_effects = ItemEffects()
            self._item_effects.__setstate__(item_effects_data)
        else:
            self._item_effects = None

        # These are stateful values and we use what's loaded from the database.
        self._state_tags = state.get("_state_tags", [])
        self._count = state.get("_count", 1)

        # TODO: If I change the number of sockets on an item in the future, this will be inconvenient. I
        # need to figure out a way (when the length of the base_data altering_item_keys is *less than* the
        # one in state) to return those items to the player before replacing the altering_item_keys.
        base_data_sockets = base_data.get("altering_item_keys", [])
        state_sockets = state.get("_altering_item_keys", [])
        if len(base_data_sockets) > len(state_sockets):
            self._altering_item_keys = state_sockets + ["" for _ in range(len(base_data_sockets) - len(state_sockets))]
        else:
            self._altering_item_keys = state.get("_altering_item_keys", base_data_sockets)

# I'm doing it this way because having a dict[ItemKey, Item] would
# mean that using the items in the dict would all point to the same
# reference of the object. That seems extremely risky, even if I copy
# the object every time I use the dict.

# The reason I don't want to use Item.load_from_key every
# time I need a new object is because I/O operations are expensive and
# with multiple potentially happening every second, that could yield
# a lot of errors due to the file being locked.
class LoadedItems():
    _states: MappingProxyType[ItemKey, dict] = MappingProxyType({
        item_key.value: json.load(open(f"./features/{item_key.value}.json", "r")) for item_key in ItemKey
    })

    def get_all_keys(self):
        return self._states.keys()

    def get_item_state(self, key: ItemKey):
        return self._states[key]

    def get_new_item(self, key: ItemKey):
        return Item.load_from_state(self._states[key])

# -----------------------------------------------------------------------------
# GLOBALS
# -----------------------------------------------------------------------------

LOADED_ITEMS = LoadedItems()
