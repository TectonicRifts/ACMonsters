import math
import re
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import tkinter.scrolledtext as scrolledtext
import os
from functools import partial
import file_helper
import skills_module
import quest_helper
import view_helper as vh
import labels_module
import tkinter.messagebox
from ctypes import windll
from pathlib import Path
import platform
import subprocess


class Toolbar:

    def __init__(self, parent, cont):
        self.frame = tk.Frame(parent)

        open_sql_button = tk.Button(self.frame, text="Open File", command=cont.open_file)
        name_filter_label = tk.Label(self.frame, text="Name contains", font=norm_font)
        name_filter_entry = tk.Entry(self.frame, bg="white", font=norm_font)
        self.creature_only = tk.IntVar(value=0)
        creature_only_check = tk.Checkbutton(
            self.frame, text="Only creatures", variable=self.creature_only, font=norm_font)

        open_sql_folder_button = tk.Button(self.frame, text="Open Folder",
                                           command=partial(cont.open_folder, name_filter_entry, self.creature_only))

        save_sql_button = tk.Button(self.frame, text="Save", bg="lightblue", command=cont.save_sql)

        open_output_button = tk.Button(self.frame, text="Output", command=cont.open_output_folder)

        # layout
        name_filter_label.grid(row=0, column=0, sticky="ew")
        name_filter_entry.grid(row=0, column=1, sticky="ew")
        creature_only_check.grid(row=0, column=2, sticky="ew")
        open_sql_folder_button.grid(row=0, column=3, sticky="ew")
        open_sql_button.grid(row=0, column=4, ipadx=10, ipady=0, sticky="ew")
        save_sql_button.grid(row=0, column=5, ipadx=25, ipady=0, sticky="ew")
        open_output_button.grid(row=0, column=6, ipadx=25, ipady=0, sticky="ew")


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
        calc_panel = CalcPanel(right_nb, cont)
        art_panel = ArtPanel(right_nb, cont)
        copy_panel = AutoPanel(right_nb, cont)
        port_panel = PortalPanel(right_nb, cont)
        kill_task_panel = TaskPanel(right_nb)
        trophies_panel = LootPanel(right_nb, cont)
        util_panel = UtilityPanel(right_nb, cont)

        # left
        left_nb.add(self.console.frame, text="Console")

        # right
        base_panel = BasePanel(right_nb, cont)

        right_nb.add(base_panel.frame, text="Base")
        right_nb.add(attributes_panel.frame, text="Attr")
        right_nb.add(skills_panel.frame, text="Skill")
        right_nb.add(calc_panel.frame, text="Calc")
        right_nb.add(item_panel.frame, text="Item")
        right_nb.add(port_panel.frame, text="Port")
        right_nb.add(mods_panel.frame, text="Mods")
        right_nb.add(art_panel.frame, text="Art")
        right_nb.add(kill_task_panel.frame, text="Task")
        right_nb.add(trophies_panel.frame, text="Loot")
        right_nb.add(util_panel.frame, text="Util")
        right_nb.add(copy_panel.frame, text="Auto")

        left_nb.grid(row=0, column=0)
        right_nb.grid(row=0, column=1, sticky="ns")

        toolbar = Toolbar(self.frame, cont)
        toolbar.frame.grid(row=1, column=0, columnspan=2)

        self.frame.grid()


class Controller:

    def __init__(self, parent):

        # sql file (i.e., sql commands) currently being worked on
        self.sql_commands = None

        # name of the output file
        self.sql_output = None

        # keys are sql file names, the values are file contents (i.e., sql commands)
        self.sql_dict = {}

        # sql file (i.e., the commands from it) being used as a template to copy from
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

        if self.sql_commands:
            with open("output/weenies/" + self.sql_output, 'w') as file_object:
                for command in self.sql_commands:
                    command = command.replace(";", "")
                    if command.strip() != "":
                        if "Lifestoned Changelog" in command:
                            pass
                        else:
                            file_object.write(command + ";")
                file_object.write("\n")
        else:
            tk.messagebox.showinfo("Info", "There was no file to save.")

    def open_output_folder(self):

        Path("output/").mkdir(parents=True, exist_ok=True)
        path = "output"

        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    def open_file(self):
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

    def open_folder(self, name_filter_entry, creature_only):
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
                base_name = os.path.basename(file_name)
                if name_filter.strip() != "":
                    if name_filter in base_name.lower():
                        sql_file = file_object.read()
                        commands = sql_file.split(";")
                        self.check_creature_filter(base_name, commands, creature_only)
                else:
                    sql_file = file_object.read()
                    commands = sql_file.split(";")
                    base_name = os.path.basename(file_name)
                    self.check_creature_filter(base_name, commands, creature_only)

    def check_creature_filter(self, base_name, commands, creature_only):

        if creature_only.get() == 1:
            item_type = file_helper.get_property(commands, "int", 1)
            if item_type is not None:
                if int(item_type[0]) == 16:  # weenie is creature
                    self.sql_dict[base_name] = commands
                    self.view.console.print(base_name + "\n")
        else:
            self.sql_dict[base_name] = commands
            self.view.console.print(base_name + "\n")

    def set_properties(self, my_dict, stat_entries, tag):
        """Set properties for a list of entries."""
        # i is a tuple with the property key and comment
        for label, i in my_dict.items():
            val = stat_entries[label].get().strip()
            if val != "":
                if tag == 'int':
                    val = int(val)
                elif tag == 'did':
                    val = int(val, 16)
                elif tag == 'float':
                    val = round(float(val), 4)
                    if val.is_integer():
                        val = int(val)

                self.sql_commands = file_helper.set_property(self.sql_commands, tag, i[0], val, i[1])

    def set_attributes(self, my_dict, stat_entries, do_override, are_vitals):
        # i is a tuple with the property key and comment
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

        str_label_list = ['quest flag', 'quest restrict']
        self.str_entries = vh.make_str_entry(self.frame, str_label_list)

        str_label_list_2 = ['destination']
        self.pos_entries = vh.make_str_entry(self.frame, str_label_list_2)

        set_button = tk.Button(self.frame, text="Set", bg="lightblue", command=self.set_portal)
        batch_button = tk.Button(self.frame, text="Run Batch",
                                 command=partial(self.cont.run_sql_batch, self.set_portal))

        loc_button = tk.Button(self.frame, text="Loc Paste", command=self.get_loc_paste)

        tooltip = ("To have the portal stamp a quest when you go through it, set quest flag. "
                   "To quest restrict the portal, so you can only go in it if on the quest, set quest restrict. "
                   "Destination is a /myloc paste."
                   )
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
        loc_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
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
            my_dict = {'quest flag': (33, "/* Quest */"), 'quest restrict': (37, "/* QuestRestrict */")}
            self.cont.set_properties(my_dict, self.str_entries, 'string')

            # destination, should be a /myloc paste
            loc_paste = self.pos_entries['destination'].get().strip()
            if loc_paste != "":
                self.cont.sql_commands = file_helper.set_position(self.cont.sql_commands, loc_paste)

    def get_loc_paste(self):
        # destination, should be a /myloc paste
        loc_paste = self.pos_entries['destination'].get().strip()
        if loc_paste != "":
            my_paste = file_helper.get_loc_paste(loc_paste)
            self.cont.view.console.print(my_paste)


