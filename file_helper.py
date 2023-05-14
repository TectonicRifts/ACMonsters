import tkinter as tk
from tkinter import END
import tkinter.messagebox
import re


def get_tag_name(tag):
    tags = {
        "int": "`weenie_properties_int`",
        "bool": "`weenie_properties_bool`",
        "float": "`weenie_properties_float`",
        "string": "`weenie_properties_string`",
        "str": "`weenie_properties_string`",
        "did": "`weenie_properties_d_i_d`"
    }

    if tag in tags.keys():
        return tags[tag]
    else:
        return None


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


def set_property(commands, tag, key, val, desc):
    """Set a property (int, bool, float, string or did) to a weenie (in sql format). If the
    property already exists, the value is updated.This function does not work for position. """

    is_padded = True
    key = int(key)

    if tag == "str" or tag == "string":
        if "'" in val:
            val = val.replace("'", "''")
        val = f"""'{val}'"""
        is_padded = False

    if tag == "bool":
        if int(val) == 0:
            val = False
        else:
            val = True

    if tag == "did":
        val = hex(val).upper().replace('X', 'x')
        if key == 32 or key == 35:
            val = val.replace('0x', '')

    tag = get_tag_name(tag)

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

            # figure out padding

            i = 0
            total_lines = len(my_dict)

            my_tuple = get_longest(my_dict)
            longest_key = my_tuple[0]
            longest_val = my_tuple[1]
            if longest_val < 8:
                longest_val = 8

            for k, v in sorted(my_dict.items()):

                if is_padded:
                    my_justified_value = str(v[0]).rjust(longest_val, " ")
                    my_justified_key = str(k).rjust(longest_key, " ")
                else:
                    my_justified_value = " " + str(v[0])
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
