import file_helper


class Spell:
    def __init__(self, spell_id, pr, name):
        self.id = spell_id
        self.pr = pr
        self.name = name


def get_spellbook(commands):
    """Returns a list with Skill objects, where each object has a skill id, name and base value of the skill."""
    wcid = file_helper.get_wcid(commands)

    for command in commands:
        if str("`weenie_properties_spell_book`") in command:
            spell_list = []
            split_command = command.split("(")

            # need columns 1 and 2
            for line in split_command:
                if str(wcid) in line:

                    # get substring between ( ) and split by comma
                    start_index = line.find("(") + 1
                    end_index = line.find(")")

                    if start_index != -1 and end_index != -1:
                        sub = line[start_index:end_index].strip()
                        sub_split = sub.split(",")
                        # print(sub_split)

                        if len(sub_split) == 3:
                            spell_id = int(sub_split[1].strip())
                            spell_pr = float(sub_split[2].strip())
                            # print(first_number)
                            # print(second_number)

                            # get the comment between /* and */
                            comment_start = line.find("/*")
                            comment_end = line.find("*/")

                            if comment_start != -1 and comment_end != -1:
                                comment = line[comment_start + 2:comment_end].strip()
                                spell_list.append(Spell(spell_id, spell_pr, comment))

            return spell_list


def make_spellbook(wcid, spells):
    """Make a new spellbook."""
    counter = 0
    new_command = "\n\nINSERT INTO `weenie_properties_spell_book` (`object_Id`, `spell`, `probability`)\n"

    for spell in spells:

        padded_spell_id = f"{spell.id:4d}"

        if counter == 0:
            entry = f"""VALUES ({wcid},  {padded_spell_id},  {spell.pr}) /* {spell.name} */\n"""
        else:
            entry = f"""     , ({wcid},  {padded_spell_id},  {spell.pr}) /* {spell.name} */\n"""

        new_command += entry
        counter += 1

    new_command = "".join(new_command.rsplit("\n", 1))

    return new_command


def upgrade_spell(spell, spell_dict, special_names, flipped_names):
    """Upgrades the spell to the next higher level. If there is no next level, returns the
    spell as is."""
    upgraded = None

    # get spell level as an integer
    level = get_spell_level(spell.name, flipped_names)
    if level == 7:
        if spell.name in flipped_names.keys():
            regular_name = flipped_names[spell.name]
            spell.name = regular_name

    next_level = level + 1
    if next_level > 8:
        next_level = 8

    old_name = spell.name.split(" ")
    # spell name without the Roman numeral
    old_name = " ".join(old_name[:-1])

    if next_level == 8:
        new_name = "Incantation of " + old_name
    else:
        # get Roman numeral for the next level
        next_roman = get_roman_level(next_level)
        # append the Roman numeral for the next level to the name
        new_name = old_name + " " + next_roman
        # print(new_name)
        if next_level == 7:
            if new_name in special_names.keys():
                new_name = special_names[new_name]

    if new_name in spell_dict.keys():
        upgraded = Spell(spell_dict[new_name], spell.pr, new_name)
        # check for special cases, convert yellow lightning bolt / arc to standard purple
        if upgraded.id == 6198:
            upgraded.id = 4451
        elif upgraded.id == 6199:
            upgraded.id = 4426

    if upgraded is not None:
        return upgraded
    else:
        return spell


def load_spell_dict():
    # key = spell name, value = spell id
    spell_dict = {}

    with open('spell_names.txt', 'r', encoding='utf-8') as file:
        for line in file:
            spell_id, spell_name = line.strip().split(',', 1)
            # print(spell_id, spell_name)
            spell_id = int(spell_id)
            spell_dict[spell_name] = spell_id

    return spell_dict


def load_special_dict():
    # key = regular level 7 spell name, value = actual, special level 7 name
    spell_dict = {}

    with open('spell_names7.txt', 'r', encoding='utf-8') as file:
        for line in file:
            regular_name, special_name = line.strip().split('\t', 1)
            spell_dict[regular_name] = special_name

    return spell_dict


def get_spell_level(spell_name, flipped_names):
    level_dict = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8}

    level = 1
    split_name = spell_name.split(" ")
    if split_name[-1] in level_dict.keys():
        level = level_dict[split_name[-1]]

    # check for special cases
    if spell_name in flipped_names.keys():
        level = 7
    elif "Incantation" in spell_name:
        level = 8

    return level


def get_roman_level(spell_level):
    level_dict = {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI', 7: 'VII', 8: 'VIII'}
    if spell_level > 8:
        spell_level = 8
    return level_dict[spell_level]
