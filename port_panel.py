import tkinter as tk
from tkinter import ttk

import port_module
import settings as st
import view_helper as vh

import sql_helper as sh

class PortPanel(tk.Frame):

    def __init__(self, parent, cont):
        super().__init__(parent, bg=st.base_bg)
        self.cont = cont

        norm_font = st.norm_font

        port_header_label = tk.Label(self, text="Portal", font=norm_font, fg='#221CD9', bg=st.base_bg)

        port_color_label = tk.Label(self, text="color", font=norm_font, bg=st.base_bg)

        # portal color dropdown
        color_options = list(port_module.portal_colors.keys())
        self.port_color_combo = ttk.Combobox(self, values=color_options, font=norm_font, state="readonly")
        self.port_color_combo.current(0)

        str_labels = ['port name', 'quest stamp', 'quest restrict', 'loc paste']
        self.str_entries = vh.make_str_entry(self, str_labels)

        angles_label = tk.Label(self, text="loc facing", font=norm_font, bg=st.base_bg)
        angles_options = list(port_module.direction_angles.keys())
        angles_options.insert(0, "no change")
        self.angles_combo = ttk.Combobox(self, values=angles_options, font=norm_font, state="readonly")
        self.angles_combo.current(0)

        int_labels = ['port wcid', 'min level']
        self.int_entries = vh.make_int_entry(self, int_labels)

        self.on_click = tk.IntVar(value=0)
        on_click_check = tk.Checkbutton(self, text="use on click", variable=self.on_click, font=norm_font,
                                          bg=st.base_bg, activebackground=st.base_bg)

        # used for portal restriction such as no recall, no summon
        bitmask_label = tk.Label(self, text="bitmask", font=norm_font, bg=st.base_bg)
        bitmask_options = list(port_module.bitmask_flipped.keys())
        self.bitmask_combo = ttk.Combobox(self, values=bitmask_options, font=norm_font, state="readonly")
        self.bitmask_combo.current(0)

        make_port_button = tk.Button(self, text="Make Portal", command=self.make_port)

        # layout
        r = 0
        c = 0

        port_header_label.grid(row=r, column=c, sticky="w", padx=2)
        r += 1

        for name, entry in self.str_entries.items():
            label = tk.Label(self, text=name, font=norm_font, bg=st.base_bg)
            label.grid(row=r, column=c, sticky="e", padx=2)
            entry.grid(row=r, column=c + 1, sticky="ew", padx=2)
            r += 1

        angles_label.grid(row=r, column=c, sticky="e", padx=2)
        self.angles_combo.grid(row=r, column=c + 1, sticky="ew", padx=2)
        r += 1

        for name, entry in self.int_entries.items():
            label = tk.Label(self, text=name, font=norm_font, bg=st.base_bg)
            label.grid(row=r, column=c, sticky="e", padx=2)
            entry.grid(row=r, column=c + 1, sticky="ew", padx=2)
            r += 1

        port_color_label.grid(row=r, column=c, sticky="e", padx=2)
        self.port_color_combo.grid(row=r, column=c + 1, sticky="ew", padx=2)
        r += 1
        bitmask_label.grid(row=r, column=c, sticky="e", padx=2)
        self.bitmask_combo.grid(row=r, column=c + 1, sticky="ew", padx=2)
        r += 1
        on_click_check.grid(row=r, column=c)
        r += 1
        make_port_button.grid(row=r, column=c, columnspan=2, padx=2, pady=5, sticky="ew")

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)


    def make_port(self):

        # port name and wcid
        port_name = self.str_entries["port name"].get().strip()
        if not port_name:
            port_name = "Placeholder Portal"

        port_wcid = self.int_entries["port wcid"].get()
        if port_wcid:
            port_wcid = int(port_wcid)
        else:
            port_wcid = 90750

        quest_stamp = self.str_entries["quest stamp"].get().strip()
        if not quest_stamp:
            quest_stamp = None

        quest_restrict = self.str_entries["quest restrict"].get().strip()
        if not quest_restrict:
            quest_restrict = None

        port_color = self.port_color_combo.get()
        port_setup = port_module.portal_colors[port_color]
        bitmask_str = self.bitmask_combo.get()
        bitmask_int = port_module.bitmask_flipped[bitmask_str]

        min_level = self.int_entries["min level"].get().strip()
        if min_level:
            min_level = int(min_level)
        else:
            min_level = 0

        if self.on_click == 1:
            use_on_click = True
        else:
            use_on_click = False

        port_body = port_module.make_portal_body(port_wcid, port_name, port_setup, bitmask_int, min_level, use_on_click, quest_stamp, quest_restrict)

        entry = self.str_entries["loc paste"]
        specific_loc = entry.get().strip()
        entry.delete(0, tk.END)

        if specific_loc:
            loc = port_module.parse_loc(specific_loc)

            selected_angle = self.angles_combo.get()
            if selected_angle == "no change":
                pass
            else:
                loc.set_angles(selected_angle)

            position_table = port_module.make_position_table(port_wcid, loc)

            commands = port_body + position_table
            sh.write_sql_file(str(port_wcid) + " " + port_name, "port", ''.join(commands))
        else:
            self.cont.view.console.print("A loc paste is required.")
