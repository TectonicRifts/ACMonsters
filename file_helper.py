import json
import tkinter as tk
from tkinter import END
from pathlib import Path
import tkinter.messagebox
import os
import statistics
import re
import labels_module


def write_sql_file(file_name, commands):
    Path("output/renumbered").mkdir(parents=True, exist_ok=True)

    with open("output/renumbered/" + file_name, 'w') as file_object:
        for command in commands:
            file_object.write(command)


def delete_sql_command(commands, tag):

    tag = get_tag_name(tag)
    my_list = []

    for command in commands:
        if tag in command:
            pass
        else:
            if command.strip() != "":
                my_list.append(command)

    return my_list


def get_tag_name(tag):
    tags = {"int": "`weenie_properties_int`", "bool": "`weenie_properties_bool`", "float": "`weenie_properties_float`",
            "string": "`weenie_properties_string`", "str": "`weenie_properties_string`",
            "did": "`weenie_properties_d_i_d`"}

    if tag in tags.keys():
        return tags[tag]
    else:
        return None


def get_longest(my_dict):
    longest_key = 0
    longest_val = 0

    for k, v in sorted(my_dict.items()):

        value_len = len(str(v[0]))
        if value_len > longest_val:
            longest_val = value_len

        key_len = len(str(k))
        if key_len > longest_key:
            longest_key = key_len

    longest_key += 1
    longest_val += 1

    return longest_key, longest_val


def set_body_table(commands, template_wcid, body_table):

    wcid = re.findall('[0-9]+', (commands[0]))[0]
    tag = "`weenie_properties_body_part`"
    my_list = []
    body_table = body_table.replace(template_wcid, wcid)

    has_command = False

    for command in commands:
        if str(tag) in command:
            has_command = True

    if has_command:
        for command in commands:
            if str(tag) in command:  # append new instead of existing
                my_list.append(body_table)
            else:
                if command.strip() != "":
                    my_list.append(command)
    else:
        commands.append(body_table)
        return commands

    return my_list


def get_destination(wcid, loc_paste):
    loc_paste = loc_paste.strip()
    split_loc = loc_paste.split(" ")

    cell_hex = split_loc[0]
    cell_dec = int(cell_hex, 16)

    ox = split_loc[1].replace("[", "")
    oy = split_loc[2]
    oz = split_loc[3].replace("]", "")

    aw = split_loc[4]
    ax = split_loc[5]
    ay = split_loc[6]
    az = split_loc[7]

    comment = "/* @teleloc " + loc_paste + " */;"
    new_value = f"""VALUES ({wcid}, 2, "{str(cell_dec)}", "{str(ox)}", "{str(oy)}", "{str(oz)}", "{str(aw)}", "{str(ax)} + ", "{str(ay)}", "{str(az)}") /* Destination */\n"{comment}"""

    return new_value


def get_property(commands, tag, key):
    tag = get_tag_name(tag)
    key = int(key)

    wcid = re.findall('[0-9]+', (commands[0]))[0]  # find number string in first line

    for command in commands:
        if str(tag) in command:

            my_dict = {}
            split_command = command.split("(")

            for line in split_command:
                if str(wcid) in line:
                    split_comma = line.split(",", 2)

                    my_key = int(split_comma[1].strip())

                    split_other = split_comma[2].split(")")
                    my_val = split_other[0].strip()
                    comment = "".join(split_other[1].rsplit(",", 1)).strip()

                    my_tuple = (my_val, comment)
                    my_dict[my_key] = my_tuple

            if key in my_dict:
                return my_dict[key]
            else:
                return None


def set_position(commands, loc_paste):
    tag = "`weenie_properties_position`"

    my_list = []
    wcid = re.findall('[0-9]+', (commands[0]))[0]  # find number string in first line

    for command in commands:
        if str(tag) in command:
            my_list.append(get_destination(wcid, loc_paste))

        else:
            if command.strip() != "":
                my_list.append(command + ";")

    return my_list


