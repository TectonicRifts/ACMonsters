import re
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import tkinter.scrolledtext as scrolledtext
import os
from functools import partial
import file_helper
import quest_helper
import view_helper as vh
import labels_module
import tkinter.messagebox
from ctypes import windll
from pathlib import Path


class Toolbar:

    def __init__(self, parent, cont):
        self.frame = tk.Frame(parent)

        open_sql_button = tk.Button(self.frame, text="Open File", command=cont.open_sql_file)
        name_filter_label = tk.Label(self.frame, text="Name must contain", font=norm_font)
        name_filter_entry = tk.Entry(self.frame, bg="white", font=norm_font)

        open_sql_folder_button = tk.Button(self.frame, text="Open Folder",
                                           command=partial(cont.open_sql_folder, name_filter_entry))

        save_sql_button = tk.Button(self.frame, text="Save", bg="lightblue", command=cont.save_sql)

        # layout
        name_filter_label.grid(row=0, column=0, sticky="ew")
        name_filter_entry.grid(row=0, column=1, sticky="ew")
        open_sql_folder_button.grid(row=0, column=2, sticky="ew")
        open_sql_button.grid(row=0, column=3, ipadx=10, ipady=0, sticky="ew")
        save_sql_button.grid(row=0, column=4, ipadx=25, ipady=0, sticky="ew")


class View:

    def __init__(self, parent, cont):
        self.frame = tk.Frame(parent)
        self.cont = cont

        right_nb = ttk.Notebook(self.frame)
        left_nb = ttk.Notebook(self.frame)

        # make panels
        self.console = ConsolePanel(left_nb, cont)
        attributes_panel = AttributesPanel(right_nb, cont)
        item_panel = ItemPanel(right_nb, cont)
        mods_panel = ModsPanel(right_nb, cont)
        skills_panel = SkillsPanel(right_nb, cont)
        art_panel = ArtPanel(right_nb, cont)
        copy_panel = AutoPanel(right_nb, cont)
        port_panel = PortalPanel(right_nb, cont)
        kill_task_panel = KillTaskPanel(right_nb)
        event_panel = EventPanel(right_nb)

        # left
        left_nb.add(self.console.frame, text="Console")

        # right
        base_panel = BasePanel(right_nb, cont)

        right_nb.add(base_panel.frame, text="Base")
        right_nb.add(attributes_panel.frame, text="Attr")
        right_nb.add(skills_panel.frame, text="Skill")
        right_nb.add(item_panel.frame, text="Item")
        right_nb.add(port_panel.frame, text="Port")
        right_nb.add(mods_panel.frame, text="Mods")
        right_nb.add(art_panel.frame, text="Art")
        right_nb.add(kill_task_panel.frame, text="Task")
        right_nb.add(event_panel.frame, text="Event")
        right_nb.add(copy_panel.frame, text="Auto")

        left_nb.grid(row=0, column=0)
        right_nb.grid(row=0, column=1, sticky="ns")

        toolbar = Toolbar(self.frame, cont)
        toolbar.frame.grid(row=1, column=0, columnspan=2)

        self.frame.grid()


class Controller:

    def __init__(self, parent):

        # this is the sql file (i.e., sql commands) currently being worked on
        self.sql_commands = None

        # this is the name of the output file
        self.sql_output = None

        # the keys are sql file names, the values are file contents (i.e., sql commands)
        self.sql_dict = {}

        # this is the sql file (i.e., the commands from it) being used as a template to copy from
        self.template_commands = None

        self.view = View(parent, self)

    def run_sql_batch(self, func):

        Path("output/weenies").mkdir(parents=True, exist_ok=True)
        self.view.console.clear()

        for file_name, commands in self.sql_dict.items():
            self.sql_commands = commands
            self.sql_output = file_name
            self.view.console.print("Working on " + file_name + "...")
            func()
            self.save_sql()
            self.view.console.print("Done.\n")

    def save_sql(self):

        if len(self.sql_commands) > 0:
            with open("output/weenies/" + self.sql_output, 'w') as file_object:
                for command in self.sql_commands:
                    command = command.replace(";", "")
                    if command.strip() != "":
                        file_object.write(command + ";")
                file_object.write("\n")
        else:
            tk.messagebox.showinfo("Info", "There was no file to save.")

    def open_sql_file(self):
        """Load a single .sql file."""
        my_file = filedialog.askopenfilename(filetypes=[("sql files", "*.sql")])
        if my_file:
            with open(my_file) as file_object:
                sql_file = file_object.read()
                self.sql_commands = sql_file.split(";")

                # this is the output file name
                self.sql_output = os.path.split(my_file)[1]
                self.view.console.clear()
                self.view.console.print("Working with: " + self.sql_output + "\n")

    def open_sql_folder(self, name_filter_entry):
        """Load all .sql files in a folder for batch processing. This will also walk through all subdirectories
        in the folder."""
        file_folder = filedialog.askdirectory()
        name_filter = name_filter_entry.get().strip().lower()

        my_list = []

        for subdir, dirs, files in os.walk(file_folder):
            for file in files:
                if ".sql" in file:
                    my_list.append(os.path.join(subdir, file))

        self.sql_dict.clear()

        self.view.console.clear()
        self.view.console.print("Found the following files:\n")

        for file_name in my_list:

            with open(os.path.join(file_folder, file_name)) as file_object:
                if name_filter.strip() != "":
                    if name_filter in file_name.lower():
                        sql_file = file_object.read()
                        commands = sql_file.split(";")
                        base_name = os.path.basename(file_name)
                        self.sql_dict[base_name] = commands
                        self.view.console.print(base_name + "\n")
                else:
                    sql_file = file_object.read()
                    commands = sql_file.split(";")
                    base_name = os.path.basename(file_name)
                    self.sql_dict[base_name] = commands
                    self.view.console.print(base_name + "\n")

    def set_properties(self, my_dict, stat_entries, tag):
        """Set properties for a list of entries. This function is for weenies in .sql format."""
        # i has the property key and comment in a tuple
        for label, i in my_dict.items():
            val = stat_entries[label].get().strip()
            if val != "":
                if tag == 'int' or tag == 'did':
                    val = int(val)
                elif tag == 'float':
                    val = round(float(val), 4)
                    if val.is_integer():
                        val = int(val)

                self.sql_commands = file_helper.set_property(self.sql_commands, tag, i[0], val, i[1])

    def set_attributes(self, my_dict, stat_entries, do_override, are_vitals):
        # i has the property key and comment in a tuple
        for label, i in my_dict.items():
            val = stat_entries[label].get().strip()
            if val != "":
                val = int(val)
                if are_vitals:
                    self.sql_commands = file_helper.set_attribute_2(self.sql_commands, i[0], val, i[1], do_override)
                else:
                    self.sql_commands = file_helper.set_attribute_1(self.sql_commands, i[0], val, i[1], do_override)


