from functools import partial
import view_helper as vh
import settings as st
import tkinter as tk


class ArtPanel:

    def __init__(self, parent, cont):
        self.frame = tk.Frame(parent, bg=st.base_bg)
        self.cont = cont

        norm_font = st.norm_font

        int_header_label = tk.Label(self.frame, text="Int or Data ID", font=norm_font, fg="blue", bg=st.base_bg)

        int_labels = ['palette template', 'palette base', 'clothing base', 'physics effect']
        self.int_entries = vh.make_int_entry(self.frame, int_labels)

        tooltip = "All fields optional."
        tooltip_label = tk.Label(self.frame, text=tooltip, font=norm_font, fg="dark green", wraplength=420,
                                 justify=tk.LEFT, bg=st.base_bg)

        float_header_label = tk.Label(self.frame, text="Float", font=norm_font, fg="blue", bg=st.base_bg)

        float_labels = ['shade', 'translucency', 'scale']
        self.float_entries = vh.make_float_entry(self.frame, float_labels)

        set_button = tk.Button(self.frame, text="Set", bg=st.button_bg, command=self.set_art)
        batch_button = tk.Button(self.frame, text="Run Batch", command=partial(self.cont.run_sql_batch, self.set_art))

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

        float_header_label.grid(row=r, column=c)
        r += 1

        for name, entry in self.float_entries.items():
            label = tk.Label(self.frame, text=name, font=norm_font, bg=st.base_bg)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1

        set_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        r += 1
        batch_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        r += 1
        tooltip_label.grid(row=r, column=c, columnspan=2, sticky="w")

    def set_art(self):
        """Set art properties for a single .sql file"""
        if len(self.cont.sql_commands) > 0:
            # int
            my_dict = {'palette template': (3, "/* PaletteTemplate */")}
            self.cont.set_properties(my_dict, self.int_entries, 'int')

            # did
            my_dict = {'palette base': (6, "/* PaletteBase */"),
                       'clothing base': (7, "/* ClothingBase */"),
                       'physics effect': (22, "/* PhysicsEffectTable */")
                       }
            self.cont.set_properties(my_dict, self.int_entries, 'did')

            # float
            my_dict = {'shade': (12, "/* Shade */"),
                       'translucency': (76, "/* Translucency */"),
                       'scale': (39, "/* DefaultScale */")
                       }
            self.cont.set_properties(my_dict, self.float_entries, 'float')