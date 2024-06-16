import statistics

import file_helper


class Skill:
    def __init__(self, skill_id, name, value):
        self.skill_id = int(skill_id)
        self.name = name
        self.value = int(value)
        if self.value < 0:
            self.value = 0

    def get_type(self):
        magic_offense = ['LifeMagic', 'WarMagic', 'CreatureMagic', 'VoidMagic']
        melee_offense = ['HeavyWeapons', 'LightWeapons', 'TwoHandedCombat',
                         'DirtyFighting', 'FinesseWeapons', 'SneakAttack']
        missile_offense = ['MissileWeapons']
        if self.name in magic_offense:
            return "magic offense"
        elif self.name in melee_offense:
            return "melee offense"
        elif self.name in missile_offense:
            return "missile offense"
        elif self.name == "MagicDefense":
            return "magic defense"
        elif self.name == "MeleeDefense":
            return "melee defense"
        elif self.name == "MissileDefense":
            return "missile defense"
        else:
            return "other"


def get_skill_id(skill_name):
    """Get the int id for a skill."""

    skills = {
        0: "Undefined",
        1: "Axe",
        2: "Bow",
        3: "Crossbow",
        4: "Dagger",
        5: "Mace",
        6: "MeleeDefense",
        7: "MissileDefense",
        8: "Sling",
        9: "Spear",
        10: "Staff",
        11: "Sword",
        12: "ThrownWeapon",
        13: "UnarmedCombat",
        14: "ArcaneLore",
        15: "MagicDefense",
        16: "ManaConversion",
        17: "Spellcraft",
        18: "ItemAppraisal",
        19: "PersonalAppraisal",
        20: "Deception",
        21: "Healing",
        22: "Jump",
        23: "Lockpick",
        24: "Run",
        25: "Awareness",
        26: "ArmsAndArmorRepair",
        27: "CreatureAppraisal",
        28: "WeaponAppraisal",
        29: "ArmorAppraisal",
        30: "MagicItemAppraisal",
        31: "CreatureEnchantment",
        32: "ItemEnchantment",
        33: "LifeMagic",
        34: "WarMagic",
        35: "Leadership",
        36: "Loyalty",
        37: "Fletching",
        38: "Alchemy",
        39: "Cooking",
        40: "Salvaging",
        41: "TwoHandedCombat",
        42: "Gearcraft",
        43: "VoidMagic",
        44: "HeavyWeapons",
        45: "LightWeapons",
        46: "FinesseWeapons",
        47: "MissileWeapons",
        48: "Shield",
        49: "DualWield",
        50: "Recklessness",
        51: "SneakAttack",
        52: "DirtyFighting",
        53: "Challenge",
        54: "Summoning"
    }

    skills = {value: key for key, value in skills.items()}

    return skills.get(skill_name)


def get_skill_table(commands):
    """Returns a list with Skill objects, where each object has a skill id, name and base value of the skill."""
    wcid = file_helper.get_wcid(commands)
    skill_list = []

    for command in commands:
        if str("`weenie_properties_skill`") in command:

            split_command = command.split("(")

            # need columns 1 and 5
            for line in split_command:
                if str(wcid) in line:
                    split_comma = line.split(",", 2)
                    my_key = int(split_comma[1].strip())
                    split_other = split_comma[2].split(")")
                    my_val = split_other[0].strip()
                    split_more = my_val.split(",")
                    my_val = split_more[3].strip()
                    comment = "".join(split_other[1].rsplit(",", 1)).strip()
                    comment = comment.replace("*/", "")
                    comment = comment.replace("/*", "")
                    comment = comment.replace("Specialized", "")
                    comment = comment.replace("Trained", "")
                    comment = comment.strip()

                    if comment == "CreatureMagic":
                        comment = "CreatureEnchantment"
                    elif comment == "ItemMagic":
                        comment = "ItemEnchantment"
                    elif comment == "TwoHanded":
                        comment = "TwoHandedCombat"

                    skill_list.append(Skill(my_key, comment, my_val))

    return skill_list