class PortalPanel:

    def __init__(self, parent, cont):
        """Use for making portals."""
        self.frame = tk.Frame(parent)
        self.cont = cont

        int_header_label = tk.Label(self.frame, text="Int", font=norm_font, fg='blue')

        int_label_list = ['min level']
        self.int_entries = vh.make_int_entry(self.frame, int_label_list)

        portal_restriction_label = tk.Label(self.frame, text="restriction", font=norm_font)
        options = ['no change',
                   '1 - unrest',
                   '17 - unrest, no sum',
                   '49 - unrest, no sum, no rec'
                   ]
        self.portal_bitmask_combo = ttk.Combobox(self.frame, values=options, font=norm_font, state="readonly")
        self.portal_bitmask_combo.current(0)

        str_header_label = tk.Label(self.frame, text="Str", font=norm_font, fg='blue')

        str_label_list = ['quest flag']
        self.str_entries = vh.make_str_entry(self.frame, str_label_list)

        str_label_list_2 = ['destination']
        self.pos_entries = vh.make_str_entry(self.frame, str_label_list_2)

        set_button = tk.Button(self.frame, text="Set", bg="lightblue", command=self.set_portal)
        batch_button = tk.Button(self.frame, text="Run Batch",
                                 command=partial(self.cont.run_sql_batch, self.set_portal))

        tooltip = "Destination is a /myloc paste."
        tooltip_label = tk.Label(self.frame, text=tooltip, font=norm_font, fg="dark green", wraplength=420,
                                 justify=tk.LEFT)

        # layout
        r = 0
        c = 0

        int_header_label.grid(row=r, column=c)
        r += 1

        for name, entry in self.int_entries.items():
            label = tk.Label(self.frame, text=name, font=norm_font)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1

        portal_restriction_label.grid(row=r, column=c)
        self.portal_bitmask_combo.grid(row=r, column=c + 1)
        r += 1

        str_header_label.grid(row=r, column=c)
        r += 1

        for name, entry in self.str_entries.items():
            label = tk.Label(self.frame, text=name, font=norm_font)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1

        for name, entry in self.pos_entries.items():
            label = tk.Label(self.frame, text=name, font=norm_font)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1

        set_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        r += 1
        batch_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        r += 1
        tooltip_label.grid(row=r, column=c, columnspan=2, sticky="w")

    def set_portal(self):

        if len(self.cont.sql_commands) > 0:

            # int
            my_dict = {'min level': (86, "/* MinLevel */")}
            self.cont.set_properties(my_dict, self.int_entries, 'int')

            # the bitmask is used for recall and summon restrictions on the portal
            portal_bitmask = self.portal_bitmask_combo.get()

            if portal_bitmask == "no change":
                pass

            elif portal_bitmask == "1 - unrest":
                desc = "/* PortalBitmask - Unrestricted */"
                self.cont.sql_commands = file_helper.set_property(self.cont.sql_commands, "int", 111, 1, desc)

            elif portal_bitmask == "17 - unrest, no summon":
                desc = "/* PortalBitmask - Unrestricted, NoSummon  */"
                self.cont.sql_commands = file_helper.set_property(self.cont.sql_commands, "int", 111, 17, desc)

            elif portal_bitmask == "49 - unrest, no sum, no rec":
                desc = "/* PortalBitmask - Unrestricted, NoSummon, NoRecall */"
                self.cont.sql_commands = file_helper.set_property(self.cont.sql_commands, "int", 111, 49, desc)

            else:
                tk.messagebox.showerror('Error', "Invalid value for portal restriction: " + str(portal_bitmask))

            # str
            my_dict = {'quest flag': (37, "/* QuestRestriction */")}
            self.cont.set_properties(my_dict, self.str_entries, 'string')

            # destination, should be a /myloc paste
            loc_paste = self.pos_entries['destination'].get().strip()
            file_helper.set_position(self.cont.sql_commands, loc_paste)


class ItemPanel:

    def __init__(self, parent, cont):
        """Use for making items."""
        self.frame = tk.Frame(parent)
        self.cont = cont

        int_header_label = tk.Label(self.frame, text="Int", font=norm_font, fg='blue')

        int_label_list = ['value', 'burden', 'max stack', 'lock resist', 'on use make']
        self.int_entries = vh.make_int_entry(self.frame, int_label_list)

        # attuned, 1 = yes, 0 = no
        self.is_attuned = tk.IntVar(value=0)
        attuned_check_box = tk.Checkbutton(self.frame, text="attuned", variable=self.is_attuned, font=norm_font)

        self.can_sell = tk.IntVar(value=0)
        sellable_check_box = tk.Checkbutton(self.frame, text="can sell", variable=self.can_sell, font=norm_font)

        # bonded, -2 = destroy on death, 0 = normal, 1 = bonded
        bonded_status_label = tk.Label(self.frame, text="bonded", font=norm_font)
        options = ['no change', 'no', 'yes', 'destroy on death']
        self.bonded_status_combo = ttk.Combobox(self.frame, values=options, font=norm_font, state="readonly")
        self.bonded_status_combo.current(0)

        str_header_label = tk.Label(self.frame, text="Str", font="Arial 12", fg='blue')

        str_label_list = ['use', 'short desc', 'long desc', 'lock code', 'key code', 'pickup timer']
        self.str_entries = vh.make_str_entry(self.frame, str_label_list)

        make_quest_button = tk.Button(self.frame, text="Make Quest", command=partial(self.make_quest))

        set_button = tk.Button(self.frame, text="Set", bg="lightblue", command=self.set_item)
        batch_button = tk.Button(self.frame, text="Run Batch",
                                 command=partial(self.cont.run_sql_batch, self.set_item))

        # layout
        r = 0
        c = 0

        int_header_label.grid(row=r, column=c)
        r += 1

        for name, entry in self.int_entries.items():
            label = tk.Label(self.frame, text=name, font=norm_font)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1

        sellable_check_box.grid(row=r, column=c)
        attuned_check_box.grid(row=r, column=c + 1)
        r += 1

        bonded_status_label.grid(row=r, column=c)
        self.bonded_status_combo.grid(row=r, column=c + 1)
        r += 1

        str_header_label.grid(row=r, column=c)
        r += 1

        for name, entry in self.str_entries.items():
            label = tk.Label(self.frame, text=name, font=norm_font)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1

        make_quest_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        r += 1
        set_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        r += 1
        batch_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")

    def set_item(self):

        if len(self.cont.sql_commands) > 0:

            is_stackable = False

            # int
            val = self.int_entries['max stack'].get().strip()
            if val != "":
                val = int(val)
                self.cont.sql_commands = file_helper.set_property(self.cont.sql_commands, "int", 11, val,
                                                                  "/* MaxStackSize */")
                self.cont.sql_commands = file_helper.set_property(self.cont.sql_commands, "int", 12, 1,
                                                                  "/* StackSize */")
                is_stackable = True

            val = self.int_entries['value'].get().strip()
            if val != "":
                val = int(val)
                self.cont.sql_commands = file_helper.set_property(
                    self.cont.sql_commands, "int", 19, val, "/* Value */")
                if is_stackable:
                    self.cont.sql_commands = file_helper.set_property(
                        self.cont.sql_commands, "int", 15, val, "/* StackUnitValue */")

            val = self.int_entries['burden'].get().strip()
            if val != "":
                val = int(val)
                self.cont.sql_commands = file_helper.set_property(
                    self.cont.sql_commands, "int", 5, val, "/* EncumbranceVal */")
                if is_stackable:
                    self.cont.sql_commands = file_helper.set_property(
                        self.cont.sql_commands, "int", 13, val, "/* StackUnitEncumbrance */")

            val = self.int_entries['lock resist'].get().strip()  # lockpick resistance
            if val != "":
                val = int(val)
                self.cont.sql_commands = file_helper.set_property(
                    self.cont.sql_commands, "int", 38, val, "/* ResistLockpick */")
                self.cont.sql_commands = file_helper.set_property(
                    self.cont.sql_commands, "bool", 2, 0, "/* Open */")
                self.cont.sql_commands = file_helper.set_property(
                    self.cont.sql_commands, "bool", 34, 0, "/* DefaultOpen */")
                self.cont.sql_commands = file_helper.set_property(
                    self.cont.sql_commands, "bool", 3, 1, "/* Locked */")
                self.cont.sql_commands = file_helper.set_property(
                    self.cont.sql_commands, "bool", 35, 1, "/* DefaultLocked */")

            val = self.int_entries['on use make'].get().strip()  # on use, destroy and make another item
            if val != "":
                val = int(val)  # this input is a wcid
                self.cont.sql_commands = file_helper.set_property(
                    self.cont.sql_commands, "did", 38, val, "/* UseCreateItem */")

            # attuned
            self.cont.sql_commands = file_helper.set_property(
                self.cont.sql_commands, "int", 114, self.is_attuned.get(), "/* Attuned */")

            # can sell
            self.cont.sql_commands = file_helper.set_property(
                self.cont.sql_commands, "bool", 69, self.can_sell.get(), "/* IsSellable */")

            # bonded
            bonded = self.bonded_status_combo.get()

            if bonded == "no change":
                pass
            elif bonded == "no":
                self.cont.sql_commands = file_helper.set_property(
                    self.cont.sql_commands, "int", 33, 0, "/* Bonded - Normal*/")

            elif bonded == "yes":
                self.cont.sql_commands = file_helper.set_property(
                    self.cont.sql_commands, "int", 33, 1, "/* Bonded - Bonded*/")

            elif bonded == "destroy on death":
                self.cont.sql_commands = file_helper.set_property(
                    self.cont.sql_commands, "int", 33, -2, "/* Bonded - Destroy */")
            else:
                tk.messagebox.showerror('Error', "Invalid value for bonded: " + str(bonded))

            # str
            my_dict = {'use': (14, "/* Use */"),
                       'short desc': (15, "/* ShortDesc */"),
                       'long desc': (16, "/* LongDesc */"),
                       'lock code': (12, "/* LockCode */"),
                       'key code': (13, "/* KeyCode */"),
                       'pickup timer': (33, "/* Quest */")
                       }

            self.cont.set_properties(my_dict, self.str_entries, 'str')

    def make_quest(self):
        """Makes a quest sql file."""
        quest_name = self.str_entries['pickup timer'].get().strip()

        if quest_name:
            quest_helper.make_quest_sql(quest_name)
        else:
            tk.messagebox.showerror("Error", "Enter a pickup timer.")


