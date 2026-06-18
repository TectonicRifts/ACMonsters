from functools import partial
import view_helper as vh
import settings as st
import tkinter as tk
import art_module


class ArtPanel(tk.Frame):

    def __init__(self, parent, cont):
        super().__init__(parent, bg=st.base_bg)
        self.cont = cont
        norm_font = st.norm_font

        # current (old) and desired (new) surface texture pairs
        self.texture_pairs = []

        did_header_label = tk.Label(self, text="Int or Data ID", font=norm_font, fg=st.label_text, bg=st.base_bg)
        did_labels = ['palette template', 'palette base', 'clothing base', 'physics effect']
        self.did_entries = vh.make_str_entry(self, did_labels)

        float_header_label = tk.Label(self, text="Float", font=norm_font, fg=st.label_text, bg=st.base_bg)
        float_labels = ['shade', 'translucency', 'scale']
        self.float_entries = vh.make_float_entry(self, float_labels)

        calc_header_label = tk.Label(self, text="Calculator", font=norm_font, fg=st.label_text, bg=st.base_bg)
        str_labels = ['hex or dec']
        self.str_entries = vh.make_str_entry(self, str_labels)

        convert_button = tk.Button(self, text="Convert", command=self.convert)

        set_button = tk.Button(self, text="Set", bg=st.button_bg, command=self.set_art)
        batch_button = tk.Button(self, text="Run Batch", command=partial(self.cont.run_sql_batch, self.set_art))

        clo_header_label = tk.Label(self, text="Custom Clothing", font=norm_font, fg=st.label_text, bg=st.base_bg)
        clor_labels = ['setup did', 'gfx object', 'old texture', 'new texture']
        self.clo_entries = vh.make_str_entry(self, clor_labels)

        add_texture_button = tk.Button(self, text="Add Texture", command=self.add_texture_pair)
        clear_textures_button = tk.Button(self, text="Clear Textures", command=self.clear_texture_pairs)
        make_clo_button = tk.Button(self, text="Make Clothing", command=self.make_custom_clothing)

        # layout
        r = 0
        c = 0

        did_header_label.grid(row=r, column=c, sticky="w", padx=2)
        r += 1
        for name, entry in self.did_entries.items():
            label = tk.Label(self, text=name, font=norm_font, bg=st.base_bg)
            label.grid(row=r, column=c, sticky="e", padx=2)
            entry.grid(row=r, column=c + 1, sticky="ew", padx=2)
            r += 1

        float_header_label.grid(row=r, column=c, sticky="w", padx=2)
        r += 1
        for name, entry in self.float_entries.items():
            label = tk.Label(self, text=name, font=norm_font, bg=st.base_bg)
            label.grid(row=r, column=c, sticky="e", padx=2)
            entry.grid(row=r, column=c + 1, sticky="ew", padx=2)
            r += 1

        calc_header_label.grid(row=r, column=c, sticky="w", padx=2)
        r += 1
        for name, entry in self.str_entries.items():
            label = tk.Label(self, text=name, font=norm_font, bg=st.base_bg)
            label.grid(row=r, column=c, sticky="e", padx=2)
            entry.grid(row=r, column=c + 1, sticky="ew", padx=2)
            r += 1

        convert_button.grid(row=r, column=c, padx=2, pady=5, sticky="ew")
        r += 1
        set_button.grid(row=r, column=c, columnspan=2, padx=2, pady=5, sticky="ew")
        r += 1
        batch_button.grid(row=r, column=c, columnspan=2, padx=2, pady=5, sticky="ew")
        r += 1

        clo_header_label.grid(row=r, column=c, sticky="w", padx=2)
        r += 1
        for name, entry in self.clo_entries.items():
            label = tk.Label(self, text=name, font=norm_font, bg=st.base_bg)
            label.grid(row=r, column=c, sticky="e", padx=2)
            entry.grid(row=r, column=c + 1, sticky="ew", padx=2)
            r += 1

        add_texture_button.grid(row=r, column=c, padx=2, pady=5, sticky="ew")
        r += 1
        clear_textures_button.grid(row=r, column=c, padx=2, pady=5, sticky="ew")
        r += 1
        make_clo_button.grid(row=r, column=c, columnspan=2, padx=2, pady=5, sticky="ew")

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)


    def set_art(self):
        """Set art properties for a single sql file"""
        if self.cont.sql_data is not None:
            # int
            my_dict = {
                'palette template': (3, "/* PaletteTemplate */")
            }
            self.cont.set_properties(my_dict, self.did_entries, 'int')

            # did
            my_dict = {
                'palette base': (6, "/* PaletteBase */"),
                'clothing base': (7, "/* ClothingBase */"),
                'physics effect': (22, "/* PhysicsEffectTable */")
            }
            self.cont.set_properties(my_dict, self.did_entries, 'did')

            # float
            my_dict = {
                'shade': (12, "/* Shade */"),
                'translucency': (76, "/* Translucency */"),
                'scale': (39, "/* DefaultScale */")
            }
            self.cont.set_properties(my_dict, self.float_entries, 'float')

        else:
            self.cont.file_warning()


    def convert(self):
        val = self.str_entries["hex or dec"].get().strip()

        if art_module.is_hex(val):
            self.hex_to_dec()
        else:
            self.dec_to_hex()


    def hex_to_dec(self):
        val = self.str_entries["hex or dec"].get().strip()

        if val == "":
            self.cont.view.console.print("Enter a hex value.\n")
            return

        try:
            # handles both "72C90013" and "0x72C90013"
            dec_val = int(val, 16)
            self.cont.view.console.print(f"{dec_val}\n")

        except ValueError:
            self.cont.view.console.print("Invalid hex value.\n")


    def dec_to_hex(self):
        val = self.str_entries["hex or dec"].get().strip()

        if val == "":
            self.cont.view.console.print("Enter a decimal value.\n")
            return

        try:
            dec_val = int(val)

            # force into 32-bit two's complement
            hex_val = f"0x{dec_val & 0xFFFFFFFF:08X}"

            self.cont.view.console.print(f"{hex_val}\n")

        except ValueError:
            self.cont.view.console.print("Invalid decimal value.\n")


    def add_texture_pair(self):
        old_texture = art_module.ensure_hex_prefix(
            self.clo_entries["old texture"].get()
        )

        new_texture = art_module.ensure_hex_prefix(
            self.clo_entries["new texture"].get()
        )

        if old_texture and new_texture:
            self.texture_pairs.append((old_texture, new_texture))
            self.cont.view.console.print(f"Added the texture pair: {old_texture} and {new_texture}.\n")

            # clear the entries
            self.clo_entries["old texture"].delete(0, tk.END)
            self.clo_entries["new texture"].delete(0, tk.END)
        else:
            self.cont.view.console.print("Enter an old and new surface texture.\n")


    def clear_texture_pairs(self):
        self.texture_pairs.clear()
        self.cont.view.console.print("The texture pairs have been cleared.\n")


    def make_custom_clothing(self):
        # custom clothing base hex, such as 0x10000938
        clothing_base = art_module.ensure_hex_prefix(
            self.did_entries["clothing base"].get()
        )

        # the setup did of the item to modify, such as 0x02001112
        setup_did = art_module.ensure_hex_prefix(
            self.clo_entries["setup did"].get()
        )

        # gfx object of the part to modify, such as 0x01003357
        gfx_object = art_module.ensure_hex_prefix(
            self.clo_entries["gfx object"].get()
        )

        if clothing_base and setup_did and gfx_object:

            json_data = art_module.create_clothing_entry(
                clothing_base=f"{clothing_base}",
                setup_did=f"{setup_did}",
                gfx_object=f"{gfx_object}",
                texture_pairs=self.texture_pairs
            )
            file_name = clothing_base.removeprefix("0x")
            art_module.write_json_file(file_name, "clothing", json_data)

        else:
            self.cont.view.console.print("Enter a clothing base, setup did and gfx object.\n")