def set_property(commands, tag, key, val, desc):
    """Set a property (int, bool, float, string or did) to a weenie (in sql format). If the
    property already exists, the value is updated.This function does not work for position. """

    tag = get_tag_name(tag)
    key = int(key)

    my_list = []
    wcid = re.findall('[0-9]+', (commands[0]))[0]  # find number string in first line

    has_tag = False

    for command in commands:
        if str(tag) in command:
            has_tag = True

    if has_tag:
        pass
    else:
        new_command = f"""\n\nINSERT INTO {tag} (`object_Id`, `type`, `value`)\nVALUES """
        new_command += f"""({wcid}, {key}, {val}) {desc}"""
        commands.append(new_command)
        return commands

    for command in commands:
        if str(tag) in command:

            my_dict = {}
            split_command = command.split("(")

            for line in split_command:
                if str(wcid) in line:
                    split_comma = line.split(",", 2)

                    my_key = int(split_comma[1].strip())

                    split_other = split_comma[2].split(")")
                    my_val = split_other[0].strip()
                    comment = "".join(split_other[1].rsplit(",", 1)).strip()

                    my_tuple = (my_val, comment)
                    my_dict[my_key] = my_tuple

            # if key not in my_dict.keys():
            my_dict[key] = (val, desc)

            new_command = f"""\n\nINSERT INTO {tag} (`object_Id`, `type`, `value`)\nVALUES """

            i = 0
            total_lines = len(my_dict)

            # figure out padding
            my_tuple = get_longest(my_dict)
            longest_key = my_tuple[0]
            longest_val = my_tuple[1]

            for k, v in sorted(my_dict.items()):

                my_justified_value = str(v[0]).rjust(longest_val, " ")
                my_justified_key = str(k).rjust(longest_key, " ")

                if i == 0:
                    new_command = new_command + f"""({wcid},{my_justified_key},{my_justified_value}) {v[1]}"""
                    if i < (total_lines - 1):
                        new_command = new_command + "\n    "
                else:
                    new_command = new_command + f""" , ({wcid},{my_justified_key},{my_justified_value}) {v[1]}"""
                    if i < (total_lines - 1):
                        new_command = new_command + "\n    "
                i += 1

            my_list.append(new_command)

        else:
            if command.strip() != "":
                my_list.append(command)

    return my_list


def get_skill_table(wcid, skills):
    counter = 0
    new_command = "\n\nINSERT INTO `weenie_properties_skill` (`object_Id`, `type`, `level_From_P_P`, `s_a_c`, `p_p`, `init_Level`, `resistance_At_Last_Check`, `last_Used_Time`)\n"

    for skill, val, in sorted(skills.items()):

        if val < 0:
            skills[skill] = 0

        key = labels_module.get_skill_id(skill)

        if counter == 0:
            entry = f"""VALUES ({wcid},  {key}, 0, 2, 0, {val}, 0, 0) /* {skill} */\n"""
        else:
            entry = f"""     , ({wcid},  {key}, 0, 2, 0, {val}, 0, 0) /* {skill} */\n"""

        new_command += entry
        counter += 1

    new_command = "".join(new_command.rsplit("\n", 1))

    return new_command


def set_spell_list(commands, key, val, desc):
    """Set a property (int, bool, float, string or did) to a weenie (in sql format). If the
    property already exists, the value is updated.This function does not work for position. """

    tag = "`weenie_properties_spell_book`"
    key = int(key)

    my_list = []
    wcid = re.findall('[0-9]+', (commands[0]))[0]  # find number string in first line

    for command in commands:
        if str(tag) in command:

            my_dict = {}
            split_command = command.split("(")

            for line in split_command:
                if str(wcid) in line:
                    split_comma = line.split(",", 2)

                    my_key = int(split_comma[1].strip())

                    split_other = split_comma[2].split(")")
                    my_val = split_other[0].strip()
                    comment = "".join(split_other[1].rsplit(",", 1)).strip()

                    my_tuple = (my_val, comment)
                    my_dict[my_key] = my_tuple

            # if key not in my_dict.keys():
            my_dict[key] = (val, desc)

            new_command = f"""\n\nINSERT INTO {tag} (`object_Id`, `spell`, `probability`)\nVALUES """

            i = 0
            total_lines = len(my_dict)

            # figure out padding
            my_tuple = get_longest(my_dict)
            longest_key = my_tuple[0]
            longest_val = my_tuple[1]

            for k, v in sorted(my_dict.items()):

                my_justified_value = str(v[0]).rjust(longest_val, " ")
                my_justified_key = str(k).rjust(longest_key, " ")

                if i == 0:
                    new_command = new_command + f"""({wcid},{my_justified_key},{my_justified_value}) {v[1]}"""
                    if i < (total_lines - 1):
                        new_command = new_command + "\n    "
                else:
                    new_command = new_command + f""" , ({wcid},{my_justified_key},{my_justified_value}) {v[1]}"""
                    if i < (total_lines - 1):
                        new_command = new_command + "\n    "
                i += 1

            my_list.append(new_command + ";")

        else:
            if command.strip() != "":
                my_list.append(command + ";")

    return my_list


