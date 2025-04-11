from view import View
from pathlib import Path
import tkinter as tk
import os
import tkinter.messagebox
from tkinter import filedialog
import file_helper
import stat_helper


class Controller:

    def __init__(self, parent):
        # sql file (i.e., sql commands) currently being worked on
        self.sql_data = None
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
            self.sql_data = commands
            self.sql_output = file_name
            self.view.console.print("Working on " + file_name + "...")
            func()
            self.save_sql()
            self.view.console.print("Done.\n")

    def save_sql(self):

        if self.sql_data:
            with open("output/weenies/" + self.sql_output, 'w') as file_object:
                for command in self.sql_data:
                    command = command.replace(";", "")
                    if command.strip() != "":
                        if "Lifestoned Changelog" in command:
                            pass
                        else:
                            file_object.write(command + ";")
                file_object.write("\n")
        else:
            tk.messagebox.showinfo("Info", "There was no file to save.")

    def open_file(self):
        """Load a single .sql file."""
        my_file = filedialog.askopenfilename(filetypes=[("sql files", "*.sql")])
        if my_file:
            with open(my_file) as file_object:
                sql_file = file_object.read()
                self.sql_data = sql_file.split(";")

                # this is the output file name
                self.sql_output = os.path.split(my_file)[1]
                self.view.console.clear()
                self.view.console.print("Working with: " + self.sql_output + "\n")
                self.view.attributes_panel.show_attributes()
                self.view.skills_panel.check_parameters()

                # for max, use 561, 607, 556, 580, 417, 1.55
                # for 150, use 435, 482, 430, 460, 322, 1.45
                self.view.calc_panel.profile_player("Max", 561, 607, 556, 580, 417, 1.55)
                self.view.calc_panel.profile_player("150", 435, 482, 430, 460, 322, 1.45)

                self.view.mods_panel.show_mods()

    def open_folder(self, name_filter_entry):
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
                if name_filter.strip():
                    if name_filter in base_name.lower():
                        sql_file = file_object.read()
                        commands = sql_file.split(";")
                        self.check_creature_filter(base_name, commands)
                else:
                    sql_file = file_object.read()
                    commands = sql_file.split(";")
                    base_name = os.path.basename(file_name)
                    self.check_creature_filter(base_name, commands)

    def file_warning(self):
        self.view.console.print("Open a file to work with.\n")

    def check_creature_filter(self, base_name, commands):
        item_type = file_helper.get_property(commands, "int", 1)
        if item_type is not None:
            if int(item_type[0]) == 16:  # weenie is creature
                self.sql_dict[base_name] = commands
                self.view.console.print(base_name + "\n")

    def set_properties(self, my_dict: dict, entries: list, property_type: str):
        """Set properties for a list of entries."""
        for label, i in my_dict.items():
            val = entries[label].get().strip()
            if val:
                if property_type == 'int':
                    val = int(val)
                elif property_type == 'did':
                    val = int(val, 16)
                elif property_type == 'float':
                    val = round(float(val), 4)
                    if val.is_integer():
                        val = int(val)
                self.sql_data = file_helper.set_property(self.sql_data, property_type, i[0], val, i[1])

    def set_attributes(self, my_dict: dict, entries: list, are_vitals: bool):
        for label, i in my_dict.items():
            val = entries[label].get().strip()
            if val:
                val = int(val)
                if are_vitals:
                    self.sql_data = stat_helper.set_attribute_2(self.sql_data, i[0], val, i[1])
                else:
                    self.sql_data = stat_helper.set_attribute_1(self.sql_data, i[0], val, i[1])

    def open_help(self):
        current_tab_name = self.view.get_current_tab_name()
        print(current_tab_name)