class ItemPanel:

    def __init__(self, parent, cont):
        """Use for making items."""
        self.frame = tk.Frame(parent)
        self.cont = cont

        int_header_label = tk.Label(self.frame, text="Int", font=norm_font, fg='blue')

        int_label_list = ['value', 'burden', 'max stack', 'lock resist', 'on use make', 'lifespan']
        self.int_entries = vh.make_int_entry(self.frame, int_label_list)

        # attuned, 1 = yes, 0 = no
        self.is_attuned = tk.IntVar(value=0)
        attuned_check_box = tk.Checkbutton(self.frame, text="attuned", variable=self.is_attuned, font=norm_font)

        self.not_sellable = tk.IntVar(value=0)
        sellable_check_box = tk.Checkbutton(self.frame, text="not sellable", variable=self.not_sellable, font=norm_font)

        # bonded, -2 = destroy on death, 0 = normal, 1 = bonded
        bonded_status_label = tk.Label(self.frame, text="bonded", font=norm_font)
        options = ['no change', 'no', 'yes', 'destroy on death']
        self.bonded_status_combo = ttk.Combobox(self.frame, values=options, font=norm_font, state="readonly")
        self.bonded_status_combo.current(0)

        str_header_label = tk.Label(self.frame, text="Str", font="Arial 12", fg='blue')

        str_label_list = ['use', 'short desc', 'long desc', 'lock code', 'key code', 'pickup timer']
        self.str_entries = vh.make_str_entry(self.frame, str_label_list)

        float_header_label = tk.Label(self.frame, text="Float", font="Arial 12", fg='blue')

        float_labels = ['reset interval']
        self.float_entries = vh.make_float_entry(self.frame, float_labels)

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

        float_header_label.grid(row=r, column=c)
        r += 1

        for name, entry in self.float_entries.items():
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

            val = self.int_entries['lifespan'].get().strip()  # lifespan in seconds
            if val != "":
                val = int(val)  # this input is a wcid
                self.cont.sql_commands = file_helper.set_property(
                    self.cont.sql_commands, "int", 267, val, "/* Lifespan */"
                )

            # attuned
            val = self.is_attuned.get()
            if val == 0:
                pass
            else:
                self.cont.sql_commands = file_helper.set_property(
                    self.cont.sql_commands, "int", 114, 1, "/* Attuned */")

            # not sellable
            val = self.not_sellable.get()
            if val == 0:
                pass
            else:
                self.cont.sql_commands = file_helper.set_property(
                    self.cont.sql_commands, "bool", 69, 0, "/* IsSellable */")

            # bonded
            bonded = self.bonded_status_combo.get()

            if bonded == "no change":
                pass
            elif bonded == "no":
                self.cont.sql_commands = file_helper.set_property(
                    self.cont.sql_commands, "int", 33, 0, "/* Bonded - Normal */")

            elif bonded == "yes":
                self.cont.sql_commands = file_helper.set_property(
                    self.cont.sql_commands, "int", 33, 1, "/* Bonded - Bonded */")

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

            # float
            my_dict = {'reset interval': (11, "/* ResetInterval */")}
            self.cont.set_properties(my_dict, self.float_entries, 'float')

    def make_quest(self):
        """Makes a quest sql file."""
        quest_name = self.str_entries['pickup timer'].get().strip()

        if quest_name:
            quest_helper.make_quest_sql(quest_name, True)
        else:
            tk.messagebox.showerror("Error", "Enter a pickup timer.")


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
        batch_autofill = tk.Button(self.frame, text="Batch Replace",
                                   command=partial(self.cont.run_sql_batch, self.autocomplete_weenie))

        tooltip = ("Use to autocomplete fields for a batch of weenies. "
                   "When using autocomplete, body and combat tables will be copied from a template and "
                   "must be adjusted later. "
                   "The spellbook and XP come from available data, and are not copied. "
                   )
        tooltip_label = tk.Label(self.frame, text=tooltip, font=norm_font, fg="dark green", wraplength=420,
                                 justify=tk.LEFT)

        header_label = tk.Label(self.frame, text="Replace or Append", font=norm_font, fg='blue')

        self.text_area = tk.scrolledtext.ScrolledText(self.frame, height=10, width=10, undo=True)
        batch_replace = tk.Button(self.frame, text="Run Batch",
                                  command=partial(self.cont.run_sql_batch, self.replace_body_table))
        batch_append = tk.Button(self.frame, text="Batch Append",
                                 command=partial(self.cont.run_sql_batch, self.append_command))

        clear_button = tk.Button(self.frame, text="Clear",
                                 command=partial(self.text_area.delete, '1.0', tk.END))

        tooltip2 = ("For batch replace, paste a new body table. For batch append, paste an emote to be added. "
                    "The wcid will be set automatically.")
        tooltip_label2 = tk.Label(self.frame, text=tooltip2, font=norm_font, fg="dark green", wraplength=420,
                                  justify=tk.LEFT)

        # layout
        check_body.grid(row=0, column=0, sticky="w")
        check_combat.grid(row=0, column=1, sticky="w")
        check_xp.grid(row=1, column=0, sticky="w")
        check_spell.grid(row=1, column=1, sticky="w")
        check_other.grid(row=2, column=0, sticky="w")
        set_button.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        batch_autofill.grid(row=4, column=0, sticky="ew", padx=5, pady=5)
        tooltip_label.grid(row=5, column=0, columnspan=2)
        header_label.grid(row=6, column=0, sticky="ew", padx=5, pady=5)
        self.text_area.grid(row=7, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        clear_button.grid(row=8, column=0, sticky="ew", padx=5, pady=5)
        batch_replace.grid(row=9, column=0, sticky="ew", padx=5, pady=5)
        batch_append.grid(row=10, column=0, sticky="ew", padx=5, pady=5)
        tooltip_label2.grid(row=11, column=0, columnspan=2)

    def replace_body_table(self):
        if len(self.cont.sql_commands) > 0:
            body_table = self.text_area.get("1.0", tk.END).strip()
            if body_table != "":
                wcid = re.findall('[0-9]+', (self.cont.sql_commands[0]))[0]
                body_table = re.sub(r'\([0-9]+', "(" + wcid, body_table)

                self.cont.sql_commands = file_helper.replace_sql_command(self.cont.sql_commands,
                                                                         "weenie_properties_body_part",
                                                                         body_table)

    def append_command(self):
        if self.cont.sql_commands is not None:
            body_table = self.text_area.get("1.0", tk.END).strip()
            if body_table != "":
                wcid = re.findall('[0-9]+', (self.cont.sql_commands[0]))[0]
                body_table = re.sub(r'\([0-9]+', "(" + wcid, body_table)
                self.cont.sql_commands = file_helper.append_sql_command(self.cont.sql_commands, body_table)

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
                if creature_species is not None:
                    species_name = labels_module.get_creature_type_label(creature_species[0])
                else:
                    species_name = None

                if species_name is not None:
                    species_name = species_name.lower()

                    templates = file_helper.get_templates()
                    matching_template = None

                    for template in templates:  # try to find a matching template

                        if species_name in template.lower():
                            matching_template = template

                    if matching_template is not None:
                        with open("templates/" + matching_template) as file_object:
                            sql_file = file_object.read()
                            self.cont.template_commands = sql_file.split(";")
                            self.copy_from_template()

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


class UtilityPanel:

    def __init__(self, parent, cont):
        self.frame = tk.Frame(parent)
        self.cont = cont

        # example, for 40% chance of casting a spell, with 4 spells
        # to have equal chance of casting each spell
        # chances_list = [0.1, 0.1, 0.1, 0.1]
        # for caster only mob, leave chances empty and specify total spells

        spell_header = tk.Label(self.frame, text="Spell Calculator", font=norm_font, fg='blue')
        spell_labels = ["chances", "total spells", "total casting"]
        self.spell_entries = vh.make_str_entry(self.frame, spell_labels)
        spell_button = tk.Button(self.frame, text="Get", command=self.get_spell_chances)
        spell_tooltip = "For example, for 40% chance of casting each spell, with 4 spells, enter 0.1, 0.1, 0.1, " \
                        "0.1. For a caster only mob, leave chances empty and specify total spells. "
        spell_tooltip_label = tk.Label(
            self.frame, text=spell_tooltip, font=norm_font, fg="dark green", wraplength=420, justify=tk.LEFT)

        delete_header = tk.Label(self.frame, text="Delete", font=norm_font, fg='blue')
        delete_labels = ["tag"]
        self.delete_entries = vh.make_str_entry(self.frame, delete_labels)

        set_button = tk.Button(self.frame, text="Set", bg="lightblue", command=self.delete_command)
        batch_button = tk.Button(
            self.frame, text="Run Batch", command=partial(self.cont.run_sql_batch, self.delete_command))

        delete_tooltip = "Use to delete a command. For example, enter weenie_properties_create_list to delete it."
        delete_tooltip_label = tk.Label(
            self.frame, text=delete_tooltip, font=norm_font, fg="dark green", wraplength=420, justify=tk.LEFT)

        # layout
        r = 0
        c = 0

        spell_header.grid(row=r, column=c)
        r += 1
        for name, entry in self.spell_entries.items():
            label = tk.Label(self.frame, text=name, font=norm_font)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1
        spell_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        r += 1
        spell_tooltip_label.grid(row=r, column=c, columnspan=2, sticky="w")
        r += 1

        delete_header.grid(row=r, column=c)
        r += 1
        for name, entry in self.delete_entries.items():
            label = tk.Label(self.frame, text=name, font=norm_font)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1
        set_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        r += 1
        batch_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        r += 1
        delete_tooltip_label.grid(row=r, column=c, columnspan=2, sticky="w")

    def get_spell_chances(self):

        chances_list = []
        total_spells = None
        total_casting = 1

        entry = self.spell_entries["chances"].get().strip()
        if entry != "":
            split = entry.split(",")
            for s in split:
                chances_list.append(float(s))

        if len(chances_list) > 0:
            total_spells = len(chances_list)
            self.get_spell_pr(total_spells, chances_list, total_casting)
        else:
            val = self.spell_entries["total spells"].get().strip()
            if val != "":
                total_spells = int(val)
            val = self.spell_entries["total casting"].get().strip()
            if val != "":
                total_casting = float(val)

            if total_spells and total_casting:
                if total_casting > 1:
                    total_casting = 1
                self.get_spell_pr(total_spells, chances_list, total_casting)

        my_sum = 0
        for c in chances_list:
            my_sum += c
        self.cont.view.console.print("total spellcasting chance: " + str(round(my_sum, 2)))
        self.cont.view.console.print("\n")

    def get_spell_pr(self, tot_spells, chances, total_pr):
        if len(chances) == 0:  # this is for a caster only mob
            for i in range(tot_spells):
                pr = total_pr / tot_spells
                chances.append(pr)

        spellbook = self.convert(chances)

        for spell in spellbook:
            self.cont.view.console.print(round(spell, 3) + 2)
            self.cont.view.console.print("\n")

    def convert(self, chances):
        spellbook = []

        for chance in chances:
            none = self.get_prob_none(spellbook)
            spellbook.append(chance / none)

        return spellbook

    def get_prob_none(self, chances):

        pr = 1.0
        for chance in chances:
            pr *= 1.0 - chance
        return pr

    def delete_command(self):

        if self.cont.sql_commands is not None:
            tag = self.delete_entries["tag"].get().strip()
            if tag != "":
                self.cont.sql_commands = file_helper.delete_sql_command(self.cont.sql_commands, tag)


class TaskPanel:

    def __init__(self, parent):
        self.frame = tk.Frame(parent)

        # kill task

        kill_task_header = tk.Label(self.frame, text="Kill Task", font=norm_font, fg='blue')

        kill_task_labels = ['kill wait', 'kill stamp']
        self.str_entries1 = vh.make_str_entry(self.frame, kill_task_labels)

        kill_count_label = ['kill count']
        self.int_entries1 = vh.make_int_entry(self.frame, kill_count_label)

        make_task_button = tk.Button(self.frame, text="Make Task", command=self.make_kill_task)

        # quest

        quest_header = tk.Label(self.frame, text="Quest", font=norm_font, fg='blue')
        quest_labels = ['quest name']
        self.str_entries3 = vh.make_str_entry(self.frame, quest_labels)
        self.is_timed = tk.IntVar(value=0)
        is_timer_check = tk.Checkbutton(
            self.frame, text="is timed", variable=self.is_timed, font=norm_font)
        make_quest_button = tk.Button(self.frame, text="Make Quest", command=self.make_quest)

        # event

        event_header = tk.Label(self.frame, text="Event", font=norm_font, fg='blue')

        event_label = ['event name']
        self.str_entries2 = vh.make_str_entry(self.frame, event_label)

        make_event_button = tk.Button(self.frame, text="Make Event", command=self.make_event)

        # layout

        r = 0
        c = 0

        kill_task_header.grid(row=r, column=c)
        r += 1

        for name, entry in self.str_entries1.items():
            label = tk.Label(self.frame, text=name, font=norm_font)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1

        for name, entry in self.int_entries1.items():
            label = tk.Label(self.frame, text=name, font=norm_font)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1

        make_task_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        r += 1

        quest_header.grid(row=r, column=c)
        r += 1
        for name, entry in self.str_entries3.items():
            label = tk.Label(self.frame, text=name, font=norm_font)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1
        is_timer_check.grid(row=r, column=c)
        r += 1
        make_quest_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        r += 1

        event_header.grid(row=r, column=c)
        r += 1

        for name, entry in self.str_entries2.items():
            label = tk.Label(self.frame, text=name, font=norm_font)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1

        make_event_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")

    def make_kill_task(self):
        kill_wait = self.str_entries1['kill wait'].get().strip()
        kill_stamp = self.str_entries1['kill stamp'].get().strip()
        kill_count = int(self.int_entries1['kill count'].get())

        if kill_wait and kill_stamp and kill_count:
            quest_helper.make_quest_sql(kill_wait, True)
            quest_helper.make_kill_count(kill_stamp, kill_count)
        else:
            tk.messagebox.showerror("Error", "Set kill wait, stamp and count.")

    def make_quest(self):
        quest_name = self.str_entries3['quest name'].get().strip()
        if self.is_timed.get() == 1:
            quest_helper.make_quest_sql(quest_name, True)
        else:
            quest_helper.make_quest_sql(quest_name, False)

    def make_event(self):
        event_name = self.str_entries2['event name'].get().strip()

        if event_name:
            quest_helper.make_event_sql(event_name)
        else:
            tk.messagebox.showerror("Error", "Enter an event name.")


class BasePanel:

    def __init__(self, parent, cont):
        self.frame = tk.Frame(parent)
        self.cont = cont

        str_labels = ['name', 'kill quest']
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

        float_labels = ['heartbeat interval', 'heartbeat timestamp', 'health rate', 'regen interval',
                        'gen radius', 'visual awareness']
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

        item_type_label.grid(row=r, column=c)
        self.item_type_combo.grid(row=r, column=c + 1)
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


class ConsolePanel:

    def __init__(self, parent, cont):
        self.frame = tk.Frame(parent)
        self.cont = cont

        self.text = scrolledtext.ScrolledText(self.frame, height=30, width=40, undo=True, font=norm_font)
        self.text.configure(state='disabled', wrap=tk.WORD)
        self.text.tag_config('field', foreground="dark green")
        self.text.tag_config('warning', foreground="red")

        # configure colors
        self.text.tag_configure("red", foreground="red")
        self.text.tag_configure("blue", foreground="blue")

        clear_button = tk.Button(self.frame, text="Clear", command=self.clear)

        # layout
        self.text.grid(row=0, column=0)
        clear_button.grid(row=1, column=0)

    def clear(self):
        self.text.configure(state='normal')
        self.text.delete('1.0', tk.END)
        self.text.configure(state='disabled')

    def print(self, line, color="black"):
        """Color is an optional parameter."""
        self.text.configure(state='normal')
        self.text.insert(tk.END, line, color)
        self.text.yview_moveto(1)
        self.text.configure(state='disabled')


class ModsPanel:

    def __init__(self, parent, cont):
        """Panel for armor and resistance mods."""
        self.frame = tk.Frame(parent)
        self.cont = cont
        self.armor_scales = {}
        self.resist_scales = {}

        self.labels = {"slash": tk.IntVar(value=1), "pierce": tk.IntVar(value=1), "bludge": tk.IntVar(value=1),
                       "cold": tk.IntVar(value=1), "fire": tk.IntVar(value=1), "acid": tk.IntVar(value=1),
                       "electric": tk.IntVar(value=1), "nether": tk.IntVar(value=1)}

        check_boxes = []
        for k, v in self.labels.items():
            check_boxes.append(tk.Checkbutton(self.frame, text=k, variable=v, font=norm_font))

        self.armor_dict = {
            "slash": (13, "/* ArmorModVsSlash */"),
            "pierce": (14, "/* ArmorModVsPierce */"),
            "bludge": (15, "/* ArmorModVsBludgeon */"),
            "cold": (16, "/* ArmorModVsCold */"),
            "fire": (17, "/* ArmorModVsFire */"),
            "acid": (18, "/* ArmorModVsAcid */"),
            "electric": (19, "/* ArmorModVsElectric */")
        }

        self.resist_dict = {
            "slash": (64, "/* ResistSlash */"),
            "pierce": (65, "/* ResistPierce */"),
            "bludge": (66, "/* ResistBludgeon */"),
            "cold": (68, "/* ResistCold */"),
            "fire": (67, "/* ResistFire */"),
            "acid": (69, "/* ResistAcid */"),
            "electric": (70, "/* ResistElectric */"),
            "nether": (166, "/* ResistNether */")
        }

        self.armor = tk.IntVar(value=1)
        armor_check_box = tk.Checkbutton(self.frame, text="Set armor", variable=self.armor, font=norm_font)

        self.resist = tk.IntVar(value=1)
        resist_check_box = tk.Checkbutton(self.frame, text="Set resist", variable=self.resist, font=norm_font)

        set_button = tk.Button(self.frame, text="Set", bg="lightblue", command=self.set_mods)
        batch_button = tk.Button(self.frame, text="Run Batch", command=partial(self.cont.run_sql_batch, self.set_mods))

        # layout
        r = 0

        left_label = tk.Label(self.frame, text="Armor (0=weak)", font=norm_font, fg='blue')
        left_label.grid(row=r, column=1)

        right_label = tk.Label(self.frame, text="Resist (0=strong)", font=norm_font, fg='blue')
        right_label.grid(row=r, column=2)

        r += 1

        for check_box in check_boxes:
            if check_box["text"] == "cold":
                check_box["fg"] = "blue"
                check_box.grid(row=r, column=0, padx=5, pady=5, sticky="w")
            elif check_box["text"] == "fire":
                check_box["fg"] = "red"
                check_box.grid(row=r, column=0, padx=5, pady=5, sticky="w")
            elif check_box["text"] == "acid":
                check_box["fg"] = "green"
                check_box.grid(row=r, column=0, padx=5, pady=5, sticky="w")
            elif check_box["text"] == "electric":
                check_box["fg"] = "purple"
                check_box.grid(row=r, column=0, padx=5, pady=5, sticky="w")
            else:
                check_box.grid(row=r, column=0, padx=5, pady=5, sticky="w")
            r += 1
        r = 1

        for k, v in self.armor_dict.items():
            armor_scale = tk.Scale(self.frame, from_=0, to=1, resolution=0.05, orient=tk.HORIZONTAL)
            # set default
            armor_scale.set(1)
            armor_scale.grid(row=r, column=1, padx=5, pady=5, sticky='ew')

            self.armor_scales[k] = armor_scale
            r += 1

        r = 1
        for k, v in self.resist_dict.items():
            resist_scale = tk.Scale(self.frame, from_=0, to=1, resolution=0.05, orient=tk.HORIZONTAL)
            # set default
            resist_scale.set(1)
            resist_scale.grid(row=r, column=2, padx=5, pady=5, sticky='ew')

            self.resist_scales[k] = resist_scale
            r += 1

        armor_check_box.grid(row=r, column=1, padx=5, pady=5, sticky="w")
        resist_check_box.grid(row=r, column=2, padx=5, pady=5, sticky="w")
        r += 1
        set_button.grid(row=r, column=0, padx=5, pady=5, sticky="ew")
        r += 1
        batch_button.grid(row=r, column=0, padx=5, pady=5, sticky="ew")

    def set_mods(self):
        """Set mods for a single .sql file. These are float properties."""

        if len(self.cont.sql_commands) > 0:

            if self.armor.get() == 1:  # do set armor mods

                for k, v in self.armor_scales.items():

                    label = self.labels.get(k)
                    if label.get() == 1:
                        mod_val = float(round(v.get(), 2))
                        self.cont.sql_commands = file_helper.set_property(self.cont.sql_commands,
                                                                          "float",
                                                                          self.armor_dict[k][0],
                                                                          mod_val,
                                                                          self.armor_dict[k][1])

            if self.resist.get() == 1:  # do set resist mods

                for k, v in self.resist_scales.items():
                    label = self.labels.get(k)
                    if label.get() == 1:
                        mod_val = float(round(v.get(), 2))
                        self.cont.sql_commands = file_helper.set_property(self.cont.sql_commands,
                                                                          "float",
                                                                          self.resist_dict[k][0],
                                                                          mod_val,
                                                                          self.resist_dict[k][1])


class AttributesPanel:

    def __init__(self, parent, cont):
        self.frame = tk.Frame(parent)
        self.cont = cont

        attributes_header = tk.Label(self.frame, text="Attributes", font=norm_font, fg='blue')
        vitals_header = tk.Label(self.frame, text="Vitals", font=norm_font, fg='blue')

        self.int_entries_1 = vh.make_int_entry(self.frame, labels_module.get_primary_attribute_labels())
        self.int_entries_2 = vh.make_int_entry(self.frame, labels_module.get_secondary_attribute_labels())

        self.replace_vitals = tk.IntVar(value=0)
        replace_vitals_check = tk.Checkbutton(
            self.frame, text="replace vitals", variable=self.replace_vitals, font=norm_font)

        set_button = tk.Button(self.frame, text="Set", bg="lightblue", command=self.set_attributes)
        batch_button = tk.Button(self.frame, text="Run Batch",
                                 command=partial(self.cont.run_sql_batch, self.set_attributes))

        tooltip = "All fields optional. Vitals are adjusted based on attributes so what you see is what you get."
        tooltip_label = tk.Label(self.frame, text=tooltip, font=norm_font, fg="dark green", wraplength=420,
                                 justify=tk.LEFT)

        # layout
        r = 0
        c = 0

        attributes_header.grid(row=r, column=c, sticky='w')
        r += 1

        for name, entry in self.int_entries_1.items():
            label = tk.Label(self.frame, text=name, font=norm_font)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1

        vitals_header.grid(row=r, column=c, sticky='w')
        r += 1

        for name, entry in self.int_entries_2.items():
            label = tk.Label(self.frame, text=name, font=norm_font)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1

        replace_vitals_check.grid(row=r, column=c + 1, padx=5, pady=5, sticky="w")
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
            if self.replace_vitals.get() == 1:
                self.cont.set_attributes(my_dict, self.int_entries_2, True, True)
            else:
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

        float_labels = ['shade', 'translucency', 'scale']
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


class SkillsPanel:

    def __init__(self, parent, cont):
        self.frame = tk.Frame(parent)
        self.cont = cont

        offensive_header = tk.Label(self.frame, text="Offensive", font=norm_font, fg='blue')
        defensive_header = tk.Label(self.frame, text="Defensive", font=norm_font, fg='blue')

        skill_labels = ['magic', 'melee', 'missile']
        self.offensive_entries = vh.make_int_entry(self.frame, skill_labels)
        self.defensive_entries = vh.make_int_entry(self.frame, skill_labels)

        # other
        self.sneak_attack = tk.IntVar(value=0)
        add_sneak_attack = tk.Checkbutton(self.frame, text="sneak attack", variable=self.sneak_attack, font=norm_font)

        self.dirty_fighting = tk.IntVar(value=0)
        add_dirty_fighting = tk.Checkbutton(self.frame, text="dirty fighting", variable=self.dirty_fighting,
                                            font=norm_font)

        self.dual_wield = tk.IntVar(value=0)
        add_dual_wield = tk.Checkbutton(self.frame, text="dual wield", variable=self.dual_wield,
                                        font=norm_font)

        self.deception = tk.IntVar(value=0)
        add_deception = tk.Checkbutton(self.frame, text="deception", variable=self.deception,
                                       font=norm_font)

        self.shield = tk.IntVar(value=0)
        add_shield = tk.Checkbutton(self.frame, text="shield", variable=self.shield,
                                    font=norm_font)

        check_attributes_button = tk.Button(self.frame, text="Check", command=self.check_parameters)
        set_button = tk.Button(self.frame, text="Set", bg="lightblue", command=self.set_skills)
        batch_button = tk.Button(self.frame, text="Run Batch",
                                 command=partial(self.cont.run_sql_batch, self.set_skills))

        tooltip = ("All fields optional. "
                   "Set attributes first and enter desired skill levels. "
                   "Melee offense sets heavy, light and two-handed weapons. "
                   "Magic offense sets life, creature, war, and void. "
                   )

        tooltip_label = tk.Label(self.frame, text=tooltip, font=norm_font, fg="dark green", wraplength=420,
                                 justify=tk.LEFT)

        # layout
        r = 0
        c = 0

        offensive_header.grid(row=r, column=c, sticky='w')
        r += 1

        for name, entry in self.offensive_entries.items():
            label = tk.Label(self.frame, text=name, font=norm_font)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1

        defensive_header.grid(row=r, column=c, sticky='w')
        r += 1

        for name, entry in self.defensive_entries.items():
            label = tk.Label(self.frame, text=name, font=norm_font)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1

        add_sneak_attack.grid(row=r, column=c, padx=5, pady=5, sticky="w")
        add_dirty_fighting.grid(row=r, column=c + 1, padx=5, pady=5, sticky="w")
        r += 1
        add_dual_wield.grid(row=r, column=c, padx=5, pady=5, sticky="w")
        add_deception.grid(row=r, column=c + 1, padx=5, pady=5, sticky="w")
        r += 1
        add_shield.grid(row=r, column=c, padx=5, pady=5, sticky="w")
        r += 1

        check_attributes_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        r += 1
        set_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        r += 1
        batch_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        r += 1
        tooltip_label.grid(row=r, column=c, columnspan=2)
        r += 1

    def check_parameters(self):
        """Check attributes, base, effective, and pcap skills."""
        if self.cont.sql_commands is not None:
            attributes = file_helper.get_all_attributes(self.cont.sql_commands)
            self.cont.view.console.print("\nAttributes\n")
            for k, v in attributes.items():
                self.cont.view.console.print(str(k) + "\t" + str(v) + "\n")

            skills = skills_module.get_skill_table(self.cont.sql_commands)
            self.cont.view.console.print("\nBase Skills\n")
            for skill in skills:
                self.cont.view.console.print(skill.name + "\t" + str(skill.value) + "\n")

            self.cont.view.console.print("\nEffective Skills\n")
            for skill in skills:
                attribute_bonus = skills_module.get_attribute_bonus(attributes, skill.name)
                effective_value = skill.value + attribute_bonus
                self.cont.view.console.print(skill.name + "\t" + str(effective_value) + "\n")

            self.cont.view.console.print("\nPCAP Skills\n")
            pcap_skills = self.get_skill_pcap()
            for k, v in pcap_skills.items():
                self.cont.view.console.print(str(k) + "\t" + str(v) + "\n")

    def set_skills(self):
        self.replace_skills()

    def get_skill_pcap(self):
        if len(self.cont.sql_commands) > 0:
            name = file_helper.get_name(self.cont.sql_commands)
            pcap_skills = skills_module.skill_look_up(name)
            return pcap_skills

    def replace_skills(self):

        if len(self.cont.sql_commands) > 0:

            wcid = file_helper.get_wcid(self.cont.sql_commands)
            attributes = file_helper.get_all_attributes(self.cont.sql_commands)

            skills = {}

            if self.deception.get() == 1:
                skills['Deception'] = 100

            if self.shield.get() == 1:
                skills['Shield'] = 100

            # offensive skills
            for k, v in self.offensive_entries.items():

                val = v.get()
                if val != "":
                    val_int = int(val)

                    if k == 'magic':
                        attribute_bonus = round((attributes['focus'] + attributes['self']) / 4)
                        val_int = val_int - attribute_bonus
                        skills['LifeMagic'] = val_int
                        skills['WarMagic'] = val_int
                        skills['CreatureEnchantment'] = val_int
                        skills['VoidMagic'] = val_int

                    elif k == 'melee':
                        attribute_bonus1 = round((attributes['strength'] + attributes['coordination']) / 3)
                        attribute_bonus2 = round((attributes['coordination'] + attributes['quickness']) / 3)
                        heavy_light_twohand = val_int - attribute_bonus1
                        finesse_skill = val_int - attribute_bonus2

                        skills['HeavyWeapons'] = heavy_light_twohand
                        skills['LightWeapons'] = heavy_light_twohand
                        skills['TwoHandedCombat'] = heavy_light_twohand
                        skills['FinesseWeapons'] = finesse_skill

                        if self.sneak_attack.get() == 1:
                            skills['SneakAttack'] = finesse_skill

                        if self.dirty_fighting.get() == 1:
                            skills['DirtyFighting'] = heavy_light_twohand

                        if self.dual_wield.get() == 1:
                            if heavy_light_twohand > finesse_skill:
                                skills['DualWield'] = heavy_light_twohand
                            else:
                                skills['DualWield'] = finesse_skill

                    elif k == 'missile':
                        attribute_bonus = round(attributes['coordination'] / 2)
                        val_int = val_int - attribute_bonus
                        skills['MissileWeapons'] = val_int
                    else:
                        tk.messagebox.showerror("Error", "A skill label was undefined.")

            # defensive skills
            for k, v in self.defensive_entries.items():

                val = v.get()
                if val != "":
                    val_int = int(val)

                    if k == 'magic':
                        attribute_bonus = round((attributes['focus'] + attributes['self']) / 7)
                        val_int = val_int - attribute_bonus
                        skills['MagicDefense'] = val_int
                    elif k == 'melee':
                        attribute_bonus = round((attributes['coordination'] + attributes['quickness']) / 3)
                        val_int = val_int - attribute_bonus
                        skills['MeleeDefense'] = val_int
                    elif k == 'missile':
                        attribute_bonus = round((attributes['coordination'] + attributes['quickness']) / 5)
                        val_int = val_int - attribute_bonus
                        skills['MissileDefense'] = val_int
                    else:
                        tk.messagebox.showerror("Error", "A skill label was undefined.")

            # make the skill table
            new_command = skills_module.make_skill_table(wcid, skills)

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


class CalcPanel:

    def __init__(self, parent, cont):
        self.frame = tk.Frame(parent)
        self.cont = cont

        skill_check_header = tk.Label(self.frame, text="Skill Calculator", font=norm_font, fg='blue')
        skill_check_labels = ['player skill', 'skill modifier', 'monster skill']
        self.skill_check_entries = vh.make_float_entry(self.frame, skill_check_labels)

        tooltip = ("All fields required. "
                   "Use a skill mod of 1.6 for missile at full accuracy. "
                   "Use a mod of 1.35 for melee since 35% is the average weapon attack mod. "
                   "Level 200 combat pet attack skill is 693 with a mod of 1. Level 180 pet skill is 653."
                   )

        tooltip_label = tk.Label(self.frame, text=tooltip, font=norm_font, fg="dark green", wraplength=420,
                                 justify=tk.LEFT)

        check_skill_button = tk.Button(self.frame, text="Check Skill", command=self.check_skill)
        check_range_button = tk.Button(self.frame, text="Check Range", command=self.check_range)

        # layout
        r = 0
        c = 0

        skill_check_header.grid(row=r, column=c, sticky='w')
        r += 1

        for name, entry in self.skill_check_entries.items():
            label = tk.Label(self.frame, text=name, font=norm_font)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1

        check_skill_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        r += 1
        check_range_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        r += 1
        tooltip_label.grid(row=r, column=c, columnspan=2)
        r += 1

    def check_skill(self):

        # mod of 1.6 for missile at full accuracy, mod of 1.35 for melee (since 35% is average weapon attack mod)
        player_skill = self.skill_check_entries.get("player skill").get().strip()
        skill_modifier = self.skill_check_entries.get("skill modifier").get().strip()
        monster_skill = self.skill_check_entries.get("monster skill").get().strip()

        if player_skill != "" and skill_modifier != "" and monster_skill != "":

            player_skill = int(player_skill)
            skill_modifier = float(skill_modifier)
            player_skill = round(player_skill * skill_modifier, 1)
            monster_skill = int(monster_skill)

            y = 1 - 1 / (1 + math.exp(0.03 * (player_skill - monster_skill)))
            self.cont.view.console.print("player skill\t" + str(player_skill) + "\tsuccess\t"
                                         + str(round(y * 100, 2)) + "\n")
        else:
            self.cont.view.console.print("Enter a value for player and monster skill, and player skill modifier.\n")

    def check_range(self):

        monster_skill = self.skill_check_entries.get("monster skill").get().strip()
        if monster_skill != "":
            monster_skill = int(monster_skill)
            self.cont.view.console.print(f"""Results for {monster_skill} monster skill:\n""")
            for player_skill in range(0, 1010, 10):
                y = 1 - 1 / (1 + math.exp(0.03 * (player_skill - monster_skill)))
                self.cont.view.console.print("player skill\t" + str(player_skill) + "\tsuccess\t"
                                             + str(round(y * 100, 2)) + "\n")
        else:
            self.cont.view.console.print("Enter a value for monster skill.\n")


class LootPanel:

    def __init__(self, parent, cont):
        self.frame = tk.Frame(parent)
        self.cont = cont

        # all fields required
        trophies_header = tk.Label(self.frame, text="Trophies", font=norm_font, fg='blue')

        int_labels = ['monster wcid', 'item wcid', 'total']
        self.trophy_entries = vh.make_int_entry(self.frame, int_labels)
        self.trophy_entries['total'].insert(tk.END, "1")

        float_labels = ['drop chance']
        self.drop_chance = vh.make_float_entry(self.frame, float_labels)

        tooltip = ("To have multiple copies of a trophy drop on death, set total on corpse. "
                   "The drop chance is also known as shade and must be a float. "
                   "If greater than 0 and less than 1 it's a chance to drop. "
                   "Set to 1 to have the trophy always drop."
                   )
        tooltip_label = tk.Label(self.frame, text=tooltip, font=norm_font, fg="dark green", wraplength=420,
                                 justify=tk.LEFT)

        make_create_list_button = tk.Button(self.frame, text="Make Create List", command=self.make_create_list)

        gen_header = tk.Label(self.frame, text="Generator", font=norm_font, fg='blue')

        gen_int_labels = ['delay']
        self.gen_int_entries = vh.make_int_entry(self.frame, gen_int_labels)

        make_on_top_gen_button = tk.Button(self.frame, text="Make On Top Gen", command=self.make_on_top_gen)
        make_scatter_gen_button = tk.Button(self.frame, text="Make Scatter Gen", command=self.make_scatter_gen)
        make_specific_gen_button = tk.Button(self.frame, text="Make Specific Gen", command=self.make_specific_gen)

        gen_tooltip = ("Enter generator wcid in the monster wcid field. "
                       "The weenie to spawn is entered in the item wcid field. "
                       "Total is only used for scatter generators. "
                       "Use drop chance like for trophies to set spawn probability. "
                       )
        gen_tooltip_label = tk.Label(self.frame, text=gen_tooltip, font=norm_font, fg="dark green", wraplength=420,
                                     justify=tk.LEFT)

        # layout
        r = 0
        c = 0
        trophies_header.grid(row=r, column=c)
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

        make_create_list_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        r += 1
        tooltip_label.grid(row=r, column=c, columnspan=2)
        r += 1
        gen_header.grid(row=r, column=c)
        r += 1

        for name, entry in self.gen_int_entries.items():
            label = tk.Label(self.frame, text=name, font=norm_font)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1

        make_on_top_gen_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        r += 1
        make_scatter_gen_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        r += 1
        make_specific_gen_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        r += 1
        gen_tooltip_label.grid(row=r, column=c, columnspan=2)

    def make_on_top_gen(self):

        monster_wcid = self.trophy_entries['monster wcid'].get()
        item_wcid = self.trophy_entries['item wcid'].get()
        delay = self.gen_int_entries['delay'].get()

        if monster_wcid == "" or item_wcid == "" or delay == "":
            tk.messagebox.showerror("Error", "The monster, item, and delay fields are required.")
        else:
            gen = """INSERT INTO `weenie_properties_generator` (`object_Id`, `probability`, `weenie_Class_Id`, `delay`, `init_Create`, `max_Create`, `when_Create`, `where_Create`, `stack_Size`, `palette_Id`, `shade`, `obj_Cell_Id`, `origin_X`, `origin_Y`, `origin_Z`, `angles_W`, `angles_X`, `angles_Y`, `angles_Z`)\n"""
            gen += f"""VALUES ({monster_wcid}, -1, {item_wcid}, {delay}, 1, 1, 1, 1, -1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0) /* Generate ({item_wcid}) (x1 up to max of 1) - Regenerate upon Destruction - Location to (re)Generate: OnTop */;\n"""
            self.cont.view.console.print(gen)

    def make_scatter_gen(self):

        monster_wcid = self.trophy_entries['monster wcid'].get()
        item_wcid = self.trophy_entries['item wcid'].get()
        total = self.trophy_entries['total'].get()
        delay = self.gen_int_entries['delay'].get()

        if monster_wcid == "" or item_wcid == "" or total == "" or delay == "":
            tk.messagebox.showerror("Error", "The monster, item, total, and delay fields are required.")
        else:
            gen = """INSERT INTO `weenie_properties_generator` (`object_Id`, `probability`, `weenie_Class_Id`, `delay`, `init_Create`, `max_Create`, `when_Create`, `where_Create`, `stack_Size`, `palette_Id`, `shade`, `obj_Cell_Id`, `origin_X`, `origin_Y`, `origin_Z`, `angles_W`, `angles_X`, `angles_Y`, `angles_Z`)\n"""
            gen += f"""VALUES ({monster_wcid}, -1, {item_wcid}, {delay}, {total}, {total}, 1, 2, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0) /* Generate  ({item_wcid}) (x{total} up to max of {total}) - Regenerate upon Destruction - Location to (re)Generate: Scatter */;\n"""
            self.cont.view.console.print(gen)

    def make_specific_gen(self):

        monster_wcid = self.trophy_entries['monster wcid'].get()
        item_wcid = self.trophy_entries['item wcid'].get()
        total = self.trophy_entries['total'].get()
        delay = self.gen_int_entries['delay'].get()

        if monster_wcid == "" or item_wcid == "" or total == "" or delay == "":
            tk.messagebox.showerror("Error", "The monster, item, total, and delay fields are required.")
        else:
            gen = """INSERT INTO `weenie_properties_generator` (`object_Id`, `probability`, `weenie_Class_Id`, `delay`, `init_Create`, `max_Create`, `when_Create`, `where_Create`, `stack_Size`, `palette_Id`, `shade`, `obj_Cell_Id`, `origin_X`, `origin_Y`, `origin_Z`, `angles_W`, `angles_X`, `angles_Y`, `angles_Z`)\n"""
            gen += f"""VALUES ({monster_wcid}, -1, {item_wcid}, {delay}, {total}, {total}, 1, 4, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0) /* Generate  ({item_wcid}) (x{total} up to max of {total}) - Regenerate upon Destruction - Location to (re)Generate: Specific */;\n"""
            self.cont.view.console.print(gen)

    def make_create_list(self):

        monster_wcid = self.trophy_entries['monster wcid'].get()
        item_wcid = self.trophy_entries['item wcid'].get()
        total = self.trophy_entries['total'].get()
        drop = self.drop_chance['drop chance'].get()

        if monster_wcid == "" or item_wcid == "" or total == "" or drop == "":
            tk.messagebox.showerror("Error", "All fields are required.")
        else:

            item_wcid = int(item_wcid)
            total_on_corpse = int(total)
            shade = round(float(drop), 2)

            if shade.is_integer():
                shade = int(shade)

            counter = 0
            create_list = ""
            for _ in range(total_on_corpse):

                if 1 > shade > 0:  # contain treasure

                    empty_slot_shade = round(float(1 - shade), 2)
                    if empty_slot_shade.is_integer():
                        empty_slot_shade = int(empty_slot_shade)

                    if counter == 0:

                        create_list += """INSERT INTO `weenie_properties_create_list` (`object_Id`, `destination_Type`, `weenie_Class_Id`, `stack_Size`, `palette`, `shade`, `try_To_Bond`)\n"""
                        create_list += f"""VALUES ({monster_wcid}, 9, {item_wcid}, 0, 0, {shade}, False) /* Create ({item_wcid}) for Contain Treasure */\n"""
                        create_list += f"""     , ({monster_wcid}, 9,     0, 0, 0, {empty_slot_shade}, False) /* Create nothing for Contain Treasure */\n"""

                    else:
                        create_list += f"""     , ({monster_wcid}, 9, {item_wcid}, 0, 0, {shade}, False) /* Create ({item_wcid}) for Contain Treasure */\n"""
                        create_list += f"""     , ({monster_wcid}, 9,     0, 0, 0, {empty_slot_shade}, False) /* Create nothing for Contain Treasure */\n"""

                else:  # contain, always

                    if counter == 0:
                        create_list += """INSERT INTO `weenie_properties_create_list` (`object_Id`, `destination_Type`, `weenie_Class_Id`, `stack_Size`, `palette`, `shade`, `try_To_Bond`)\n"""
                        create_list += f"""VALUES ({monster_wcid}, 9, {item_wcid},  0, 0,   1, False) /* Create ({item_wcid}) for Contain */\n"""

                    else:
                        create_list += f"""     , ({monster_wcid}, 9, {item_wcid},  0, 0,   1, False) /* Create ({item_wcid}) for Contain */\n"""

                counter += 1

            create_list += ";"
            create_list = create_list.replace("\n;", ";\n")
            self.cont.view.console.print(create_list)


norm_font = ("Arial", 12)


def main():
    # if on Windows, fix blurry font
    if os.name == 'nt':
        windll.shcore.SetProcessDpiAwareness(1)

    version = 0.9
    root = tk.Tk()
    root.title("AC Monsters " + str(version))
    Controller(root)
    root.mainloop()


if __name__ == '__main__':
    main()