def set_attribute_1(commands, key, val, desc, do_override):
    tag = "`weenie_properties_attribute`"
    key = int(key)

    my_list = []
    wcid = re.findall('[0-9]+', (commands[0]))[0]  # find number string in first line

    for command in commands:
        if str(tag) in command:

            my_dict = {}
            split_command = command.split("(")

            for line in split_command:
                if str(wcid) in line:
                    split_comma = line.split(",", 2)

                    my_key = int(split_comma[1].strip())
                    # print("My key: " + str(my_key))

                    split_other = split_comma[2].split(")")
                    my_val = split_other[0].strip()
                    split_more = my_val.split(",", 1)
                    my_val = split_more[0]
                    # print("My val: " + str(my_val))
                    comment = "".join(split_other[1].rsplit(",", 1)).strip()

                    my_tuple = (my_val, comment)
                    my_dict[my_key] = my_tuple

            # if true, replace existing value
            if do_override:
                my_dict[key] = (val, desc)
            else:
                if key not in my_dict.keys():
                    my_dict[key] = (val, desc)

            param_list = "(`object_Id`, `type`, `init_Level`, `level_From_C_P`, `c_P_Spent`)"
            new_command = f"""\n\nINSERT INTO {tag} {param_list}\nVALUES """

            i = 0
            total_lines = len(my_dict)

            # figure out padding
            my_tuple = get_longest(my_dict)
            longest_key = my_tuple[0]
            longest_val = my_tuple[1]

            for k, v in sorted(my_dict.items()):

                my_justified_value = str(v[0]).rjust(longest_val, " ")
                my_justified_key = str(k).rjust(longest_key, " ")

                if i == 0:
                    new_command = new_command + f"""({wcid},{my_justified_key},{my_justified_value}, 0, 0) {v[1]}"""
                    if i < (total_lines - 1):
                        new_command = new_command + "\n    "
                else:
                    new_command = new_command + f""" , ({wcid},{my_justified_key},{my_justified_value}, 0, 0) {v[1]}"""
                    if i < (total_lines - 1):
                        new_command = new_command + "\n    "
                i += 1

            my_list.append(new_command + ";")

        else:
            if command.strip() != "":
                my_list.append(command + ";")

    return my_list


def get_attribute(wcid, command, key):
    my_dict = {}
    split_command = command.split("(")

    for line in split_command:
        if str(wcid) in line:
            split_comma = line.split(",", 2)

            my_key = int(split_comma[1].strip())
            # print("My key: " + str(my_key))

            split_other = split_comma[2].split(")")
            my_val = split_other[0].strip()
            split_more = my_val.split(",", 1)
            my_val = split_more[0]
            # print("My val: " + str(my_val))
            comment = "".join(split_other[1].rsplit(",", 1)).strip()

            my_tuple = (my_val, comment)
            my_dict[my_key] = my_tuple

    return my_dict[key][0]


def set_attribute_2(commands, key, val, desc, do_override):
    tag = "`weenie_properties_attribute_2nd`"
    key = int(key)

    my_list = []
    wcid = re.findall('[0-9]+', (commands[0]))[0]  # find number string in first line

    # needed for health, stamina or mana adjustment
    my_attribute = 0

    for command in commands:
        if str("`weenie_properties_attribute`") in command:
            if str("`weenie_properties_attribute_2nd`") not in command:

                if key == 1 or key == 3:  # health or stamina, need endurance
                    my_attribute = get_attribute(wcid, command, 2)
                elif key == 5:  # mana, need self
                    my_attribute = get_attribute(wcid, command, 6)

    for command in commands:
        if str(tag) in command:

            my_dict = {}
            split_command = command.split("(")

            for line in split_command:
                if str(wcid) in line:
                    split_comma = line.split(",", 2)

                    my_key = int(split_comma[1].strip())
                    # print("My key: " + str(my_key))

                    split_other = split_comma[2].split(")")
                    init_level = split_other[0].strip()
                    split_more = init_level.split(",")
                    init_level = split_more[0]
                    current_level = split_more[3]

                    # print("init level: " + str(init_level))
                    # print("curr level: " + str(current_level))
                    comment = "".join(split_other[1].rsplit(",", 1)).strip()
                    # print("comment: " + str(comment))

                    my_tuple = (init_level, current_level, comment)
                    my_dict[my_key] = my_tuple

            init = val
            curr = 0

            # must compute
            if key == 1:  # health
                curr = compute_health(val, my_attribute)
            elif key == 3:  # stamina
                curr = compute_stamina(val, my_attribute)
            elif key == 5:  # mana
                curr = compute_mana(val, my_attribute)

            # if true, replace existing value
            if do_override:
                my_dict[key] = (init, curr, desc)
            else:
                if key not in my_dict.keys():
                    my_dict[key] = (init, curr, desc)

            param_list = "(`object_Id`, `type`, `init_Level`, `level_From_C_P`, `c_P_Spent`, `current_Level`)"
            new_command = f"""\n\nINSERT INTO {tag} {param_list}\nVALUES """

            i = 0
            total_lines = len(my_dict)

            # figure out padding
            longest_tuple = get_longest(my_dict)
            longest_key = longest_tuple[0]
            longest_init = longest_tuple[1]
            longest_curr = 0

            for k, v in sorted(my_dict.items()):

                value_len = len(str(v[1]))
                if value_len > longest_curr:
                    longest_curr = value_len

            for k, v in sorted(my_dict.items()):

                just_init = str(v[0]).rjust(longest_init, " ")
                just_curr = str(v[1]).rjust(longest_curr, " ")
                just_key = str(k).rjust(longest_key, " ")

                if i == 0:
                    new_command = new_command + f"""({wcid},{just_key},{just_curr}, 0, 0,{just_init}) {v[2]}"""
                    if i < (total_lines - 1):
                        new_command = new_command + "\n    "
                else:
                    new_command = new_command + f""" , ({wcid},{just_key},{just_curr}, 0, 0,{just_init}) {v[2]}"""
                    if i < (total_lines - 1):
                        new_command = new_command + "\n    "
                i += 1

            my_list.append(new_command + ";")

        else:
            if command.strip() != "":
                my_list.append(command)

    return my_list


