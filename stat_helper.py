import re
from file_helper import get_wcid
from file_helper import get_longest


def get_all_attributes(commands):
    """Return a dictionary with all attributes."""
    wcid = get_wcid(commands)
    my_dict = {}
    keys = [1, 2, 3, 4, 5, 6]

    for command in commands:
        if str("`weenie_properties_attribute`") in command:
            if str("`weenie_properties_attribute_2nd`") not in command:

                # 1 = str, 2 = endu, 3 = quick, 4 = coord, 5 = foc, 6 = self
                for key in keys:
                    my_dict[key] = int(get_attribute(wcid, command, key))

    attributes = {'strength': my_dict[1], 'endurance': my_dict[2], 'coordination': my_dict[4],
                  'quickness': my_dict[3], 'focus': my_dict[5], 'self': my_dict[6]}
    return attributes


def get_all_vitals(commands):

    values = [1, 1, 1]

    for command in commands:
        if str("`weenie_properties_attribute_2nd`") in command:
            values = [int(value) for value in re.findall(r'\((?:[^()]+)?, (?:[^()]+)?, (?:[^()]+)?, (?:[^()]+)?, (?:[^()]+)?, (\d+)', command)]

    vitals = {'health': values[0], 'stamina': values[1], 'mana': values[2]}
    return vitals


def get_attribute(wcid, command, key):
    my_dict = {}
    split_command = command.split("(")

    for line in split_command:
        if str(wcid) in line:
            split_comma = line.split(",", 2)

            my_key = int(split_comma[1].strip())

            split_other = split_comma[2].split(")")
            my_val = split_other[0].strip()
            split_more = my_val.split(",", 1)
            my_val = split_more[0]
            comment = "".join(split_other[1].rsplit(",", 1)).strip()

            my_tuple = (my_val, comment)
            my_dict[my_key] = my_tuple

    return my_dict[key][0]


def set_attribute_1(commands, key, val, desc):
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

            # always replace existing values
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


def set_attribute_2(commands, key, val, desc):
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

                    split_other = split_comma[2].split(")")
                    init_level = split_other[0].strip()
                    split_more = init_level.split(",")
                    init_level = split_more[0]
                    current_level = split_more[3]

                    comment = "".join(split_other[1].rsplit(",", 1)).strip()

                    my_tuple = (init_level, current_level, comment)
                    my_dict[my_key] = my_tuple

            init = 0
            curr = val

            # must compute
            if key == 1:  # health
                init = compute_health(val, my_attribute)
            elif key == 3:  # stamina
                init = compute_stamina(val, my_attribute)
            elif key == 5:  # mana
                init = compute_mana(val, my_attribute)

            # always replace existing values
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
                    new_command = new_command + f"""({wcid},{just_key},{just_init}, 0, 0,{just_curr}) {v[2]}"""
                    if i < (total_lines - 1):
                        new_command = new_command + "\n    "
                else:
                    new_command = new_command + f""" , ({wcid},{just_key},{just_init}, 0, 0,{just_curr}) {v[2]}"""
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
