import tkinter as tk
from functools import partial

import settings as st
import view_helper as vh
import file_helper as fh


class ModsPanel(tk.Frame):

    def __init__(self, parent, cont):
        """Panel for armor and resistance mods."""
        super().__init__(parent, bg=st.base_bg)
        self.cont = cont

        norm_font = st.norm_font

        mod_labels = ['slash', 'pierce', 'bludge', 'cold', 'fire', 'acid', 'electric', 'nether']

        armor_header_label = tk.Label(self, text="Armor (0=weak)", font="Arial 12", fg='#221CD9', bg=st.base_bg)
        self.armor_entries = vh.make_float_entry(self, mod_labels)

        resist_header_label = tk.Label(self, text="Resist (0=strong)", font="Arial 12", fg='#221CD9', bg=st.base_bg)
        self.resist_entries = vh.make_float_entry(self, mod_labels)

        set_button = tk.Button(self, text="Set", bg=st.button_bg, command=self.set_mods)
        batch_button = tk.Button(self, text="Run Batch", command=partial(self.cont.run_sql_batch, self.set_mods))

        # ratings
        int_header_label = tk.Label(self, text="Int", font=norm_font, fg='#221CD9', bg=st.base_bg)

        int_labels = ['damage', 'dmg resist', 'crit', 'crit resist', 'overpower']
        self.int_entries = vh.make_int_entry(self, int_labels)

        set_ratings_button = tk.Button(self, text="Set", bg=st.button_bg, command=self.set_ratings)
        batch_ratings_button = tk.Button(self, text="Run Batch",
                                 command=partial(self.cont.run_sql_batch, self.set_ratings))

        # layout

        r = 0
        c = 0

        armor_header_label.grid(row=r, column=c + 1)
        resist_header_label.grid(row=r, column=c + 2)
        r += 1

        # col 1
        for name, entry in self.armor_entries.items():
            label = tk.Label(self, text=name, font=norm_font, bg=st.base_bg)
            label.grid(row=r, column=c, sticky="e", padx=2)
            entry.grid(row=r, column=c + 1, sticky="ew", padx=2)
            entry.config(width=5)
            r += 1

        # reset the row to start col 2
        r = 1
        for name, entry in self.resist_entries.items():
            entry.grid(row=r, column=c + 2, sticky="ew", padx=2)
            entry.config(width=6)
            r += 1

        set_button.grid(row=r, column=c, columnspan=3, padx=2, pady=5, sticky="ew")
        r += 1
        batch_button.grid(row=r, column=c, columnspan=3, padx=2, pady=5, sticky="ew")
        r += 1

        # ratings layout
        int_header_label.grid(row=r, column=c)
        r += 1

        for name, entry in self.int_entries.items():
            label = tk.Label(self, text=name, font=norm_font, bg=st.base_bg)
            label.grid(row=r, column=c, sticky="e", padx=2)
            entry.grid(row=r, column=c + 1, columnspan= 2, sticky="ew", padx=2)
            r += 1

        set_ratings_button.grid(row=r, column=c, columnspan=3, padx=2, pady=5, sticky="ew")
        r += 1
        batch_ratings_button.grid(row=r, column=c, columnspan=3, padx=2, pady=5, sticky="ew")

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)


    def show_mods(self):
        if self.cont.sql_data is not None:
            # clear existing
            for name, entry in self.armor_entries.items():
                entry.delete(0, tk.END)
            for name, entry in self.resist_entries.items():
                entry.delete(0, tk.END)

            armor_mods = fh.get_armor_mods(self.cont.sql_data)
            resist_mods = fh.get_resist_mods(self.cont.sql_data)

            for name, entry in self.armor_entries.items():
                if name in armor_mods.keys():
                    result = armor_mods.get(name)
                    if result is not None:
                        entry.insert(0, result)

            for name, entry in self.resist_entries.items():
                if name in resist_mods.keys():
                    result = resist_mods.get(name)
                    if result is not None:
                        entry.insert(0, result)

    def set_mods(self):
        if self.cont.sql_data is not None:
            armor_dict = {
                "slash": (13, "/* ArmorModVsSlash */"),
                "pierce": (14, "/* ArmorModVsPierce */"),
                "bludge": (15, "/* ArmorModVsBludgeon */"),
                "cold": (16, "/* ArmorModVsCold */"),
                "fire": (17, "/* ArmorModVsFire */"),
                "acid": (18, "/* ArmorModVsAcid */"),
                "electric": (19, "/* ArmorModVsElectric */"),
                "nether": (165, "/* ArmorModVsNether */")
            }
            self.cont.set_properties(armor_dict, self.armor_entries, 'float')

            resist_dict = {
                "slash": (64, "/* ResistSlash */"),
                "pierce": (65, "/* ResistPierce */"),
                "bludge": (66, "/* ResistBludgeon */"),
                "cold": (68, "/* ResistCold */"),
                "fire": (67, "/* ResistFire */"),
                "acid": (69, "/* ResistAcid */"),
                "electric": (70, "/* ResistElectric */"),
                "nether": (166, "/* ResistNether */")
            }
            self.cont.set_properties(resist_dict, self.resist_entries, 'float')

        else:
            self.cont.file_warning()


    def set_ratings(self):
        if self.cont.sql_data is not None:
            # int
            my_dict = {'damage': (307, "/* DamageRating */"),
                       'dmg resist': (308, "/* DamageResistRating */"),
                       'crit': (313, "/* CritRating */"),
                       'crit resist': (316, "/* CritDamageResistRating */"),
                       'overpower': (386, "/* Overpower */")
                       }
            self.cont.set_properties(my_dict, self.int_entries, 'int')