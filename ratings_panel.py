import tkinter as tk
from functools import partial

import file_helper
import view_helper as vh
import settings as st


class RatingsPanel:

    def __init__(self, parent, cont):
        self.frame = tk.Frame(parent, bg=st.base_bg)
        self.cont = cont

        norm_font = st.norm_font
        int_header_label = tk.Label(self.frame, text="Int", font=norm_font, fg='#221CD9', bg=st.base_bg)

        int_labels = ['damage', 'damage resist', 'crit', 'crit resist', 'overpower']
        self.int_entries = vh.make_int_entry(self.frame, int_labels)

        set_button = tk.Button(self.frame, text="Set", bg=st.button_bg, command=self.set_ratings)
        batch_button = tk.Button(self.frame, text="Run Batch",
                                 command=partial(self.cont.run_sql_batch, self.set_ratings))

        # layout

        r = 0
        c = 0

        int_header_label.grid(row=r, column=c)
        r += 1

        for name, entry in self.int_entries.items():
            label = tk.Label(self.frame, text=name, font=norm_font, bg=st.base_bg)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1

        set_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        r += 1
        batch_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")

    def set_ratings(self):

        if self.cont.sql_data is not None:
            # int
            my_dict = {'damage': (307, "/* DamageRating */"),
                       'damage resist': (308, "/* DamageResistRating */"),
                       'crit': (313, "/* CritRating */"),
                       'crit resist': (316, "/* CritDamageResistRating */"),
                       'overpower': (386, "/* Overpower */")
                       }
            self.cont.set_properties(my_dict, self.int_entries, 'int')
