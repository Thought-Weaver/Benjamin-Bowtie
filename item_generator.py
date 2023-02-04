from __future__ import annotations

import json
import numpy
import os
import random

from math import ceil
from typing import Dict, List, Tuple
from features.shared.attributes import Attributes
from features.shared.effect import Effect, EffectType, ItemEffectCategory, ItemEffects
from features.shared.enums import ClassTag
from features.shared.item import Rarity, WeaponStats, ArmorStats
from features.shared.statuseffect import StatusEffectKey

# Note: This is inclusive!
def frange(start: float, stop: float, step: float) -> List[float]:
    if step > 0 and stop > start:
        return list(numpy.arange(start=start, stop=stop + step, step=step))
    else:
        return [start, stop]

CLASS_TAGS: Dict[ClassTag.Weapon | ClassTag.Equipment, List[ClassTag.Weapon | ClassTag.Equipment]] = {
    ClassTag.Weapon.Dagger: [ClassTag.Equipment.Equipment, ClassTag.Weapon.Weapon, ClassTag.Weapon.Dagger, ClassTag.Equipment.MainHand],
    ClassTag.Weapon.Sword: [ClassTag.Equipment.Equipment, ClassTag.Weapon.Weapon, ClassTag.Weapon.Sword, ClassTag.Equipment.MainHand],
    ClassTag.Weapon.Greatsword: [ClassTag.Equipment.Equipment, ClassTag.Weapon.Weapon, ClassTag.Weapon.Greatsword, ClassTag.Equipment.MainHand],
    ClassTag.Weapon.Knuckles: [ClassTag.Equipment.Equipment, ClassTag.Weapon.Weapon, ClassTag.Weapon.Knuckles, ClassTag.Equipment.MainHand],
    ClassTag.Weapon.Spear: [ClassTag.Equipment.Equipment, ClassTag.Weapon.Weapon, ClassTag.Weapon.Spear, ClassTag.Equipment.MainHand],
    ClassTag.Weapon.Staff: [ClassTag.Equipment.Equipment, ClassTag.Weapon.Weapon, ClassTag.Weapon.Staff, ClassTag.Equipment.MainHand],
    ClassTag.Weapon.Shield: [ClassTag.Equipment.Equipment, ClassTag.Weapon.Shield, ClassTag.Weapon.Spear, ClassTag.Equipment.MainHand],

    ClassTag.Equipment.Helmet: [ClassTag.Equipment.Equipment, ClassTag.Equipment.Helmet],
    ClassTag.Equipment.ChestArmor: [ClassTag.Equipment.Equipment, ClassTag.Equipment.ChestArmor],
    ClassTag.Equipment.Gloves: [ClassTag.Equipment.Equipment, ClassTag.Equipment.Gloves],
    ClassTag.Equipment.Boots: [ClassTag.Equipment.Equipment, ClassTag.Equipment.Boots],
    ClassTag.Equipment.Amulet: [ClassTag.Equipment.Equipment, ClassTag.Equipment.Amulet],
    ClassTag.Equipment.Ring: [ClassTag.Equipment.Equipment, ClassTag.Equipment.Ring],
    ClassTag.Equipment.Leggings: [ClassTag.Equipment.Equipment, ClassTag.Equipment.Leggings]
}

NAMES_AND_ICONS: Dict[ClassTag.Weapon | ClassTag.Equipment, List[Tuple[str, str]]] = {
    ClassTag.Weapon.Dagger: [
        ("Dagger", "\uD83D\uDDE1\uFE0F"),
        ("Shiv", "\uD83D\uDD2A"),
        ("Sickle", "\u26CF\uFE0F"),
        ("Knife", "\uD83D\uDD2A"),
        ("Blade", "\uD83D\uDDE1\uFE0F"),
        ("Poignard", "\uD83D\uDDE1\uFE0F"),
        ("Rondel", "\uD83D\uDDE1\uFE0F"),
        ("Scramasax", "\uD83D\uDDE1\uFE0F"),
        ("Rondel", "\uD83D\uDDE1\uFE0F"),
        ("Trident Dagger", "\uD83D\uDD31"),
        ("Gauche", "\uD83D\uDDE1\uFE0F"),
        ("Piercer", "\uD83D\uDDE1\uFE0F")
    ],
    ClassTag.Weapon.Sword: [
        ("Broadsword", "\u2694\uFE0F"),
        ("Blade", "\u2694\uFE0F"),
        ("Falchion", "\u2694\uFE0F"),
        ("Shortsword", "\u2694\uFE0F"),
        ("Rapier", "\u2694\uFE0F"),
        ("Longsword", "\u2694\uFE0F"),
        ("Hook Sword", "\u2694\uFE0F"),
        ("Saber", "\u2694\uFE0F"),
        ("Estoc", "\u2694\uFE0F"),
        ("Gladius", "\u2694\uFE0F"),
        ("Sword", "\u2694\uFE0F"),
        ("Flowing Sword", "\u2694\uFE0F")
    ],
    ClassTag.Weapon.Greatsword: [
        ("Greatsword", "\u2694\uFE0F"),
        ("Claymore", "\u2694\uFE0F"),
        ("Flamberge", "\u2694\uFE0F"),
        ("Cleaver", "\u2694\uFE0F"),
        ("Reaver", "\u2694\uFE0F"),
        ("Grandsword", "\u2694\uFE0F"),
        ("Warblade", "\u2694\uFE0F")
    ],
    ClassTag.Weapon.Knuckles: [
        ("Knuckles", "\uD83E\uDD4A"),
        ("Cestus", "\uD83E\uDD4A"),
        ("Star Fist", "\uD83E\uDD4A"),
        ("Claws", "\uD83E\uDD4A"),
        ("Talons", "\uD83E\uDD4A"),
        ("Gadlings", "\uD83E\uDD4A")
    ],
    ClassTag.Weapon.Spear: [
        ("Spear", "\uD83C\uDF62"),
        ("Partisan", "\uD83C\uDF62"),
        ("Pike", "\uD83C\uDF62"),
        ("Harpoon", "\uD83C\uDF62"),
        ("Torchpole", "\uD83C\uDF62"),
        ("Lance", "\uD83C\uDF62"),
        ("Glaive", "\uD83C\uDF62"),
        ("Fauchard", "\uD83C\uDF62"),
        ("Halberd", "\uD83C\uDF62"),
        ("Poleaxe", "\uD83C\uDF62"),
        ("Trident", "\uD83D\uDD31"),
        ("War Fork", "\uD83D\uDD31")
    ],
    ClassTag.Weapon.Staff: [
        ("Staff", "\uD83E\uDE84"),
        ("Fisher's Staff", "\uD83E\uDE84"),
        ("Crook", "\uD83E\uDE84"),
        ("Rod", "\uD83E\uDE84"),
        ("Scepter", "\uD83E\uDE84"),
        ("Battle Staff", "\uD83E\uDE84"),
        ("Bone Staff", "\uD83E\uDDB4"),
        ("Gnarled Staff", "\uD83E\uDE84"),
        ("War Staff", "\uD83E\uDE84")
    ],
    ClassTag.Weapon.Shield: [
        ("Shield", "\uD83D\uDEE1\uFE0F"),
        ("Buckler", "\uD83D\uDEE1\uFE0F"),
        ("Greatshield", "\uD83D\uDEE1\uFE0F"),
        ("Targe", "\uD83D\uDEE1\uFE0F"),
        ("Round Shield", "\uD83D\uDEE1\uFE0F"),
        ("Gilded Shield", "\uD83D\uDD30"),
        ("Crested Shield", "\uD83D\uDD30"),
        ("Kite Shield", "\uD83D\uDD30")
    ],

    ClassTag.Equipment.Helmet: [
        ("Pointed Hat", "\uD83C\uDF93"),
        ("Hat", "\uD83C\uDFA9"),
        ("Cloth Mask", "\uD83E\uDDE3"),
        ("Hood", "\uD83C\uDFA9"),
        ("Mail Hood", "\uD83C\uDFA9"),
        ("Circlet", "\uD83D\uDC51"),
        ("Flower Crown", "\uD83C\uDF3A"),
        ("Bucket", "\uD83E\uDEE7"),
        ("Mushroom Crown", "\uD83C\uDF44"),
        ("Helm", "\uD83C\uDFA9"),
        ("Helmet", "\uD83C\uDFA9"),
        ("Cowl", "\uD83C\uDFA9"),
        ("Crown", "\uD83D\uDC51"),
        ("Horned Headband", "\uD83D\uDC52"),
        ("Mask", "\uD83C\uDFAD")
    ],
    ClassTag.Equipment.ChestArmor: [
        ("Coat", "\uD83E\uDDE5"),
        ("Cloak", "\uD83E\uDDE5"),
        ("Tunic", "\uD83E\uDDE5"),
        ("Mail Armor", "\uD83E\uDDE5"),
        ("Cuirass", "\uD83E\uDDE5"),
        ("Surcoat", "\uD83E\uDDE5")
    ],
    ClassTag.Equipment.Gloves: [
        ("Gloves", "\uD83E\uDDE4"),
        ("Machettes", "\uD83E\uDDE4"),
        ("Bracers", "\uD83E\uDDE4"),
        ("Gauntlets", "\uD83E\uDDE4"),
        ("Wraps", "\uD83E\uDDE4"),
        ("Grips", "\uD83E\uDDE4"),
        ("Manifers", "\uD83E\uDDE4")
    ],
    ClassTag.Equipment.Boots: [
        ("Boots", "\uD83E\uDD7E"),
        ("Greaves", "\uD83E\uDD7E"),
        ("Sabatons", "\uD83E\uDD7E"),
        ("Treads", "\uD83E\uDD7E"),
        ("Tracks", "\uD83E\uDD7E"),
        ("Shoes", "\uD83E\uDD7E"),
        ("Sandals", "\uD83D\uDC61")
    ],
    ClassTag.Equipment.Amulet: [
        ("Necklace", "\uD83D\uDCFF"),
        ("Amulet", "\uD83D\uDCFF"),
        ("Periapt", "\uD83D\uDCFF"),
        ("Sigil", "\uD83D\uDCFF"),
        ("Pendant", "\uD83D\uDCFF"),
        ("Carcanet", "\uD83D\uDCFF"),
        ("Strand", "\uD83D\uDCFF"),
        ("Lariat", "\uD83D\uDCFF")
    ],
    ClassTag.Equipment.Ring: [
        ("Ring", "\uD83D\uDC8D"),
        ("Signet", "\uD83D\uDC8D"),
        ("Band", "\u2B55"),
        ("Loop", "\u2B55"),
        ("Circle", "\u2B55"),
        ("Cord", "\u2B55"),
        ("Flower Band", "\uD83C\uDF38"),
        ("Mushroom Band", "\uD83C\uDF44")
    ],
    ClassTag.Equipment.Leggings: [
        ("Trousers", "\uD83D\uDC56"),
        ("Pants", "\uD83D\uDC56"),
        ("Leggings", "\uD83D\uDC56"),
        ("Breeches", "\uD83D\uDC56"),
        ("Legwraps", "\uD83D\uDC56"),
        ("Chausses", "\uD83D\uDC56"),
        ("Faulds", "\uD83D\uDC56"),
        ("Poleyns", "\uD83D\uDC56"),
        ("Schynbalds", "\uD83D\uDC56"),
        ("Tassets", "\uD83D\uDC56")
    ]
}

# Note: These have +1 on the upper end since range is exclusive
SLOTS_PER_ITEM_TYPE: Dict[ClassTag.Weapon | ClassTag.Equipment, range] = {
    ClassTag.Weapon.Dagger: range(0, 3),
    ClassTag.Weapon.Sword: range(0, 4),
    ClassTag.Weapon.Greatsword: range(0, 4),
    ClassTag.Weapon.Knuckles: range(0, 3),
    ClassTag.Weapon.Spear: range(0, 4),
    ClassTag.Weapon.Staff: range(0, 4),
    ClassTag.Weapon.Shield: range(0, 4),

    ClassTag.Equipment.Helmet: range(0, 3),
    ClassTag.Equipment.ChestArmor: range(0, 4),
    ClassTag.Equipment.Gloves: range(0, 2),
    ClassTag.Equipment.Boots: range(0, 3),
    ClassTag.Equipment.Amulet: range(0, 2),
    ClassTag.Equipment.Ring: range(0, 2),
    ClassTag.Equipment.Leggings: range(0, 3)
}

GOOD_SUFFIXES: Dict[EffectType, List[str] | Dict[StatusEffectKey, List[str]]] = {
    EffectType.CleanseStatusEffects: ["of Purification", "of Cleansing"],

    EffectType.ConMod: ["of Fortification", "of Constitution", "of the Bear"],
    EffectType.StrMod: ["of Strength", "of Might"],
    EffectType.DexMod: ["of Dexterity", "of Precision", "of Haste", "of Accuracy", "of the Wind", "of Shadows"],
    EffectType.IntMod: ["of Knowledge", "of the Erudite", "of Intelligence", "of Arcana", "of the Augur", "of the Sage"],
    EffectType.LckMod: ["of Luck", "of Fortune", "of Serendipity"],
    EffectType.MemMod: ["of Remembrance", "of Memory"],

    EffectType.DmgReflect: ["of Reflection", "of Mirrors", "of the Turtle", "of Brambles", "of Thorns"],
    EffectType.DmgResist: ["of Absorption", "of Nullifcation", "of Endurance"],
    EffectType.DmgBuff: ["of Force", "of the Storm", "of Brutality"],
    EffectType.DmgBuffSelfMaxHealth: ["of the Hemocrafter", "of the Butcher"],
    EffectType.DmgBuffSelfRemainingHealth: ["of the Hemocrafter", "of the Butcher"],
    EffectType.DmgBuffOtherMaxHealth: ["of the Hemocrafter", "of the Butcher"],
    EffectType.DmgBuffOtherRemainingHealth: ["of the Hemocrafter", "of the Butcher"],

    EffectType.DmgBuffLegends: ["of the Titan", "of Legends"],
    EffectType.DmgBuffPoisoned: ["of the Serpent", "of Toxicity"],
    EffectType.DmgBuffBleeding: ["of the Bloodthirsty", "of the Macabre", "of Agony"],
    EffectType.DmgBuffFromDex: ["of Balance", "of Accuracy", "of Precision"],
    EffectType.DmgBuffFromInt: ["of Knowledge", "of Brilliance", "of the Erudite"],
    EffectType.DmgBuffFromLck: ["of Fortune", "of the Fated", "of Luck", "of Serendipity"],

    EffectType.RestoreArmor: ["of Weavebonding", "of Metalbonding", "of Repair"],
    EffectType.RestorePercentArmor: ["of Weavebonding", "of Metalbonding", "of Repair"],
    EffectType.PiercingDmg: ["of Slaying", "of Carnage"],
    EffectType.PiercingPercentDmg: ["of Slaying", "of Carnage"],
    EffectType.SplashDmg: ["of the Giant", "of the Earthquake"],
    EffectType.SplashPercentMaxDmg: ["of the Giant", "of the Earthquake"],

    EffectType.CritDmgBuff: ["of Focus"],
    EffectType.CritDmgReduction: ["of Focus"],
    
    EffectType.HealthSteal: ["of the Vampire", "of the Leech", "of the Ichordrinker"],
    EffectType.ManaSteal: ["of the Wraith", "of the Lamprey", "of the Sycophant"],
    EffectType.AdjustedCDs: ["of Haste", "of Celerity"],

    EffectType.ChanceStatusEffect: {
        StatusEffectKey.Bleeding: ["of Maiming", "of Bloodletting"],
        StatusEffectKey.Poisoned: ["of the Viper", "of Virulence", "of the Asp"],
        StatusEffectKey.DmgReduction: ["of Protection", "of Preservation", "of Shielding"],
        StatusEffectKey.DmgVulnerability: ["of Frailty", "of Weakening", "of Diminishing"],
        StatusEffectKey.FixedDmgTick: ["of the Voice", "of the Spark", "of Flame"],
        StatusEffectKey.TurnSkipChance: ["of Halting", "of Breaking", "of Stunning"],
        StatusEffectKey.Taunted: ["of Taunting", "of Torment", "of Goading"],
        StatusEffectKey.CannotTarget: ["of the Ghost", "of the Spectre"],
        StatusEffectKey.Generating: ["of the Rich"],
        StatusEffectKey.Tarnished: ["of Coin Cursing"],
        StatusEffectKey.ManaToHP: ["of Transmutation", "of Sanguination"],
        StatusEffectKey.PotionBuff: ["of the Alchemist", "of the Hermetics", "of Decoction"],
        StatusEffectKey.PoisonHeals: ["of Transmutation", "of Festering", "of Greenclot"],
        StatusEffectKey.DmgBuff: ["of Force", "of the Storm", "of Brutality"],
        StatusEffectKey.DmgDebuff: ["of Emaciation", "of Withering", "of the Haggard"],
        StatusEffectKey.DmgReflect: ["of Reflection", "of Mirrors", "of the Turtle"],
        StatusEffectKey.Charmed: ["of Charming", "of Captivation", "of Hypnosis", "of Bewitching"],
        StatusEffectKey.CannotAttack: ["of Wasting", "of Debilitation", "of Deterioration"],
        StatusEffectKey.Sleeping: ["of the Dream", "of the Slumbering"],
        StatusEffectKey.Decaying: ["of Decay", "of Decomposition", "of Rot"],
        StatusEffectKey.Undying: ["of the Immortal", "of the Eternal", "of the Deathless"],
        StatusEffectKey.CannotUseAbilities: ["of Enfeeblement", "of Exhaustion", "of Depletion"],
        StatusEffectKey.StackingDamage: ["of Resonance", "of Reverberation"]
    },

    EffectType.ResistStatusEffect: {
        StatusEffectKey.Bleeding: ["of Clotting", "of Cauterization", "of Coagulation", "of Embolization"],
        StatusEffectKey.Poisoned: ["of Decontamination", "of the Antidote"],
        StatusEffectKey.DmgVulnerability: ["of Resilience", "of the Formidable", "of Tenacity"],
        StatusEffectKey.TurnSkipChance: ["of the Steady", "of the Unwavering"],
        StatusEffectKey.Taunted: ["of the Calm", "of the Stoic"],
        StatusEffectKey.CannotTarget: ["of Concentration", "of the Focused"],
        StatusEffectKey.DmgDebuff: ["of Might", "of Power", "of the Ardent"],
        StatusEffectKey.Charmed: ["of the Serene", "of the Composed"],
        StatusEffectKey.CannotAttack: ["of the Persistent", "of the Unabating"],
        StatusEffectKey.Sleeping: ["of the Sleepless", "of the Insomniac"],
        StatusEffectKey.Decaying: ["of the Vigorous", "of the Flourishing"]
    },

    EffectType.RestoreHealth: ["of Recovery", "of Restoration", "of Rejuvenation"],
    EffectType.RestorePercentHealth: ["of Recovery", "of Restoration", "of Rejuvenation"],
    EffectType.RestoreMana: ["of Sorcery", "of the Occult", "of the Mystic"],
    EffectType.RestorePercentMana: ["of Sorcery", "of the Occult", "of the Mystic"],

    EffectType.AdjustedManaCosts: ["of the Cryptic", "of Incantations"],
    EffectType.HealingAbilityBuff: ["of the Healer", "of Healing"],
    EffectType.AdditionalXP: ["of Expertise", "of the Adept", "of Comprehension"],
    EffectType.PotionMod: ["of the Alchemist", "of the Hermetic"],

    EffectType.Damage: ["of Harm", "of Mutilation", "of Ruin"],
    EffectType.ResurrectOnce: ["of the Phoenix", "of Revivication"]
}