class WeaponDamagePanel:

    def __init__(self, parent, cont):
        self.frame = tk.Frame(parent)
        self.cont = cont

        # all fields are required here
        weap_dmg_label = tk.Label(self.frame, text="Weapon Damage", font=norm_font, fg='blue')
        labels = ['min', 'max']
        self.weapon_dmg = vh.make_int_entry(self.frame, labels)

        tooltip = "Auto-computes and sets the variance of the weapon to get desired min and max damage."
        tooltip_label = tk.Label(self.frame, text=tooltip, font=norm_font, fg="dark green", wraplength=420,
                                 justify=tk.LEFT)

        set_button = tk.Button(self.frame, text="Set", bg="lightblue", command=self.set_weapon_dmg)
        batch_button = tk.Button(self.frame, text="Run Batch",
                                 command=partial(self.cont.set_batch, self.set_weapon_dmg))

        # layout
        r = 0
        c = 0

        weap_dmg_label.grid(row=r, column=c)
        r += 1

        for name, entry in self.weapon_dmg.items():
            label = tk.Label(self.frame, text=name, font=norm_font)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1

        set_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        batch_button.grid(row=r, column=c + 1, padx=5, pady=5, sticky="ew")

        r += 1
        tooltip_label.grid(row=r, column=c, columnspan=2)

    def set_weapon_dmg(self):

        if self.cont.input_file:

            wpn_min = self.weapon_dmg['min'].get()
            wpn_max = self.weapon_dmg['max'].get()

            if wpn_min != "" and wpn_max != "":
                wpn_var = self.get_weapon_variance(wpn_min, wpn_max)
                self.cont.json_updater.set_stat(self.cont.input_file, 'intStats', 44, wpn_max)
                self.cont.json_updater.set_stat(self.cont.input_file, 'floatStats', 22, wpn_var)
            else:
                tk.messagebox.showerror("Error", "Both min and max are required.")

    def get_weapon_variance(self, min_dmg, max_dmg):
        """Return weapon variance given min and max damage."""
        wpn_var = (max_dmg - min_dmg) / max
        return round(float(wpn_var), 1)


class UnarmedDamagePanel:

    def __init__(self, parent, cont):
        """Use to set unarmed damage for monsters, and damage for weapons."""
        self.frame = tk.Frame(parent)
        self.cont = cont

        mob_ua_label = tk.Label(self.frame, text="Unarmed Damage", font=norm_font, fg='blue')

        dmg_type_label = tk.Label(self.frame, text="type", font=norm_font)
        options = ['no change', 'undefined', 'slash', 'pierce', 'bludge', 'cold', 'fire', 'acid', 'electric', 'nether']
        self.dmg_type_combo = ttk.Combobox(self.frame, values=options, font=norm_font, state="readonly")
        self.dmg_type_combo.current(0)

        # damage value
        dmg_val_label = ['value']
        self.unarmed_damage = vh.make_int_entry(self.frame, dmg_val_label)

        # damage variance
        var_val_label = ['variance']
        self.unarmed_variance = vh.make_float_entry(self.frame, var_val_label)

        set_button = tk.Button(self.frame, text="Set", bg="lightblue", command=self.set_dmg)
        batch_button = tk.Button(self.frame, text="Run Batch", command=partial(self.cont.set_batch, self.set_dmg))

        # layout
        r = 0
        c = 0

        mob_ua_label.grid(row=r, column=c)
        r += 1
        dmg_type_label.grid(row=r, column=c)
        self.dmg_type_combo.grid(row=r, column=c + 1)
        r += 1

        for name, entry in self.unarmed_damage.items():
            label = tk.Label(self.frame, text=name, font=norm_font)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1

        for name, entry in self.unarmed_variance.items():
            label = tk.Label(self.frame, text=name, font=norm_font)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1

        set_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        batch_button.grid(row=r, column=c + 1, padx=5, pady=5, sticky="ew")

    def set_dmg(self):

        if self.cont.input_file:

            damage_dict = {}

            d_type = self.dmg_type_combo.get()

            if d_type != "no change":
                damage_dict['dtype'] = labels_module.get_damage_type_int(d_type)

            # damage value
            ua_dam = self.unarmed_damage['value'].get()
            if ua_dam != "":
                damage_dict['value'] = int(ua_dam)

            # damage variance
            ua_var = self.unarmed_variance['variance'].get()
            if ua_var != "":
                damage_dict['variance'] = round(float(ua_var), 1)

            self.cont.json_updater.set_body_part_damage(self.cont.input_file, damage_dict)
            self.cont.view.console.preview()


class ArmorPanel:

    def __init__(self, parent, cont):
        self.frame = tk.Frame(parent)
        self.cont = cont

        dmg_type_labels = labels_module.get_armor_labels()
        self.scale_panel = SliderPanel(self.frame, "Armor", "weak (0) - strong (800)", dmg_type_labels, 0, 800, 50, 400)

        set_button = tk.Button(self.frame, text="Set", bg="lightblue", command=self.set_body_armor)
        batch_button = tk.Button(self.frame, text="Run Batch",
                                 command=partial(self.cont.set_batch, self.set_body_armor))

        # layout
        r = 0
        c = 0
        self.scale_panel.frame.grid(row=r, column=c, columnspan=2)
        r += 1
        set_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        batch_button.grid(row=r, column=c + 1, padx=5, pady=5, sticky="ew")

    def set_body_armor(self):

        mods = {}
        if self.cont.input_file:
            for k, v in self.scale_panel.scales.items():
                mods[k] = v.get()
            self.cont.json_updater.set_base_armor(self.cont.input_file, mods)
            self.cont.view.console.preview()


