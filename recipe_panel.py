import view_helper as vh
import sql_helper as sh
import settings as st
import tkinter as tk

class RecipePanel(tk.Frame):

    def __init__(self, parent, cont):
        super().__init__(parent, bg=st.base_bg)
        self.cont = cont

        norm_font = st.norm_font

        int_header_label = tk.Label(self, text="Int", font=norm_font, fg=st.label_text, bg=st.base_bg)
        int_labels = ["recipe id", "source wcid", "target wcid", "result wcid"]
        self.int_entries = vh.make_int_entry(self, int_labels)

        str_header_label = tk.Label(self, text="Str", font=norm_font, fg=st.label_text, bg=st.base_bg)
        str_labels = ["source name", "target name", "result name", "success text", "failure text"]
        self.str_entries = vh.make_str_entry(self, str_labels)

        make_recipe_button = tk.Button(self, text="Make Recipe", command=self.make_recipe)

        # layout
        r = 0
        c = 0

        int_header_label.grid(row=r, column=c, sticky="w", padx=2)
        r += 1
        for name, entry in self.int_entries.items():
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

        make_recipe_button.grid(row=r, column=c, columnspan=2, padx=2, pady=5, sticky="ew")

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)


    def make_recipe(self):
        # only supports no skill recipe
        int_fields = {}
        for name, entry in self.int_entries.items():
            val = entry.get().strip()
            if val == "":
                self.cont.view.console.print(f"There was an invalid or missing integer field.\n")
                return
            else:
                int_fields[name] = val

        str_fields = {}
        for name, entry in self.str_entries.items():
            val = entry.get().strip()
            if val == "":
                self.cont.view.console.print(f"There was an invalid or missing text field.\n")
                return
            else:
                # escape any apostrophes
                str_fields[name] = val.replace("'", "''")

        recipe_id = int_fields["recipe id"]
        source_wcid = int_fields["source wcid"]
        target_wcid = int_fields["target wcid"]
        result_wcid = int_fields["result wcid"]

        source_name = str_fields["source name"]
        target_name = str_fields["target name"]
        result_name = str_fields["result name"]

        success_text = str_fields["success text"]
        failure_text = str_fields["failure text"]

        commands = [
            f"DELETE FROM `recipe` WHERE `id` = {recipe_id};\n\n",
            f"INSERT INTO `recipe` (`id`, `unknown_1`, `skill`, `difficulty`, `salvage_Type`, `success_W_C_I_D`, `success_Amount`, `success_Message`, `fail_W_C_I_D`, `fail_Amount`, `fail_Message`, `success_Destroy_Source_Chance`, `success_Destroy_Source_Amount`, `success_Destroy_Source_Message`, `success_Destroy_Target_Chance`, `success_Destroy_Target_Amount`, `success_Destroy_Target_Message`, `fail_Destroy_Source_Chance`, `fail_Destroy_Source_Amount`, `fail_Destroy_Source_Message`, `fail_Destroy_Target_Chance`, `fail_Destroy_Target_Amount`, `fail_Destroy_Target_Message`, `data_Id`, `last_Modified`)\n",
            f"VALUES ({recipe_id}, 0, 0, 0, 0, {result_wcid} /* {result_name} */, 1, '{success_text}', 0, 0, '{failure_text}', 1, 1, NULL, 1, 1, NULL, 1, 1, NULL, 1, 1, NULL, 0, '2005-02-09 10:00:00');\n\n",
            f"DELETE FROM `cook_book` WHERE `recipe_Id` = {recipe_id};\n\n",
            f"INSERT INTO `cook_book` (`recipe_Id`, `source_W_C_I_D`, `target_W_C_I_D`, `last_Modified`)\n",
            f"VALUES ({recipe_id}, {source_wcid} /* {source_name} */,  {target_wcid} /* {target_name} */, '2005-02-09 10:00:00');\n"
        ]
        sh.write_sql_file(str(recipe_id) + " " + result_name, "recipes", ''.join(commands))