BAD_SUFFIXES: Dict[EffectType, List[str] | Dict[StatusEffectKey, List[str]]] = {
    EffectType.CleanseStatusEffects: [],

    EffectType.ConMod: ["of Shattering", "of the Weak"],
    EffectType.StrMod: ["of Withering", "of Diminishing"],
    EffectType.DexMod: ["of Halting", "of the Slow"],
    EffectType.IntMod: ["of the Foolish", "of the Dull", "of the Mindless"],
    EffectType.LckMod: ["of the Unlucky", "of the Luckless", "of the Ill-Fated"],
    EffectType.MemMod: ["of the Distracted", "of the Amnesiac"],

    EffectType.DmgReflect: [],
    EffectType.DmgResist: [],
    EffectType.DmgBuff: [],
    EffectType.DmgBuffSelfMaxHealth: [],
    EffectType.DmgBuffSelfRemainingHealth: [],
    EffectType.DmgBuffOtherMaxHealth: [],
    EffectType.DmgBuffOtherRemainingHealth: [],

    EffectType.DmgBuffLegends: [],
    EffectType.DmgBuffPoisoned: [],
    EffectType.DmgBuffBleeding: [],
    EffectType.DmgBuffFromDex: [],
    EffectType.DmgBuffFromInt: [],
    EffectType.DmgBuffFromLck: [],

    EffectType.RestoreArmor: [],
    EffectType.RestorePercentArmor: [],
    EffectType.PiercingDmg: [],
    EffectType.PiercingPercentDmg: [],
    EffectType.SplashDmg: [],
    EffectType.SplashPercentMaxDmg: [],

    EffectType.CritDmgBuff: [],
    EffectType.CritDmgReduction: [],
    
    EffectType.HealthSteal: [],
    EffectType.ManaSteal: [],
    EffectType.AdjustedCDs: ["of Confusion", "of Dithering"],

    EffectType.ChanceStatusEffect: {},

    EffectType.ResistStatusEffect: {},

    EffectType.RestoreHealth: [],
    EffectType.RestorePercentHealth: [],
    EffectType.RestoreMana: [],
    EffectType.RestorePercentMana: [],

    EffectType.AdjustedManaCosts: ["of the Incompetent", "of the Inept"],
    EffectType.HealingAbilityBuff: ["of Decay", "of Decomposition"],
    EffectType.AdditionalXP: ["of the Fool", "of Lunacy", "of Madness"],
    EffectType.PotionMod: ["of the Powerless", "of Effete", "of the Barren"],

    EffectType.Damage: [],
    EffectType.ResurrectOnce: []
}

GOOD_PREFIXES: Dict[EffectType, List[str] | Dict[StatusEffectKey, List[str]]] = {
    EffectType.CleanseStatusEffects: ["Cleansing", "Purifying"],

    EffectType.ConMod: ["Fortifying", "Tower's", "Impenetrable", "Unbreaking", "Bear's", "Stalwart", "Robust"],
    EffectType.StrMod: ["Empowering", "Strong", "Hefty", "Giant's"],
    EffectType.DexMod: ["Quick", "Dextrous", "Precise", "Accurate", "Nimble", "Deft"],
    EffectType.IntMod: ["Knowing", "Brilliant", "Acute", "Arcane"],
    EffectType.LckMod: ["Lucky", "Fated", "Prosperous", "Serendipitous"],
    EffectType.MemMod: ["Recollecting"],

    EffectType.DmgReflect: ["Turtle's", "Reflecting", "Mirror's", "Rebounding", "Barbed"],
    EffectType.DmgResist: ["Absorbing", "Nullifying", "Enduring", "Outlasting"],
    EffectType.DmgBuff: ["Empowering", "Annihilating", "Storm's", "Jagged", "Deadly", "Brutal", "Savage", "Heavy", "Merciless"],
    EffectType.DmgBuffSelfMaxHealth: ["Bloodbound", "Lifestrike", "Hemocrafter's"],
    EffectType.DmgBuffSelfRemainingHealth: ["Bloodbound", "Lifestrike", "Hemocrafter's"],
    EffectType.DmgBuffOtherMaxHealth: ["Bloodbound", "Lifestrike", "Hemocrafter's"],
    EffectType.DmgBuffOtherRemainingHealth: ["Bloodbound", "Lifestrike", "Hemocrafter's"],

    EffectType.DmgBuffLegends: ["Titanic", "Doombringer's", "Fabled", "Mythic"],
    EffectType.DmgBuffPoisoned: ["Serpent's", "Corrosive", "Toxic", "Pestilent"],
    EffectType.DmgBuffBleeding: ["Sanguinary", "Bloodthirsty", "Macabre"],
    EffectType.DmgBuffFromDex: ["Quick", "Balanced", "Accurate", "Precise"],
    EffectType.DmgBuffFromInt: ["Knowing", "Brilliant", "Erudite's", "Acute"],
    EffectType.DmgBuffFromLck: ["Lucky", "Fated", "Prosperous", "Serendipitous"],

    EffectType.RestoreArmor: ["Repairing", "Restructuring", "Weavebonded", "Metalbonded", "Carapaced"],
    EffectType.RestorePercentArmor: ["Repairing", "Restructuring", "Weavebonded", "Metalbonded", "Carapaced"],
    EffectType.PiercingDmg: ["Eviscerating", "Piercing"],
    EffectType.PiercingPercentDmg: ["Eviscerating", "Piercing"],
    EffectType.SplashDmg: ["Giant", "Sweeping", "Quaking"],
    EffectType.SplashPercentMaxDmg: ["Giant", "Sweeping", "Quaking"],

    EffectType.CritDmgBuff: ["Honed", "Focused", "Critical"],
    EffectType.CritDmgReduction: ["Honed", "Focused", "Critical"],
    
    EffectType.HealthSteal: ["Vampiric", "Lifestealing", "Leeching", "Ichordrinking"],
    EffectType.ManaSteal: ["Lamprey's", "Manastealing", "Depleting"],
    EffectType.AdjustedCDs: ["Hastening", "Ephemeral", "Temporal"],

    EffectType.ChanceStatusEffect: {
        StatusEffectKey.Bleeding: ["Bloodletting", "Vicious", "Exsanguinating", "Hemorrhaging"],
        StatusEffectKey.Poisoned: ["Poisonous", "Virulent", "Toxic", "Septic", "Noxious"],
        StatusEffectKey.DmgReduction: ["Defensive", "Shielding", "Preserving"],
        StatusEffectKey.DmgVulnerability: ["Enervating", "Weakening", "Diminishing"],
        StatusEffectKey.FixedDmgTick: ["Singing", "Sparking", "Burning", "Quavering", "Intoning", "Murmuring", "Whispering"],
        StatusEffectKey.TurnSkipChance: ["Stunning", "Halting", "Breaking", "Hindering", "Impeding"],
        StatusEffectKey.Taunted: ["Taunting", "Provoking", "Tormenting", "Goading"],
        StatusEffectKey.CannotTarget: ["Ghostly", "Shifting", "Inconstant", "Flickering"],
        StatusEffectKey.Generating: ["Generating", "Lucrative", "Gainful", "Remunerative"],
        StatusEffectKey.Tarnished: ["Tarnished"],
        StatusEffectKey.ManaToHP: ["Sanguinating", "Vermillion", "Transmuting"],
        StatusEffectKey.PotionBuff: ["Alchemist's", "Hermetical"],
        StatusEffectKey.PoisonHeals: ["Transmuting", "Festering", "Greenclot"],
        StatusEffectKey.DmgBuff: ["Empowering", "Annihilating", "Jagged", "Brutal", "Deadly", "Savage"],
        StatusEffectKey.DmgDebuff: ["Withering", "Haggard"],
        StatusEffectKey.DmgReflect: ["Turtle's", "Reflecting", "Mirror's", "Returning", "Rebounding"],
        StatusEffectKey.Charmed: ["Charming", "Alluring", "Entrancing", "Captivating", "Hypnotizing", "Fair", "Beguiling", "Bewitching", "Fair"],
        StatusEffectKey.CannotAttack: ["Atrophying", "Deteriorating", "Wasting", "Waning", "Debilitating"],
        StatusEffectKey.Sleeping: ["Soporific", "Somiferous", "Lulling", "Slumberous", "Langorous"],
        StatusEffectKey.Decaying: ["Decaying", "Decomposing", "Moldering", "Spoiling", "Rotting"],
        StatusEffectKey.Undying: ["Immortal", "Deathless", "Eternal", "Everlasting", "Perpetual"],
        StatusEffectKey.CannotUseAbilities: ["Enfeebling", "Draining", "Torpefying"],
        StatusEffectKey.StackingDamage: ["Reverberating", "Accumulating", "Resonating"]
    },

    EffectType.ResistStatusEffect: {
        StatusEffectKey.Bleeding: ["Coagulating", "Clotting", "Cauterizing"],
        StatusEffectKey.Poisoned: ["Decontaminating", "Lustrating"],
        StatusEffectKey.DmgVulnerability: ["Resilient", "Formidable", "Tenacious"],
        StatusEffectKey.TurnSkipChance: ["Unwavering", "Steadfast", "Steady", "Unyielding"],
        StatusEffectKey.Taunted: ["Stoic", "Calm", "Impassive"],
        StatusEffectKey.CannotTarget: ["Focused", "Assiduous"],
        StatusEffectKey.DmgDebuff: ["Mighty", "Powerful", "Robust", "Ardent"],
        StatusEffectKey.Charmed: ["Calm", "Serene", "Composed", "Fair", "Equanimous"],
        StatusEffectKey.CannotAttack: ["Persistent", "Unabating", "Braced", "Rivited", "Even"],
        StatusEffectKey.Sleeping: ["Awoken", "Insomniac's"],
        StatusEffectKey.Decaying: ["Persistent", "Unabating", "Sheltering"]
    },

    EffectType.RestoreHealth: ["Restorative", "Rejuvenating"],
    EffectType.RestorePercentHealth: ["Restorative", "Rejuvenating"],
    EffectType.RestoreMana: ["Sorcerer's", "Occult", "Mystic"],
    EffectType.RestorePercentMana: ["Sorcerer's", "Occult", "Mystic"],

    EffectType.AdjustedManaCosts: ["Efficient", "Cryptic's", "Secret", "Cabalistic"],
    EffectType.HealingAbilityBuff: ["Healer's", "Alleviating", "Attenuated"],
    EffectType.AdditionalXP: ["Skillful", "Adept's"],
    EffectType.PotionMod: ["Alchemist's", "Hermetical", "Decocting"],

    EffectType.Damage: ["Harmful", "Vicious", "Mutilating", "Ruinous"],
    EffectType.ResurrectOnce: ["Phoenix's", "Reviving"]
}

BAD_PREFIXES: Dict[EffectType, List[str] | Dict[StatusEffectKey, List[str]]] = {
    EffectType.CleanseStatusEffects: [],

    EffectType.ConMod: ["Shattering", "Weakening", "Eroding"],
    EffectType.StrMod: ["Weakening", "Withering", "Debiliating", "Diminishing"],
    EffectType.DexMod: ["Slow", "Unbalanced", "Inaccurate"],
    EffectType.IntMod: ["Foolish", "Mindless", "Slow", "Vacuous", "Vapid", "Dull"],
    EffectType.LckMod: ["Unlucky", "Unfortunate", "Unfavorable", "Ill-Fated", "Luckless"],
    EffectType.MemMod: ["Forgetful", "Amnesic"],

    EffectType.DmgReflect: [],
    EffectType.DmgResist: [],
    EffectType.DmgBuff: [],
    EffectType.DmgBuffSelfMaxHealth: [],
    EffectType.DmgBuffSelfRemainingHealth: [],
    EffectType.DmgBuffOtherMaxHealth: [],
    EffectType.DmgBuffOtherRemainingHealth: [],

    EffectType.DmgBuffLegends: [],
    EffectType.DmgBuffPoisoned: [],
    EffectType.DmgBuffBleeding: [],
    EffectType.DmgBuffFromDex: [],
    EffectType.DmgBuffFromInt: [],
    EffectType.DmgBuffFromLck: [],

    EffectType.RestoreArmor: [],
    EffectType.RestorePercentArmor: [],
    EffectType.PiercingDmg: [],
    EffectType.PiercingPercentDmg: [],
    EffectType.SplashDmg: [],
    EffectType.SplashPercentMaxDmg: [],

    EffectType.CritDmgBuff: [],
    EffectType.CritDmgReduction: [],
    
    EffectType.HealthSteal: [],
    EffectType.ManaSteal: [],
    EffectType.AdjustedCDs: ["Confusing", "Perplexing"],

    EffectType.ChanceStatusEffect: {},

    EffectType.ResistStatusEffect: {},

    EffectType.RestoreHealth: [],
    EffectType.RestorePercentHealth: [],
    EffectType.RestoreMana: [],
    EffectType.RestorePercentMana: [],

    EffectType.AdjustedManaCosts: ["Inefficient", "Wasteful"],
    EffectType.HealingAbilityBuff: ["Decaying", "Decomposing", "Moldering", "Spoiling", "Rotting"],
    EffectType.AdditionalXP: ["Foolish", "Fool's", "Maddening"],
    EffectType.PotionMod: ["Ineffectual", "Impotent", "Powerless"],

    EffectType.Damage: [],
    EffectType.ResurrectOnce: []
}