class AutoPanel:

    def __init__(self, parent, cont):
        """This is used to autocomplete weenie properties."""
        self.frame = tk.Frame(parent)
        self.cont = cont

        self.copy_body = tk.IntVar(value=1)
        check_body = tk.Checkbutton(self.frame, text="body table", variable=self.copy_body, font=norm_font)

        self.copy_combat = tk.IntVar(value=1)
        check_combat = tk.Checkbutton(self.frame, text="combat table", variable=self.copy_combat, font=norm_font)

        self.fill_xp = tk.IntVar(value=1)
        check_xp = tk.Checkbutton(self.frame, text="xp", variable=self.fill_xp, font=norm_font)

        self.fill_spell = tk.IntVar(value=1)
        check_spell = tk.Checkbutton(self.frame, text="spellbook", variable=self.fill_spell, font=norm_font)

        self.fill_other = tk.IntVar(value=1)
        check_other = tk.Checkbutton(self.frame, text="other", variable=self.fill_other, font=norm_font)

        set_button = tk.Button(self.frame, text="Set", bg="lightblue", command=self.autocomplete_weenie)
        batch_autofill = tk.Button(self.frame, text="Run Batch",
                                   command=partial(self.cont.run_sql_batch, self.autocomplete_weenie))

        tooltip = ("Use to autocomplete fields for a batch of weenies. "
                   "When using autocomplete, body and combat tables will be copied from a template and "
                   "must be adjusted later. "
                   "The spellbook and XP come from available data, and are not copied. "
                   )
        tooltip_label = tk.Label(self.frame, text=tooltip, font=norm_font, fg="dark green", wraplength=500,
                                 justify=tk.LEFT)

        # layout
        check_body.grid(row=0, column=0, sticky="w")
        check_combat.grid(row=0, column=1, sticky="w")
        check_xp.grid(row=1, column=0, sticky="w")
        check_spell.grid(row=1, column=1, sticky="w")
        check_other.grid(row=2, column=0, sticky="w")
        set_button.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        batch_autofill.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        tooltip_label.grid(row=4, column=0, columnspan=2)

    def autocomplete_from_data(self):
        """This method does not depend on source or template."""
        if len(self.cont.sql_commands) > 0:

            if self.fill_xp.get() == 1:  # xp, this is based on level, not copied
                level = file_helper.get_property(self.cont.sql_commands, "int", 25)

                if level is not None:
                    xp_value = file_helper.get_xp_value(level[0])
                    self.cont.sql_commands = file_helper.set_property(
                        self.cont.sql_commands, "int", 146, xp_value, "/* XpOverride */")

            if self.fill_spell.get() == 1:  # spellbook, this is from pcaps, not copied
                self.autocomplete_spell()
        else:
            tk.messagebox.showerror("Error", "There was no input file.")

    def copy_from_template(self):
        """Copy properties from one weenie into another. A source or a template weenie is required."""

        if len(self.cont.template_commands) > 0 and len(self.cont.sql_commands) > 0:

            if self.copy_body.get() == 1:  # body table from template

                # wcid for the template
                template_wcid = re.findall('[0-9]+', (self.cont.template_commands[0]))[0]

                for command in self.cont.template_commands:
                    if "`weenie_properties_body_part`" in command:
                        # when there's a match, command is the body table
                        self.cont.sql_commands = file_helper.set_body_table(self.cont.sql_commands, template_wcid,
                                                                            command)

            if self.copy_combat.get() == 1:  # combat table from template
                combat_table = file_helper.get_property(self.cont.template_commands, "did", 4)
                self.cont.sql_commands = file_helper.set_property(self.cont.sql_commands, "did", 4, combat_table[0],
                                                                  combat_table[1])

            if self.fill_other.get() == 1:

                int_stats = [3, 68]

                for int_stat in int_stats:

                    existing_value = file_helper.get_property(self.cont.sql_commands, "int", int_stat)
                    template_value = file_helper.get_property(self.cont.template_commands, "int", int_stat)

                    if existing_value is None and template_value is not None:
                        self.cont.sql_commands = file_helper.set_property(self.cont.sql_commands, "int", int_stat,
                                                                          template_value[0], template_value[1])

                float_stats = [1, 2, 3, 4, 5, 12, 31, 34, 36, 80, 104, 122, 125]

                for float_stat in float_stats:
                    existing_value = file_helper.get_property(self.cont.sql_commands, "float", float_stat)
                    template_value = file_helper.get_property(self.cont.template_commands, "float", float_stat)

                    if existing_value is None and template_value is not None:

                        new_val = float(template_value[0])
                        new_val = round(new_val, 4)
                        if new_val.is_integer():
                            new_val = int(new_val)

                        if new_val == 0.0:
                            new_val = 0

                        self.cont.sql_commands = file_helper.set_property(self.cont.sql_commands, "float", float_stat,
                                                                          new_val, template_value[1])

                did_stats = [7]

                for did_stat in did_stats:
                    existing_value = file_helper.get_property(self.cont.sql_commands, "did", did_stat)
                    template_value = file_helper.get_property(self.cont.template_commands, "did", did_stat)

                    if existing_value is None and template_value is not None:
                        self.cont.sql_commands = file_helper.set_property(self.cont.sql_commands, "did", did_stat,
                                                                          template_value[0], template_value[1])

        else:
            tk.messagebox.showerror("Error", "There was no input file or no template to copy from.")

    def autocomplete_weenie(self):
        """Autocomplete as many properties in a weenie as possible."""

        if len(self.cont.sql_commands) > 0:

            item_type = file_helper.get_property(self.cont.sql_commands, "int", 1)
            if int(item_type[0]) == 16:  # weenie is creature

                creature_species = file_helper.get_property(self.cont.sql_commands, "int", 2)
                species_name = labels_module.get_creature_type_label(creature_species[0])

                if species_name is not None:
                    species_name = species_name.lower()
                    print(species_name)

                    templates = file_helper.get_templates()
                    matching_template = None

                    for template in templates:  # try to find a matching template

                        if species_name in template.lower():
                            matching_template = template
                        else:
                            wcid = re.findall('[0-9]+', (self.cont.sql_commands[0]))[0]
                            name = file_helper.get_property(self.cont.sql_commands, "str", 1)
                            self.cont.view.console.print("Warning! No template found for " + str(wcid) + " " + name)

                    if matching_template is not None:
                        with open("templates/" + matching_template) as file_object:
                            sql_file = file_object.read()
                            self.cont.template_commands = sql_file.split(";")
                            self.copy_from_template()
                else:
                    wcid = re.findall('[0-9]+', (self.cont.sql_commands[0]))[0]
                    name = file_helper.get_property(self.cont.sql_commands, "str", 1)
                    self.cont.view.console.print("Warning! No species set for " + str(wcid) + " " + name)

            # still autocomplete from data, regardless of template or source
            self.autocomplete_from_data()

        else:
            tk.messagebox.showerror("Error", "There was no input file.")

    def autocomplete_spell(self):

        if len(self.cont.sql_commands) > 0:

            spell_pr = 2.05

            # get name of weenie, used to search for its spells
            name = file_helper.get_property(self.cont.sql_commands, "string", 1)
            spell_dict = file_helper.get_spell_list(name[0])

            for spell_id in spell_dict.keys():
                spell_name = "/* " + spell_dict[spell_id] + " */"
                file_helper.set_spell_list(self.cont.sql_commands, spell_id, spell_pr, spell_name)


class DeletePanel:

    def __init__(self, parent, cont):
        self.frame = tk.Frame(parent)
        self.cont = cont

        header_label = tk.Label(self.frame, text="Delete", font=norm_font, fg='blue')
        str_labels = ["tag"]
        self.str_entries = vh.make_str_entry(self.frame, str_labels)

        delete_button = tk.Button(self.frame, text="Delete", command=self.delete_command)

        tooltip = ("Use to delete a command in a batch of SQL files. "
                   "To target a command, enter a tag, such as weenie_properties_create_list."
                   )
        tooltip_label = tk.Label(self.frame, text=tooltip, font=norm_font, fg="dark green", wraplength=420,
                                 justify=tk.LEFT)

        # layout
        r = 0
        c = 0

        header_label.grid(row=r, column=c)
        r += 1

        for name, entry in self.str_entries.items():
            label = tk.Label(self.frame, text=name, font=norm_font)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1

        delete_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")

        r += 1
        tooltip_label.grid(row=r, column=c, columnspan=2)

    def delete_command(self):

        tag = self.str_entries["tag"].get().strip()

        if tag != "":
            for file_name, sql_file in self.cont.sql_dict.items():
                commands = sql_file.split(";")
                file_helper.write_clean_sql(file_name, commands, tag)


