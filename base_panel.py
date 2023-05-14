import tkinter as tk
from functools import partial
from tkinter import ttk
import settings as st
import file_helper
import view_helper as vh
import labels_module


class BasePanel:

    def __init__(self, parent, cont):
        self.frame = tk.Frame(parent)
        self.cont = cont

        norm_font = st.norm_font

        str_labels = ['name', 'kill quest']
        self.str_entries = vh.make_str_entry(self.frame, str_labels)

        creature_type_label = tk.Label(self.frame, text="creature type", font=norm_font)
        creature_options = sorted(labels_module.get_all_creature_types())
        creature_options.insert(0, "no change")
        self.creature_type_combo = ttk.Combobox(self.frame, values=creature_options, font=norm_font, state="readonly")
        self.creature_type_combo.current(0)

        gen_dest_label = tk.Label(self.frame, text="gen dest", font=norm_font)
        gen_dest_options = sorted(labels_module.get_all_gen_dest_types())
        gen_dest_options.insert(0, "no change")
        self.gen_dest_combo = ttk.Combobox(self.frame, values=gen_dest_options, font=norm_font, state="readonly")
        self.gen_dest_combo.current(0)

        int_header_label = tk.Label(self.frame, text="Int", font=norm_font, fg='blue')

        int_labels = ['gen init', 'gen max', 'level', 'xp override', 'faction bits']
        self.int_entries = vh.make_int_entry(self.frame, int_labels)

        did_header_label = tk.Label(self.frame, text="Data ID", font=norm_font, fg='blue')

        did_labels = ['combat table', 'wield treasure', 'death treasure']
        self.did_entries = vh.make_int_entry(self.frame, did_labels)

        float_header_label = tk.Label(self.frame, text="Float", font="Arial 12", fg='blue')

        float_labels = ['health rate', 'regen interval', 'gen radius', 'visual awareness']
        self.float_entries = vh.make_float_entry(self.frame, float_labels)

        self.edge_slide = tk.IntVar(value=0)
        edge_slide_check = tk.Checkbutton(self.frame, text="edge slide", variable=self.edge_slide, font=norm_font)

        self.npc_like_object = tk.IntVar(value=0)
        npc_like_object_check = tk.Checkbutton(self.frame, text="npc like object", variable=self.npc_like_object,
                                               font=norm_font)

        self.ignore_life_magic = tk.IntVar(value=0)
        ignore_life_check = tk.Checkbutton(
            self.frame, text="life hollow", variable=self.ignore_life_magic, font=norm_font)

        self.ignore_item_magic = tk.IntVar(value=0)
        ignore_item_check = tk.Checkbutton(
            self.frame, text="item hollow", variable=self.ignore_item_magic, font=norm_font)

        self.ignore_shield = tk.IntVar(value=0)
        ignore_shield_check = tk.Checkbutton(
            self.frame, text="shield hollow", variable=self.ignore_shield, font=norm_font)

        self.no_corpse = tk.IntVar(value=0)
        no_corpse_check = tk.Checkbutton(
            self.frame, text="no corpse", variable=self.no_corpse, font=norm_font)

        set_button = tk.Button(self.frame, text="Set", bg="lightblue", command=self.set_misc_stats)
        batch_button = tk.Button(self.frame, text="Run Batch",
                                 command=partial(self.cont.run_sql_batch, self.set_misc_stats))

        # layout

        r = 0
        c = 0

        for name, entry in self.str_entries.items():
            label = tk.Label(self.frame, text=name, font=norm_font)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1

        edge_slide_check.grid(row=r, column=c, sticky="w", padx=5)
        npc_like_object_check.grid(row=r, column=c + 1, sticky="w", padx=5)
        r += 1
        ignore_life_check.grid(row=r, column=c, sticky="w", padx=5)
        ignore_item_check.grid(row=r, column=c + 1, sticky="w", padx=5)
        r += 1
        ignore_shield_check.grid(row=r, column=c, sticky="w", padx=5)
        no_corpse_check.grid(row=r, column=c + 1, sticky="w", padx=5)
        r += 1

        int_header_label.grid(row=r, column=c)
        r += 1

        creature_type_label.grid(row=r, column=c)
        self.creature_type_combo.grid(row=r, column=c + 1)
        r += 1

        gen_dest_label.grid(row=r, column=c)
        self.gen_dest_combo.grid(row=r, column=c + 1)
        r += 1

        for name, entry in self.int_entries.items():
            label = tk.Label(self.frame, text=name, font=norm_font)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1

        did_header_label.grid(row=r, column=c)
        r += 1

        for name, entry in self.did_entries.items():
            label = tk.Label(self.frame, text=name, font=norm_font)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1

        float_header_label.grid(row=r, column=c)
        r += 1

        for name, entry in self.float_entries.items():
            label = tk.Label(self.frame, text=name, font=norm_font)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1

        set_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        r += 1
        batch_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")

    def set_misc_stats(self):

        if len(self.cont.sql_commands) > 0:

            # creature type
            selected = self.creature_type_combo.get()

            if selected == "no change":
                pass
            else:
                val = labels_module.get_creature_type_int(selected)
                desc = "/* CreatureType - " + selected + " */"
                self.cont.sql_commands = file_helper.set_property(self.cont.sql_commands, "int", 2, int(val), desc)

            # gen dest type
            selected = self.gen_dest_combo.get()

            if selected == "no change":
                pass
            else:
                val = labels_module.get_gen_dest_int(selected)
                desc = "/* GeneratorDestructionType - " + selected + " */"
                self.cont.sql_commands = file_helper.set_property(self.cont.sql_commands, "int", 103, int(val), desc)

            # str
            my_dict = {'name': (1, "/* Name */"),
                       'kill quest': (45, "/* KillQuest */")
                       }
            self.cont.set_properties(my_dict, self.str_entries, 'str')

            # int
            my_dict = {'gen init': (82, "/* InitGeneratedObjects */"),
                       'gen max': (81, "/* MaxGeneratedObjects */"),
                       'level': (25, "/* Level */"),
                       'xp override': (146, "/* XpOverride */"),
                       'faction bits': (281, "/* Faction1Bits */")
                       }
            self.cont.set_properties(my_dict, self.int_entries, 'int')

            # did
            my_dict = {'combat table': (4, "/* CombatTable */"),
                       'wield treasure': (32, "/* WieldedTreasureType */"),
                       'death treasure': (35, "/* DeathTreasureType */")
                       }
            self.cont.set_properties(my_dict, self.did_entries, 'did')

            # float
            my_dict = {'heartbeat interval': (1, "/* HeartbeatInterval */"),
                       'heartbeat timestamp': (2, "/* HeartbeatTimestamp */"),
                       'health rate': (3, "/* HealthRate */"),
                       'regen interval': (41, "/* RegenerationInterval */"),
                       'gen radius': (43, "/* GeneratorRadius */"),
                       'visual awareness': (31, "/* VisualAwarenessRange */")
                       }
            self.cont.set_properties(my_dict, self.float_entries, 'float')

            # set to npc
            if self.edge_slide.get() == 1:
                self.cont.sql_commands = file_helper.set_property(self.cont.sql_commands, "bool", 42, 1,
                                                                  "/* AllowEdgeSlide */")
            # set npc should appear as an object
            if self.npc_like_object.get() == 1:
                self.cont.sql_commands = file_helper.set_property(self.cont.sql_commands, "bool", 52, 1,
                                                                  "/* AiImmobile */")
                self.cont.sql_commands = file_helper.set_property(self.cont.sql_commands, "bool", 82, 1,
                                                                  "/* DontTurnOrMoveWhenGiving */")
                self.cont.sql_commands = file_helper.set_property(self.cont.sql_commands, "bool", 83, 1,
                                                                  "/* NpcLooksLikeObject */")

            # attacks of the monster ignore life magic, i.e., ignores life armor, imperil, prots, vulns
            if self.ignore_life_magic.get() == 1:
                self.cont.sql_commands = file_helper.set_property(self.cont.sql_commands, "bool", 65, 1,
                                                                  "/* IgnoreMagicResist */")

            # attacks of the monster ignore item magic, i.e., impen, brittlemail, banes, lures
            if self.ignore_item_magic.get() == 1:
                self.cont.sql_commands = file_helper.set_property(self.cont.sql_commands, "bool", 66, 1,
                                                                  "/* IgnoreMagicArmor */")
            # ignore shield, this is a float
            if self.ignore_shield.get() == 1:
                self.cont.sql_commands = file_helper.set_property(self.cont.sql_commands, "float", 151, 1,
                                                                  "/* IgnoreShield */")
            # no corpse, this is a bool
            if self.no_corpse.get() == 1:
                self.cont.sql_commands = file_helper.set_property(self.cont.sql_commands, "bool", 29, 1,
                                                                  "/* NoCorpse */")
