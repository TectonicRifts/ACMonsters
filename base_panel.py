import tkinter as tk
from functools import partial
from tkinter import ttk

import settings as st
import file_helper as fh
import view_helper as vh
import labels_module


class BasePanel(tk.Frame):

    def __init__(self, parent, cont):
        super().__init__(parent, bg=st.base_bg)
        self.cont = cont

        norm_font = st.norm_font

        # str entries
        str_labels = ['name', 'kill quest']
        self.str_entries = vh.make_str_entry(self, str_labels)

        creature_type_label = tk.Label(self, text="creature type", font=norm_font, bg=st.base_bg)
        creature_options = sorted(labels_module.get_all_creature_types())
        creature_options.insert(0, "no change")
        self.creature_type_combo = ttk.Combobox(self, values=creature_options, font=norm_font, state="readonly")
        self.creature_type_combo.current(0)

        # int entries
        int_header_label = tk.Label(self, text="Int", font=norm_font, fg='#221CD9', bg=st.base_bg)
        int_labels = ['level', 'xp override', 'luminance', 'lifespan', 'faction bits']
        self.int_entries = vh.make_int_entry(self, int_labels)

        # did entries
        did_header_label = tk.Label(self, text="Data ID", font=norm_font, fg='#221CD9', bg=st.base_bg)
        did_labels = ['combat table', 'wield treasure', 'death treasure']
        self.did_entries = vh.make_int_entry(self, did_labels)

        # float entries
        float_header_label = tk.Label(self, text="Float", font="Arial 12", fg='#221CD9', bg=st.base_bg)
        float_labels = ['health rate', 'visual awareness']
        self.float_entries = vh.make_float_entry(self, float_labels)

        # checkbox entries
        self.edge_slide = tk.IntVar(value=0)
        edge_slide_check = tk.Checkbutton(
            self, text="edge slide", variable=self.edge_slide, font=norm_font, bg=st.base_bg, activebackground=st.base_bg
        )

        self.npc_like_object = tk.IntVar(value=0)
        npc_like_object_check = tk.Checkbutton(
            self, text="npc like object", variable=self.npc_like_object, font=norm_font, bg=st.base_bg, activebackground=st.base_bg
        )

        self.ignore_life_magic = tk.IntVar(value=0)
        ignore_life_check = tk.Checkbutton(
            self, text="life hollow", variable=self.ignore_life_magic, font=norm_font, bg=st.base_bg, activebackground=st.base_bg
        )

        self.ignore_item_magic = tk.IntVar(value=0)
        ignore_item_check = tk.Checkbutton(
            self, text="item hollow", variable=self.ignore_item_magic, font=norm_font, bg=st.base_bg, activebackground=st.base_bg
        )

        self.ignore_shield = tk.IntVar(value=0)
        ignore_shield_check = tk.Checkbutton(
            self, text="shield hollow", variable=self.ignore_shield, font=norm_font, bg=st.base_bg, activebackground=st.base_bg
        )

        self.debuff_immune = tk.IntVar(value=0)
        debuff_immune_check = tk.Checkbutton(
            self, text="debuff immune", variable=self.debuff_immune, font=norm_font, bg=st.base_bg, activebackground=st.base_bg
        )

        self.no_corpse = tk.IntVar(value=0)
        no_corpse_check = tk.Checkbutton(
            self, text="no corpse", variable=self.no_corpse, font=norm_font, bg=st.base_bg, activebackground=st.base_bg
        )

        self.allow_give = tk.IntVar(value=0)
        allow_give_check = tk.Checkbutton(
            self, text="allow give", variable=self.allow_give, font=norm_font, bg=st.base_bg, activebackground=st.base_bg
        )

        # buttons
        set_button = tk.Button(self, text="Set", bg=st.button_bg, command=self.set_misc_stats)
        batch_button = tk.Button(self, text="Run Batch",
                                 command=partial(self.cont.run_sql_batch, self.set_misc_stats))

        xp_from_level_button = tk.Button(self, text="Find XP", command=self.set_xp_from_level)

        # layout
        r = 0
        c = 0

        for name, entry in self.str_entries.items():
            label = tk.Label(self, text=name, font=norm_font, bg=st.base_bg)
            label.grid(row=r, column=c, sticky="e", padx=2)
            entry.grid(row=r, column=c + 1, sticky="ew", padx=2)
            r += 1

        edge_slide_check.grid(row=r, column=c, sticky="w", padx=5)
        npc_like_object_check.grid(row=r, column=c + 1, sticky="w", padx=5)
        r += 1
        ignore_life_check.grid(row=r, column=c, sticky="w", padx=5)
        ignore_item_check.grid(row=r, column=c + 1, sticky="w", padx=5)
        r += 1
        ignore_shield_check.grid(row=r, column=c, sticky="w", padx=5)
        debuff_immune_check.grid(row=r, column=c + 1, sticky="w", padx=5)
        r += 1
        no_corpse_check.grid(row=r, column=c, sticky="w", padx=5)
        allow_give_check.grid(row=r, column=c + 1, sticky="w", padx=5)
        r += 1

        int_header_label.grid(row=r, column=c, sticky="w")
        r += 1
        creature_type_label.grid(row=r, column=c, sticky="e", padx=2)
        self.creature_type_combo.grid(row=r, column=c + 1, sticky="ew", padx=2)
        r += 1

        for name, entry in self.int_entries.items():
            label = tk.Label(self, text=name, font=norm_font, bg=st.base_bg)
            label.grid(row=r, column=c, sticky="e", padx=2)
            entry.grid(row=r, column=c + 1, sticky="ew", padx=2)
            r += 1

        xp_from_level_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        r += 1

        did_header_label.grid(row=r, column=c, sticky="w")
        r += 1
        for name, entry in self.did_entries.items():
            label = tk.Label(self, text=name, font=norm_font, bg=st.base_bg)
            label.grid(row=r, column=c, sticky="e", padx=2)
            entry.grid(row=r, column=c + 1, sticky="ew", padx=2)
            r += 1

        float_header_label.grid(row=r, column=c, sticky="w")
        r += 1
        for name, entry in self.float_entries.items():
            label = tk.Label(self, text=name, font=norm_font, bg=st.base_bg)
            label.grid(row=r, column=c, sticky="e", padx=2)
            entry.grid(row=r, column=c + 1, sticky="ew", padx=2)
            r += 1

        set_button.grid(row=r, column=c, columnspan=2, padx=2, pady=5, sticky="ew")
        r += 1
        batch_button.grid(row=r, column=c, columnspan=2, padx=2, pady=5, sticky="ew")

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)


    def set_misc_stats(self):

        if self.cont.sql_data is not None:
            # creature type
            selected = self.creature_type_combo.get()

            if selected == "no change":
                pass
            else:
                val = labels_module.get_creature_type_int(selected)
                desc = "/* CreatureType - " + selected + " */"
                self.cont.sql_data = fh.set_property(self.cont.sql_data, "int", 2, int(val), desc)

            # str
            my_dict = {
                'name': (1, "/* Name */"),
                'kill quest': (45, "/* KillQuest */")
            }
            self.cont.set_properties(my_dict, self.str_entries, 'str')

            # int
            my_dict = {
                'level': (25, "/* Level */"),
                'xp override': (146, "/* XpOverride */"),
                'luminance': (332, "/* LuminanceAward */"),
                'lifespan': (267, "/* Lifespan */"),
                'faction bits': (281, "/* Faction1Bits */")
            }
            self.cont.set_properties(my_dict, self.int_entries, 'int')

            # did
            my_dict = {
                'combat table': (4, "/* CombatTable */"),
                'wield treasure': (32, "/* WieldedTreasureType */"),
                'death treasure': (35, "/* DeathTreasureType */")
            }
            self.cont.set_properties(my_dict, self.did_entries, 'did')

            # float
            my_dict = {
                'health rate': (3, "/* HealthRate */"),
                'visual awareness': (31, "/* VisualAwarenessRange */")
            }
            self.cont.set_properties(my_dict, self.float_entries, 'float')

            # set to npc
            if self.edge_slide.get() == 1:
                self.cont.sql_data = fh.set_property(self.cont.sql_data, "int", 93, 4195336, "/* PhysicsState - ReportCollisions, Gravity, EdgeSlide */")
                self.cont.sql_data = fh.set_property(self.cont.sql_data, "bool", 42, 1, "/* AllowEdgeSlide */")

            # set npc should appear as an object
            if self.npc_like_object.get() == 1:
                self.cont.sql_data = fh.set_property(self.cont.sql_data, "bool", 52, 1, "/* AiImmobile */")
                self.cont.sql_data = fh.set_property(self.cont.sql_data, "bool", 82, 1, "/* DontTurnOrMoveWhenGiving */")
                self.cont.sql_data = fh.set_property(self.cont.sql_data, "bool", 83, 1, "/* NpcLooksLikeObject */")

            # attacks of the monster ignore life magic, i.e., ignores life armor, imperil, prots, vulns
            if self.ignore_life_magic.get() == 1:
                self.cont.sql_data = fh.set_property(self.cont.sql_data, "bool", 65, 1, "/* IgnoreMagicResist */")

            # attacks of the monster ignore item magic, i.e., impen, brittlemail, banes, lures
            if self.ignore_item_magic.get() == 1:
                self.cont.sql_data = fh.set_property(self.cont.sql_data, "bool", 66, 1, "/* IgnoreMagicArmor */")

            # ignore shield, this is a float
            if self.ignore_shield.get() == 1:
                self.cont.sql_data = fh.set_property(self.cont.sql_data, "float", 151, 1, "/* IgnoreShield */")

            # debuff immune, this is a bool
            if self.debuff_immune.get() == 1:
                self.cont.sql_data = self.cont.sql_data = fh.set_property(self.cont.sql_data, "bool", 103, 1, "/* NonProjectileMagicImmune */")

            # no corpse, this is a bool
            if self.no_corpse.get() == 1:
                self.cont.sql_data = fh.set_property(self.cont.sql_data, "bool", 29, 1, "/* NoCorpse */")

            # allow give, this is a bool
            if self.allow_give.get() == 1:
                self.cont.sql_data = fh.set_property(self.cont.sql_data, "bool", 8, 1, "/* AllowGive */")
        else:
            self.cont.file_warning()

    def set_xp_from_level(self):
        if self.cont.sql_data is not None:
            level = fh.get_property(self.cont.sql_data, "int", 25)[0]

            if level is not None:
                xp_value = fh.get_xp_value(level)

                for name, entry in self.int_entries.items():
                    if name == "xp override":
                        entry.delete(0, tk.END)  # delete existing
                        entry.insert(0, xp_value)  # insert new