class RenumberPanel:

    def __init__(self, parent, cont):
        self.frame = tk.Frame(parent)
        self.cont = cont

        header_label = tk.Label(self.frame, text="Renumber", font=norm_font, fg='blue')
        int_labels = ['change by', 'if greater than']
        self.int_entries = vh.make_int_entry(self.frame, int_labels)

        self.subtract_check = tk.IntVar(value=1)
        subtract_box = tk.Checkbutton(self.frame, text="subtract", variable=self.subtract_check, font=norm_font)

        renumber_button = tk.Button(self.frame, text="Renumber", command=self.renumber)

        tooltip = "Use to renumber WCIDs in a batch of SQL files by a constant value."
        tooltip_label = tk.Label(self.frame, text=tooltip, font=norm_font, fg="dark green", wraplength=420,
                                 justify=tk.LEFT)

        # layout
        r = 0
        c = 0

        header_label.grid(row=r, column=c)
        r += 1

        for name, entry in self.int_entries.items():
            label = tk.Label(self.frame, text=name, font=norm_font)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1

        subtract_box.grid(row=r, column=c)
        r += 1
        renumber_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        r += 1
        tooltip_label.grid(row=r, column=c, columnspan=2)

    def renumber(self):

        delta = int(self.int_entries['change by'].get())

        if self.subtract_check.get() == 1:
            delta = delta * -1

        threshold = int(self.int_entries['if greater than'].get())

        # get wcid list
        wcid_list = []
        file_dict = {}
        tag = "DELETE FROM `weenie` WHERE `class_Id`"

        for file_name, sql_file in self.cont.sql_dict.items():
            commands = sql_file.split(";")

            for command in commands:
                if tag in command:
                    my_split = command.split("=")
                    wcid = int(my_split[1].strip())
                    if wcid > threshold:
                        wcid_list.append(wcid)
                        file_dict[file_name] = sql_file
                        break
        # renumber
        for file_name, sql_file in file_dict.items():
            commands = sql_file.split(";")
            renumbered = []

            for command in commands:

                for wcid in wcid_list:
                    new_wcid = wcid + delta

                    if str(wcid) in command:
                        new_command = command.replace(str(wcid), str(new_wcid))
                        renumbered.append(new_command + ";")
                    if str(wcid) in file_name:
                        file_name = file_name.replace(str(wcid), str(new_wcid))

            file_helper.write_sql_file(file_name, renumbered)


class KillTaskPanel:

    def __init__(self, parent):
        self.frame = tk.Frame(parent)

        header_label = tk.Label(self.frame, text="Kill Task", font=norm_font, fg='blue')

        str_labels = ['kill wait', 'kill stamp']
        self.str_entries = vh.make_str_entry(self.frame, str_labels)

        kill_count_label = ['kill count']
        self.kill_task_entries = vh.make_int_entry(self.frame, kill_count_label)

        make_task_button = tk.Button(self.frame, text="Make Task", command=self.make_kill_task)

        # layout

        r = 0
        c = 0

        header_label.grid(row=r, column=c)
        r += 1

        for name, entry in self.str_entries.items():
            label = tk.Label(self.frame, text=name, font=norm_font)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1

        for name, entry in self.kill_task_entries.items():
            label = tk.Label(self.frame, text=name, font=norm_font)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1

        make_task_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")

    def make_kill_task(self):
        kill_wait = self.str_entries['kill wait'].get().strip()
        kill_stamp = self.str_entries['kill stamp'].get().strip()
        kill_count = int(self.kill_task_entries['kill count'].get())

        if kill_wait and kill_stamp and kill_count:
            quest_helper.make_quest_sql(kill_wait)
            quest_helper.make_kill_count(kill_stamp, kill_count)
        else:
            tk.messagebox.showerror("Error", "Set kill wait, stamp and count.")


class EventPanel:

    def __init__(self, parent):
        self.frame = tk.Frame(parent)

        header_label = tk.Label(self.frame, text="Event", font=norm_font, fg='blue')

        str_labels = ['event name']
        self.str_entries = vh.make_str_entry(self.frame, str_labels)

        make_event_button = tk.Button(self.frame, text="Make Event", command=self.make_event)

        # layout

        r = 0
        c = 0

        header_label.grid(row=r, column=c)
        r += 1

        for name, entry in self.str_entries.items():
            label = tk.Label(self.frame, text=name, font=norm_font)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1

        make_event_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")

    def make_event(self):
        event_name = self.str_entries['event name'].get().strip()

        if event_name:
            quest_helper.make_event_sql(event_name)
        else:
            tk.messagebox.showerror("Error", "Enter an event name.")


class BasePanel:

    def __init__(self, parent, cont):
        self.frame = tk.Frame(parent)
        self.cont = cont

        str_labels = ['name', 'kill flag']
        self.str_entries = vh.make_str_entry(self.frame, str_labels)

        item_type_label = tk.Label(self.frame, text="item type", font=norm_font)
        item_options = sorted(labels_module.get_all_item_types())
        item_options.insert(0, "no change")
        self.item_type_combo = ttk.Combobox(self.frame, values=item_options, font=norm_font, state="readonly")
        self.item_type_combo.current(0)

        creature_type_label = tk.Label(self.frame, text="creature type", font=norm_font)
        creature_options = sorted(labels_module.get_all_creature_types())
        creature_options.insert(0, "no change")
        self.creature_type_combo = ttk.Combobox(self.frame, values=creature_options, font=norm_font, state="readonly")
        self.creature_type_combo.current(0)

        int_header_label = tk.Label(self.frame, text="Int", font=norm_font, fg='blue')

        int_labels = ['gen init', 'gen max']
        self.int_entries = vh.make_int_entry(self.frame, int_labels)

        did_header_label = tk.Label(self.frame, text="Data ID", font=norm_font, fg='blue')

        did_labels = ['combat table', 'death treasure']
        self.did_entries = vh.make_int_entry(self.frame, did_labels)

        float_header_label = tk.Label(self.frame, text="Float", font="Arial 12", fg='blue')

        float_labels = ['regen interval', 'gen radius']
        self.float_entries = vh.make_float_entry(self.frame, float_labels)

        self.npc_check = tk.IntVar(value=0)
        is_npc_box = tk.Checkbutton(self.frame, text="is npc", variable=self.npc_check, font=norm_font)

        self.npc_like_object = tk.IntVar(value=0)
        npc_like_object_box = tk.Checkbutton(self.frame, text="npc like object", variable=self.npc_like_object,
                                             font=norm_font)

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

        is_npc_box.grid(row=r, column=c)
        npc_like_object_box.grid(row=r, column=c + 1)
        r += 1

        int_header_label.grid(row=r, column=c)
        r += 1

        item_type_label.grid(row=r, column=c)
        self.item_type_combo.grid(row=r, column=c + 1)
        r += 1

        creature_type_label.grid(row=r, column=c)
        self.creature_type_combo.grid(row=r, column=c + 1)
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

            # item type
            selected = self.item_type_combo.get()

            if selected == "no change":
                pass
            else:
                val = labels_module.get_item_type_int(selected)
                desc = "/* ItemType - " + selected + " */"
                self.cont.sql_commands = file_helper.set_property(self.cont.sql_commands, "int", 1, int(val), desc)

            # creature type
            selected = self.creature_type_combo.get()

            if selected == "no change" or not self.cont.json_updater.is_creature(self.cont.input_file):
                pass
            else:
                val = labels_module.get_creature_type_int(selected)
                desc = "/* CreatureType - " + selected + " */"
                self.cont.sql_commands = file_helper.set_property(self.cont.sql_commands, "int", 2, int(val), desc)

            # str
            my_dict = {'name': (1, "/* Name */"),
                       'kill flag': (45, "/* KillQuest */")
                       }
            self.cont.set_properties(my_dict, self.str_entries, 'str')

            # int
            my_dict = {'gen init': (82, "/* InitGeneratedObjects */"),
                       'gen max': (81, "/* MaxGeneratedObjects */")
                       }
            self.cont.set_properties(my_dict, self.int_entries, 'int')

            # did
            my_dict = {'combat table': (4, "/* CombatTable */"),
                       'death treasure': (45, "/* DeathTreasureType */")
                       }
            self.cont.set_properties(my_dict, self.did_entries, 'did')

            # float
            my_dict = {'regen interval': (41, "/* RegenerationInterval */"),
                       'gen radius': (43, "/* GeneratorRadius */")
                       }
            self.cont.set_properties(my_dict, self.float_entries, 'float')

            # set to npc
            if self.npc_check.get() == 1:
                desc = "/* PlayerKillerStatus - RubberGlue */"
                self.cont.sql_commands = file_helper.set_property(self.cont.sql_commands, "int", 134, 16, desc)
                self.cont.sql_commands = file_helper.set_property(self.cont.sql_commands, "bool", 19, 0,
                                                                  "/* Attackable */")

            # set npc should appear as an object
            if self.npc_like_object.get() == 1:
                self.cont.sql_commands = file_helper.set_property(self.cont.sql_commands, "bool", 52, 1,
                                                                  "/* AiImmobile */")
                self.cont.sql_commands = file_helper.set_property(self.cont.sql_commands, "bool", 82, 1,
                                                                  "/* DontTurnOrMoveWhenGiving */")
                self.cont.sql_commands = file_helper.set_property(self.cont.sql_commands, "bool", 83, 1,
                                                                  "/* NpcLooksLikeObject */")


