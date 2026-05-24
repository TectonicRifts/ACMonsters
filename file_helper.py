import tkinter as tk
from tkinter import END
import tkinter.messagebox
import re


PROPERTY_HEADERS = {
    "int": "`weenie_properties_int`",
    "bool": "`weenie_properties_bool`",
    "float": "`weenie_properties_float`",
    "string": "`weenie_properties_string`",
    "str": "`weenie_properties_string`",
    "did": "`weenie_properties_d_i_d`"
}

ARMOR_MOD_IDS = {
    "slash": 13,
    "pierce": 14,
    "bludge": 15,
    "cold": 16,
    "fire": 17,
    "acid": 18,
    "electric": 19
}

RESIST_MOD_IDS = {
    "slash": 64,
    "pierce": 65,
    "bludge": 66,
    "cold": 68,
    "fire": 67,
    "acid": 69,
    "electric": 70,
    "nether": 166
}


def get_property_header(property_type: str) -> str | None:
    """Property types are int, bool, float, str, and did."""
    return PROPERTY_HEADERS.get(property_type)


def get_armor_mods(sql_data: list) -> dict:
    return extract_float_properties(sql_data, ARMOR_MOD_IDS)


def get_resist_mods(sql_data: list) -> dict:
    return extract_float_properties(sql_data, RESIST_MOD_IDS)


def extract_float_properties(sql_data: list, property_ids: dict) -> dict:
    result = {}

    for k, v in property_ids.items():
        mod = get_property(sql_data, "float", v)
        match = re.search(r"'([\d.]+)'", str(mod))

        if match:
            result[k] = float(match.group(1))
        else:
            result[k] = None

    return result


def get_property(sql_data: list, property_type: str, key: int) -> tuple[str, str] | None:
    """
    Returns a tuple (val, comment) or None if the property type is invalid, the property table does
    not exist, or the given key is not found in the property table.
    """
    property_header = get_property_header(property_type)
    if property_header is None:
        return None

    wcid = get_wcid(sql_data)

    for command in sql_data:
        if property_header in command:
            parsed_sql_data = {}
            split_command = command.split("(")

            for line in split_command:
                if str(wcid) in line:
                    # split on the first two commas only
                    split_comma = line.split(",", 2)
                    my_key = int(split_comma[1].strip())

                    split_other = split_comma[2].split(")")
                    my_val = split_other[0].strip()
                    comment = "".join(split_other[1].rsplit(",", 1)).strip()

                    parsed_sql_data[my_key] = (my_val, comment)

            return parsed_sql_data.get(key)

    return None


def set_property(sql_data: list, property_type: str, key, val, desc) -> list:
    """Set a property (int, bool, float, string or did) to a weenie (in sql format). If the
    property already exists, the value is updated. This function does not work for position. """

    is_padded = True
    key = int(key)

    # format value depending on property type
    if property_type in ("str", "string"):
        val = val.replace("'", "''")
        val = f"""'{val}'"""
        is_padded = False

    elif property_type == "bool":
        if int(val) == 0:
            val = False
        else:
            val = True

    elif property_type == "did":
        val = hex(val).upper().replace('X', 'x')
        # these did properties are stored without the 0x prefix
        if key in (32, 35):
            val = val.replace('0x', '')

    property_header = get_property_header(property_type)

    # find number string in first line
    wcid = re.findall('[0-9]+', (sql_data[0]))[0]

    # check if this property table already exists
    has_property_table = False

    for command in sql_data:
        if str(property_header) in command:
            has_property_table = True

    # if not, add a new insert command
    if not has_property_table:
        new_command = f"""\n\nINSERT INTO {property_header} (`object_Id`, `type`, `value`)\nVALUES """
        new_command += f"""({wcid}, {key}, {val}) {desc}"""
        sql_data.append(new_command)
        return sql_data

    new_sql_data = []

    for command in sql_data:
        if str(property_header) in command:

            properties = {}
            split_command = command.split("(")

            for line in split_command:
                if str(wcid) in line:
                    split_comma = line.split(",", 2)

                    existing_key = int(split_comma[1].strip())

                    split_other = split_comma[2].split(")")
                    existing_val = split_other[0].strip()
                    comment = "".join(split_other[1].rsplit(",", 1)).strip()

                    properties[existing_key] = (existing_val, comment)

            # add or replace the target property
            properties[key] = (val, desc)

            # rebuild the insert command
            new_command = f"""\n\nINSERT INTO {property_header} (`object_Id`, `type`, `value`)\nVALUES """

            # figure out padding
            i = 0
            total_lines = len(properties)

            longest_key, longest_val = get_longest(properties)

            if longest_val < 8:
                longest_val = 8

            for k, v in sorted(properties.items()):

                if is_padded:
                    justified_value = str(v[0]).rjust(longest_val, " ")
                    justified_key = str(k).rjust(longest_key, " ")
                else:
                    justified_value = " " + str(v[0])
                    justified_key = str(k).rjust(longest_key, " ")

                if i == 0:
                    new_command = new_command + f"""({wcid},{justified_key},{justified_value}) {v[1]}"""
                    if i < (total_lines - 1):
                        new_command = new_command + "\n    "
                else:
                    new_command = new_command + f""" , ({wcid},{justified_key},{justified_value}) {v[1]}"""
                    if i < (total_lines - 1):
                        new_command = new_command + "\n    "
                i += 1

            new_sql_data.append(new_command)

        else:
            if command.strip() != "":
                new_sql_data.append(command)

    return new_sql_data


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


def get_wcid(commands):
    wcid = re.findall('[0-9]+', (commands[0]))[0]
    return wcid


def get_name(commands):
    name = str(get_property(commands, "str", 1))
    split = name.split(",")[0]
    name = split.replace("(", "")
    name = name.replace("''", "'")
    name = name[2:-2]
    return name


def get_xp_value(level):
    with open("xp_by_level.txt", 'r') as my_file:
        for line in my_file:
            split = line.split("\t")
            if int(level) == int(split[0].strip()):
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


def set_body_table(sql_data, template_wcid, body_table) -> list:
    # TODO not used anymore?
    wcid = re.findall('[0-9]+', (sql_data[0]))[0]
    property_header = "`weenie_properties_body_part`"
    my_list = []
    body_table = body_table.replace(template_wcid, wcid)

    has_command = False
    for command in sql_data:
        if str(property_header) in command:
            has_command = True

    if has_command:
        for command in sql_data:
            if str(property_header) in command:  # append new instead of existing
                my_list.append(body_table)
            else:
                if command.strip() != "":
                    my_list.append(command)
    else:
        sql_data.append(body_table)
        return sql_data

    return my_list
