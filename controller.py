from view import View
from pathlib import Path
import os
from tkinter import filedialog
import file_helper
import stat_helper


class Controller:

    def __init__(self, parent):
        # sql file (i.e., weenie) currently being worked on
        self.weenie_sql = None
        # name of the output file
        self.output_sql = None
        # keys are sql file names, values are file contents (i.e., weenie sql)
        self.sql_dict = {}

        self.view = View(parent, self)

    def run_sql_batch(self, func):

        Path("output/weenies").mkdir(parents=True, exist_ok=True)
        self.clear_console()

        for file_name, weenie_sql in self.sql_dict.items():
            self.weenie_sql = weenie_sql
            self.output_sql = file_name
            self.print("Working on " + file_name + "...")
            func()
            self.save_sql()
            self.print("Done.\n")

    def save_sql(self):

        Path("output/weenies").mkdir(parents=True, exist_ok=True)

        if self.weenie_sql is not None:
            with open("output/weenies/" + self.output_sql, 'w') as file_object:
                for table_sql in self.weenie_sql:
                    table_sql = table_sql.replace(";", "")
                    if table_sql.strip():
                        if "Lifestoned Changelog" in table_sql:
                            pass
                        else:
                            file_object.write(table_sql + ";")
                file_object.write("\n")
        else:
            self.print("There was no file to save.")

    def open_file(self):
        """Loads a single .sql file as list of strings, where each table (i.e., insert block)
        is a string."""
        my_file = filedialog.askopenfilename(filetypes=[("sql files", "*.sql")])
        if my_file:
            with open(my_file) as file_object:
                sql_file = file_object.read()
                self.weenie_sql = sql_file.split(";")

                # this is the output file name
                self.output_sql = os.path.split(my_file)[1]
                self.clear_console()
                self.print("Working with: " + self.output_sql + "\n")
                self.view.refresh()

    def open_folder(self, name_filter_entry):
        """Load all .sql files in a folder for batch processing. This will also walk through all subdirectories
        in the folder."""
        file_folder = filedialog.askdirectory()

        if not file_folder:
            return

        name_filter = name_filter_entry.get().strip().lower()
        my_list = []

        for subdir, dirs, files in os.walk(file_folder):
            for file in files:
                if file.lower().endswith(".sql"):
                    my_list.append(os.path.join(subdir, file))

        self.sql_dict.clear()
        self.clear_console()
        self.print("Found the following files:\n")

        for file_name in my_list:
            with open(os.path.join(file_folder, file_name)) as file_object:
                base_name = os.path.basename(file_name)

                if name_filter.strip():
                    if name_filter in base_name.lower():
                        sql_file = file_object.read()
                        weenie_sql = sql_file.split(";")
                        self.check_creature_filter(base_name, weenie_sql)
                else:
                    sql_file = file_object.read()
                    weenie_sql = sql_file.split(";")
                    base_name = os.path.basename(file_name)
                    self.check_creature_filter(base_name, weenie_sql)

    def check_creature_filter(self, base_name, weenie_sql):
        item_type = file_helper.get_property(weenie_sql, "int", 1)
        if item_type is not None:
            if int(item_type[0]) == 16:  # weenie is creature
                self.sql_dict[base_name] = weenie_sql
                self.print(base_name + "\n")

    def get_wcid(self) -> int | None:
        if self.weenie_sql is None:
            self.file_warning()
            return None

        return int(file_helper.get_wcid(self.weenie_sql))

    def set_properties(self, property_map: dict, entries: dict, property_type: str):
        for label, (property_id, comment) in property_map.items():
            new_value = entries[label].get().strip()
            if new_value:
                if property_type == 'int':
                    new_value = int(new_value)
                elif property_type == 'did':
                    new_value = int(new_value, 16)
                elif property_type == 'float':
                    new_value = round(float(new_value), 4)
                    if new_value.is_integer():
                        new_value = int(new_value)
                self.weenie_sql = file_helper.set_property(
                    self.weenie_sql, property_type, property_id, new_value, comment
                )

    def set_attributes(self, property_map: dict, entries: dict, are_vitals: bool):
        for label, (property_id, comment) in property_map.items():
            new_value = entries[label].get().strip()
            if new_value:
                new_value = int(new_value)
                if are_vitals:
                    self.weenie_sql = stat_helper.set_attribute_2(self.weenie_sql, property_id, new_value, comment)
                else:
                    self.weenie_sql = stat_helper.set_attribute_1(self.weenie_sql, property_id, new_value, comment)

    def set_sql_table(self, table_name: str, new_table: list):
        if self.weenie_sql is not None:
            self.weenie_sql = file_helper.set_sql_table(self.weenie_sql, table_name, new_table)

    def print(self, text: str, color: str = "black"):
        self.view.console.print(text, color)

    def clear_console(self):
        self.view.console.clear()

    def file_warning(self):
        self.print("Open a file to work with.\n")

    def show_help(self):
        self.view.show_help()