class ConsolePanel:

    def __init__(self, parent, cont):
        self.frame = tk.Frame(parent)
        self.cont = cont

        self.text = scrolledtext.ScrolledText(self.frame, height=30, width=40, undo=True, font=norm_font)
        self.text.configure(state='disabled', wrap=tk.WORD)
        self.text.tag_config('field', foreground="dark green")
        self.text.tag_config('warning', foreground="red")

        clear_button = tk.Button(self.frame, text="Clear", command=self.clear)

        # layout
        self.text.grid(row=0, column=0)
        clear_button.grid(row=1, column=0)

    def clear(self):
        self.text.configure(state='normal')
        self.text.delete('1.0', tk.END)
        self.text.configure(state='disabled')

    def print(self, line):
        self.text.configure(state='normal')
        self.text.insert(tk.END, line)
        self.text.configure(state='disabled')


class ModsPanel:

    def __init__(self, parent, cont):
        """Panel for armor and resistance mods."""
        self.frame = tk.Frame(parent)
        self.cont = cont

        damage_type_labels = labels_module.get_damage_labels()
        self.mod_scales = SliderPanel(self.frame, "Mod", "weak (0) - strong (2)", damage_type_labels, 0, 2, 0.1, 1)

        self.armor = tk.IntVar(value=1)
        armor_check_box = tk.Checkbutton(self.frame, text="armor", variable=self.armor, font=norm_font)

        self.resist = tk.IntVar(value=1)
        resist_check_box = tk.Checkbutton(self.frame, text="resist", variable=self.resist, font=norm_font)

        set_button = tk.Button(self.frame, text="Set", bg="lightblue", command=self.set_mods)
        batch_button = tk.Button(self.frame, text="Run Batch", command=partial(self.cont.run_sql_batch, self.set_mods))

        # layout
        self.mod_scales.frame.grid(row=0, column=0, columnspan=2)
        armor_check_box.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        resist_check_box.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        set_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        batch_button.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

    def set_mods(self):
        """Set mods for a single .sql file."""

        armor_dict = {
            13: "/* ArmorModVsSlash */",
            14: "/* ArmorModVsPierce */",
            15: "/* ArmorModVsBludgeon */",
            16: "/* ArmorModVsCold */",
            17: "/* ArmorModVsFire */",
            18: "/* ArmorModVsAcid */",
            19: "/* ArmorModVsElectric */"
        }

        resist_dict = {
            64: "/* ResistSlash */",
            65: "/* ResistPierce */",
            66: "/* ResistBludgeon */",
            67: "/* ResistFire */",
            68: "/* ResistCold */",
            69: "/* ResistAcid */",
            70: "/* ResistElectric */"
        }

        if len(self.cont.sql_commands) > 0:

            if self.armor.get() == 1:

                for k, v in self.mod_scales.scales.items():
                    mod_val = round(v.get(), 1)
                    self.cont.sql_commands = file_helper.set_property(self.cont.sql_commands, "float", k, mod_val,
                                                                      armor_dict[k])

            if self.resist.get() == 1:

                for k, v in self.mod_scales.scales.items():
                    mod_val = v.get()

                    if mod_val < 1:
                        mod_val = 2 - mod_val
                    elif mod_val > 1:
                        mod_val = abs(mod_val - 2)
                    else:
                        pass

                    mod_val = round(mod_val, 1)
                    self.cont.sql_commands = file_helper.set_property(self.cont.sql_commands, "float", k, mod_val,
                                                                      resist_dict[k])


class AttributesPanel:

    def __init__(self, parent, cont):
        self.frame = tk.Frame(parent)
        self.cont = cont

        self.int_entries_1 = vh.make_int_entry(self.frame, labels_module.get_primary_attribute_labels())
        self.int_entries_2 = vh.make_int_entry(self.frame, labels_module.get_secondary_attribute_labels())

        set_button = tk.Button(self.frame, text="Set", bg="lightblue", command=self.set_attributes)
        batch_button = tk.Button(self.frame, text="Run Batch",
                                 command=partial(self.cont.run_sql_batch, self.set_attributes))

        tooltip = "All fields optional. Vitals are adjusted based on attributes so what you see is what you get."
        tooltip_label = tk.Label(self.frame, text=tooltip, font=norm_font, fg="dark green", wraplength=420,
                                 justify=tk.LEFT)

        # layout
        r = 0
        c = 0

        for name, entry in self.int_entries_1.items():
            label = tk.Label(self.frame, text=name, font=norm_font)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1

        for name, entry in self.int_entries_2.items():
            label = tk.Label(self.frame, text=name, font=norm_font)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1

        set_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        r += 1
        batch_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        r += 1
        tooltip_label.grid(row=r, column=c, columnspan=2)

    def set_attributes(self):

        if len(self.cont.sql_commands) > 0:
            my_dict = {'strength': (1, "/* Strength */"),
                       'endurance': (2, "/* Endurance */"),
                       'quickness': (3, "/* Quickness */"),
                       'coordination': (4, "/* Coordination */"),
                       'focus': (5, "/* Focus */"),
                       'self': (6, "/* Self */")
                       }
            self.cont.set_attributes(my_dict, self.int_entries_1, True, False)

            my_dict = {'health': (1, "/* MaxHealth */"),
                       'stamina': (3, "/* MaxStamina */"),
                       'mana': (5, "/* MaxMana */")
                       }

            self.cont.set_attributes(my_dict, self.int_entries_2, False, True)


class ArtPanel:

    def __init__(self, parent, cont):
        self.frame = tk.Frame(parent)
        self.cont = cont

        int_header_label = tk.Label(self.frame, text="Int or Data ID", font=norm_font, fg="blue")

        int_labels = ['palette template', 'palette base', 'clothing base', 'physics effect']
        self.int_entries = vh.make_int_entry(self.frame, int_labels)

        tooltip = "All fields are optional."
        tooltip_label = tk.Label(self.frame, text=tooltip, font=norm_font, fg="dark green", wraplength=420,
                                 justify=tk.LEFT)

        float_header_label = tk.Label(self.frame, text="Float", font=norm_font, fg="blue")

        float_labels = ['shade']
        self.float_entries = vh.make_float_entry(self.frame, float_labels)

        set_button = tk.Button(self.frame, text="Set", bg="lightblue", command=self.set_art)
        batch_button = tk.Button(self.frame, text="Run Batch", command=partial(self.cont.run_sql_batch, self.set_art))

        # layout
        r = 0
        c = 0

        int_header_label.grid(row=r, column=c)
        r += 1

        for name, entry in self.int_entries.items():
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
        r += 1
        tooltip_label.grid(row=r, column=c, columnspan=2)

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
            my_dict = {'shade': (12, "/* Shade */")}
            self.cont.set_properties(my_dict, self.float_entries, 'float')


