import tkinter as tk
from functools import partial

import settings as st
import stat_helper
import view_helper as vh
import labels_module


class AttributesPanel:

    def __init__(self, parent, cont):
        self.frame = tk.Frame(parent, bg=st.base_bg)
        self.cont = cont

        norm_font = st.norm_font

        attributes_header = tk.Label(self.frame, text="Attributes", font=norm_font, fg=st.label_text, bg=st.base_bg)
        vitals_header = tk.Label(self.frame, text="Vitals", font=norm_font, fg=st.label_text, bg=st.base_bg)

        self.int_entries_1 = vh.make_int_entry(self.frame, labels_module.get_primary_attribute_labels())
        self.int_entries_2 = vh.make_int_entry(self.frame, labels_module.get_secondary_attribute_labels())

        set_button = tk.Button(self.frame, text="Set", bg=st.button_bg, command=self.set_attributes)
        batch_button = tk.Button(self.frame, text="Run Batch",
                                 command=partial(self.cont.run_sql_batch, self.set_attributes))

        tooltip = "All fields optional. Vitals are adjusted based on attributes."
        tooltip_label = tk.Label(self.frame, text=tooltip, font=norm_font, fg="dark green", wraplength=420,
                                 justify=tk.LEFT, bg=st.base_bg)

        # layout
        r = 0
        c = 0

        attributes_header.grid(row=r, column=c, sticky='w')
        r += 1
        for name, entry in self.int_entries_1.items():
            label = tk.Label(self.frame, text=name, font=norm_font, bg=st.base_bg)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1

        vitals_header.grid(row=r, column=c, sticky='w')
        r += 1
        for name, entry in self.int_entries_2.items():
            label = tk.Label(self.frame, text=name, font=norm_font, bg=st.base_bg)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1

        set_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        r += 1
        batch_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        r += 1
        tooltip_label.grid(row=r, column=c, columnspan=2)

    def show_attributes(self):

        if self.cont.sql_data is not None:
            attributes = stat_helper.get_all_attributes(self.cont.sql_data)

            for name, entry in self.int_entries_1.items():
                if name in attributes.keys():
                    entry.delete(0, tk.END)  # delete existing
                    entry.insert(0, attributes.get(name))  # insert new

            vitals = stat_helper.get_all_vitals(self.cont.sql_data)

            for name, entry in self.int_entries_2.items():
                if name in vitals.keys():
                    entry.delete(0, tk.END)  # delete existing
                    entry.insert(0, vitals.get(name))  # insert new

    def set_attributes(self):

        if self.cont.sql_data is not None:
            my_dict = {
                'strength': (1, "/* Strength */"),
                'endurance': (2, "/* Endurance */"),
                'quickness': (3, "/* Quickness */"),
                'coordination': (4, "/* Coordination */"),
                'focus': (5, "/* Focus */"),
                'self': (6, "/* Self */")
            }
            self.cont.set_attributes(my_dict, self.int_entries_1, False)

            my_dict = {
                'health': (1, "/* MaxHealth */"),
                'stamina': (3, "/* MaxStamina */"),
                'mana': (5, "/* MaxMana */")
            }
            self.cont.set_attributes(my_dict, self.int_entries_2, True)
        else:
            self.cont.file_warning()