def get_attribute_bonus(attributes, name):
    """Return how much attributes would add to a base skill."""

    magic = ["LifeMagic", "WarMagic", "CreatureEnchantment", "ItemEnchantment", "VoidMagic"]
    str_based = ["HeavyWeapons", "LightWeapons", "TwoHandedCombat", "DirtyFighting",
                 "Axe", "Mace", "Sword", "Spear", "Staff", "UnarmedCombat"]
    quick_based = ["FinesseWeapons", "SneakAttack", "Dagger"]
    coord_based = ["MissileWeapons", "Bow", "Crossbow", "ThrownWeapon"]

    attribute_bonus = 0
    match = True

    if name in magic:
        attribute_bonus = round((attributes['focus'] + attributes['self']) / 4)
    elif name in str_based:
        attribute_bonus = round((attributes['strength'] + attributes['coordination']) / 3)
    elif name in quick_based:
        attribute_bonus = round((attributes['coordination'] + attributes['quickness']) / 3)
    elif name == "DualWield":
        attribute_bonus = round((attributes['coordination'] + attributes['coordination']) / 3)
    elif name in coord_based:
        attribute_bonus = round(attributes['coordination'] / 2)
    elif name == "MagicDefense":
        attribute_bonus = round((attributes['focus'] + attributes['self']) / 7)
    elif name == "MeleeDefense":
        attribute_bonus = round((attributes['coordination'] + attributes['quickness']) / 3)
    elif name == "MissileDefense":
        attribute_bonus = round((attributes['coordination'] + attributes['quickness']) / 5)
    elif name == "Shield":
        attribute_bonus = round((attributes['strength'] + attributes['coordination']) / 2)
    elif name == "Run":
        attribute_bonus = attributes['quickness']
    elif name == "ManaConversion":
        attribute_bonus = round((attributes['focus'] + attributes['self']) / 6)
    elif name == "Jump":
        attribute_bonus = round((attributes['strength'] + attributes['coordination']) / 2)
    else:
        match = False

    if match:
        return attribute_bonus
    else:
        return 0


def make_skill_table(wcid, skills):
    """Make a new skill table."""
    counter = 0
    new_command = "\n\nINSERT INTO `weenie_properties_skill` (`object_Id`, `type`, `level_From_P_P`, `s_a_c`, `p_p`, `init_Level`, `resistance_At_Last_Check`, `last_Used_Time`)\n"

    skill_list = []
    for name, val in skills.items():
        skill_list.append(Skill(get_skill_id(name), name, val))
    # sort by id, x is passed into the lambda, here x is each skill object, x.skill_id is returned
    skill_list.sort(key=lambda x: x.skill_id)

    for skill in skill_list:
        # padding
        skill_id = skill.skill_id
        if skill_id < 10:
            skill_id = " " + str(skill_id)
        skill_val = skill.value
        if skill_val < 100:
            skill_val = " " + str(skill_val)

        if counter == 0:
            entry = f"""VALUES ({wcid}, {skill_id}, 0, 2, 0, {skill_val}, 0, 0) /* {skill.name} */\n"""
        else:
            entry = f"""     , ({wcid}, {skill_id}, 0, 2, 0, {skill_val}, 0, 0) /* {skill.name} */\n"""

        new_command += entry
        counter += 1

    new_command = "".join(new_command.rsplit("\n", 1))

    return new_command


def skill_look_up(name):
    with open('pcap_creature_skills.txt') as my_file:

        melee_attack = []
        melee_defense = []

        missile_attack = []
        missile_defense = []

        magic_attack = []
        magic_defense = []

        my_dict = {'melee offense': melee_attack,
                   'melee defense': melee_defense,
                   'missile offense': missile_attack,
                   'missile defense': missile_defense,
                   'magic offense': magic_attack,
                   'magic defense': magic_defense
                   }

        for line in my_file:
            split = line.split("\t")

            if split[0] == name:

                if split[1] == "ATTACKER_NOTIFICATION_EVENT" and split[2] == "MISSILE_WEAPONS_SKILL":
                    # print('missile defense', split[3], 'hits', split[4])
                    for i in range(int(split[4])):
                        missile_defense.append(int(split[3]))

                elif split[1] == "ATTACKER_NOTIFICATION_EVENT" and "WEAPONS_SKILL" in split[2]:
                    # print('melee defense', split[3], 'hits', split[4])
                    for i in range(int(split[4])):
                        melee_defense.append(int(split[3]))

                elif split[1] == "ATTACKER_NOTIFICATION_EVENT" and split[2] == "TWO_HANDED_COMBAT_SKILL":
                    # print('melee defense', split[3], 'hits', split[4])
                    for i in range(int(split[4])):
                        melee_defense.append(int(split[3]))

                elif split[1] == "EVASION_DEFENDER_NOTIFICATION_EVENT" and split[2] == "MELEE_DEFENSE_SKILL":
                    # print('melee attack', split[3], 'hits', split[4])
                    for i in range(int(split[4])):
                        melee_attack.append(int(split[3]))

                elif split[1] == "EVASION_DEFENDER_NOTIFICATION_EVENT" and split[2] == "MISSILE_DEFENSE_SKILL":
                    # print('missile attack', split[3], 'hits', split[4])
                    for i in range(int(split[4])):
                        missile_attack.append(int(split[3]))

                elif split[1] == "Textbox Resist" and split[2] == "MAGIC_DEFENSE_SKILL":
                    # print('magic attack', split[3], 'hits', split[4])
                    for i in range(int(split[4])):
                        magic_attack.append(int(split[3]))

        skill_levels = {}

        for k, v in my_dict.items():
            if len(v) > 1:
                avg = round(statistics.mean(v))
                min_val = min(v)
                max_val = max(v)
                skill_levels[k] = (avg, min_val, max_val)
            elif len(v) == 1:
                skill_levels[k] = (v[0], 0, 0)
            else:
                skill_levels[k] = (0, 0, 0)

        return skill_levels