class WieldPanel:

    def __init__(self, parent, cont):
        self.frame = tk.Frame(parent)
        self.cont = cont

        wield_header_label = tk.Label(self.frame, text="Wield (all fields required)", font=norm_font, fg='blue')

        int_labels = ['wcid', 'palette']
        self.wield_entries = vh.make_int_entry(self.frame, int_labels)
        self.wield_entries['palette'].insert(tk.END, "0")

        float_labels = ['shade']
        self.wield_shade = vh.make_float_entry(self.frame, float_labels)
        self.wield_shade['shade'].insert(tk.END, "0")

        self.is_wield_treasure = tk.IntVar(value=0)
        check_box = tk.Checkbutton(self.frame, text="is wield treasure", variable=self.is_wield_treasure,
                                   font=norm_font)

        set_button = tk.Button(self.frame, text="Set", bg="lightblue", command=self.set_wield)
        batch_button = tk.Button(self.frame, text="Run Batch", command=partial(self.cont.set_batch, self.set_wield))

        find_label = tk.Label(self.frame, text="Find from PCAPs", font=norm_font, fg='blue')

        self.search_entry = tk.Entry(self.frame, bg="white", font="Arial 12")

        text_area = scrolledtext.ScrolledText(self.frame, height=15, width=50, undo=True)
        text_area.configure(state='disabled', wrap=tk.WORD)

        find_button = tk.Button(self.frame, text="Find by Name",
                                command=partial(file_helper.find_wielded_items, 'pcap_wielded_items.txt',
                                                self.search_entry, text_area))

        # layout
        r = 0
        c = 0

        wield_header_label.grid(row=r, column=c)
        r += 1

        for name, entry in self.wield_entries.items():
            label = tk.Label(self.frame, text=name, font=norm_font)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1

        for name, entry in self.wield_shade.items():
            label = tk.Label(self.frame, text=name, font=norm_font)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1

        check_box.grid(row=r, column=c)
        r += 1
        find_label.grid(row=r, column=c)
        r += 1
        self.search_entry.grid(row=r, column=c, sticky="ew")
        find_button.grid(row=r, column=c + 1, padx=5, pady=5, sticky="w")
        r += 1
        text_area.grid(row=r, column=c, columnspan=2)
        r += 1
        set_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        batch_button.grid(row=r, column=c + 1, padx=5, pady=5, sticky="ew")

    def set_wield(self):

        if self.cont.input_file:

            wcid = self.wield_entries['wcid'].get()
            palette = self.wield_entries['palette'].get()
            shade_str = self.wield_shade['shade'].get()
            destination = 2

            if wcid == "" or palette == "" or shade_str == "":
                tk.messagebox.showerror("Error", "All wield fields are required.")
            else:
                wcid = int(wcid)
                palette = int(palette)
                shade = float(shade_str)
                self.cont.json_updater.add_create_list(self.cont.input_file)

                if self.is_wield_treasure.get() == 1:
                    destination = 10

                self.cont.json_updater.set_create_list(self.cont.input_file, wcid, destination, palette, shade, 0)
                self.cont.view.console.preview()


class SkillsPanel:

    def __init__(self, parent, cont):
        self.frame = tk.Frame(parent)
        self.cont = cont

        skill_labels = labels_module.get_skill_labels()
        self.skill_entries = vh.make_int_entry(self.frame, skill_labels)

        self.sneak_attack = tk.IntVar(value=0)
        add_sneak_attack = tk.Checkbutton(self.frame, text="sneak attack", variable=self.sneak_attack, font=norm_font)

        self.dirty_fighting = tk.IntVar(value=0)
        add_dirty_fighting = tk.Checkbutton(self.frame, text="dirty fighting", variable=self.dirty_fighting,
                                            font=norm_font)

        self.fill_from_pcap = tk.IntVar(value=1)
        pcap_check = tk.Checkbutton(self.frame, text="fill from pcap", variable=self.fill_from_pcap, font=norm_font)

        set_button = tk.Button(self.frame, text="Set", bg="lightblue", command=self.set_skills)
        batch_button = tk.Button(self.frame, text="Run Batch",
                                 command=partial(self.cont.run_sql_batch, self.set_skills))

        tooltip = ("All fields optional. "
                   "Set attributes first and enter desired skill levels, which are adjusted down based on attributes. "
                   "Melee offense includes heavy, light and two-handed weapons. "
                   "Magic offense includes life, creature, war, void, and mana conversion. "
                   "Sneak attack and dirty fighting are set to the same level as melee offense. "
                   "For fill from PCAPs to work, enter any value for each desired skill. "
                   )

        tooltip_label = tk.Label(self.frame, text=tooltip, font=norm_font, fg="dark green", wraplength=420,
                                 justify=tk.LEFT)

        # layout
        r = 0
        c = 0

        for name, entry in self.skill_entries.items():
            label = tk.Label(self.frame, text=name, font=norm_font)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1

        add_sneak_attack.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        add_dirty_fighting.grid(row=r, column=c + 1, padx=5, pady=5, sticky="ew")
        r += 1
        pcap_check.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        r += 1
        set_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        r += 1
        batch_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        r += 1
        tooltip_label.grid(row=r, column=c, columnspan=2)

    def set_skills(self):

        if len(self.cont.sql_commands) > 0:

            my_dict = {}
            keys = [1, 2, 3, 4, 5, 6]
            wcid = re.findall('[0-9]+', (self.cont.sql_commands[0]))[0]

            for command in self.cont.sql_commands:
                if str("`weenie_properties_attribute`") in command:
                    if str("`weenie_properties_attribute_2nd`") not in command:

                        # 1 = str, 2 = endu, 3 = quick, 4 = coord, 5 = foc, 6 = self
                        for key in keys:
                            my_dict[key] = int(file_helper.get_attribute(wcid, command, key))
                else:
                    for key in keys:
                        my_dict[key] = 100

            attributes = {'strength': my_dict[1], 'endurance': my_dict[2], 'coordination': my_dict[3],
                          'quickness': my_dict[4], 'focus': my_dict[5], 'self': my_dict[6]}

            skills = {}
            pcap_dict = {}

            if self.fill_from_pcap.get() == 1:
                name = file_helper.get_property(self.cont.sql_commands, "str", 1)[0]
                name = name.replace("'", "")
                pcap_dict = file_helper.skill_look_up(name)

            for k, v in self.skill_entries.items():

                val = v.get()

                if val != "":
                    val_int = int(val)

                    if k == 'melee offense':

                        if 'melee offense' in pcap_dict.keys():
                            if pcap_dict['melee offense'] > 0:
                                val_int = int(pcap_dict['melee offense'])

                        base_skill = round((attributes['strength'] + attributes['coordination']) / 3)
                        val_int = val_int - base_skill
                        skills['HeavyWeapons'] = val_int
                        skills['LightWeapons'] = val_int
                        skills['TwoHanded'] = val_int

                        # sneak attack and dirty fighting set to same level as melee offense
                        if self.sneak_attack.get() == 1:
                            skills['SneakAttack'] = val_int

                        if self.dirty_fighting.get() == 1:
                            skills['DirtyFighting'] = val_int

                    elif k == 'finesse weapons':

                        if 'finesse weapons' in pcap_dict.keys():
                            if pcap_dict['finesse weapons'] > 0:
                                val_int = int(pcap_dict['finesse weapons'])

                        base_skill = round((attributes['coordination'] + attributes['quickness']) / 3)
                        val_int = val_int - base_skill
                        skills['FinesseWeapons'] = val_int

                    elif k == 'magic offense':

                        if 'magic offense' in pcap_dict.keys():
                            if pcap_dict['magic offense'] > 0:
                                val_int = int(pcap_dict['magic offense'])

                        base_skill = round((attributes['focus'] + attributes['self']) / 4)
                        val_int = val_int - base_skill
                        skills['LifeMagic'] = val_int
                        skills['WarMagic'] = val_int
                        skills['CreatureMagic'] = val_int
                        skills['VoidMagic'] = val_int
                        skills['ManaConversion'] = val_int

                    elif k == 'melee defense':

                        if 'melee defense' in pcap_dict.keys():
                            if pcap_dict['melee defense'] > 0:
                                val_int = int(pcap_dict['melee defense'])

                        base_skill = round((attributes['coordination'] + attributes['quickness']) / 3)
                        val_int = val_int - base_skill
                        skills['MeleeDefense'] = val_int

                    elif k == 'missile defense':

                        if 'missile defense' in pcap_dict.keys():
                            if pcap_dict['missile defense'] > 0:
                                val_int = int(pcap_dict['missile defense'])

                        base_skill = round((attributes['coordination'] + attributes['quickness']) / 5)
                        val_int = val_int - base_skill
                        skills['MissileDefense'] = val_int

                    elif k == 'magic defense':

                        if 'magic defense' in pcap_dict.keys():
                            if pcap_dict['magic defense'] > 0:
                                val_int = int(pcap_dict['magic defense'])

                        base_skill = round((attributes['focus'] + attributes['self']) / 7)
                        val_int = val_int - base_skill
                        skills['MagicDefense'] = val_int

                    elif k == 'missile weapons':

                        if 'missile offense' in pcap_dict.keys():
                            if pcap_dict['missile offense'] > 0:
                                val_int = int(pcap_dict['missile offense'])

                        base_skill = round(attributes['coordination'] / 2)
                        val_int = val_int - base_skill
                        skills['MissileDefense'] = val_int

                    else:
                        tk.messagebox.showerror("Error", "A skill was undefined.")

            # if negative, set to 0
            for k, v in skills.items():
                if v < 0:
                    skills[k] = 0

            # make the skill table
            new_command = file_helper.get_skill_table(wcid, skills)

            my_list = []

            # delete if already there
            for command in self.cont.sql_commands:
                if str("`weenie_properties_skill`") in command:
                    pass
                else:
                    if command.strip() != "":
                        my_list.append(command)

            my_list.append(new_command)
            self.cont.sql_commands = my_list


