import os
import subprocess
import tkinter as tk
from functools import partial
from pathlib import Path
import platform

import settings as st


class Toolbar:

    def __init__(self, parent, cont):
        self.frame = tk.Frame(parent, bg=st.base_bg)

        open_sql_button = tk.Button(self.frame, text="Open File", command=cont.open_file)
        name_filter_label = tk.Label(self.frame, text="Name contains", font=st.norm_font, bg=st.base_bg)
        name_filter_entry = tk.Entry(self.frame, bg=st.entry_bg, font=st.norm_font)
        self.creature_only = tk.IntVar(value=0)

        open_sql_folder_button = tk.Button(self.frame, text="Open Folder",
                                           command=partial(cont.open_folder, name_filter_entry))

        save_sql_button = tk.Button(self.frame, text="Save", bg=st.button_bg, command=cont.save_sql)
        open_output_button = tk.Button(self.frame, text="Output", command=open_output_folder)
        help_button = tk.Button(self.frame, text="Help", command=cont.open_help)

        # layout
        name_filter_label.grid(row=0, column=0, sticky="ew")
        name_filter_entry.grid(row=0, column=1, sticky="ew", padx=10)
        open_sql_folder_button.grid(row=0, column=3, sticky="ew", padx=(10, 0))  # 10 pad to left, 0 pad to right
        open_sql_button.grid(row=0, column=4, ipadx=10, ipady=0, sticky="ew")
        save_sql_button.grid(row=0, column=5, ipadx=25, ipady=0, sticky="ew")
        open_output_button.grid(row=0, column=6, ipadx=25, ipady=0, sticky="ew")
        help_button.grid(row=0, column=7, ipadx=25, ipady=0, sticky="ew")


def open_output_folder():
    Path("output/").mkdir(parents=True, exist_ok=True)
    path = "output"

    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])