# Each rarity will have a dict containing an enum value indicating the
# effect category. Each category will have a list of a list of two elements, 
# the first being the effect value range and the second being the effect
# value time.
# 
# Missing effects or missing item effect categories are assumed to be invalid
# combinations and should be skipped if randomly selected.
EFFECTS_BY_RARITY: Dict[Rarity, Dict[EffectType, Dict[ItemEffectCategory, List[List[List[float] | range]]] | Dict[StatusEffectKey, Dict[ItemEffectCategory, List[List[List[float] | range]]]]]] = {
    Rarity.Uncommon: {
        EffectType.CritDmgBuff: {
            ItemEffectCategory.Permanent: [[frange(0.05, 0.1, 0.025), range(-1, -1)]]
        },
        EffectType.CritDmgReduction: {
            ItemEffectCategory.Permanent: [[frange(0.05, 0.1, 0.025), range(-1, -1)]]
        },
        EffectType.ChanceStatusEffect: {
            StatusEffectKey.Bleeding: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.025, 0.05, 0.025), range(1, 2)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.025, 0.05, 0.025), range(1, 2)]],
                ItemEffectCategory.OnAttacked: [[frange(0.05, 0.075, 0.025), range(1, 2)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.05, 0.075, 0.025), range(1, 2)]],
                ItemEffectCategory.OnDamaged: [[frange(0.05, 0.075, 0.025), range(1, 2)]]
            },
            StatusEffectKey.Poisoned: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.025, 0.05, 0.025), range(1, 2)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.025, 0.05, 0.025), range(1, 2)]],
                ItemEffectCategory.OnAttacked: [[frange(0.05, 0.075, 0.025), range(1, 2)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.05, 0.075, 0.025), range(1, 2)]],
                ItemEffectCategory.OnDamaged: [[frange(0.05, 0.075, 0.025), range(1, 2)]]
            },
            StatusEffectKey.FixedDmgTick: {
                ItemEffectCategory.OnSuccessfulAttack: [[range(1, 2), range(1, 2)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(1, 2), range(1, 2)]],
                ItemEffectCategory.OnAttacked: [[range(1, 2), range(1, 2)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[range(1, 2), range(1, 2)]],
                ItemEffectCategory.OnDamaged: [[range(1, 2), range(1, 2)]]
            },
            StatusEffectKey.DmgBuff: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.05, 0.1, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.05, 0.1, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.05, 0.1, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.1, 0.15, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.1, 0.15, 0.025), range(1, 1)]]
            },
            StatusEffectKey.DmgDebuff: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.05, 0.1, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.05, 0.1, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.05, 0.1, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.1, 0.15, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.1, 0.15, 0.025), range(1, 1)]]
            },
            StatusEffectKey.Decaying: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.1, 0.2, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.1, 0.2, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.1, 0.2, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.1, 0.3, 0.05), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.1, 0.3, 0.05), range(1, 1)]]
            }
        },
        EffectType.HealingAbilityBuff: {
            ItemEffectCategory.Permanent: [[frange(0.1, 0.2, 0.05), range(-1, -1)]]
        },
        EffectType.PotionMod: {
            ItemEffectCategory.Permanent: [[frange(0.1, 0.2, 0.05), range(-1, -1)]]
        },
    },
    Rarity.Rare: {
        EffectType.CleanseStatusEffects: {
            ItemEffectCategory.OnAttacked: [[range(-1, -1), range(-1, -1)]],
            ItemEffectCategory.OnDamaged: [[range(-1, -1), range(-1, -1)]],
            ItemEffectCategory.OnTurnStart: [[range(-1, -1), range(-1, -1)]],
            ItemEffectCategory.OnTurnEnd: [[range(-1, -1), range(-1, -1)]],
        },

        EffectType.ConMod: {
            ItemEffectCategory.Permanent: [[range(1, 1), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAttack: [[range(1, 1), range(1, 2)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(1, 1), range(1, 2)]],
            ItemEffectCategory.OnAttacked: [[range(1, 1), range(1, 2)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[range(1, 1), range(1, 2)]],
            ItemEffectCategory.OnDamaged: [[range(1, 1), range(1, 2)]],
            ItemEffectCategory.OnTurnStart: [[range(1, 1), range(1, 2)]],
            ItemEffectCategory.OnTurnEnd: [[range(1, 1), range(1, 2)]]
        },
        EffectType.StrMod: {
            ItemEffectCategory.Permanent: [[range(1, 2), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAttack: [[range(1, 3), range(1, 2)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(1, 3), range(1, 2)]],
            ItemEffectCategory.OnAttacked: [[range(1, 3), range(1, 2)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[range(1, 3), range(1, 2)]],
            ItemEffectCategory.OnDamaged: [[range(1, 3), range(1, 2)]],
            ItemEffectCategory.OnTurnStart: [[range(1, 2), range(1, 2)]],
            ItemEffectCategory.OnTurnEnd: [[range(1, 2), range(1, 2)]]
        },
        EffectType.DexMod: {
            ItemEffectCategory.Permanent: [[range(1, 1), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAttack: [[range(1, 1), range(1, 2)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(1, 1), range(1, 2)]],
            ItemEffectCategory.OnAttacked: [[range(1, 1), range(1, 2)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[range(1, 1), range(1, 2)]],
            ItemEffectCategory.OnDamaged: [[range(1, 1), range(1, 2)]],
            ItemEffectCategory.OnTurnStart: [[range(1, 1), range(1, 2)]],
            ItemEffectCategory.OnTurnEnd: [[range(1, 1), range(1, 2)]]
        },
        EffectType.IntMod: {
            ItemEffectCategory.Permanent: [[range(1, 1), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAttack: [[range(1, 1), range(1, 2)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(1, 1), range(1, 2)]],
            ItemEffectCategory.OnAttacked: [[range(1, 1), range(1, 2)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[range(1, 1), range(1, 2)]],
            ItemEffectCategory.OnDamaged: [[range(1, 1), range(1, 2)]],
            ItemEffectCategory.OnTurnStart: [[range(1, 1), range(1, 2)]],
            ItemEffectCategory.OnTurnEnd: [[range(1, 1), range(1, 2)]]
        },
        EffectType.LckMod: {
            ItemEffectCategory.Permanent: [[range(1, 2), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAttack: [[range(1, 3), range(1, 2)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(1, 3), range(1, 2)]],
            ItemEffectCategory.OnAttacked: [[range(1, 3), range(1, 2)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[range(1, 3), range(1, 2)]],
            ItemEffectCategory.OnDamaged: [[range(1, 3), range(1, 2)]],
            ItemEffectCategory.OnTurnStart: [[range(1, 2), range(1, 2)]],
            ItemEffectCategory.OnTurnEnd: [[range(1, 2), range(1, 2)]]
        },
        EffectType.MemMod: {},

        EffectType.DmgReflect: {
            ItemEffectCategory.Permanent: [[frange(0.01, 0.05, 0.005), range(-1, -1)]]
        },
        EffectType.DmgResist: {
            ItemEffectCategory.Permanent: [[frange(0.01, 0.05, 0.005), range(-1, -1)]]
        },
        EffectType.DmgBuff: {
            ItemEffectCategory.Permanent: [[frange(0.05, 0.1, 0.01), range(-1, -1)]]
        },
        EffectType.DmgBuffSelfMaxHealth: {},
        EffectType.DmgBuffSelfRemainingHealth: {},
        EffectType.DmgBuffOtherMaxHealth: {},
        EffectType.DmgBuffOtherRemainingHealth: {},

        EffectType.DmgBuffLegends: {},
        EffectType.DmgBuffPoisoned: {
            ItemEffectCategory.Permanent: [[frange(0.05, 0.1, 0.01), range(-1, -1)]]
        },
        EffectType.DmgBuffBleeding: {
            ItemEffectCategory.Permanent: [[frange(0.05, 0.1, 0.01), range(-1, -1)]]
        },
        EffectType.DmgBuffFromDex: {},
        EffectType.DmgBuffFromInt: {},
        EffectType.DmgBuffFromLck: {
            ItemEffectCategory.Permanent: [[frange(0.025, 0.025, 0), range(-1, -1)]]
        },

        EffectType.RestoreArmor: {
            ItemEffectCategory.OnSuccessfulAttack: [[range(1, 2), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(1, 2), range(-1, -1)]],
            ItemEffectCategory.OnAttacked: [[range(1, 2), range(-1, -1)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[range(1, 2), range(-1, -1)]],
            ItemEffectCategory.OnDamaged: [[range(1, 4), range(-1, -1)]],
            ItemEffectCategory.OnTurnStart: [[range(1, 1), range(-1, -1)]],
            ItemEffectCategory.OnTurnEnd: [[range(1, 1), range(-1, -1)]]
        },
        EffectType.RestorePercentArmor: {
            ItemEffectCategory.OnSuccessfulAttack: [[frange(0.01, 0.02, 0.005), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.01, 0.02, 0.005), range(-1, -1)]],
            ItemEffectCategory.OnAttacked: [[frange(0.01, 0.02, 0.005), range(-1, -1)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.01, 0.02, 0.005), range(-1, -1)]],
            ItemEffectCategory.OnDamaged: [[frange(0.01, 0.03, 0.005), range(-1, -1)]],
            ItemEffectCategory.OnTurnStart: [[frange(0.01, 0.01, 0), range(-1, -1)]],
            ItemEffectCategory.OnTurnEnd: [[frange(0.01, 0.01, 0), range(-1, -1)]]
        },
        EffectType.PiercingDmg: {
            ItemEffectCategory.Permanent: [[range(1, 5), range(-1, -1)]]
        },
        EffectType.PiercingPercentDmg: {
            ItemEffectCategory.Permanent: [[frange(0.1, 0.25, 0.05), range(-1, -1)]]
        },
        EffectType.SplashDmg: {
            ItemEffectCategory.Permanent: [[range(1, 5), range(-1, -1)]]
        },
        EffectType.SplashPercentMaxDmg: {
            ItemEffectCategory.Permanent: [[frange(0.1, 0.15, 0.025), range(-1, -1)]]
        },

        EffectType.CritDmgBuff: {
            ItemEffectCategory.Permanent: [[frange(0.1, 0.15, 0.025), range(-1, -1)]]
        },
        EffectType.CritDmgReduction: {
            ItemEffectCategory.Permanent: [[frange(0.1, 0.15, 0.025), range(-1, -1)]]
        },
        
        EffectType.HealthSteal: {},
        EffectType.ManaSteal: {},
        EffectType.AdjustedCDs: {},

        EffectType.ChanceStatusEffect: {
            StatusEffectKey.Bleeding: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.05, 0.1, 0.025), range(2, 3)], [frange(0.1, 0.15, 0.025), range(1, 2)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.05, 0.1, 0.025), range(2, 3)], [frange(0.1, 0.15, 0.025), range(1, 2)]],
                ItemEffectCategory.OnAttacked: [[frange(0.075, 0.125, 0.025), range(2, 3)], [frange(0.1, 0.15, 0.025), range(1, 2)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.075, 0.125, 0.025), range(2, 3)], [frange(0.1, 0.15, 0.025), range(1, 2)]],
                ItemEffectCategory.OnDamaged: [[frange(0.01, 0.15, 0.025), range(2, 3)], [frange(0.125, 0.2, 0.025), range(1, 2)]]
            },
            StatusEffectKey.Poisoned: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.05, 0.1, 0.025), range(2, 3)], [frange(0.1, 0.15, 0.025), range(1, 2)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.05, 0.1, 0.025), range(2, 3)], [frange(0.1, 0.15, 0.025), range(1, 2)]],
                ItemEffectCategory.OnAttacked: [[frange(0.075, 0.125, 0.025), range(2, 3)], [frange(0.1, 0.15, 0.025), range(1, 2)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.075, 0.125, 0.025), range(2, 3)], [frange(0.1, 0.15, 0.025), range(1, 2)]],
                ItemEffectCategory.OnDamaged: [[frange(0.01, 0.15, 0.025), range(2, 3)], [frange(0.125, 0.2, 0.025), range(1, 2)]]
            },
            StatusEffectKey.DmgReduction: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.01, 0.05, 0.01), range(1, 2)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.01, 0.05, 0.01), range(1, 2)]],
                ItemEffectCategory.OnAttacked: [[frange(0.025, 0.075, 0.025), range(1, 2)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.025, 0.075, 0.025), range(1, 2)]],
                ItemEffectCategory.OnDamaged: [[frange(0.05, 0.1, 0.05), range(1, 2)]]
            },
            StatusEffectKey.DmgVulnerability: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.01, 0.05, 0.01), range(1, 2)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.01, 0.05, 0.01), range(1, 2)]],
                ItemEffectCategory.OnAttacked: [[frange(0.025, 0.075, 0.025), range(1, 2)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.025, 0.075, 0.025), range(1, 2)]],
                ItemEffectCategory.OnDamaged: [[frange(0.05, 0.1, 0.05), range(1, 2)]]
            },
            StatusEffectKey.FixedDmgTick: {
                ItemEffectCategory.OnSuccessfulAttack: [[range(1, 2), range(3, 4)], [range(3, 4), range(1, 2)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(1, 2), range(3, 4)], [range(3, 4), range(1, 2)]],
                ItemEffectCategory.OnAttacked: [[range(1, 2), range(3, 4)], [range(3, 4), range(1, 2)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[range(1, 2), range(3, 4)], [range(3, 4), range(1, 2)]],
                ItemEffectCategory.OnDamaged: [[range(1, 2), range(3, 4)], [range(3, 4), range(1, 2)]]
            },
            StatusEffectKey.TurnSkipChance: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.025, 0.05, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.025, 0.05, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.025, 0.05, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.025, 0.05, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.025, 0.05, 0.025), range(1, 1)]]
            },
            StatusEffectKey.Taunted: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.05, 0.1, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.05, 0.1, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.1, 0.15, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.1, 0.15, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.1, 0.15, 0.025), range(1, 1)]]
            },
            StatusEffectKey.CannotTarget: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.05, 0.1, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.05, 0.1, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.1, 0.15, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.1, 0.15, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.1, 0.15, 0.025), range(1, 1)]]
            },
            StatusEffectKey.Generating: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.05, 0.1, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.05, 0.1, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.1, 0.15, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.1, 0.15, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.1, 0.15, 0.025), range(1, 1)]],
                ItemEffectCategory.OnTurnStart: [[frange(0.05, 0.1, 0.025), range(1, 1)]],
                ItemEffectCategory.OnTurnEnd: [[frange(0.05, 0.1, 0.025), range(1, 1)]]
            },
            StatusEffectKey.Tarnished: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.05, 0.1, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.05, 0.1, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.1, 0.15, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.1, 0.15, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.1, 0.15, 0.025), range(1, 1)]],
                ItemEffectCategory.OnTurnStart: [[frange(0.05, 0.1, 0.025), range(1, 1)]],
                ItemEffectCategory.OnTurnEnd: [[frange(0.05, 0.1, 0.025), range(1, 1)]]
            },
            StatusEffectKey.DmgBuff: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.2, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.2, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.25, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.25, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.25, 0.025), range(1, 1)]]
            },
            StatusEffectKey.DmgDebuff: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.2, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.2, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.25, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.25, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.25, 0.025), range(1, 1)]]
            },
            StatusEffectKey.Charmed: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.05, 0.1, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.05, 0.1, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.1, 0.15, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.1, 0.15, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.1, 0.15, 0.025), range(1, 1)]]
            },
            StatusEffectKey.CannotAttack: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.2, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.2, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.25, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.25, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.25, 0.025), range(1, 1)]]
            },
            StatusEffectKey.Sleeping: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.2, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.2, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.25, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.25, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.25, 0.025), range(1, 1)]]
            },
            StatusEffectKey.Decaying: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.25, 0.3, 0.025), range(2, 2)], [frange(0.35, 0.4, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.25, 0.3, 0.025), range(2, 2)], [frange(0.35, 0.4, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.3, 0.35, 0.025), range(2, 2)], [frange(0.4, 0.45, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.3, 0.35, 0.025), range(2, 2)], [frange(0.4, 0.45, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.3, 0.35, 0.025), range(2, 2)], [frange(0.4, 0.45, 0.025), range(1, 1)]]
            },
            StatusEffectKey.Undying: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.025, 0.05, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.025, 0.05, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.025, 0.05, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.025, 0.05, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.025, 0.05, 0.025), range(1, 1)]]
            },
            StatusEffectKey.CannotUseAbilities: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.2, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.2, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.25, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.25, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.25, 0.025), range(1, 1)]]
            },
            StatusEffectKey.StackingDamage: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.25, 0.3, 0.025), range(2, 2)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.25, 0.3, 0.025), range(2, 2)]]
            }
        },

        EffectType.ResistStatusEffect: {
            StatusEffectKey.Bleeding: {
                ItemEffectCategory.Permanent: [[frange(0.1, 0.2, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.Poisoned: {
                ItemEffectCategory.Permanent: [[frange(0.1, 0.2, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.DmgVulnerability: {
                ItemEffectCategory.Permanent: [[frange(0.1, 0.2, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.TurnSkipChance: {
                ItemEffectCategory.Permanent: [[frange(0.1, 0.2, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.Taunted: {
                ItemEffectCategory.Permanent: [[frange(0.1, 0.2, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.CannotTarget: {
                ItemEffectCategory.Permanent: [[frange(0.1, 0.2, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.DmgDebuff: {
                ItemEffectCategory.Permanent: [[frange(0.1, 0.2, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.Charmed: {
                ItemEffectCategory.Permanent: [[frange(0.1, 0.2, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.CannotAttack: {
                ItemEffectCategory.Permanent: [[frange(0.1, 0.2, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.Sleeping: {
                ItemEffectCategory.Permanent: [[frange(0.1, 0.2, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.Decaying: {
                ItemEffectCategory.Permanent: [[frange(0.1, 0.2, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.CannotUseAbilities: {
                ItemEffectCategory.Permanent: [[frange(0.1, 0.2, 0.05), range(-1, -1)]]
            }
        },

        EffectType.RestoreHealth: {
            ItemEffectCategory.OnSuccessfulAttack: [[range(1, 2), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(1, 2), range(-1, -1)]],
            ItemEffectCategory.OnAttacked: [[range(1, 2), range(-1, -1)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[range(1, 2), range(-1, -1)]],
            ItemEffectCategory.OnDamaged: [[range(1, 3), range(-1, -1)]],
            ItemEffectCategory.OnTurnStart: [[range(1, 1), range(-1, -1)]],
            ItemEffectCategory.OnTurnEnd: [[range(1, 1), range(-1, -1)]]
        },
        EffectType.RestorePercentHealth: {
            ItemEffectCategory.OnSuccessfulAttack: [[frange(0.01, 0.03, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.01, 0.03, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnAttacked: [[frange(0.01, 0.04, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.01, 0.03, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnDamaged: [[frange(0.01, 0.03, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnTurnStart: [[frange(0.01, 0.01, 0), range(-1, -1)]],
            ItemEffectCategory.OnTurnEnd: [[frange(0.01, 0.01, 0), range(-1, -1)]]
        },
        EffectType.RestoreMana: {
            ItemEffectCategory.OnSuccessfulAttack: [[range(1, 2), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(1, 2), range(-1, -1)]],
            ItemEffectCategory.OnAttacked: [[range(1, 2), range(-1, -1)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[range(1, 2), range(-1, -1)]],
            ItemEffectCategory.OnDamaged: [[range(1, 3), range(-1, -1)]],
            ItemEffectCategory.OnTurnStart: [[range(1, 1), range(-1, -1)]],
            ItemEffectCategory.OnTurnEnd: [[range(1, 1), range(-1, -1)]]
        },
        EffectType.RestorePercentMana: {
            ItemEffectCategory.OnSuccessfulAttack: [[frange(0.01, 0.03, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.01, 0.03, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnAttacked: [[frange(0.01, 0.04, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.01, 0.03, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnDamaged: [[frange(0.01, 0.03, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnTurnStart: [[frange(0.01, 0.01, 0), range(-1, -1)]],
            ItemEffectCategory.OnTurnEnd: [[frange(0.01, 0.01, 0), range(-1, -1)]]
        },

        EffectType.AdjustedManaCosts: {},
        EffectType.HealingAbilityBuff: {
            ItemEffectCategory.Permanent: [[frange(0.2, 0.3, 0.05), range(-1, -1)]]
        },
        EffectType.AdditionalXP: {
            ItemEffectCategory.Permanent: [[frange(0.25, 0.45, 0.05), range(-1, -1)]]
        },
        EffectType.PotionMod: {
            ItemEffectCategory.Permanent: [[frange(0.2, 0.3, 0.05), range(-1, -1)]]
        },

        EffectType.Damage: {
            ItemEffectCategory.OnSuccessfulAttack: [[range(1, 3), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(1, 3), range(-1, -1)]],
            ItemEffectCategory.OnAttacked: [[range(1, 3), range(-1, -1)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[range(1, 3), range(-1, -1)]],
            ItemEffectCategory.OnDamaged: [[range(1, 5), range(-1, -1)]]
        },
        EffectType.ResurrectOnce: {}
    },
    Rarity.Epic: {
        EffectType.CleanseStatusEffects: {
            ItemEffectCategory.OnAttacked: [[range(-1, -1), range(-1, -1)]],
            ItemEffectCategory.OnDamaged: [[range(-1, -1), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAttack: [[range(-1, -1), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(-1, -1), range(-1, -1)]],
            ItemEffectCategory.OnTurnStart: [[range(-1, -1), range(-1, -1)]],
            ItemEffectCategory.OnTurnEnd: [[range(-1, -1), range(-1, -1)]],
        },

        EffectType.ConMod: {
            ItemEffectCategory.Permanent: [[range(2, 2), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAttack: [[range(1, 1), range(3, 4)], [range(2, 2), range(1, 2)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(1, 1), range(3, 4)], [range(2, 2), range(1, 2)]],
            ItemEffectCategory.OnAttacked: [[range(1, 1), range(3, 4)], [range(2, 2), range(1, 2)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[range(1, 1), range(3, 4)], [range(2, 2), range(1, 2)]],
            ItemEffectCategory.OnDamaged: [[range(1, 1), range(3, 4)], [range(2, 2), range(1, 2)]],
            ItemEffectCategory.OnTurnStart: [[range(1, 1), range(2, 3)]],
            ItemEffectCategory.OnTurnEnd: [[range(1, 1), range(2, 3)]]
        },
        EffectType.StrMod: {
            ItemEffectCategory.Permanent: [[range(3, 4), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAttack: [[range(1, 3), range(3, 4)], [range(4, 6), range(1, 2)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(1, 3), range(3, 4)], [range(4, 6), range(1, 2)]],
            ItemEffectCategory.OnAttacked: [[range(1, 3), range(3, 4)], [range(4, 6), range(1, 2)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[range(1, 3), range(3, 4)], [range(4, 6), range(1, 2)]],
            ItemEffectCategory.OnDamaged: [[range(1, 3), range(3, 4)], [range(4, 6), range(1, 2)]],
            ItemEffectCategory.OnTurnStart: [[range(1, 2), range(2, 3)]],
            ItemEffectCategory.OnTurnEnd: [[range(1, 2), range(2, 3)]]
        },
        EffectType.DexMod: {
            ItemEffectCategory.Permanent: [[range(2, 2), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAttack: [[range(1, 1), range(3, 4)], [range(2, 2), range(1, 2)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(1, 1), range(3, 4)], [range(2, 2), range(1, 2)]],
            ItemEffectCategory.OnAttacked: [[range(1, 1), range(3, 4)], [range(2, 2), range(1, 2)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[range(1, 1), range(3, 4)], [range(2, 2), range(1, 2)]],
            ItemEffectCategory.OnDamaged: [[range(1, 1), range(3, 4)], [range(2, 2), range(1, 2)]],
            ItemEffectCategory.OnTurnStart: [[range(1, 1), range(2, 3)]],
            ItemEffectCategory.OnTurnEnd: [[range(1, 1), range(2, 3)]]
        },
        EffectType.IntMod: {
            ItemEffectCategory.Permanent: [[range(2, 2), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAttack: [[range(1, 1), range(3, 4)], [range(2, 2), range(1, 2)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(1, 1), range(3, 4)], [range(2, 2), range(1, 2)]],
            ItemEffectCategory.OnAttacked: [[range(1, 1), range(3, 4)], [range(2, 2), range(1, 2)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[range(1, 1), range(3, 4)], [range(2, 2), range(1, 2)]],
            ItemEffectCategory.OnDamaged: [[range(1, 1), range(3, 4)], [range(2, 2), range(1, 2)]],
            ItemEffectCategory.OnTurnStart: [[range(1, 1), range(2, 3)]],
            ItemEffectCategory.OnTurnEnd: [[range(1, 1), range(2, 3)]]
        },
        EffectType.LckMod: {
            ItemEffectCategory.Permanent: [[range(3, 4), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAttack: [[range(1, 3), range(3, 4)], [range(4, 6), range(1, 2)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(1, 3), range(3, 4)], [range(4, 6), range(1, 2)]],
            ItemEffectCategory.OnAttacked: [[range(1, 3), range(3, 4)], [range(4, 6), range(1, 2)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[range(1, 3), range(3, 4)], [range(4, 6), range(1, 2)]],
            ItemEffectCategory.OnDamaged: [[range(1, 3), range(3, 4)], [range(4, 6), range(1, 2)]],
            ItemEffectCategory.OnTurnStart: [[range(1, 2), range(2, 3)]],
            ItemEffectCategory.OnTurnEnd: [[range(1, 2), range(2, 3)]]
        },
        EffectType.MemMod: {
            ItemEffectCategory.Permanent: [[range(1, 1), range(-1, -1)]],
        },

        EffectType.DmgReflect: {
            ItemEffectCategory.Permanent: [[frange(0.05, 0.075, 0.005), range(-1, -1)]]
        },
        EffectType.DmgResist: {
            ItemEffectCategory.Permanent: [[frange(0.05, 0.075, 0.005), range(-1, -1)]]
        },
        EffectType.DmgBuff: {
            ItemEffectCategory.Permanent: [[frange(0.1, 0.15, 0.01), range(-1, -1)]]
        },
        EffectType.DmgBuffSelfMaxHealth: {
            ItemEffectCategory.Permanent: [[frange(0.01, 0.01, 0), range(-1, -1)]]
        },
        EffectType.DmgBuffSelfRemainingHealth: {
            ItemEffectCategory.Permanent: [[frange(0.01, 0.01, 0), range(-1, -1)]]
        },
        EffectType.DmgBuffOtherMaxHealth: {
            ItemEffectCategory.Permanent: [[frange(0.01, 0.01, 0), range(-1, -1)]]
        },
        EffectType.DmgBuffOtherRemainingHealth: {
            ItemEffectCategory.Permanent: [[frange(0.01, 0.01, 0), range(-1, -1)]]
        },

        EffectType.DmgBuffLegends: {
            ItemEffectCategory.Permanent: [[frange(0.1, 0.15, 0.01), range(-1, -1)]]
        },
        EffectType.DmgBuffPoisoned: {
            ItemEffectCategory.Permanent: [[frange(0.1, 0.15, 0.01), range(-1, -1)]]
        },
        EffectType.DmgBuffBleeding: {
            ItemEffectCategory.Permanent: [[frange(0.1, 0.15, 0.01), range(-1, -1)]]
        },
        EffectType.DmgBuffFromDex: {
            ItemEffectCategory.Permanent: [[frange(0.025, 0.025, 0), range(-1, -1)]]
        },
        EffectType.DmgBuffFromInt: {
            ItemEffectCategory.Permanent: [[frange(0.025, 0.025, 0), range(-1, -1)]]
        },
        EffectType.DmgBuffFromLck: {
            ItemEffectCategory.Permanent: [[frange(0.025, 0.025, 0), range(-1, -1)]]
        },

        EffectType.RestoreArmor: {
            ItemEffectCategory.OnSuccessfulAttack: [[range(3, 4), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(3, 4), range(-1, -1)]],
            ItemEffectCategory.OnAttacked: [[range(3, 4), range(-1, -1)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[range(3, 4), range(-1, -1)]],
            ItemEffectCategory.OnDamaged: [[range(5, 9), range(-1, -1)]],
            ItemEffectCategory.OnTurnStart: [[range(2, 2), range(-1, -1)]],
            ItemEffectCategory.OnTurnEnd: [[range(2, 2), range(-1, -1)]]
        },
        EffectType.RestorePercentArmor: {
            ItemEffectCategory.OnSuccessfulAttack: [[frange(0.03, 0.04, 0.005), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.03, 0.04, 0.005), range(-1, -1)]],
            ItemEffectCategory.OnAttacked: [[frange(0.03, 0.04, 0.005), range(-1, -1)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.03, 0.04, 0.005), range(-1, -1)]],
            ItemEffectCategory.OnDamaged: [[frange(0.04, 0.06, 0.005), range(-1, -1)]],
            ItemEffectCategory.OnTurnStart: [[frange(0.02, 0.02, 0), range(-1, -1)]],
            ItemEffectCategory.OnTurnEnd: [[frange(0.02, 0.02, 0), range(-1, -1)]]
        },
        EffectType.PiercingDmg: {
            ItemEffectCategory.Permanent: [[range(3, 8), range(-1, -1)]]
        },
        EffectType.PiercingPercentDmg: {
            ItemEffectCategory.Permanent: [[frange(0.3, 0.4, 0.05), range(-1, -1)]]
        },
        EffectType.SplashDmg: {
            ItemEffectCategory.Permanent: [[range(3, 8), range(-1, -1)]]
        },
        EffectType.SplashPercentMaxDmg: {
            ItemEffectCategory.Permanent: [[frange(0.15, 0.2, 0.025), range(-1, -1)]]
        },

        EffectType.CritDmgBuff: {
            ItemEffectCategory.Permanent: [[frange(0.15, 0.2, 0.05), range(-1, -1)]]
        },
        EffectType.CritDmgReduction: {
            ItemEffectCategory.Permanent: [[frange(0.15, 0.2, 0.05), range(-1, -1)]]
        },
        
        EffectType.HealthSteal: {
            ItemEffectCategory.OnSuccessfulAttack: [[frange(0.01, 0.02, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.01, 0.02, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnAttacked: [[frange(0.01, 0.03, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.01, 0.03, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnDamaged: [[frange(0.01, 0.03, 0.01), range(-1, -1)]]
        },
        EffectType.ManaSteal: {
            ItemEffectCategory.OnSuccessfulAttack: [[frange(0.01, 0.02, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.01, 0.02, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnAttacked: [[frange(0.01, 0.03, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.01, 0.03, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnDamaged: [[frange(0.01, 0.03, 0.01), range(-1, -1)]]
        },
        EffectType.AdjustedCDs: {},

        EffectType.ChanceStatusEffect: {
            StatusEffectKey.Bleeding: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.15, 0.2, 0.025), range(2, 3)], [frange(0.2, 0.25, 0.025), range(1, 2)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.15, 0.2, 0.025), range(2, 3)], [frange(0.2, 0.25, 0.025), range(1, 2)]],
                ItemEffectCategory.OnAttacked: [[frange(0.15, 0.2, 0.025), range(2, 3)], [frange(0.2, 0.25, 0.025), range(1, 2)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.15, 0.2, 0.025), range(2, 3)], [frange(0.2, 0.25, 0.025), range(1, 2)]],
                ItemEffectCategory.OnDamaged: [[frange(0.2, 0.25, 0.025), range(2, 3)], [frange(0.25, 0.3, 0.025), range(1, 2)]]
            },
            StatusEffectKey.Poisoned: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.15, 0.2, 0.025), range(2, 3)], [frange(0.2, 0.25, 0.025), range(1, 2)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.15, 0.2, 0.025), range(2, 3)], [frange(0.2, 0.25, 0.025), range(1, 2)]],
                ItemEffectCategory.OnAttacked: [[frange(0.15, 0.2, 0.025), range(2, 3)], [frange(0.2, 0.25, 0.025), range(1, 2)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.15, 0.2, 0.025), range(2, 3)], [frange(0.2, 0.25, 0.025), range(1, 2)]],
                ItemEffectCategory.OnDamaged: [[frange(0.2, 0.25, 0.025), range(2, 3)], [frange(0.25, 0.3, 0.025), range(1, 2)]]
            },
            StatusEffectKey.DmgReduction: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.05, 0.075, 0.025), range(2, 3)], [frange(0.1, 0.15, 0.025), range(1, 2)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.05, 0.075, 0.025), range(2, 3)], [frange(0.1, 0.15, 0.025), range(1, 2)]],
                ItemEffectCategory.OnAttacked: [[frange(0.075, 0.1, 0.025), range(2, 3)], [frange(0.1, 0.2, 0.05), range(1, 2)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.075, 0.1, 0.025), range(2, 3)], [frange(0.1, 0.2, 0.05), range(1, 2)]],
                ItemEffectCategory.OnDamaged: [[frange(0.075, 0.1, 0.025), range(2, 3)], [frange(0.1, 0.2, 0.05), range(1, 2)]]
            },
            StatusEffectKey.DmgVulnerability: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.05, 0.075, 0.025), range(2, 3)], [frange(0.1, 0.15, 0.025), range(1, 2)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.05, 0.075, 0.025), range(2, 3)], [frange(0.1, 0.15, 0.025), range(1, 2)]],
                ItemEffectCategory.OnAttacked: [[frange(0.075, 0.1, 0.025), range(2, 3)], [frange(0.1, 0.2, 0.05), range(1, 2)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.075, 0.01, 0.025), range(2, 3)], [frange(0.1, 0.2, 0.05), range(1, 2)]],
                ItemEffectCategory.OnDamaged: [[frange(0.075, 0.01, 0.025), range(2, 3)], [frange(0.1, 0.2, 0.05), range(1, 2)]]
            },
            StatusEffectKey.FixedDmgTick: {
                ItemEffectCategory.OnSuccessfulAttack: [[range(3, 4), range(3, 4)], [range(5, 6), range(1, 2)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(3, 4), range(3, 4)], [range(5, 6), range(1, 2)]],
                ItemEffectCategory.OnAttacked: [[range(3, 4), range(3, 4)], [range(5, 6), range(1, 2)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[range(3, 4), range(3, 4)], [range(5, 6), range(1, 2)]],
                ItemEffectCategory.OnDamaged: [[range(3, 4), range(3, 4)], [range(5, 6), range(1, 2)]]
            },
            StatusEffectKey.TurnSkipChance: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.025, 0.05, 0.025), range(2, 2)], [frange(0.05, 0.075, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.025, 0.05, 0.025), range(2, 2)], [frange(0.05, 0.075, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.05, 0.075, 0.025), range(2, 2)], [frange(0.075, 0.1, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.05, 0.075, 0.025), range(2, 2)], [frange(0.075, 0.1, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.05, 0.075, 0.025), range(2, 2)], [frange(0.075, 0.1, 0.025), range(1, 1)]]
            },
            StatusEffectKey.Taunted: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.05, 0.1, 0.025), range(2, 2)], [frange(0.1, 0.15, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.05, 0.1, 0.025), range(2, 2)], [frange(0.1, 0.15, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.2, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.2, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.2, 0.025), range(1, 1)]]
            },
            StatusEffectKey.CannotTarget: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.05, 0.1, 0.025), range(2, 2)], [frange(0.1, 0.15, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.05, 0.1, 0.025), range(2, 2)], [frange(0.1, 0.15, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.2, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.2, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.2, 0.025), range(1, 1)]]
            },
            StatusEffectKey.Generating: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.05, 0.1, 0.025), range(2, 2)], [frange(0.1, 0.15, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.05, 0.1, 0.025), range(2, 2)], [frange(0.1, 0.15, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.2, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.2, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.2, 0.025), range(1, 1)]],
                ItemEffectCategory.OnTurnStart: [[frange(0.05, 0.1, 0.025), range(2, 2)], [frange(0.1, 0.15, 0.025), range(1, 1)]],
                ItemEffectCategory.OnTurnEnd: [[frange(0.05, 0.1, 0.025), range(2, 2)], [frange(0.1, 0.15, 0.025), range(1, 1)]]
            },
            StatusEffectKey.Tarnished: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.05, 0.1, 0.025), range(2, 2)], [frange(0.1, 0.15, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.05, 0.1, 0.025), range(2, 2)], [frange(0.1, 0.15, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.2, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.2, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.2, 0.025), range(1, 1)]],
                ItemEffectCategory.OnTurnStart: [[frange(0.05, 0.1, 0.025), range(2, 2)], [frange(0.1, 0.15, 0.025), range(1, 1)]],
                ItemEffectCategory.OnTurnEnd: [[frange(0.05, 0.1, 0.025), range(2, 2)], [frange(0.1, 0.15, 0.025), range(1, 1)]]
            },
            StatusEffectKey.ManaToHP: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.15, 0.25, 0.05), range(2, 2)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.15, 0.25, 0.05), range(2, 2)]],
                ItemEffectCategory.OnAttacked: [[frange(0.15, 0.25, 0.05), range(2, 2)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.15, 0.25, 0.05), range(2, 2)]],
                ItemEffectCategory.OnDamaged: [[frange(0.15, 0.25, 0.05), range(2, 2)]]
            },
            StatusEffectKey.PoisonHeals: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.15, 0.25, 0.05), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.15, 0.25, 0.05), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.15, 0.25, 0.05), range(1, 2)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.15, 0.25, 0.05), range(1, 2)]],
                ItemEffectCategory.OnDamaged: [[frange(0.15, 0.25, 0.05), range(1, 2)]]
            },
            StatusEffectKey.DmgBuff: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.2, 0.25, 0.025), range(2, 2)], [frange(0.25, 0.3, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed:[[frange(0.2, 0.25, 0.025), range(2, 2)], [frange(0.25, 0.3, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.25, 0.3, 0.025), range(2, 2)], [frange(0.3, 0.35, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.25, 0.3, 0.025), range(2, 2)], [frange(0.3, 0.35, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.25, 0.3, 0.025), range(2, 2)], [frange(0.3, 0.35, 0.025), range(1, 1)]]
            },
            StatusEffectKey.DmgDebuff: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.2, 0.25, 0.025), range(2, 2)], [frange(0.25, 0.3, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed:[[frange(0.2, 0.25, 0.025), range(2, 2)], [frange(0.25, 0.3, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.25, 0.3, 0.025), range(2, 2)], [frange(0.3, 0.35, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.25, 0.3, 0.025), range(2, 2)], [frange(0.3, 0.35, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.25, 0.3, 0.025), range(2, 2)], [frange(0.3, 0.35, 0.025), range(1, 1)]]
            },
            StatusEffectKey.Charmed: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.05, 0.1, 0.025), range(2, 2)], [frange(0.075, 0.125, 0.025), range(2, 2)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.05, 0.1, 0.025), range(2, 2)], [frange(0.075, 0.125, 0.025), range(2, 2)]],
                ItemEffectCategory.OnAttacked: [[frange(0.1, 0.125, 0.025), range(2, 2)], [frange(0.125, 0.5, 0.025), range(2, 2)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.1, 0.125, 0.025), range(2, 2)], [frange(0.125, 0.5, 0.025), range(2, 2)]],
                ItemEffectCategory.OnDamaged: [[frange(0.1, 0.125, 0.025), range(2, 2)], [frange(0.125, 0.5, 0.025), range(2, 2)]]
            },
            StatusEffectKey.CannotAttack: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.2, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.2, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.3, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.3, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.3, 0.025), range(1, 1)]]
            },
            StatusEffectKey.Sleeping: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.2, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.2, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.3, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.3, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.3, 0.025), range(1, 1)]]
            },
            StatusEffectKey.Decaying: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.3, 0.35, 0.025), range(2, 2)], [frange(0.4, 0.45, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.3, 0.35, 0.025), range(2, 2)], [frange(0.4, 0.45, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.35, 0.4, 0.025), range(2, 2)], [frange(0.45, 0.5, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.35, 0.4, 0.025), range(2, 2)], [frange(0.45, 0.5, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.35, 0.4, 0.025), range(2, 2)], [frange(0.45, 0.5, 0.025), range(1, 1)]]
            },
            StatusEffectKey.Undying: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.025, 0.05, 0.025), range(1, 2), frange(0.05, 0.075, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.025, 0.05, 0.025), range(1, 2), frange(0.05, 0.075, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.05, 0.075, 0.025), range(1, 2), frange(0.075, 0.125, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.05, 0.075, 0.025), range(1, 2), frange(0.075, 0.125, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.05, 0.075, 0.025), range(1, 2), frange(0.075, 0.125, 0.025), range(1, 1)]]
            },
            StatusEffectKey.CannotUseAbilities: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.2, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.2, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.3, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.3, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.3, 0.025), range(1, 1)]]
            },
            StatusEffectKey.StackingDamage: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.25, 0.3, 0.025), range(3, 3)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.35, 0.4, 0.025), range(2, 2)]]
            }
        },

        EffectType.ResistStatusEffect: {
            StatusEffectKey.Bleeding: {
                ItemEffectCategory.Permanent: [[frange(0.2, 0.3, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.Poisoned: {
                ItemEffectCategory.Permanent: [[frange(0.2, 0.3, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.DmgVulnerability: {
                ItemEffectCategory.Permanent: [[frange(0.2, 0.3, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.TurnSkipChance: {
                ItemEffectCategory.Permanent: [[frange(0.2, 0.3, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.Taunted: {
                ItemEffectCategory.Permanent: [[frange(0.2, 0.3, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.CannotTarget: {
                ItemEffectCategory.Permanent: [[frange(0.2, 0.3, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.DmgDebuff: {
                ItemEffectCategory.Permanent: [[frange(0.2, 0.3, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.Charmed: {
                ItemEffectCategory.Permanent: [[frange(0.2, 0.3, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.CannotAttack: {
                ItemEffectCategory.Permanent: [[frange(0.2, 0.3, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.Sleeping: {
                ItemEffectCategory.Permanent: [[frange(0.2, 0.3, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.Decaying: {
                ItemEffectCategory.Permanent: [[frange(0.2, 0.3, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.CannotUseAbilities: {
                ItemEffectCategory.Permanent: [[frange(0.2, 0.3, 0.05), range(-1, -1)]]
            }
        },

        EffectType.RestoreHealth: {
            ItemEffectCategory.OnSuccessfulAttack: [[range(3, 4), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(3, 4), range(-1, -1)]],
            ItemEffectCategory.OnAttacked: [[range(3, 4), range(-1, -1)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[range(3, 4), range(-1, -1)]],
            ItemEffectCategory.OnDamaged: [[range(4, 6), range(-1, -1)]],
            ItemEffectCategory.OnTurnStart: [[range(1, 2), range(-1, -1)]],
            ItemEffectCategory.OnTurnEnd: [[range(1, 2), range(-1, -1)]]
        },
        EffectType.RestorePercentHealth: {
            ItemEffectCategory.OnSuccessfulAttack: [[frange(0.03, 0.04, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.03, 0.04, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnAttacked: [[frange(0.03, 0.04, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.03, 0.04, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnDamaged: [[frange(0.04, 0.06, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnTurnStart: [[frange(0.01, 0.02, 0), range(-1, -1)]],
            ItemEffectCategory.OnTurnEnd: [[frange(0.01, 0.02, 0), range(-1, -1)]]
        },
        EffectType.RestoreMana: {
            ItemEffectCategory.OnSuccessfulAttack: [[range(3, 4), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(3, 4), range(-1, -1)]],
            ItemEffectCategory.OnAttacked: [[range(3, 4), range(-1, -1)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[range(3, 4), range(-1, -1)]],
            ItemEffectCategory.OnDamaged: [[range(4, 6), range(-1, -1)]],
            ItemEffectCategory.OnTurnStart: [[range(1, 2), range(-1, -1)]],
            ItemEffectCategory.OnTurnEnd: [[range(1, 2), range(-1, -1)]]
        },
        EffectType.RestorePercentMana: {
            ItemEffectCategory.OnSuccessfulAttack: [[frange(0.03, 0.04, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.03, 0.04, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnAttacked: [[frange(0.03, 0.04, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.03, 0.04, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnDamaged: [[frange(0.04, 0.06, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnTurnStart: [[frange(0.01, 0.02, 0), range(-1, -1)]],
            ItemEffectCategory.OnTurnEnd: [[frange(0.01, 0.02, 0), range(-1, -1)]]
        },

        EffectType.AdjustedManaCosts: {
            ItemEffectCategory.Permanent: [[frange(-0.25, -0.1, 0.05), range(-1, -1)]]
        },
        EffectType.HealingAbilityBuff: {
            ItemEffectCategory.Permanent: [[frange(0.3, 0.4, 0.05), range(-1, -1)]]
        },
        EffectType.AdditionalXP: {
            ItemEffectCategory.Permanent: [[frange(0.5, 0.65, 0.05), range(-1, -1)]]
        },
        EffectType.PotionMod: {
            ItemEffectCategory.Permanent: [[frange(0.3, 0.4, 0.05), range(-1, -1)]]
        },

        EffectType.Damage: {
            ItemEffectCategory.OnSuccessfulAttack: [[range(4, 6), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(4, 6), range(-1, -1)]],
            ItemEffectCategory.OnAttacked: [[range(4, 6), range(-1, -1)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[range(4, 6), range(-1, -1)]],
            ItemEffectCategory.OnDamaged: [[range(6, 10), range(-1, -1)]]
        },
        EffectType.ResurrectOnce: {}
    },
    Rarity.Legendary: {
        EffectType.CleanseStatusEffects: {
            ItemEffectCategory.OnAttacked: [[range(-1, -1), range(-1, -1)]],
            ItemEffectCategory.OnDamaged: [[range(-1, -1), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAttack: [[range(-1, -1), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(-1, -1), range(-1, -1)]],
            ItemEffectCategory.OnTurnStart: [[range(-1, -1), range(-1, -1)]],
            ItemEffectCategory.OnTurnEnd: [[range(-1, -1), range(-1, -1)]],
        },

        EffectType.ConMod: {
            ItemEffectCategory.Permanent: [[range(3, 3), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAttack: [[range(2, 2), range(3, 4)], [range(3, 3), range(1, 2)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(2, 2), range(3, 4)], [range(3, 3), range(1, 2)]],
            ItemEffectCategory.OnAttacked: [[range(2, 2), range(3, 4)], [range(3, 3), range(1, 2)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[range(2, 2), range(3, 4)], [range(3, 3), range(1, 2)]],
            ItemEffectCategory.OnDamaged: [[range(2, 2), range(3, 4)], [range(3, 3), range(1, 2)]],
            ItemEffectCategory.OnTurnStart: [[range(1, 1), range(3, 4)]],
            ItemEffectCategory.OnTurnEnd: [[range(1, 1), range(3, 4)]]
        },
        EffectType.StrMod: {
            ItemEffectCategory.Permanent: [[range(5, 6), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAttack: [[range(4, 6), range(3, 4)], [range(6, 8), range(1, 2)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(4, 6), range(3, 4)], [range(6, 8), range(1, 2)]],
            ItemEffectCategory.OnAttacked: [[range(4, 6), range(3, 4)], [range(6, 8), range(1, 2)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[range(4, 6), range(3, 4)], [range(6, 8), range(1, 2)]],
            ItemEffectCategory.OnDamaged: [[range(4, 6), range(3, 4)], [range(6, 8), range(1, 2)]],
            ItemEffectCategory.OnTurnStart: [[range(1, 2), range(3, 4)]],
            ItemEffectCategory.OnTurnEnd: [[range(1, 2), range(3, 4)]]
        },
        EffectType.DexMod: {
            ItemEffectCategory.Permanent: [[range(3, 3), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAttack: [[range(2, 2), range(3, 4)], [range(3, 3), range(1, 2)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(2, 2), range(3, 4)], [range(3, 3), range(1, 2)]],
            ItemEffectCategory.OnAttacked: [[range(2, 2), range(3, 4)], [range(3, 3), range(1, 2)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[range(2, 2), range(3, 4)], [range(3, 3), range(1, 2)]],
            ItemEffectCategory.OnDamaged: [[range(2, 2), range(3, 4)], [range(3, 3), range(1, 2)]],
            ItemEffectCategory.OnTurnStart: [[range(1, 1), range(3, 4)]],
            ItemEffectCategory.OnTurnEnd: [[range(1, 1), range(3, 4)]]
        },
        EffectType.IntMod: {
            ItemEffectCategory.Permanent: [[range(3, 3), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAttack: [[range(2, 2), range(3, 4)], [range(3, 3), range(1, 2)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(2, 2), range(3, 4)], [range(3, 3), range(1, 2)]],
            ItemEffectCategory.OnAttacked: [[range(2, 2), range(3, 4)], [range(3, 3), range(1, 2)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[range(2, 2), range(3, 4)], [range(3, 3), range(1, 2)]],
            ItemEffectCategory.OnDamaged: [[range(2, 2), range(3, 4)], [range(3, 3), range(1, 2)]],
            ItemEffectCategory.OnTurnStart: [[range(1, 1), range(3, 4)]],
            ItemEffectCategory.OnTurnEnd: [[range(1, 1), range(3, 4)]]
        },
        EffectType.LckMod: {
            ItemEffectCategory.Permanent: [[range(5, 6), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAttack: [[range(4, 6), range(3, 4)], [range(6, 8), range(1, 2)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(4, 6), range(3, 4)], [range(6, 8), range(1, 2)]],
            ItemEffectCategory.OnAttacked: [[range(4, 6), range(3, 4)], [range(6, 8), range(1, 2)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[range(4, 6), range(3, 4)], [range(6, 8), range(1, 2)]],
            ItemEffectCategory.OnDamaged: [[range(4, 6), range(3, 4)], [range(6, 8), range(1, 2)]],
            ItemEffectCategory.OnTurnStart: [[range(1, 2), range(3, 4)]],
            ItemEffectCategory.OnTurnEnd: [[range(1, 2), range(3, 4)]]
        },
        EffectType.MemMod: {
            ItemEffectCategory.Permanent: [[range(1, 2), range(-1, -1)]],
        },

        EffectType.DmgReflect: {
            ItemEffectCategory.Permanent: [[frange(0.075, 0.1, 0.005), range(-1, -1)]]
        },
        EffectType.DmgResist: {
            ItemEffectCategory.Permanent: [[frange(0.075, 0.1, 0.005), range(-1, -1)]]
        },
        EffectType.DmgBuff: {
            ItemEffectCategory.Permanent: [[frange(0.15, 0.2, 0.01), range(-1, -1)]]
        },
        EffectType.DmgBuffSelfMaxHealth: {
            ItemEffectCategory.Permanent: [[frange(0.02, 0.02, 0), range(-1, -1)]]
        },
        EffectType.DmgBuffSelfRemainingHealth: {
            ItemEffectCategory.Permanent: [[frange(0.02, 0.02, 0), range(-1, -1)]]
        },
        EffectType.DmgBuffOtherMaxHealth: {
            ItemEffectCategory.Permanent: [[frange(0.02, 0.02, 0), range(-1, -1)]]
        },
        EffectType.DmgBuffOtherRemainingHealth: {
            ItemEffectCategory.Permanent: [[frange(0.02, 0.02, 0), range(-1, -1)]]
        },

        EffectType.DmgBuffLegends: {
            ItemEffectCategory.Permanent: [[frange(0.2, 0.25, 0.01), range(-1, -1)]]
        },
        EffectType.DmgBuffPoisoned: {
            ItemEffectCategory.Permanent: [[frange(0.15, 0.2, 0.01), range(-1, -1)]]
        },
        EffectType.DmgBuffBleeding: {
            ItemEffectCategory.Permanent: [[frange(0.15, 0.2, 0.01), range(-1, -1)]]
        },
        EffectType.DmgBuffFromDex: {
            ItemEffectCategory.Permanent: [[frange(0.025, 0.05, 0.025), range(-1, -1)]]
        },
        EffectType.DmgBuffFromInt: {
            ItemEffectCategory.Permanent: [[frange(0.025, 0.05, 0.025), range(-1, -1)]]
        },
        EffectType.DmgBuffFromLck: {
            ItemEffectCategory.Permanent: [[frange(0.025, 0.05, 0.025), range(-1, -1)]]
        },

        EffectType.RestoreArmor: {
            ItemEffectCategory.OnSuccessfulAttack: [[range(5, 6), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(5, 6), range(-1, -1)]],
            ItemEffectCategory.OnAttacked: [[range(5, 6), range(-1, -1)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[range(5, 6), range(-1, -1)]],
            ItemEffectCategory.OnDamaged: [[range(10, 14), range(-1, -1)]],
            ItemEffectCategory.OnTurnStart: [[range(3, 3), range(-1, -1)]],
            ItemEffectCategory.OnTurnEnd: [[range(3, 3), range(-1, -1)]]
        },
        EffectType.RestorePercentArmor: {
            ItemEffectCategory.OnSuccessfulAttack: [[frange(0.05, 0.06, 0.005), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.05, 0.06, 0.005), range(-1, -1)]],
            ItemEffectCategory.OnAttacked: [[frange(0.05, 0.06, 0.005), range(-1, -1)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.05, 0.06, 0.005), range(-1, -1)]],
            ItemEffectCategory.OnDamaged: [[frange(0.07, 0.09, 0.005), range(-1, -1)]],
            ItemEffectCategory.OnTurnStart: [[frange(0.03, 0.03, 0), range(-1, -1)]],
            ItemEffectCategory.OnTurnEnd: [[frange(0.03, 0.03, 0), range(-1, -1)]]
        },
        EffectType.PiercingDmg: {
            ItemEffectCategory.Permanent: [[range(4, 12), range(-1, -1)]]
        },
        EffectType.PiercingPercentDmg: {
            ItemEffectCategory.Permanent: [[frange(0.45, 0.55, 0.05), range(-1, -1)]]
        },
        EffectType.SplashDmg: {
            ItemEffectCategory.Permanent: [[range(4, 12), range(-1, -1)]]
        },
        EffectType.SplashPercentMaxDmg: {
            ItemEffectCategory.Permanent: [[frange(0.3, 0.4, 0.025), range(-1, -1)]]
        },

        EffectType.CritDmgBuff: {
            ItemEffectCategory.Permanent: [[frange(0.2, 0.25, 0.05), range(-1, -1)]]
        },
        EffectType.CritDmgReduction: {
            ItemEffectCategory.Permanent: [[frange(0.2, 0.25, 0.05), range(-1, -1)]]
        },
        
        EffectType.HealthSteal: {
            ItemEffectCategory.OnSuccessfulAttack: [[frange(0.03, 0.04, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.03, 0.04, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnAttacked: [[frange(0.04, 0.06, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.04, 0.06, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnDamaged: [[frange(0.04, 0.06, 0.01), range(-1, -1)]]
        },
        EffectType.ManaSteal: {
            ItemEffectCategory.OnSuccessfulAttack: [[frange(0.03, 0.04, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.03, 0.04, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnAttacked: [[frange(0.04, 0.06, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.04, 0.06, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnDamaged: [[frange(0.04, 0.06, 0.01), range(-1, -1)]]
        },
        EffectType.AdjustedCDs: {
            ItemEffectCategory.Permanent: [[range(-1, -1), range(-1, -1)]]
        },

        EffectType.ChanceStatusEffect: {
            StatusEffectKey.Bleeding: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.25, 0.3, 0.025), range(2, 3)], [frange(0.3, 0.35, 0.025), range(1, 2)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.25, 0.3, 0.025), range(2, 3)], [frange(0.3, 0.35, 0.025), range(1, 2)]],
                ItemEffectCategory.OnAttacked: [[frange(0.25, 0.3, 0.025), range(2, 3)], [frange(0.3, 0.35, 0.025), range(1, 2)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.25, 0.3, 0.025), range(2, 3)], [frange(0.3, 0.35, 0.025), range(1, 2)]],
                ItemEffectCategory.OnDamaged: [[frange(0.3, 0.35, 0.025), range(2, 3)], [frange(0.4, 0.45, 0.025), range(1, 2)]]
            },
            StatusEffectKey.Poisoned: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.25, 0.3, 0.025), range(2, 3)], [frange(0.3, 0.35, 0.025), range(1, 2)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.25, 0.3, 0.025), range(2, 3)], [frange(0.3, 0.35, 0.025), range(1, 2)]],
                ItemEffectCategory.OnAttacked: [[frange(0.25, 0.3, 0.025), range(2, 3)], [frange(0.3, 0.35, 0.025), range(1, 2)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.25, 0.3, 0.025), range(2, 3)], [frange(0.3, 0.35, 0.025), range(1, 2)]],
                ItemEffectCategory.OnDamaged: [[frange(0.3, 0.35, 0.025), range(2, 3)], [frange(0.4, 0.45, 0.025), range(1, 2)]]
            },
            StatusEffectKey.DmgReduction: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.1, 0.15, 0.025), range(2, 3)], [frange(0.15, 0.2, 0.025), range(1, 2)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.1, 0.15, 0.025), range(2, 3)], [frange(0.15, 0.2, 0.025), range(1, 2)]],
                ItemEffectCategory.OnAttacked: [[frange(0.15, 0.2, 0.025), range(2, 3)], [frange(0.225, 0.25, 0.05), range(1, 2)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.15, 0.2, 0.025), range(2, 3)], [frange(0.225, 0.25, 0.05), range(1, 2)]],
                ItemEffectCategory.OnDamaged: [[frange(0.2, 0.25, 0.025), range(2, 3)], [frange(0.3, 0.35, 0.05), range(1, 2)]]
            },
            StatusEffectKey.DmgVulnerability: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.1, 0.15, 0.025), range(2, 3)], [frange(0.15, 0.2, 0.025), range(1, 2)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.1, 0.15, 0.025), range(2, 3)], [frange(0.15, 0.2, 0.025), range(1, 2)]],
                ItemEffectCategory.OnAttacked: [[frange(0.15, 0.2, 0.025), range(2, 3)], [frange(0.225, 0.25, 0.05), range(1, 2)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.15, 0.2, 0.025), range(2, 3)], [frange(0.225, 0.25, 0.05), range(1, 2)]],
                ItemEffectCategory.OnDamaged: [[frange(0.2, 0.25, 0.025), range(2, 3)], [frange(0.3, 0.35, 0.05), range(1, 2)]]
            },
            StatusEffectKey.FixedDmgTick: {
                ItemEffectCategory.OnSuccessfulAttack: [[range(5, 6), range(3, 4)], [range(7, 8), range(1, 2)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(5, 6), range(3, 4)], [range(7, 8), range(1, 2)]],
                ItemEffectCategory.OnAttacked: [[range(5, 6), range(3, 4)], [range(7, 8), range(1, 2)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[range(5, 6), range(3, 4)], [range(7, 8), range(1, 2)]],
                ItemEffectCategory.OnDamaged: [[range(5, 6), range(3, 4)], [range(7, 8), range(1, 2)]]
            },
            StatusEffectKey.TurnSkipChance: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.05, 0.1, 0.025), range(2, 2)], [frange(0.1, 0.15, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.05, 0.1, 0.025), range(2, 2)], [frange(0.1, 0.15, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.25, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.25, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.25, 0.025), range(1, 1)]]
            },
            StatusEffectKey.Taunted: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.25, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.25, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.35, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.35, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.35, 0.025), range(1, 1)]]
            },
            StatusEffectKey.CannotTarget: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.25, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.25, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.35, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.35, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.35, 0.025), range(1, 1)]]
            },
            StatusEffectKey.Generating: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.25, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.25, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.35, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.35, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.35, 0.025), range(1, 1)]],
                ItemEffectCategory.OnTurnStart: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.2, 0.025), range(1, 1)]],
                ItemEffectCategory.OnTurnEnd: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.2, 0.025), range(1, 1)]]
            },
            StatusEffectKey.Tarnished: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.25, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.25, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.35, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.35, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.35, 0.025), range(1, 1)]],
                ItemEffectCategory.OnTurnStart: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.2, 0.025), range(1, 1)]],
                ItemEffectCategory.OnTurnEnd: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.2, 0.025), range(1, 1)]]
            },
            StatusEffectKey.ManaToHP: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.25, 0.35, 0.05), range(2, 2)], [frange(0.35, 0.45, 0.05), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.25, 0.35, 0.05), range(2, 2)], [frange(0.35, 0.45, 0.05), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.25, 0.35, 0.05), range(2, 2)], [frange(0.35, 0.45, 0.05), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.25, 0.35, 0.05), range(2, 2)], [frange(0.35, 0.45, 0.05), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.25, 0.35, 0.05), range(2, 2)], [frange(0.35, 0.45, 0.05), range(1, 1)]]
            },
            StatusEffectKey.PoisonHeals: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.15, 0.25, 0.05), range(2, 3)], [frange(0.35, 0.45, 0.05), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.15, 0.25, 0.05), range(2, 3)], [frange(0.35, 0.45, 0.05), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.15, 0.25, 0.05), range(3, 4)], [frange(0.35, 0.45, 0.05), range(1, 2)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.15, 0.25, 0.05), range(3, 4)], [frange(0.35, 0.45, 0.05), range(1, 2)]],
                ItemEffectCategory.OnDamaged: [[frange(0.15, 0.25, 0.05), range(3, 4)], [frange(0.35, 0.45, 0.05), range(1, 2)]]
            },
            StatusEffectKey.DmgBuff: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.3, 0.35, 0.025), range(2, 2)], [frange(0.35, 0.4, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.3, 0.35, 0.025), range(2, 2)], [frange(0.35, 0.4, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.3, 0.35, 0.025), range(2, 2)], [frange(0.35, 0.4, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.35, 0.4, 0.025), range(2, 2)], [frange(0.4, 0.45, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.35, 0.4, 0.025), range(2, 2)], [frange(0.4, 0.45, 0.025), range(1, 1)]]
            },
            StatusEffectKey.DmgDebuff: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.3, 0.35, 0.025), range(2, 2)], [frange(0.35, 0.4, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.3, 0.35, 0.025), range(2, 2)], [frange(0.35, 0.4, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.3, 0.35, 0.025), range(2, 2)], [frange(0.35, 0.4, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.35, 0.4, 0.025), range(2, 2)], [frange(0.4, 0.45, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.35, 0.4, 0.025), range(2, 2)], [frange(0.4, 0.45, 0.025), range(1, 1)]]
            },
            StatusEffectKey.Charmed: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.2, 0.025), range(2, 2)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.2, 0.025), range(2, 2)]],
                ItemEffectCategory.OnAttacked: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.2, 0.025), range(2, 2)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.35, 0.025), range(2, 2)]],
                ItemEffectCategory.OnDamaged: [[frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.35, 0.025), range(2, 2)]]
            },
            StatusEffectKey.CannotAttack: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.2, 0.25, 0.025), range(2, 2)], [frange(0.25, 0.3, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.2, 0.25, 0.025), range(2, 2)], [frange(0.25, 0.3, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.2, 0.25, 0.025), range(2, 2)], [frange(0.25, 0.3, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.3, 0.4, 0.025), range(2, 2)], [frange(0.35, 0.45, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.3, 0.4, 0.025), range(2, 2)], [frange(0.35, 0.45, 0.025), range(1, 1)]]
            },
            StatusEffectKey.Sleeping: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.2, 0.25, 0.025), range(2, 2)], [frange(0.25, 0.3, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.2, 0.25, 0.025), range(2, 2)], [frange(0.25, 0.3, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.2, 0.25, 0.025), range(2, 2)], [frange(0.25, 0.3, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.3, 0.4, 0.025), range(2, 2)], [frange(0.35, 0.45, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.3, 0.4, 0.025), range(2, 2)], [frange(0.35, 0.45, 0.025), range(1, 1)]]
            },
            StatusEffectKey.Decaying: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.4, 0.45, 0.025), range(2, 2)], [frange(0.45, 0.55, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.4, 0.45, 0.025), range(2, 2)], [frange(0.45, 0.55, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.4, 0.45, 0.025), range(2, 2)], [frange(0.45, 0.55, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.45, 0.5, 0.025), range(2, 2)], [frange(0.55, 0.6, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.45, 0.5, 0.025), range(2, 2)], [frange(0.55, 0.6, 0.025), range(1, 1)]]
            },
            StatusEffectKey.Undying: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.05, 0.1, 0.025), range(2, 2)], [frange(0.1, 0.15, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.05, 0.1, 0.025), range(2, 2)], [frange(0.1, 0.15, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.25, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.25, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.2, 0.025), range(1, 1)]]
            },
            StatusEffectKey.CannotUseAbilities: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.2, 0.25, 0.025), range(2, 2)], [frange(0.25, 0.3, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.2, 0.25, 0.025), range(2, 2)], [frange(0.25, 0.3, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.2, 0.25, 0.025), range(2, 2)], [frange(0.25, 0.3, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.3, 0.4, 0.025), range(2, 2)], [frange(0.35, 0.45, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.3, 0.4, 0.025), range(2, 2)], [frange(0.35, 0.45, 0.025), range(1, 1)]]
            },
            StatusEffectKey.StackingDamage: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.35, 0.4, 0.025), range(3, 3)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.45, 0.5, 0.025), range(2, 2)]]
            }
        },

        EffectType.ResistStatusEffect: {
            StatusEffectKey.Bleeding: {
                ItemEffectCategory.Permanent: [[frange(0.3, 0.4, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.Poisoned: {
                ItemEffectCategory.Permanent: [[frange(0.3, 0.4, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.DmgVulnerability: {
                ItemEffectCategory.Permanent: [[frange(0.3, 0.4, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.TurnSkipChance: {
                ItemEffectCategory.Permanent: [[frange(0.3, 0.4, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.Taunted: {
                ItemEffectCategory.Permanent: [[frange(0.3, 0.4, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.CannotTarget: {
                ItemEffectCategory.Permanent: [[frange(0.3, 0.4, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.DmgDebuff: {
                ItemEffectCategory.Permanent: [[frange(0.3, 0.4, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.Charmed: {
                ItemEffectCategory.Permanent: [[frange(0.3, 0.4, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.CannotAttack: {
                ItemEffectCategory.Permanent: [[frange(0.3, 0.4, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.Sleeping: {
                ItemEffectCategory.Permanent: [[frange(0.3, 0.4, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.Decaying: {
                ItemEffectCategory.Permanent: [[frange(0.3, 0.4, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.CannotUseAbilities: {
                ItemEffectCategory.Permanent: [[frange(0.3, 0.4, 0.05), range(-1, -1)]]
            }
        },

        EffectType.RestoreHealth: {
            ItemEffectCategory.OnSuccessfulAttack: [[range(5, 6), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(5, 6), range(-1, -1)]],
            ItemEffectCategory.OnAttacked: [[range(5, 6), range(-1, -1)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[range(5, 6), range(-1, -1)]],
            ItemEffectCategory.OnDamaged: [[range(7, 9), range(-1, -1)]],
            ItemEffectCategory.OnTurnStart: [[range(1, 3), range(-1, -1)]],
            ItemEffectCategory.OnTurnEnd: [[range(1, 3), range(-1, -1)]]
        },
        EffectType.RestorePercentHealth: {
            ItemEffectCategory.OnSuccessfulAttack: [[frange(0.05, 0.06, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.05, 0.06, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnAttacked: [[frange(0.05, 0.06, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.05, 0.06, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnDamaged: [[frange(0.07, 0.09, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnTurnStart: [[frange(0.01, 0.03, 0), range(-1, -1)]],
            ItemEffectCategory.OnTurnEnd: [[frange(0.01, 0.03, 0), range(-1, -1)]]
        },
        EffectType.RestoreMana: {
            ItemEffectCategory.OnSuccessfulAttack: [[range(5, 6), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(5, 6), range(-1, -1)]],
            ItemEffectCategory.OnAttacked: [[range(5, 6), range(-1, -1)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[range(5, 6), range(-1, -1)]],
            ItemEffectCategory.OnDamaged: [[range(7, 9), range(-1, -1)]],
            ItemEffectCategory.OnTurnStart: [[range(1, 3), range(-1, -1)]],
            ItemEffectCategory.OnTurnEnd: [[range(1, 3), range(-1, -1)]]
        },
        EffectType.RestorePercentMana: {
            ItemEffectCategory.OnSuccessfulAttack: [[frange(0.05, 0.06, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.05, 0.06, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnAttacked: [[frange(0.05, 0.06, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.05, 0.06, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnDamaged: [[frange(0.07, 0.09, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnTurnStart: [[frange(0.01, 0.03, 0), range(-1, -1)]],
            ItemEffectCategory.OnTurnEnd: [[frange(0.01, 0.03, 0), range(-1, -1)]]
        },

        EffectType.AdjustedManaCosts: {
            ItemEffectCategory.Permanent: [[frange(-0.5, -0.25, 0.05), range(-1, -1)]]
        },
        EffectType.HealingAbilityBuff: {
            ItemEffectCategory.Permanent: [[frange(0.4, 0.5, 0.05), range(-1, -1)]]
        },
        EffectType.AdditionalXP: {
            ItemEffectCategory.Permanent: [[frange(0.75, 0.9, 0.05), range(-1, -1)]]
        },
        EffectType.PotionMod: {
            ItemEffectCategory.Permanent: [[frange(0.4, 0.5, 0.05), range(-1, -1)]]
        },

        EffectType.Damage: {
            ItemEffectCategory.OnSuccessfulAttack: [[range(7, 9), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(7, 9), range(-1, -1)]],
            ItemEffectCategory.OnAttacked: [[range(7, 9), range(-1, -1)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[range(7, 9), range(-1, -1)]],
            ItemEffectCategory.OnDamaged: [[range(8, 12), range(-1, -1)]]
        },
        EffectType.ResurrectOnce: {}
    },
    Rarity.Artifact: {
        EffectType.CleanseStatusEffects: {
            ItemEffectCategory.OnAttacked: [[range(-1, -1), range(-1, -1)]],
            ItemEffectCategory.OnDamaged: [[range(-1, -1), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAttack: [[range(-1, -1), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(-1, -1), range(-1, -1)]],
            ItemEffectCategory.OnTurnStart: [[range(-1, -1), range(-1, -1)]],
            ItemEffectCategory.OnTurnEnd: [[range(-1, -1), range(-1, -1)]],
        },

        EffectType.ConMod: {
            ItemEffectCategory.Permanent: [[range(3, 6), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAttack: [[range(2, 3), range(3, 4)], [range(2, 4), range(1, 2)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(2, 3), range(3, 4)], [range(2, 4), range(1, 2)]],
            ItemEffectCategory.OnAttacked: [[range(2, 3), range(3, 4)], [range(2, 4), range(1, 2)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[range(2, 3), range(3, 4)], [range(2, 4), range(1, 2)]],
            ItemEffectCategory.OnDamaged: [[range(2, 3), range(3, 4)], [range(2, 4), range(1, 2)]],
            ItemEffectCategory.OnTurnStart: [[range(1, 1), range(4, 5)]],
            ItemEffectCategory.OnTurnEnd: [[range(1, 1), range(4, 5)]]
        },
        EffectType.StrMod: {
            ItemEffectCategory.Permanent: [[range(5, 25), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAttack: [[range(5, 8), range(3, 4)], [range(8, 12), range(1, 2)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(5, 8), range(3, 4)], [range(8, 12), range(1, 2)]],
            ItemEffectCategory.OnAttacked: [[range(5, 8), range(3, 4)], [range(8, 12), range(1, 2)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[range(5, 8), range(3, 4)], [range(8, 12), range(1, 2)]],
            ItemEffectCategory.OnDamaged: [[range(5, 8), range(3, 4)], [range(8, 12), range(1, 2)]],
            ItemEffectCategory.OnTurnStart: [[range(1, 3), range(4, 5)]],
            ItemEffectCategory.OnTurnEnd: [[range(1, 3), range(4, 5)]]
        },
        EffectType.DexMod: {
            ItemEffectCategory.Permanent: [[range(5, 20), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAttack: [[range(2, 3), range(3, 4)], [range(2, 4), range(1, 2)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(2, 3), range(3, 4)], [range(2, 4), range(1, 2)]],
            ItemEffectCategory.OnAttacked: [[range(2, 3), range(3, 4)], [range(2, 4), range(1, 2)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[range(2, 3), range(3, 4)], [range(2, 4), range(1, 2)]],
            ItemEffectCategory.OnDamaged: [[range(2, 3), range(3, 4)], [range(2, 4), range(1, 2)]],
            ItemEffectCategory.OnTurnStart: [[range(1, 1), range(4, 5)]],
            ItemEffectCategory.OnTurnEnd: [[range(1, 1), range(4, 5)]]
        },
        EffectType.IntMod: {
            ItemEffectCategory.Permanent: [[range(3, 6), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAttack: [[range(2, 3), range(3, 4)], [range(2, 4), range(1, 2)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(2, 3), range(3, 4)], [range(2, 4), range(1, 2)]],
            ItemEffectCategory.OnAttacked: [[range(2, 3), range(3, 4)], [range(2, 4), range(1, 2)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[range(2, 3), range(3, 4)], [range(2, 4), range(1, 2)]],
            ItemEffectCategory.OnDamaged: [[range(2, 3), range(3, 4)], [range(2, 4), range(1, 2)]],
            ItemEffectCategory.OnTurnStart: [[range(1, 1), range(4, 5)]],
            ItemEffectCategory.OnTurnEnd: [[range(1, 1), range(4, 5)]]
        },
        EffectType.LckMod: {
            ItemEffectCategory.Permanent: [[range(5, 25), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAttack: [[range(5, 8), range(3, 4)], [range(8, 12), range(1, 2)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(5, 8), range(3, 4)], [range(8, 12), range(1, 2)]],
            ItemEffectCategory.OnAttacked: [[range(5, 8), range(3, 4)], [range(8, 12), range(1, 2)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[range(5, 8), range(3, 4)], [range(8, 12), range(1, 2)]],
            ItemEffectCategory.OnDamaged: [[range(5, 8), range(3, 4)], [range(8, 12), range(1, 2)]],
            ItemEffectCategory.OnTurnStart: [[range(1, 3), range(4, 5)]],
            ItemEffectCategory.OnTurnEnd: [[range(1, 3), range(4, 5)]]
        },
        EffectType.MemMod: {
            ItemEffectCategory.Permanent: [[range(1, 5), range(-1, -1)]],
        },

        EffectType.DmgReflect: {
            ItemEffectCategory.Permanent: [[frange(0.1, 0.5, 0.05), range(-1, -1)]]
        },
        EffectType.DmgResist: {
            ItemEffectCategory.Permanent: [[frange(0.1, 0.5, 0.05), range(-1, -1)]]
        },
        EffectType.DmgBuff: {
            ItemEffectCategory.Permanent: [[frange(0.2, 0.5, 0.05), range(-1, -1)]]
        },
        EffectType.DmgBuffSelfMaxHealth: {
            ItemEffectCategory.Permanent: [[frange(0.01, 0.05, 0), range(-1, -1)]]
        },
        EffectType.DmgBuffSelfRemainingHealth: {
            ItemEffectCategory.Permanent: [[frange(0.01, 0.05, 0), range(-1, -1)]]
        },
        EffectType.DmgBuffOtherMaxHealth: {
            ItemEffectCategory.Permanent: [[frange(0.01, 0.05, 0), range(-1, -1)]]
        },
        EffectType.DmgBuffOtherRemainingHealth: {
            ItemEffectCategory.Permanent: [[frange(0.01, 0.05, 0), range(-1, -1)]]
        },

        EffectType.DmgBuffLegends: {
            ItemEffectCategory.Permanent: [[frange(0.3, 1, 0.05), range(-1, -1)]]
        },
        EffectType.DmgBuffPoisoned: {
            ItemEffectCategory.Permanent: [[frange(0.2, 0.75, 0.05), range(-1, -1)]]
        },
        EffectType.DmgBuffBleeding: {
            ItemEffectCategory.Permanent: [[frange(0.2, 0.75, 0.05), range(-1, -1)]]
        },
        EffectType.DmgBuffFromDex: {
            ItemEffectCategory.Permanent: [[frange(0.025, 0.075, 0.025), range(-1, -1)]]
        },
        EffectType.DmgBuffFromInt: {
            ItemEffectCategory.Permanent: [[frange(0.025, 0.075, 0.025), range(-1, -1)]]
        },
        EffectType.DmgBuffFromLck: {
            ItemEffectCategory.Permanent: [[frange(0.025, 0.075, 0.025), range(-1, -1)]]
        },

        EffectType.RestoreArmor: {
            ItemEffectCategory.OnSuccessfulAttack: [[range(5, 15), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(5, 15), range(-1, -1)]],
            ItemEffectCategory.OnAttacked: [[range(5, 15), range(-1, -1)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[range(5, 15), range(-1, -1)]],
            ItemEffectCategory.OnDamaged: [[range(10, 20), range(-1, -1)]],
            ItemEffectCategory.OnTurnStart: [[range(3, 10), range(-1, -1)]],
            ItemEffectCategory.OnTurnEnd: [[range(3, 10), range(-1, -1)]]
        },
        EffectType.RestorePercentArmor: {
            ItemEffectCategory.OnSuccessfulAttack: [[frange(0.05, 0.1, 0.005), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.05, 0.1, 0.005), range(-1, -1)]],
            ItemEffectCategory.OnAttacked: [[frange(0.05, 0.1, 0.005), range(-1, -1)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.05, 0.1, 0.005), range(-1, -1)]],
            ItemEffectCategory.OnDamaged: [[frange(0.05, 0.15, 0.005), range(-1, -1)]],
            ItemEffectCategory.OnTurnStart: [[frange(0.03, 0.06, 0), range(-1, -1)]],
            ItemEffectCategory.OnTurnEnd: [[frange(0.03, 0.06, 0), range(-1, -1)]]
        },
        EffectType.PiercingDmg: {
            ItemEffectCategory.Permanent: [[range(5, 25), range(-1, -1)]]
        },
        EffectType.PiercingPercentDmg: {
            ItemEffectCategory.Permanent: [[frange(0.5, 1, 0.05), range(-1, -1)]]
        },
        EffectType.SplashDmg: {
            ItemEffectCategory.Permanent: [[range(5, 25), range(-1, -1)]]
        },
        EffectType.SplashPercentMaxDmg: {
            ItemEffectCategory.Permanent: [[frange(0.5, 1, 0.05), range(-1, -1)]]
        },

        EffectType.CritDmgBuff: {
            ItemEffectCategory.Permanent: [[frange(0.3, 0.75, 0.05), range(-1, -1)]]
        },
        EffectType.CritDmgReduction: {
            ItemEffectCategory.Permanent: [[frange(0.3, 0.75, 0.05), range(-1, -1)]]
        },
        
        EffectType.HealthSteal: {
            ItemEffectCategory.OnSuccessfulAttack: [[frange(0.05, 0.1, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.05, 0.1, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnAttacked: [[frange(0.05, 0.1, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.05, 0.1, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnDamaged: [[frange(0.05, 0.1, 0.01), range(-1, -1)]]
        },
        EffectType.ManaSteal: {
            ItemEffectCategory.OnSuccessfulAttack: [[frange(0.05, 0.1, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.05, 0.1, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnAttacked: [[frange(0.05, 0.1, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.05, 0.1, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnDamaged: [[frange(0.05, 0.1, 0.01), range(-1, -1)]]
        },
        EffectType.AdjustedCDs: {
            ItemEffectCategory.Permanent: [[range(-3, -1), range(-1, -1)]]
        },

        EffectType.ChanceStatusEffect: {
            StatusEffectKey.Bleeding: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.3, 0.35, 0.025), range(3, 4)], [frange(0.35, 0.45, 0.025), range(2, 3)], [frange(0.5, 0.75, 0.025), range(1, 2)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.3, 0.35, 0.025), range(3, 4)], [frange(0.35, 0.45, 0.025), range(2, 3)], [frange(0.5, 0.75, 0.025), range(1, 2)]],
                ItemEffectCategory.OnAttacked: [[frange(0.3, 0.35, 0.025), range(3, 4)], [frange(0.35, 0.45, 0.025), range(2, 3)], [frange(0.5, 0.75, 0.025), range(1, 2)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.3, 0.5, 0.025), range(3, 4)], [frange(0.35, 0.55, 0.025), range(2, 3)], [frange(0.5, 0.9, 0.025), range(1, 2)]],
                ItemEffectCategory.OnDamaged: [[frange(0.3, 0.5, 0.025), range(3, 4)], [frange(0.35, 0.55, 0.025), range(2, 3)], [frange(0.5, 0.9, 0.025), range(1, 2)]]
            },
            StatusEffectKey.Poisoned: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.3, 0.35, 0.025), range(3, 4)], [frange(0.35, 0.45, 0.025), range(2, 3)], [frange(0.5, 0.75, 0.025), range(1, 2)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.3, 0.35, 0.025), range(3, 4)], [frange(0.35, 0.45, 0.025), range(2, 3)], [frange(0.5, 0.75, 0.025), range(1, 2)]],
                ItemEffectCategory.OnAttacked: [[frange(0.3, 0.35, 0.025), range(3, 4)], [frange(0.35, 0.45, 0.025), range(2, 3)], [frange(0.5, 0.75, 0.025), range(1, 2)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.3, 0.5, 0.025), range(3, 4)], [frange(0.35, 0.55, 0.025), range(2, 3)], [frange(0.5, 0.9, 0.025), range(1, 2)]],
                ItemEffectCategory.OnDamaged: [[frange(0.3, 0.5, 0.025), range(3, 4)], [frange(0.35, 0.55, 0.025), range(2, 3)], [frange(0.5, 0.9, 0.025), range(1, 2)]]
            },
            StatusEffectKey.DmgReduction: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.15, 0.25, 0.025), range(2, 3)], [frange(0.25, 0.5, 0.025), range(1, 2)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.15, 0.25, 0.025), range(2, 3)], [frange(0.25, 0.5, 0.025), range(1, 2)]],
                ItemEffectCategory.OnAttacked: [[frange(0.2, 0.25, 0.025), range(2, 3)], [frange(0.3, 0.5, 0.025), range(1, 2)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.2, 0.25, 0.025), range(2, 3)], [frange(0.3, 0.5, 0.025), range(1, 2)]],
                ItemEffectCategory.OnDamaged: [[frange(0.3, 0.35, 0.025), range(2, 3)], [frange(0.3, 0.5, 0.05), range(1, 2)]]
            },
            StatusEffectKey.DmgVulnerability: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.15, 0.25, 0.025), range(2, 3)], [frange(0.25, 0.5, 0.025), range(1, 2)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.15, 0.25, 0.025), range(2, 3)], [frange(0.25, 0.5, 0.025), range(1, 2)]],
                ItemEffectCategory.OnAttacked: [[frange(0.2, 0.25, 0.025), range(2, 3)], [frange(0.3, 0.5, 0.025), range(1, 2)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.2, 0.25, 0.025), range(2, 3)], [frange(0.3, 0.5, 0.025), range(1, 2)]],
                ItemEffectCategory.OnDamaged: [[frange(0.3, 0.35, 0.025), range(2, 3)], [frange(0.3, 0.5, 0.05), range(1, 2)]]
            },
            StatusEffectKey.FixedDmgTick: {
                ItemEffectCategory.OnSuccessfulAttack: [[range(7, 10), range(3, 4)], [range(10, 25), range(1, 2)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(7, 10), range(3, 4)], [range(10, 25), range(1, 2)]],
                ItemEffectCategory.OnAttacked: [[range(7, 10), range(3, 4)], [range(10, 25), range(1, 2)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[range(7, 10), range(3, 4)], [range(10, 25), range(1, 2)]],
                ItemEffectCategory.OnDamaged: [[range(7, 10), range(3, 4)], [range(10, 25), range(1, 2)]]
            },
            StatusEffectKey.TurnSkipChance: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.05, 0.1, 0.025), range(3, 3)], [frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.5, 0.05), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.05, 0.1, 0.025), range(3, 3)], [frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.5, 0.05), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.05, 0.1, 0.025), range(3, 3)], [frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.5, 0.05), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.05, 0.1, 0.025), range(3, 3)], [frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.5, 0.05), range(1, 1)]]
            },
            StatusEffectKey.Taunted: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.1, 0.15, 0.025), range(3, 3)], [frange(0.15, 0.25, 0.025), range(2, 2)], [frange(0.3, 0.5, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed:  [[frange(0.1, 0.15, 0.025), range(3, 3)], [frange(0.15, 0.25, 0.025), range(2, 2)], [frange(0.3, 0.5, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked:  [[frange(0.15, 0.2, 0.025), range(3, 3)], [frange(0.2, 0.3, 0.025), range(2, 2)], [frange(0.4, 0.6, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.15, 0.2, 0.025), range(3, 3)], [frange(0.2, 0.3, 0.025), range(2, 2)], [frange(0.4, 0.6, 0.05), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.15, 0.2, 0.025), range(3, 3)], [frange(0.2, 0.3, 0.025), range(2, 2)], [frange(0.4, 0.6, 0.05), range(1, 1)]]
            },
            StatusEffectKey.CannotTarget: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.1, 0.15, 0.025), range(3, 3)], [frange(0.15, 0.25, 0.025), range(2, 2)], [frange(0.3, 0.5, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed:  [[frange(0.1, 0.15, 0.025), range(3, 3)], [frange(0.15, 0.25, 0.025), range(2, 2)], [frange(0.3, 0.5, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked:  [[frange(0.15, 0.2, 0.025), range(3, 3)], [frange(0.2, 0.3, 0.025), range(2, 2)], [frange(0.4, 0.6, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.15, 0.2, 0.025), range(3, 3)], [frange(0.2, 0.3, 0.025), range(2, 2)], [frange(0.4, 0.6, 0.05), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.15, 0.2, 0.025), range(3, 3)], [frange(0.2, 0.3, 0.025), range(2, 2)], [frange(0.4, 0.6, 0.05), range(1, 1)]]
            },
            StatusEffectKey.Generating: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.1, 0.15, 0.025), range(3, 3)], [frange(0.15, 0.25, 0.025), range(2, 2)], [frange(0.3, 0.75, 0.05), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.1, 0.15, 0.025), range(3, 3)], [frange(0.15, 0.25, 0.025), range(2, 2)], [frange(0.3, 0.75, 0.05), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.1, 0.15, 0.025), range(3, 3)], [frange(0.15, 0.25, 0.025), range(2, 2)], [frange(0.3, 0.75, 0.05), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.1, 0.15, 0.025), range(3, 3)], [frange(0.15, 0.25, 0.025), range(2, 2)], [frange(0.3, 0.75, 0.05), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.1, 0.15, 0.025), range(3, 3)], [frange(0.15, 0.25, 0.025), range(2, 2)], [frange(0.3, 0.75, 0.05), range(1, 1)]],
                ItemEffectCategory.OnTurnStart: [[frange(0.1, 0.15, 0.025), range(3, 3)], [frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.5, 0.05), range(1, 1)]],
                ItemEffectCategory.OnTurnEnd: [[frange(0.1, 0.15, 0.025), range(3, 3)], [frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.5, 0.05), range(1, 1)]],
            },
            StatusEffectKey.Tarnished: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.25, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.25, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.35, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.35, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.15, 0.2, 0.025), range(2, 2)], [frange(0.2, 0.35, 0.025), range(1, 1)]],
                ItemEffectCategory.OnTurnStart: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.2, 0.025), range(1, 1)]],
                ItemEffectCategory.OnTurnEnd: [[frange(0.1, 0.15, 0.025), range(2, 2)], [frange(0.15, 0.2, 0.025), range(1, 1)]]
            },
            StatusEffectKey.ManaToHP: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.35, 0.5, 0.025), range(2, 2)], [frange(0.4, 0.75, 0.05), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.35, 0.5, 0.025), range(2, 2)], [frange(0.4, 0.75, 0.05), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.35, 0.5, 0.025), range(2, 2)], [frange(0.4, 0.75, 0.05), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.35, 0.5, 0.025), range(2, 2)], [frange(0.4, 0.75, 0.05), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.35, 0.5, 0.025), range(2, 2)], [frange(0.4, 0.75, 0.05), range(1, 1)]]
            },
            StatusEffectKey.PoisonHeals: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.25, 0.4, 0.05), range(2, 3)], [frange(0.45, 0.75, 0.05), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.25, 0.4, 0.05), range(2, 3)], [frange(0.45, 0.75, 0.05), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.25, 0.4, 0.05), range(2, 3)], [frange(0.45, 0.75, 0.05), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.25, 0.4, 0.05), range(2, 3)], [frange(0.45, 0.75, 0.05), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.25, 0.4, 0.05), range(2, 3)], [frange(0.45, 0.75, 0.05), range(1, 1)]]
            },
            StatusEffectKey.DmgBuff: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.3, 0.35, 0.025), range(3, 4)], [frange(0.35, 0.4, 0.025), range(1, 2)], [frange(0.5, 0.75, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.3, 0.35, 0.025), range(3, 4)], [frange(0.35, 0.4, 0.025), range(1, 2)], [frange(0.5, 0.75, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.3, 0.35, 0.025), range(3, 4)], [frange(0.35, 0.4, 0.025), range(1, 2)], [frange(0.5, 0.75, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.3, 0.35, 0.025), range(3, 4)], [frange(0.35, 0.4, 0.025), range(1, 2)], [frange(0.5, 0.75, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.3, 0.35, 0.025), range(3, 4)], [frange(0.35, 0.4, 0.025), range(1, 2)], [frange(0.5, 0.75, 0.025), range(1, 1)]]
            },
            StatusEffectKey.DmgDebuff: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.3, 0.35, 0.025), range(3, 4)], [frange(0.35, 0.4, 0.025), range(1, 2)], [frange(0.5, 0.75, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.3, 0.35, 0.025), range(3, 4)], [frange(0.35, 0.4, 0.025), range(1, 2)], [frange(0.5, 0.75, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.3, 0.35, 0.025), range(3, 4)], [frange(0.35, 0.4, 0.025), range(1, 2)], [frange(0.5, 0.75, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.3, 0.35, 0.025), range(3, 4)], [frange(0.35, 0.4, 0.025), range(1, 2)], [frange(0.5, 0.75, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.3, 0.35, 0.025), range(3, 4)], [frange(0.35, 0.4, 0.025), range(1, 2)], [frange(0.5, 0.75, 0.025), range(1, 1)]]
            },
            StatusEffectKey.Charmed: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.1, 0.15, 0.025), range(3, 4)], [frange(0.15, 0.2, 0.025), range(2, 3)], [frange(0.25, 0.75, 0.05), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.1, 0.15, 0.025), range(3, 4)], [frange(0.15, 0.2, 0.025), range(2, 3)], [frange(0.25, 0.75, 0.05), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.1, 0.15, 0.025), range(3, 4)], [frange(0.15, 0.2, 0.025), range(2, 3)], [frange(0.25, 0.75, 0.05), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.15, 0.2, 0.025), range(3, 4)], [frange(0.2, 0.25, 0.025), range(2, 3)], [frange(0.25, 0.75, 0.05), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.15, 0.2, 0.025), range(3, 4)], [frange(0.2, 0.25, 0.025), range(2, 3)], [frange(0.25, 0.75, 0.05), range(1, 1)]]
            },
            StatusEffectKey.CannotAttack: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.2, 0.25, 0.025), range(3, 4)], [frange(0.25, 0.3, 0.025), range(2, 3)], [frange(0.35, 0.5, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.2, 0.25, 0.025), range(3, 4)], [frange(0.25, 0.3, 0.025), range(2, 3)], [frange(0.35, 0.5, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.25, 0.3, 0.025), range(3, 4)], [frange(0.3, 0.35, 0.025), range(2, 3)], [frange(0.35, 0.5, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.25, 0.3, 0.025), range(3, 4)], [frange(0.3, 0.35, 0.025), range(2, 3)], [frange(0.35, 0.5, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.25, 0.3, 0.025), range(3, 4)], [frange(0.3, 0.35, 0.025), range(2, 3)], [frange(0.35, 0.5, 0.025), range(1, 1)]],
            },
            StatusEffectKey.Sleeping: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.2, 0.25, 0.025), range(2, 3)], [frange(0.25, 0.3, 0.025), range(1, 2)], [frange(0.35, 0.75, 0.05), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.2, 0.25, 0.025), range(2, 3)], [frange(0.25, 0.3, 0.025), range(1, 2)], [frange(0.35, 0.75, 0.05), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.2, 0.25, 0.025), range(2, 3)], [frange(0.25, 0.3, 0.025), range(1, 2)], [frange(0.35, 0.75, 0.05), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.3, 0.4, 0.025), range(2, 3)], [frange(0.35, 0.45, 0.025), range(1, 2)], [frange(0.5, 0.8, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.3, 0.4, 0.025), range(2, 3)], [frange(0.35, 0.45, 0.025), range(1, 2)], [frange(0.5, 0.8, 0.025), range(1, 1)]]
            },
            StatusEffectKey.Decaying: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.4, 0.45, 0.025), range(3, 4)], [frange(0.45, 0.55, 0.025), range(2, 3)], [frange(0.6, 2, 0.1), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.4, 0.45, 0.025), range(3, 4)], [frange(0.45, 0.55, 0.025), range(2, 3)], [frange(0.6, 2, 0.1), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.4, 0.45, 0.025), range(3, 4)], [frange(0.45, 0.55, 0.025), range(2, 3)], [frange(0.6, 2, 0.1), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.4, 0.45, 0.025), range(3, 4)], [frange(0.45, 0.55, 0.025), range(2, 3)], [frange(0.6, 2, 0.1), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.4, 0.45, 0.025), range(3, 4)], [frange(0.45, 0.55, 0.025), range(2, 3)], [frange(0.6, 2, 0.1), range(1, 1)]]
            },
            StatusEffectKey.Undying: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.05, 0.1, 0.025), range(2, 3)], [frange(0.1, 0.15, 0.025), range(1, 2)], [frange(0.15, 0.25, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.05, 0.1, 0.025), range(2, 3)], [frange(0.1, 0.15, 0.025), range(1, 2)], [frange(0.15, 0.25, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.05, 0.1, 0.025), range(2, 3)], [frange(0.1, 0.15, 0.025), range(1, 2)], [frange(0.15, 0.25, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.05, 0.1, 0.025), range(2, 3)], [frange(0.1, 0.15, 0.025), range(1, 2)], [frange(0.15, 0.25, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.05, 0.1, 0.025), range(2, 3)], [frange(0.1, 0.15, 0.025), range(1, 2)], [frange(0.15, 0.25, 0.025), range(1, 1)]]
            },
            StatusEffectKey.CannotUseAbilities: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.2, 0.25, 0.025), range(3, 4)], [frange(0.25, 0.3, 0.025), range(2, 3)], [frange(0.35, 0.5, 0.025), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.2, 0.25, 0.025), range(3, 4)], [frange(0.25, 0.3, 0.025), range(2, 3)], [frange(0.35, 0.5, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAttacked: [[frange(0.25, 0.3, 0.025), range(3, 4)], [frange(0.3, 0.35, 0.025), range(2, 3)], [frange(0.35, 0.5, 0.025), range(1, 1)]],
                ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.25, 0.3, 0.025), range(3, 4)], [frange(0.3, 0.35, 0.025), range(2, 3)], [frange(0.35, 0.5, 0.025), range(1, 1)]],
                ItemEffectCategory.OnDamaged: [[frange(0.25, 0.3, 0.025), range(3, 4)], [frange(0.3, 0.35, 0.025), range(2, 3)], [frange(0.35, 0.5, 0.025), range(1, 1)]],
            },
            StatusEffectKey.StackingDamage: {
                ItemEffectCategory.OnSuccessfulAttack: [[frange(0.35, 0.4, 0.025), range(3, 4)], [frange(0.45, 0.55, 0.025), range(2, 3)], [frange(0.6, 1, 0.05), range(1, 1)]],
                ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.35, 0.4, 0.025), range(3, 4)], [frange(0.45, 0.55, 0.025), range(2, 3)], [frange(0.6, 1, 0.05), range(1, 1)]]
            }
        },

        EffectType.ResistStatusEffect: {
            StatusEffectKey.Bleeding: {
                ItemEffectCategory.Permanent: [[frange(0.4, 1, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.Poisoned: {
                ItemEffectCategory.Permanent: [[frange(0.4, 1, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.DmgVulnerability: {
                ItemEffectCategory.Permanent: [[frange(0.4, 1, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.TurnSkipChance: {
                ItemEffectCategory.Permanent: [[frange(0.4, 1, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.Taunted: {
                ItemEffectCategory.Permanent: [[frange(0.4, 1, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.CannotTarget: {
                ItemEffectCategory.Permanent: [[frange(0.4, 1, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.DmgDebuff: {
                ItemEffectCategory.Permanent: [[frange(0.4, 1, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.Charmed: {
                ItemEffectCategory.Permanent: [[frange(0.4, 1, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.CannotAttack: {
                ItemEffectCategory.Permanent: [[frange(0.4, 1, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.Sleeping: {
                ItemEffectCategory.Permanent: [[frange(0.4, 1, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.Decaying: {
                ItemEffectCategory.Permanent: [[frange(0.4, 1, 0.05), range(-1, -1)]]
            },
            StatusEffectKey.CannotUseAbilities: {
                ItemEffectCategory.Permanent: [[frange(0.4, 1, 0.05), range(-1, -1)]]
            }
        },

        EffectType.RestoreHealth: {
            ItemEffectCategory.OnSuccessfulAttack: [[range(7, 8), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(7, 8), range(-1, -1)]],
            ItemEffectCategory.OnAttacked: [[range(7, 8), range(-1, -1)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[range(7, 8), range(-1, -1)]],
            ItemEffectCategory.OnDamaged: [[range(10, 20), range(-1, -1)]],
            ItemEffectCategory.OnTurnStart: [[range(1, 5), range(-1, -1)]],
            ItemEffectCategory.OnTurnEnd: [[range(1, 5), range(-1, -1)]]
        },
        EffectType.RestorePercentHealth: {
            ItemEffectCategory.OnSuccessfulAttack: [[frange(0.06, 0.1, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.06, 0.1, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnAttacked: [[frange(0.06, 0.1, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.06, 0.1, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnDamaged: [[frange(0.1, 0.15, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnTurnStart: [[frange(0.01, 0.05, 0), range(-1, -1)]],
            ItemEffectCategory.OnTurnEnd: [[frange(0.01, 0.05, 0), range(-1, -1)]]
        },
        EffectType.RestoreMana: {
            ItemEffectCategory.OnSuccessfulAttack: [[range(7, 8), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(7, 8), range(-1, -1)]],
            ItemEffectCategory.OnAttacked: [[range(7, 8), range(-1, -1)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[range(7, 8), range(-1, -1)]],
            ItemEffectCategory.OnDamaged: [[range(10, 20), range(-1, -1)]],
            ItemEffectCategory.OnTurnStart: [[range(1, 5), range(-1, -1)]],
            ItemEffectCategory.OnTurnEnd: [[range(1, 5), range(-1, -1)]]
        },
        EffectType.RestorePercentMana: {
            ItemEffectCategory.OnSuccessfulAttack: [[frange(0.06, 0.1, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[frange(0.06, 0.1, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnAttacked: [[frange(0.06, 0.1, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[frange(0.06, 0.1, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnDamaged: [[frange(0.1, 0.15, 0.01), range(-1, -1)]],
            ItemEffectCategory.OnTurnStart: [[frange(0.01, 0.05, 0), range(-1, -1)]],
            ItemEffectCategory.OnTurnEnd: [[frange(0.01, 0.05, 0), range(-1, -1)]]
        },

        EffectType.AdjustedManaCosts: {
            ItemEffectCategory.Permanent: [[frange(-1, -0.5, 0.05), range(-1, -1)]]
        },
        EffectType.HealingAbilityBuff: {
            ItemEffectCategory.Permanent: [[frange(0.5, 1, 0.05), range(-1, -1)]]
        },
        EffectType.AdditionalXP: {
            ItemEffectCategory.Permanent: [[frange(0.75, 1.5, 0.05), range(-1, -1)]]
        },
        EffectType.PotionMod: {
            ItemEffectCategory.Permanent: [[frange(0.5, 1, 0.05), range(-1, -1)]]
        },

        EffectType.Damage: {
            ItemEffectCategory.OnSuccessfulAttack: [[range(8, 15), range(-1, -1)]],
            ItemEffectCategory.OnSuccessfulAbilityUsed: [[range(8, 15), range(-1, -1)]],
            ItemEffectCategory.OnAttacked: [[range(8, 15), range(-1, -1)]],
            ItemEffectCategory.OnAbilityUsedAgainst: [[range(8, 15), range(-1, -1)]],
            ItemEffectCategory.OnDamaged: [[range(10, 25), range(-1, -1)]]
        },
        EffectType.ResurrectOnce: {
            ItemEffectCategory.Permanent: [[range(-1, -1), range(-1, -1)]]
        }
    }
}

EFFECT_CHANCES: Dict[EffectType, float] = {
    EffectType.CleanseStatusEffects: 0.01,

    EffectType.ConMod: 0.02,
    EffectType.StrMod: 0.02,
    EffectType.DexMod: 0.02,
    EffectType.IntMod: 0.02,
    EffectType.LckMod: 0.02,
    EffectType.MemMod: 0.02,

    EffectType.DmgReflect: 0.02,
    EffectType.DmgResist: 0.02,
    EffectType.DmgBuff: 0.02,
    EffectType.DmgBuffSelfMaxHealth: 0.005,
    EffectType.DmgBuffSelfRemainingHealth: 0.005,
    EffectType.DmgBuffOtherMaxHealth: 0.005,
    EffectType.DmgBuffOtherRemainingHealth: 0.005,

    EffectType.DmgBuffLegends: 0.02,
    EffectType.DmgBuffPoisoned: 0.02,
    EffectType.DmgBuffBleeding: 0.02,
    EffectType.DmgBuffFromDex: 0.02,
    EffectType.DmgBuffFromInt: 0.02,
    EffectType.DmgBuffFromLck: 0.02,

    EffectType.RestoreArmor: 0.02,
    EffectType.RestorePercentArmor: 0.02,
    EffectType.PiercingDmg: 0.02,
    EffectType.PiercingPercentDmg: 0.02,
    EffectType.SplashDmg: 0.02,
    EffectType.SplashPercentMaxDmg: 0.02,

    EffectType.CritDmgBuff: 0.02,
    EffectType.CritDmgReduction: 0.02,
    
    EffectType.HealthSteal: 0.02,
    EffectType.ManaSteal: 0.02,
    EffectType.AdjustedCDs: 0.02,

    EffectType.ChanceStatusEffect: 0.3,

    EffectType.ResistStatusEffect: 0.2,

    EffectType.RestoreHealth: 0.02,
    EffectType.RestorePercentHealth: 0.02,
    EffectType.RestoreMana: 0.02,
    EffectType.RestorePercentMana: 0.02,

    EffectType.AdjustedManaCosts: 0.02,
    EffectType.HealingAbilityBuff: 0.02,
    EffectType.AdditionalXP: 0.02,
    EffectType.PotionMod: 0.02,

    EffectType.Damage: 0.02,
    EffectType.ResurrectOnce: 0.02
}

if __name__ == "__main__":
    for item_index in range(2000):
        # Order should be as follows:
        #   (1) Choose random item type using a class tag, i.e. dagger, shield, etc.
        #   (2) Choose rarity at random from the list
        #   (3) Generate effects based on rarity at random
        #        (*) With a small chance to negate an effect value and change its rarity to Cursed
        #   (4) Name the item based on the effects
        #   (5) Generate armor or weapon stats based on item type
        #   (6) Based on armor/weapon stats, give it a level requirement
        #   (7) Based on the item type and armor/weapon stats, give it attribute requirements
        #   (8) Based on the level requirement, rarity, and effects, assign it a value
        #   (9) Choose a random number of slots to give the item based on its type and assign other details
        item_type = random.choice(list(CLASS_TAGS.keys()))
        rarity = random.choices(
            [Rarity.Uncommon, Rarity.Rare, Rarity.Epic, Rarity.Legendary, Rarity.Artifact],
            [0.05, 0.4, 0.3, 0.2, 0.05],
            k=1
        )[0]
        pre_curse_rarity = rarity

        item_effects = ItemEffects([], [], [], [], [], [], [], [])
        num_effects = 1
        if rarity == Rarity.Uncommon:
            num_effects = 1
        elif rarity == Rarity.Rare:
            num_effects = 1
        elif rarity == Rarity.Epic:
            num_effects = random.randint(1, 2)
        elif rarity == Rarity.Legendary:
            num_effects = random.randint(1, 3)
        elif rarity == Rarity.Artifact:
            num_effects = random.randint(1, 4)

        valid_effect_types = {et: v for et, v in EFFECT_CHANCES.items() if et in EFFECTS_BY_RARITY[rarity].keys()}

        possible_prefixes = []
        possible_suffixes = []
        
        for effect_index in range(num_effects):
            effect_type = random.choices(list(valid_effect_types.keys()), list(valid_effect_types.values()), k=1)[0]
            item_effect_cat = None
            effect = None

            if effect_type != EffectType.ResistStatusEffect and effect_type != EffectType.ChanceStatusEffect:
                possible_effects = EFFECTS_BY_RARITY[pre_curse_rarity].get(effect_type, None)
                if possible_effects is None or len(possible_effects) == 0:
                    continue
                
                item_effect_cat = random.choice(list(possible_effects.keys()))
                effect_params: List[List[float] | range] = random.choice(possible_effects[item_effect_cat])

                # Since range is exclusive but I'd like to be able to identify parameters at a glance
                # above, this remaps the range with stop + 1.
                value_range = effect_params[0]
                if isinstance(value_range, range):
                    value_range = range(value_range.start, value_range.stop + 1)
                effect_value: int | float = round(random.choice(list(value_range)), 3)

                time_range = effect_params[1]
                if isinstance(time_range, range):
                    time_range = range(time_range.start, time_range.stop + 1)
                effect_time: int = random.choice(list(time_range))

                if random.random() < 0.005 and (len(BAD_PREFIXES.get(effect_type, [])) > 0 or len(BAD_SUFFIXES.get(effect_type, [])) > 0):
                    effect_value *= -1
                    rarity = Rarity.Cursed
                    possible_prefixes = BAD_PREFIXES.get(effect_type, [])
                    possible_suffixes = BAD_SUFFIXES.get(effect_type, [])

                if rarity != Rarity.Cursed:
                    possible_prefixes += GOOD_PREFIXES.get(effect_type, [])
                    possible_suffixes += GOOD_SUFFIXES.get(effect_type, [])

                effect = Effect(effect_type, effect_value, effect_time, [], [])
            else:
                possible_statuses = EFFECTS_BY_RARITY[pre_curse_rarity].get(effect_type, None)
                if possible_statuses is None or len(possible_statuses) == 0:
                    continue
                
                status_effect_key = random.choice(list(possible_statuses.keys()))

                possible_effects = possible_statuses[status_effect_key]
                if possible_effects is None or len(possible_effects) == 0:
                    continue
                
                item_effect_cat = random.choice(list(possible_effects.keys()))

                effect_params: List[List[float] | range] = random.choice(possible_effects[item_effect_cat])

                value_range = effect_params[0]
                if isinstance(value_range, range):
                    value_range = range(value_range.start, value_range.stop + 1)
                effect_value = round(random.choice(list(value_range)), 3)

                time_range = effect_params[1]
                if isinstance(time_range, range):
                    time_range = range(time_range.start, time_range.stop + 1)
                effect_time: int = random.choice(list(time_range))

                if rarity != Rarity.Cursed:
                    possible_prefixes += GOOD_PREFIXES.get(effect_type, {}).get(status_effect_key, [])
                    possible_suffixes += GOOD_SUFFIXES.get(effect_type, {}).get(status_effect_key, [])

                effect = Effect(effect_type, effect_value, effect_time, [], [], status_effect_key)

            if item_effect_cat is not None and effect is not None:
                if item_effect_cat == ItemEffectCategory.Permanent:
                    item_effects.permanent.append(effect)
                elif item_effect_cat == ItemEffectCategory.OnTurnStart:
                    item_effects.on_turn_start.append(effect)
                elif item_effect_cat == ItemEffectCategory.OnTurnEnd:
                    item_effects.on_turn_end.append(effect)
                elif item_effect_cat == ItemEffectCategory.OnDamaged:
                    item_effects.on_damaged.append(effect)
                elif item_effect_cat == ItemEffectCategory.OnSuccessfulAbilityUsed:
                    item_effects.on_successful_ability_used.append(effect)
                elif item_effect_cat == ItemEffectCategory.OnSuccessfulAttack:
                    item_effects.on_successful_attack.append(effect)
                elif item_effect_cat == ItemEffectCategory.OnAttacked:
                    item_effects.on_attacked.append(effect)
                elif item_effect_cat == ItemEffectCategory.OnAbilityUsedAgainst:
                    item_effects.on_ability_used_against.append(effect)

        name, icon = random.choice(NAMES_AND_ICONS[item_type])
        if len(item_effects) > 0:
            prefix = ""
            suffix = ""
            if random.random() < 0.5:
                if len(possible_prefixes) != 0:
                    prefix = random.choice(possible_prefixes)
            else:
                if len(possible_suffixes) != 0:
                    suffix = random.choice(possible_suffixes)
            
            # Occasionally, items get both a suffix and a prefix!
            if random.random() < 0.25 and len(item_effects) > 1:
                if prefix == "" and len(possible_prefixes) != 0:
                    prefix = random.choice(possible_prefixes)
                elif suffix == "" and len(possible_suffixes) != 0:
                    suffix = random.choice(possible_suffixes)
            
            if prefix != "":
                name = prefix + " " + name
            if suffix != "":
                name = name + " " + suffix
        else:
            # Just skip the item if it didn't get any valid item effects
            continue
        
        attr_reqs = Attributes(0, 0, 0, 0, 0, 0)
        level_req = 0

        weapon_stats = None
        armor_stats = None
        if item_type == ClassTag.Weapon.Dagger:
            min_damage = random.randint(1, 40)
            max_damage = ceil(min_damage * 1.25) + 1
            weapon_stats = WeaponStats(min_damage, max_damage)
            
            attr_reqs.dexterity = max_damage
            level_req = 2 * max_damage

            item_effects.permanent.append(Effect(
                EffectType.DmgBuffFromDex,
                0.05,
                -1,
                [],
                []
            ))
        elif item_type == ClassTag.Weapon.Greatsword:
            min_damage = random.randint(1, 60)
            max_damage = ceil(min_damage * 1.25) + 1
            weapon_stats = WeaponStats(min_damage, max_damage)

            attr_reqs.strength = max_damage
            level_req = 2 * max_damage
        elif item_type == ClassTag.Weapon.Knuckles:
            min_damage = random.randint(1, 30)
            max_damage = ceil(min_damage * 1.25) + 1
            weapon_stats = WeaponStats(min_damage, max_damage, 2)

            attr_reqs.strength = max_damage
            level_req = int(3.5 * max_damage)
        elif item_type == ClassTag.Weapon.Spear:
            min_damage = random.randint(1, 60)
            max_damage = ceil(min_damage * 1.25) + 1
            weapon_stats = WeaponStats(min_damage, max_damage)

            attr_reqs.dexterity = max_damage
            level_req = 2 * max_damage
        elif item_type == ClassTag.Weapon.Staff:
            min_damage = random.randint(1, 60)
            max_damage = ceil(min_damage * 1.25) + 1
            weapon_stats = WeaponStats(min_damage, max_damage)

            attr_reqs.intelligence = max_damage
            level_req = 2 * max_damage

            item_effects.permanent.append(Effect(
                EffectType.DmgBuffFromInt,
                0.05,
                -1,
                [],
                []
            ))
        elif item_type == ClassTag.Weapon.Sword:
            min_damage = random.randint(1, 50)
            max_damage = ceil(min_damage * 1.25) + 1
            weapon_stats = WeaponStats(min_damage, max_damage)

            attr_reqs.strength = max(max_damage - 5, 0)
            level_req = 2 * max_damage
        elif item_type == ClassTag.Equipment.Helmet:
            armor = random.randint(5, 150)
            armor_stats = ArmorStats(armor)

            attr_reqs.constitution = int(random.uniform(0.2, 0.4) * armor)
            level_req = int(0.75 * armor)
        elif item_type == ClassTag.Equipment.ChestArmor:
            armor = random.randint(5, 300)
            armor_stats = ArmorStats(armor)

            attr_reqs.constitution = int(random.uniform(0.2, 0.4) * armor)
            level_req = int(0.5 * armor)
        elif item_type == ClassTag.Equipment.Gloves:
            armor = random.randint(5, 100)
            armor_stats = ArmorStats(armor)

            attr_reqs.constitution = int(random.uniform(0.2, 0.4) * armor)
            level_req = int(1.4 * armor) if armor < 60 else int(0.8 * armor)
        elif item_type == ClassTag.Equipment.Leggings:
            armor = random.randint(5, 150)
            armor_stats = ArmorStats(armor)

            attr_reqs.constitution = int(random.uniform(0.2, 0.4) * armor)
            level_req = int(1.2 * armor) if armor < 60 else int(0.7 * armor)
        elif item_type == ClassTag.Equipment.Boots:
            armor = random.randint(5, 150)
            armor_stats = ArmorStats(armor)

            attr_reqs.constitution = int(random.uniform(0.2, 0.4) * armor)
            level_req = int(1.05 * armor) if armor < 60 else int(0.6 * armor)
        elif item_type == ClassTag.Weapon.Shield:
            armor = random.randint(5, 200)
            armor_stats = ArmorStats(armor)

            attr_reqs.constitution = int(random.uniform(0.2, 0.4) * armor)
            level_req = int(0.9 * armor) if armor < 60 else int(0.7 * armor)
        elif item_type == ClassTag.Equipment.Ring or item_type == ClassTag.Equipment.Amulet:
            level_req = 10 * len(item_effects)

        num_slots = random.choice(list(SLOTS_PER_ITEM_TYPE[item_type]))

        value = 15 * level_req
        if rarity == Rarity.Uncommon:
            value *= 2 + len(item_effects)
        elif rarity == Rarity.Rare:
            value *= 3 + len(item_effects)
        elif rarity == Rarity.Epic:
            value *= 4 + len(item_effects)
        elif rarity == Rarity.Legendary:
            value *= 5 + len(item_effects)
        elif rarity == Rarity.Artifact:
            value *= 6 + len(item_effects)
        value += 5 * random.randint(level_req, 2 * level_req)
        value += 250 * num_slots

        path_name = name.replace(" ", "_").replace("'", "").lower()
        key = ""
        if item_type == ClassTag.Weapon.Dagger:
            key = f"items/weapon/dagger/{path_name}"
        elif item_type == ClassTag.Weapon.Greatsword:
            key = f"items/weapon/greatsword/{path_name}"
        elif item_type == ClassTag.Weapon.Knuckles:
            key = f"items/weapon/knuckles/{path_name}"
        elif item_type == ClassTag.Weapon.Spear:
            key = f"items/weapon/spear/{path_name}"
        elif item_type == ClassTag.Weapon.Staff:
            key = f"items/weapon/staff/{path_name}"
        elif item_type == ClassTag.Weapon.Sword:
            key = f"items/weapon/sword/{path_name}"
        elif item_type == ClassTag.Equipment.Helmet:
            key = f"items/equipment/helmet/{path_name}"
        elif item_type == ClassTag.Equipment.ChestArmor:
            key = f"items/equipment/chest_armor/{path_name}"
        elif item_type == ClassTag.Equipment.Gloves:
            key = f"items/equipment/gloves/{path_name}"
        elif item_type == ClassTag.Equipment.Leggings:
            key = f"items/equipment/leggings/{path_name}"
        elif item_type == ClassTag.Equipment.Boots:
            key = f"items/equipment/boots/{path_name}"
        elif item_type == ClassTag.Weapon.Shield:
            key = f"items/weapon/shield/{path_name}"
        elif item_type == ClassTag.Equipment.Ring:
            key = f"items/equipment/ring/{path_name}"
        elif item_type == ClassTag.Equipment.Amulet:
            key = f"items/equipment/amulet/{path_name}"

        item = {
            "key": key,
            "icon": icon,
            "name": name,
            "value": value,
            "rarity": str(rarity),
            "description": "",
            "flavor_text": "",
            "class_tags": [str(ct) for ct in CLASS_TAGS[item_type]],
            "state_tags": [],
            "count": 1,
            "level_requirement": level_req,
            "altering_item_keys": ["" for _ in range(num_slots)]
        }

        if len(item_effects) > 0:
            item["item_effects"] = {}
            item["item_effects"]["permanent"] = [effect.__dict__ for effect in item_effects.permanent]
            item["item_effects"]["on_turn_start"] = [effect.__dict__ for effect in item_effects.on_turn_start]
            item["item_effects"]["on_turn_end"] = [effect.__dict__ for effect in item_effects.on_turn_end]
            item["item_effects"]["on_damaged"] = [effect.__dict__ for effect in item_effects.on_damaged]
            item["item_effects"]["on_successful_ability_used"] = [effect.__dict__ for effect in item_effects.on_successful_ability_used]
            item["item_effects"]["on_successful_attack"] = [effect.__dict__ for effect in item_effects.on_successful_attack]
            item["item_effects"]["on_attacked"] = [effect.__dict__ for effect in item_effects.on_attacked]
            item["item_effects"]["on_ability_used_against"] = [effect.__dict__ for effect in item_effects.on_ability_used_against]

        if weapon_stats is not None:
            item["weapon_stats"] = {
                "min_damage": weapon_stats._min_damage,
                "max_damage": weapon_stats._max_damage,
                "num_targets": weapon_stats._num_targets
            }
        if armor_stats is not None:
            item["armor_stats"] = {
                "armor": armor_stats._armor_amount
            }
        
        attr_requirements_dict = {}
        if attr_reqs.constitution > 0:
            attr_requirements_dict["constitution"] = attr_reqs.constitution
        if attr_reqs.strength > 0:
            attr_requirements_dict["strength"] = attr_reqs.strength
        if attr_reqs.dexterity > 0:
            attr_requirements_dict["dexterity"] = attr_reqs.dexterity
        if attr_reqs.intelligence > 0:
            attr_requirements_dict["intelligence"] = attr_reqs.intelligence
        if attr_reqs.luck > 0:
            attr_requirements_dict["luck"] = attr_reqs.luck
        if attr_reqs.memory > 0:
            attr_requirements_dict["memory"] = attr_reqs.memory

        json_str = json.dumps(item, indent=4)
        filename = f"./generated_items/{key}.json"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as file:
            file.write(json_str)
