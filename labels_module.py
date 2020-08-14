def get_attribute_labels():
    labels = ['strength', 'endurance', 'coordination', 'quickness', 'focus', 'self', 'health', 'stamina', 'mana']
    return labels


def get_primary_attribute_labels():
    labels = ['strength', 'endurance', 'coordination', 'quickness', 'focus', 'self']
    return labels

def get_secondary_attribute_labels():
    labels = ['health', 'stamina', 'mana']
    return labels


def get_damage_labels():
    labels = ['slash', 'pierce', 'bludge', 'cold', 'fire', 'acid', 'electric']
    return labels


def get_skill_labels():
    labels = ['melee defense', 'magic defense', 'missile defense', 'melee offense', 'finesse weapons', 'magic offense',
              'missile weapons']
    return labels


def get_armor_labels():
    labels = ['armor_vs_slash', 'armor_vs_pierce', 'armor_vs_bludgeon', 'armor_vs_cold', 'armor_vs_fire',
              'armor_vs_acid', 'armor_vs_electric', 'base_armor']
    return labels


def get_damage_type_int(damage_type):
    damage_types = {'undefined': 0, 'slash': 1, 'pierce': 2, 'bludge': 4, 'cold': 8, 'fire': 16, 'acid': 32,
                    'electric': 64, 'health': 128, 'stamina': 256, 'mana': 512, 'nether': 1024}

    if damage_type in damage_types:
        return damage_types[damage_type]
    else:
        return damage_types['undefined']


def get_creature_dict():
    monsters = {1: "Olthoi", 2: "Banderling", 3: "Drudge", 4: "Mosswart", 5: "Lugian", 6: "Tumerok", 7: "Mite",
                8: "Tusker", 9: "Phyntos Wasp", 10: "Rat", 11: "Auroch", 12: "Cow", 13: "Golem", 14: "Undead",
                15: "Gromnie", 16: "Reedshark", 17: "Armoredillo", 18: "Fae", 19: "Virindi", 20: "Wisp",
                21: "Knathtead", 22: "Shadow", 23: "Mattekar", 24: "Mumiyah", 25: "Rabbit", 26: "Sclavus",
                27: "Shallows Shark", 28: "Monouga", 29: "Zefir", 30: "Skeleton", 31: "Human", 32: "Shreth",
                33: "Chittick", 34: "Moarsman", 35: "Olthoi Larvae", 36: "Slithis", 38: "Fire Elemental",
                39: "Snowman", 40: "Unknown", 41: "Bunny", 42: "Lightning Elemental", 44: "Grievver", 45: "Niffis",
                46: "Ursuin", 47: "Crystal", 48: "Hollow Minion", 49: "Scarecrow", 50: "Idol", 51: "Empyrean",
                52: "Hopeslayer", 53: "Doll", 54: "Marionette", 55: "Carenzi", 56: "Siraluun", 57: "Aun Tumerok",
                58: "Hea Tumerok", 59: "Simulacrum", 60: "Acid Elemental", 61: "Frost Elemental", 62: "Elemental",
                63: "Statue", 64: "Wall", 65: "Altered Human", 66: "Device", 67: "Harbinger",
                68: "Dark Sarcophagus", 69: "Chicken", 70: "Gotrok Lugian", 71: "Margul", 72: "Bleached Rabbit",
                73: "Nasty Rabbit", 74: "Grimacing Rabbit", 75: "Burun", 76: "Target", 77: "Ghost", 78: "Fiun",
                79: "Eater", 80: "Penguin", 81: "Ruschk", 82: "Thrungus", 83: "Viamontian Knight", 84: "Remoran",
                85: "Swarm", 86: "Moar", 87: "Enchanted Arms", 88: "Sleech", 89: "Mukkir", 90: "Merwart",
                91: "Food", 92: "Paradox Olthoi", 94: "Energy", 95: "Apparition", 96: "Aerbax", 97: "Touched",
                98: "Blighted Moarsman", 99: "Gear Knight", 100: "Gurog", 101: "A'nekshay"}

    return monsters


def get_creature_type_label(creature_type_int):
    """Returns the label corresponding to a creature type int (int stats 2)"""
    creature_dict = get_creature_dict()

    creature_type_int = int(creature_type_int)

    if creature_type_int in creature_dict:
        return creature_dict[creature_type_int]
    else:
        return None


def get_all_creature_types():
    creature_dict = get_creature_dict()
    return list(creature_dict.values())


def get_creature_type_int(creature_type_label):
    """Returns the creature type integer corresponding to the given item type label."""
    my_dict = get_creature_dict()
    # keys become values, values become keys
    flipped_dict = dict((v, k) for k, v in my_dict.items())
    return flipped_dict[creature_type_label]


def get_skill_id(skill_name):
    """Get the int representation of a skill."""
    skill_types = {'MeleeDefense': 6, 'MissileDefense': 7, 'MagicDefense': 15, 'ManaConversion': 16, 'Jump': 22,
                   'Run': 24, 'CreatureMagic': 31, 'ItemMagic': 32, 'LifeMagic': 33, 'WarMagic': 34,
                   'TwoHanded': 41, 'VoidMagic': 43, 'HeavyWeapons': 44, 'LightWeapons': 45,
                   'FinesseWeapons': 46, 'MissileWeapons': 47, 'Shield': 48, 'DualWield': 49, 'Recklessness': 50,
                   'SneakAttack': 51, 'DirtyFighting': 52}

    if skill_name in skill_types:
        return skill_types[skill_name]
    else:
        return None


def get_item_types():
    types = {
        1: "melee weapon",
        2: "armor",
        4: "clothing",
        8: "jewelry",
        16: "creature",
        32: "food",
        64: "money",
        128: "misc",
        256: "missile weapon",
        512: "container",
        1024: "useless",
        2048: "gem",
        4096: "spell components",
        8192: "writable",
        16384: "key",
        32768: "caster",
        65536: "portal",
        131072: "lockable",
        262144: "promissory note",
        524288: "manastone",
        4481568: "grocer",
        4194304: "cooking base",
        8388608: "alchemy base",
        16777216: "fletching base",
        33554432: "cooking intermediate",
        67108864: "alchemy intermediate",
        134217728: "fletching intermediate",
        536870912: "tinkering tool",
        1073741824: "tinkering material",
        1208248231: "shopkeep"
    }

    return types


def get_all_item_types():
    """Returns a list of all item type labels."""
    my_dict = get_item_types()
    return list(my_dict.values())


def get_item_type_label(item_type_int):
    """Returns the item type label corresponding to the given item type integer.
    If no label is found, returns the integer."""
    my_dict = get_item_types()

    if item_type_int in my_dict:
        return my_dict[item_type_int]
    else:
        return str(item_type_int)


def get_item_type_int(item_type_label):
    """Returns the item type integer corresponding to the given item type label."""
    my_dict = get_item_types()
    # keys become values, values become keys
    flipped_dict = dict((v, k) for k, v in my_dict.items())
    return flipped_dict[item_type_label]