def compute_health(health, endurance):
    """Compute the initial level of health based on endurance."""
    health = int(health) - round(int(endurance) / 2)
    if health < 0:
        health = 0
    return health


def compute_stamina(stamina, endurance):
    """Compute the initial level of stamina based on endurance."""
    stamina = int(stamina) - int(endurance)
    if stamina < 0:
        stamina = 0
    return stamina


def compute_mana(mana, self):
    """Compute the initial level of mana based on self."""
    mana = int(mana) - int(self)
    if mana < 0:
        mana = 0
    return mana


def get_templates():
    my_list = []

    for file in os.listdir("templates"):
        if file.endswith(".sql"):
            my_list.append(file)

    return my_list


def get_xp_value(level):
    with open("xp_by_level.txt", 'r') as my_file:
        for line in my_file:
            split = line.split("\t")
            if level == int(split[0].strip()):
                return split[1].strip()

    return 0


def find_listbox_output(file_name, entry, listbox):
    results_list = []
    search_phrase = entry.get().strip().lower()

    if not search_phrase:  # empty string
        tk.messagebox.showerror("Error", "Enter something to search for.")
    else:
        with open(file_name, 'r') as my_file:
            for line in my_file:
                if search_phrase in line.lower():
                    split = line.split("\t")
                    results_list.append(split[0] + "," + split[1])

        # clear the listbox first
        listbox.delete(0, END)

        # add the result to the listbox
        i = 0
        for result in results_list:
            listbox.insert(i, result)
            i += 1


def find_death_treasure(file_name, entry, text_area):
    results_list = []
    search_phrase = entry.get().strip().lower()

    text_area.configure(state='normal')
    text_area.delete('1.0', END)

    if not search_phrase:
        text_area.insert(END, "Enter something to search for.")
    else:
        with open(file_name, 'r') as my_file:
            for line in my_file:
                split = line.split('\t')
                if search_phrase in split[0]:
                    results_list.append(split[1].strip())

        text_area.insert(END, "Options for Loot Tier " + search_phrase + "\n")
        for result in results_list:
            text_area.insert(END, result + "\t")

    text_area.configure(state='disabled')


def get_spell_list(name):
    results_dict = {}
    search_phrase = name.strip().lower()

    if not search_phrase:  # empty string
        tk.messagebox.showerror("Error", "Enter a spell name.")
    else:
        with open("spell_data.txt", 'r') as my_file:
            for line in my_file:
                if search_phrase in line.lower():
                    split1 = line.split("\t")
                    spell_name = split1[1]
                    split2 = split1[2].split(",")
                    split3 = split2[0].split(":")
                    spell_id = split3[1].strip()

                    results_dict[spell_id] = spell_name

    return results_dict


def find_wielded_items(file_name, entry, results_text):
    results_list = []
    search_phrase = entry.get().strip().lower()

    results_text.configure(state='normal')
    results_text.delete('1.0', END)

    if not search_phrase:
        results_text.insert(END, "Enter something to search for.")
    else:
        with open(file_name, 'r') as my_file:
            for line in my_file:
                split = line.split('\t')
                if search_phrase == split[0] or search_phrase in split[1].lower():
                    results_list.append(split[0] + " - " + split[1] + ", " + split[2] + " - " + split[3] + "\n")

        for result in results_list:
            results_text.insert(END, result)

    results_text.configure(state='disabled')


def skill_look_up(name):

    with open('pcap_creature_skills.txt') as my_file:

        melee_attack = []
        melee_defense = []

        missile_attack = []
        missile_defense = []

        magic_attack = []
        magic_defense = []

        my_dict = {'melee offense': melee_attack,
                   'finesse weapons': melee_attack,
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
                skill_levels[k] = round(statistics.mean(v))
            elif len(v) == 1:
                skill_levels[k] = v[0]
            else:
                skill_levels[k] = 0

        return skill_levels
