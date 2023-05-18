import tkinter as tk
from functools import partial
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

        open_output_button = tk.Button(self.frame, text="Output", command=cont.open_output_folder)

        # layout
        name_filter_label.grid(row=0, column=0, sticky="ew")
        name_filter_entry.grid(row=0, column=1, sticky="ew")
        open_sql_folder_button.grid(row=0, column=3, sticky="ew")
        open_sql_button.grid(row=0, column=4, ipadx=10, ipady=0, sticky="ew")
        save_sql_button.grid(row=0, column=5, ipadx=25, ipady=0, sticky="ew")
        open_output_button.grid(row=0, column=6, ipadx=25, ipady=0, sticky="ew")
