import tkinter as tk
from functools import partial
from tkinter import ttk

import port_module
import settings as st
import file_helper as fh
import view_helper as vh
import labels_module
import gen_module
import sql_helper as sh

class GenPanel(tk.Frame):

    def __init__(self, parent, cont):
        super().__init__(parent, bg=st.base_bg)
        self.cont = cont

        norm_font = st.norm_font

        # gen destruction
        gen_dest_label = tk.Label(self, text="gen dest", font=norm_font, bg=st.base_bg)
        gen_dest_options = sorted(labels_module.get_all_gen_dest_types())
        gen_dest_options.insert(0, "no change")
        self.gen_dest_combo = ttk.Combobox(self, values=gen_dest_options, font=norm_font, state="readonly")
        self.gen_dest_combo.current(0)

        # gen time type
        gen_time_label = tk.Label(self, text="gen time", font=norm_font, bg=st.base_bg)
        gen_time_options = sorted(labels_module.get_all_gen_time_types())
        gen_time_options.insert(0, "no change")
        self.gen_time_combo = ttk.Combobox(self, values=gen_time_options, font=norm_font, state="readonly")
        self.gen_time_combo.current(0)

        # int entries
        int_header_label = tk.Label(self, text="Int", font=norm_font, fg='#221CD9', bg=st.base_bg)
        int_labels = ['gen init', 'gen max']
        self.int_entries = vh.make_int_entry(self, int_labels)

        # float entries
        float_header_label = tk.Label(self, text="Float", font="Arial 12", fg='#221CD9', bg=st.base_bg)
        float_labels = ['regen interval', 'gen radius', 'init delay']
        self.float_entries = vh.make_float_entry(self, float_labels)

        # str entries
        str_header_label = tk.Label(self, text="Str", font="Arial 12", fg='#221CD9', bg=st.base_bg)
        str_labels = ['gen event']
        self.str_entries = vh.make_str_entry(self, str_labels)

        # buttons
        set_button = tk.Button(self, text="Set", bg=st.button_bg, command=self.set_gen_properties)
        batch_button = tk.Button(self, text="Run Batch",
                                 command=partial(self.cont.run_sql_batch, self.set_gen_properties))

        # gen templates
        self.specific_locs = []

        gen_header_label = tk.Label(self, text="Gen Table", font=norm_font, fg='#221CD9', bg=st.base_bg)

        gen_int_labels = ['gen wcid', 'top total', 'scatter total']
        self.gen_int_entries = vh.make_int_entry(self, gen_int_labels)

        gen_str_labels = ['gen name', 'loc paste']
        self.gen_str_entries = vh.make_str_entry(self, gen_str_labels)

        gen_angles_label = tk.Label(self, text="loc facing", font=norm_font, bg=st.base_bg)
        gen_angles_options = list(port_module.direction_angles.keys())
        gen_angles_options.insert(0, "no change")
        self.gen_angles_combo = ttk.Combobox(self, values=gen_angles_options, font=norm_font, state="readonly")
        self.gen_angles_combo.current(0)

        template_label = tk.Label(self, text="template", font=norm_font, bg=st.base_bg)
        gen_templates = ["default", "wave"]
        template_options = gen_templates
        self.templates_combo = ttk.Combobox(self, values=template_options, font=norm_font, state="readonly")
        self.templates_combo.current(0)

        add_loc_button = tk.Button(self, text="Add Loc", command=self.add_specific_loc)
        clear_locs_button = tk.Button(self, text="Clear Locs", command=self.clear_specific_locs)

        set_gen_button = tk.Button(self, text="Set", bg=st.button_bg, command=self.set_gen_table)
        make_gen_button = tk.Button(self, text="Make Gen", command=self.make_standalone_gen)

        # layout
        r = 0
        c = 0

        int_header_label.grid(row=r, column=c, sticky="w", padx=2)
        r += 1
        gen_dest_label.grid(row=r, column=c, sticky="e", padx=2)
        self.gen_dest_combo.grid(row=r, column=c + 1, sticky="ew", padx=2)
        r += 1
        gen_time_label.grid(row=r, column=c, sticky="e", padx=2)
        self.gen_time_combo.grid(row=r, column=c + 1, sticky="ew", padx=2)
        r += 1

        for name, entry in self.int_entries.items():
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

        str_header_label.grid(row=r, column=c, sticky="w", padx=2)
        r += 1
        for name, entry in self.str_entries.items():
            label = tk.Label(self, text=name, font=norm_font, bg=st.base_bg)
            label.grid(row=r, column=c, sticky="e", padx=2)
            entry.grid(row=r, column=c + 1, sticky="ew", padx=2)
            r += 1

        set_button.grid(row=r, column=c, columnspan=2, padx=5, pady=5, sticky="ew")
        r += 1
        batch_button.grid(row=r, column=c, columnspan=2, padx=5, pady=5, sticky="ew")
        r += 1

        gen_header_label.grid(row=r, column=c, sticky="w", padx=2)
        r += 1
        template_label.grid(row=r, column=c, sticky="e", padx=2)
        self.templates_combo.grid(row=r, column=c + 1, sticky="ew", padx=2)
        r += 1
        for name, entry in self.gen_int_entries.items():
            label = tk.Label(self, text=name, font=norm_font, bg=st.base_bg)
            label.grid(row=r, column=c, sticky="e", padx=2)
            entry.grid(row=r, column=c + 1, sticky="ew", padx=2)
            r += 1
        for name, entry in self.gen_str_entries.items():
            label = tk.Label(self, text=name, font=norm_font, bg=st.base_bg)
            label.grid(row=r, column=c, sticky="e", padx=2)
            entry.grid(row=r, column=c + 1, sticky="ew", padx=2)
            r += 1
        gen_angles_label.grid(row=r, column=c, sticky="e", padx=2)
        self.gen_angles_combo.grid(row=r, column=c + 1, sticky="ew", padx=2)
        r += 1
        add_loc_button.grid(row=r, column=c, padx=2, pady=5, sticky="ew")
        r += 1
        clear_locs_button.grid(row=r, column=c, padx=2, pady=5, sticky="ew")
        r += 1
        set_gen_button.grid(row=r, column=c, columnspan=2, padx=2, pady=5, sticky="ew")
        r += 1
        make_gen_button.grid(row=r, column=c, columnspan=2, padx=2, pady=5, sticky="ew")

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

    def set_gen_properties(self):
        # gen dest type
        selected = self.gen_dest_combo.get()

        if selected == "no change":
            pass
        else:
            val = labels_module.get_gen_dest_int(selected)
            desc = "/* GeneratorDestructionType - " + selected + " */"
            self.cont.weenie_sql = fh.set_property(self.cont.weenie_sql, "int", 103, int(val), desc)

        # gen time type
        selected = self.gen_time_combo.get()

        if selected == "no change":
            pass
        else:
            val = labels_module.get_gen_time_int(selected)
            desc = "/* GeneratorTimeType - " + selected + " */"
            self.cont.weenie_sql = fh.set_property(self.cont.weenie_sql, "int", 142, int(val), desc)

            # to destroy spawns when gen event ends
            if selected == "Event":
                desc = "/* GeneratorEndDestructionType - Destroy " + selected + " */"
                self.cont.weenie_sql = fh.set_property(self.cont.weenie_sql, "int", 145, 2, desc)

        # int
        my_dict = {
            'gen init': (82, "/* InitGeneratedObjects */"),
            'gen max': (81, "/* MaxGeneratedObjects */")
        }
        self.cont.set_properties(my_dict, self.int_entries, 'int')

        # float
        my_dict = {
            'regen interval': (41, "/* RegenerationInterval */"),
            'gen radius': (43, "/* GeneratorRadius */"),
            'init delay': (121, "/* GeneratorInitialDelay */")
        }
        self.cont.set_properties(my_dict, self.float_entries, 'float')

        # str
        my_dict = {
            'gen event': (34, "/* GeneratorEvent */")
        }
        self.cont.set_properties(my_dict, self.str_entries, 'str')

    def add_specific_loc(self):
        entry = self.gen_str_entries["loc paste"]
        specific_loc = entry.get().strip()
        entry.delete(0, tk.END)
        
        if specific_loc:
            loc = port_module.parse_loc(specific_loc)

            selected_angle = self.gen_angles_combo.get()
            if selected_angle == "no change":
                pass
            else:
                loc.set_angles(selected_angle)

            self.specific_locs.append(loc)
            loc_str = f"@teleloc {loc.cell_id} [{loc.ox} {loc.oy} {loc.oz}] {loc.aw} {loc.ax} {loc.ay} {loc.az}\n"
            self.cont.print("Added: " + loc_str)
            self.cont.print("Total locs: " + str(len(self.specific_locs)) + "\n")

    def clear_specific_locs(self):
        self.specific_locs.clear()
        self.cont.print("Cleared all specific locs.\n")

    def build_gen_table(self, gen_wcid: int) -> list:
        gen_rows = []
        child_wcid = gen_wcid + 1

        top_total = self.gen_int_entries["top total"].get()
        top_total = int(top_total) if top_total else 0

        scatter_total = self.gen_int_entries["scatter total"].get()
        scatter_total = int(scatter_total) if scatter_total else 0

        specific_total = len(self.specific_locs)
        tot_rows = top_total + scatter_total + specific_total

        if tot_rows == 0:
            self.cont.print("Add at least one row to the generator table.\n")
            return gen_rows

        selected_template = self.templates_combo.get()

        if selected_template == "wave":
            delay = 3600
            # list with -1 repeated tot_rows times
            gen_prs = [-1] * tot_rows
        else:
            delay = 30
            gen_prs = gen_module.get_gen_prs(tot_rows)

        pr_index = 0

        for i in range(top_total):
            spawn_pr = gen_prs[pr_index]
            gen_rows.append(
                gen_module.make_gen_row(gen_wcid, child_wcid, fh.GenWhere.TOP.value, delay, spawn_pr)
            )
            child_wcid += 1
            pr_index += 1

        for i in range(scatter_total):
            spawn_pr = gen_prs[pr_index]
            gen_rows.append(
                gen_module.make_gen_row(gen_wcid, child_wcid, fh.GenWhere.SCATTER.value, delay, spawn_pr)
            )
            child_wcid += 1
            pr_index += 1

        for loc in self.specific_locs:
            spawn_pr = gen_prs[pr_index]
            gen_rows.append(
                gen_module.make_gen_row(gen_wcid, child_wcid, fh.GenWhere.SPECIFIC.value, delay, spawn_pr, loc)
            )
            child_wcid += 1
            pr_index += 1

        return gen_module.get_gen_table(gen_rows)

    def set_gen_table(self):
        gen_wcid = self.cont.get_wcid()
        gen_table = self.build_gen_table(gen_wcid)
        self.cont.set_sql_table("`weenie_properties_generator`", gen_table)

    def make_standalone_gen(self):
        # gen name and wcid
        gen_name = self.gen_str_entries["gen name"].get().strip()
        if not gen_name:
            gen_name = "Placeholder Gen"

        try:
            gen_wcid = int(self.gen_int_entries["gen wcid"].get())
        except ValueError:
            gen_wcid = 90750

        # other gen properties
        gen_init = self.int_entries["gen init"].get()
        gen_max = self.int_entries["gen max"].get()

        gen_init = int(gen_init) if gen_init else 1
        gen_max = int(gen_max) if gen_max else 1

        regen_interval = self.float_entries["regen interval"].get()
        gen_radius = self.float_entries["gen radius"].get()
        init_delay = self.float_entries["init delay"].get()

        regen_interval = int(regen_interval) if regen_interval else 60
        gen_radius = int(gen_radius) if gen_radius else 20
        init_delay = int(init_delay) if init_delay else 0

        # gen body
        selected_time = self.gen_time_combo.get()
        if selected_time == "Event":
            event_name = self.str_entries["gen event"].get().strip()
            gen_body = gen_module.get_event_gen_body(
                gen_wcid, gen_name, gen_init, gen_max, regen_interval, gen_radius, event_name, init_delay
            )
        else:
            gen_body = gen_module.get_default_gen_body(
                gen_wcid, gen_name, gen_init, gen_max, regen_interval, gen_radius
            )

        gen_table = self.build_gen_table(gen_wcid)

        sql_statements = gen_body + gen_table
        sh.write_sql_file(str(gen_wcid) + " " + gen_name, "gen", ''.join(sql_statements))
