import tkinter as tk
import re
import settings as st


def make_int_entry(parent, label_list: list) -> dict:
    entries = {}
    vcmd = parent.register(validate_int)

    for name in label_list:
        entry = tk.Entry(parent, validate='all', validatecommand=(vcmd, '%P'), bg=st.entry_bg, font="Arial 12")
        entries[name] = entry

    return entries


def make_str_entry(parent, label_list: list) -> dict:
    entries = {}
    for name in label_list:
        entry = tk.Entry(parent, bg=st.entry_bg, font="Arial 12")
        entries[name] = entry

    return entries


def make_float_entry(parent, label_list: list) -> dict:
    entries = {}
    vcmd = parent.register(validate_float)

    for name in label_list:
        entry = tk.Entry(parent, validate='all', validatecommand=(vcmd, '%P'), bg=st.entry_bg, font="Arial 12")
        entries[name] = entry

    return entries


def validate_int(user_input: str) -> bool:
    if str.isdigit(user_input) or user_input == "" or int(user_input, 16):
        return True
    else:
        return False


def validate_float(user_input: str) -> bool:
    regex = re.compile(r"[0-9.]*$")
    result = regex.match(user_input)
    return user_input == "" or (user_input.count('.') <= 1 and result is not None and result.group(0) != "")


def make_listbox(parent, my_font, selection_mode):
    """Returns a frame and a listbox with a vertical scrollbar."""
    frame = tk.Frame(parent)

    listbox = tk.Listbox(frame, selectmode=selection_mode, font=my_font, bg=st.entry_bg)
    listbox['width'] = 30
    listbox.pack(side="left", fill="y")

    scrollbar = tk.Scrollbar(frame, orient="vertical")
    scrollbar.config(command=listbox.yview)
    scrollbar.pack(side="right", fill="y")
    listbox.config(yscrollcommand=scrollbar.set)

    return frame, listbox


def get_selected(listbox):
    """Return a list with selected values in a listbox."""
    values = [listbox.get(idx) for idx in listbox.curselection()]
    wcids = []
    for i in range(len(values)):
        wcids.append(values[i].split(',')[0])

    return wcids