class LootPanel:

    def __init__(self, parent, cont):
        self.frame = tk.Frame(parent)
        self.cont = cont

        header_label = tk.Label(self.frame, text="Random Loot", font=norm_font, fg='blue')

        int_labels = ['death treasure']
        self.death_treasure = vh.make_int_entry(self.frame, int_labels)
        self.search_entry = tk.Entry(self.frame, bg="white", font=norm_font)

        text_area = scrolledtext.ScrolledText(self.frame, height=5, width=50, undo=True)
        text_area.configure(state='disabled', wrap=tk.WORD)

        find_button = tk.Button(self.frame, text="Find by Tier",
                                command=partial(file_helper.find_death_treasure, 'death_treasure.txt',
                                                self.search_entry, text_area))

        tooltip = ("This is an integer for the loot tier profile of a monster. "
                   "Must look up, for example from another monster in the same loot tier or the list above. "
                   "To search for available options, enter a loot tier (e.g., 1, 2, etc.)"
                   )
        tooltip_label = tk.Label(self.frame, text=tooltip, font=norm_font, fg="dark green", wraplength=500,
                                 justify=tk.LEFT)

        set_button = tk.Button(self.frame, text="Set", bg="lightblue", command=self.set_death_treasure)
        batch_button = tk.Button(self.frame, text="Run Batch",
                                 command=partial(self.cont.set_batch, self.set_death_treasure))

        # layout
        r = 0
        c = 0

        header_label.grid(row=r, column=c)
        r += 1

        for name, entry in self.death_treasure.items():
            label = tk.Label(self.frame, text=name, font=norm_font)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1

        self.search_entry.grid(row=r, column=c, sticky="ew")
        find_button.grid(row=r, column=c + 1, padx=5, pady=5, sticky="w")
        r += 1
        text_area.grid(row=r, column=c, columnspan=2)
        r += 1

        set_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        batch_button.grid(row=r, column=c + 1, padx=5, pady=5, sticky="ew")

        r += 1
        tooltip_label.grid(row=r, column=c, columnspan=2)

    def set_death_treasure(self):
        """Set death treasure for a single .json file."""
        if self.cont.input_file:

            val = self.death_treasure['death treasure'].get().strip()
            if val != "":
                val = int(val)
                self.cont.json_updater.set_stat(self.cont.input_file, 'didStats', 35, val)


class TrophiesPanel:

    def __init__(self, parent, cont):
        self.frame = tk.Frame(parent)
        self.cont = cont

        # all fields required
        header_label = tk.Label(self.frame, text="Trophies", font=norm_font, fg='blue')

        int_labels = ['wcid', 'total on corpse']
        self.trophy_entries = vh.make_int_entry(self.frame, int_labels)
        self.trophy_entries['total on corpse'].insert(tk.END, "1")

        float_labels = ['drop chance']
        self.drop_chance = vh.make_float_entry(self.frame, float_labels)

        tooltip = ("To have multiple copies of a trophy drop on death, set total on corpse. "
                   "The drop chance is also known as shade and must be a float. "
                   "If greater than 0 and less than 1 it's a chance to drop. "
                   "Set to 1 to have the trophy always drop."
                   )
        tooltip_label = tk.Label(self.frame, text=tooltip, font=norm_font, fg="dark green", wraplength=500,
                                 justify=tk.LEFT)

        set_button = tk.Button(self.frame, text="Set", bg="lightblue", command=self.set_trophy)
        batch_button = tk.Button(self.frame, text="Run Batch", command=partial(self.cont.set_batch, self.set_trophy))

        # layout
        r = 0
        c = 0
        header_label.grid(row=r, column=c)
        r += 1

        for name, entry in self.trophy_entries.items():
            label = tk.Label(self.frame, text=name, font=norm_font)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1

        for name, entry in self.drop_chance.items():
            label = tk.Label(self.frame, text=name, font=norm_font)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1

        set_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        batch_button.grid(row=r, column=c + 1, padx=5, pady=5, sticky="ew")

        r += 1
        tooltip_label.grid(row=r, column=c, columnspan=2)

    def set_trophy(self):

        if self.cont.input_file:

            wcid = self.trophy_entries['wcid'].get()
            total = self.trophy_entries['total on corpse'].get()
            drop = self.drop_chance['drop chance'].get()

            if wcid == "" or total == "" or drop == "":
                tk.messagebox.showerror("Error", "All trophy fields are required.")
            else:

                wcid = int(wcid)
                total_on_corpse = int(total)
                shade = float(drop)

                self.cont.json_updater.add_create_list(self.cont.input_file)

                for _ in range(total_on_corpse):

                    if 1 > shade > 0:  # contain treasure
                        self.cont.json_updater.set_create_list(self.cont.input_file, wcid, 9, 0, shade, 1)
                        self.cont.json_updater.add_empty_slot(self.cont.input_file, (1 - shade))
                    else:  # contain, always
                        self.cont.json_updater.append_item(self.cont.input_file, wcid, 1, 0, shade, 1)


class SliderPanel:

    def __init__(self, parent, col_1, col_2, label_list, s_from, s_to, s_res, s_def):
        self.frame = tk.Frame(parent)
        self.scales = {}

        row_i = 0

        left_label = tk.Label(self.frame, text=col_1, font=norm_font)
        right_label = tk.Label(self.frame, text=col_2, font=norm_font)

        left_label.grid(row=row_i, column=0)
        right_label.grid(row=row_i, column=1)

        row_i += 1

        for name in label_list:
            label = tk.Label(self.frame, text=name, font=norm_font)
            label.grid(row=row_i, column=0, padx=5, pady=5)

            scale = tk.Scale(self.frame, from_=s_from, to=s_to, resolution=s_res, orient=tk.HORIZONTAL)
            scale.set(s_def)
            scale.grid(row=row_i, column=1, padx=5, pady=5, sticky='ew')

            self.scales[name] = scale
            row_i += 1


norm_font = ("Arial", 12)


def main():
    # if on Windows, fix blurry font
    if os.name == 'nt':
        windll.shcore.SetProcessDpiAwareness(1)

    root = tk.Tk()
    root.title("AC Monsters")
    Controller(root)
    root.mainloop()


if __name__ == '__main__':
    main()
