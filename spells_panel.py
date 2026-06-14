import tkinter as tk
from functools import partial
from tkinter import ttk

import file_helper
import settings as st
import spells_module


class SpellsPanel(tk.Frame):

    def __init__(self, parent, cont):
        super().__init__(parent, bg=st.base_bg)
        self.cont = cont

        self.spell_dict = spells_module.load_spell_dict()
        self.current_spells = []

        self.id_to_spell = {v: k for k, v in self.spell_dict.items()}
        self.special_names = spells_module.load_special_dict()
        self.flipped_names = {v: k for k, v in self.special_names.items()}

        self.info_label = tk.Label(self, text="No spellbook found.", bg=st.base_bg, font=st.norm_font, anchor="w")

        # find spell by name
        find_label = tk.Label(self, text="Find spell by name", bg=st.base_bg, font=st.norm_font)
        self.find_entry = tk.Entry(self, bg=st.entry_bg, font=st.norm_font)
        find_button = tk.Button(self, text="Find", command=self.find_spell)

        # update or delete spell
        add_update_button = tk.Button(self, text="Add / Update", command=self.add_or_update_spell)
        delete_button = tk.Button(self, text="Delete", command=self.delete_selected_spell)
        set_button = tk.Button(self, text="Set", bg=st.button_bg, command=self.save_spellbook)

        # upgrade spells
        upgrade_button = tk.Button(self, text="Upgrade", bg=st.button_bg, command=self.upgrade_spells)
        batch_button = tk.Button(self, text="Batch Upgrade",
                                 command=partial(self.cont.run_sql_batch, self.upgrade_spells))

        # spellbook treeview
        style = ttk.Style()
        style.configure(
            "Spellbook.Treeview",
            rowheight=24,
            font=st.norm_font,
            fieldbackground=st.entry_bg
        )

        self.spell_tree = ttk.Treeview(
            self,
            style="Spellbook.Treeview",
            columns=("id", "name", "probability"),
            show="headings",
            selectmode="browse",
            height=15
        )

        # configure treeview headings
        self.spell_tree.heading("id", text="Spell ID")
        self.spell_tree.heading("name", text="Spell")
        self.spell_tree.heading("probability", text="Cast %")

        # configure treeview columns
        self.spell_tree.column("id", width=40, anchor="w")
        self.spell_tree.column("name", width=140, anchor="w")
        self.spell_tree.column("probability", width=40, anchor="e")

        # load spell on select
        self.spell_tree.bind("<<TreeviewSelect>>", self.load_selected_spell)

        scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.spell_tree.yview
        )

        self.spell_tree.configure(
            yscrollcommand=scrollbar.set
        )


        self.total_label = tk.Label(self, text="Total cast chance: 0.00%", bg=st.base_bg, font=st.norm_font, anchor="w")

        # spell labels and entries
        spell_id_label = tk.Label(self, text="Spell ID", bg=st.base_bg, font=st.norm_font)
        chance_label = tk.Label(self, text="Cast %", bg=st.base_bg, font=st.norm_font)

        self.spell_id_entry = tk.Entry(self, bg=st.entry_bg, font=st.norm_font)
        self.chance_entry = tk.Entry(self, bg=st.entry_bg, font=st.norm_font)

        # layout
        r = 0
        c = 0

        self.info_label.grid(row=r, column=c, columnspan=2, padx=2, pady=5, sticky="ew")
        r += 1
        self.spell_tree.grid(row=r, column=c, columnspan=2, padx=2, pady=2, sticky="nsew")
        scrollbar.grid(row=r, column=c + 2, sticky="ns")
        r += 1
        self.total_label.grid(row=r, column=c, columnspan=2, padx=2, pady=5, sticky="ew")
        r += 1

        spell_id_label.grid(row=r, column=c, padx=2, pady=2, sticky="w")
        chance_label.grid(row=r, column=c + 1, padx=2, pady=2, sticky="w")
        r += 1
        self.spell_id_entry.grid(row=r, column=c, padx=2, pady=2, sticky="ew")
        self.chance_entry.grid(row=r, column=c + 1, padx=2, pady=2, sticky="ew")
        r += 1
        add_update_button.grid(row=r, column=c, padx=2, pady=2, sticky="ew")
        find_label.grid(row=r, column=c + 1, padx=2, pady=2, sticky="w")
        r += 1
        delete_button.grid(row=r, column=c, padx=2, pady=2, sticky="ew")
        self.find_entry.grid(row=r, column=c + 1, padx=2, pady=5, sticky="ew")
        r += 1
        set_button.grid(row=r, column=c, padx=2, pady=2, sticky="ew")
        find_button.grid(row=r, column=c + 1, padx=2, pady=5, sticky="ew")
        r += 1
        upgrade_button.grid(row=r, column=c, padx=2, pady=2, sticky="ew")
        batch_button.grid(row=r, column=c + 1, padx=2, pady=2, sticky="ew")

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)


    def find_spell(self):
        search_text = self.find_entry.get().strip().lower()

        if search_text == "":
            self.cont.view.console.print("Enter a spell name to search for.\n")
            return

        matches = []

        for spell_name, spell_id in self.spell_dict.items():
            if search_text in spell_name.lower():
                matches.append((spell_id, spell_name))

        if not matches:
            self.cont.view.console.print("No matching spells found.\n")
            return

        self.cont.view.console.print("\nMatching spells:\n")

        for spell_id, spell_name in matches:
            self.cont.view.console.print(f"{spell_id}\t{spell_name}\n")


    def clear_spell_tree(self):
        for item in self.spell_tree.get_children():
            self.spell_tree.delete(item)


    def refresh_spell_tree(self):
        self.clear_spell_tree()

        total = 0

        for spell in self.current_spells:
            self.spell_tree.insert(
                "",
                "end",
                values=(spell["id"], spell["short_name"], f'{spell["chance"]:.2f}%')
            )

            total += spell["chance"]

        self.total_label.config(text=f"Total cast chance: {total:.2f}%")


    def check_spells(self):
        if self.cont.sql_data is None:
            self.cont.file_warning()
            return

        wcid = file_helper.get_wcid(self.cont.sql_data)
        name = file_helper.get_name(self.cont.sql_data)
        self.info_label.config(text=f"{wcid} {name}")

        spells = spells_module.get_spellbook(self.cont.sql_data)

        self.current_spells = []

        if spells:
            stored = []

            for spell in spells:
                stored.append(spell.pr)

            independent = spells_module.spellbook_stored_to_independent_percents(stored)

            for spell, pct in zip(spells, independent):
                self.current_spells.append({
                    "id": spell.id,
                    "name": spell.name,
                    "short_name": spell.short_name,
                    "chance": pct
                })

        self.refresh_spell_tree()

        if not spells:
            self.total_label.config(text="No spells found.")


    def load_selected_spell(self, _event=None):
        selected = self.spell_tree.selection()

        if not selected:
            return

        item = selected[0]
        values = self.spell_tree.item(item, "values")

        spell_id = values[0]
        chance = values[2].replace("%", "")

        self.spell_id_entry.delete(0, tk.END)
        self.spell_id_entry.insert(0, spell_id)

        self.chance_entry.delete(0, tk.END)
        self.chance_entry.insert(0, chance)


    def add_or_update_spell(self):
        spell_id_text = self.spell_id_entry.get().strip()
        chance_text = self.chance_entry.get().strip().replace("%", "")

        if spell_id_text == "" or chance_text == "":
            self.cont.view.console.print("Enter a spell ID and chance.\n")
            return

        try:
            spell_id = int(spell_id_text)
            chance = float(chance_text)
        except ValueError:
            self.cont.view.console.print("Spell ID must be an integer and chance must be a number.\n")
            return

        if chance < 0 or chance > 100:
            self.cont.view.console.print("Chance must be between 0 and 100.\n")
            return

        spell_name = self.id_to_spell.get(spell_id, "Unknown Spell")
        new_spell = spells_module.Spell(spell_id, 2.0, spell_name)

        found = False

        for spell in self.current_spells:
            if spell["id"] == spell_id:
                spell["name"] = new_spell.name
                spell["short_name"] = new_spell.short_name
                spell["chance"] = chance
                found = True

        if not found:
            self.current_spells.append({
                "id": new_spell.id,
                "name": new_spell.name,
                "short_name": new_spell.short_name,
                "chance": chance
            })

        self.refresh_spell_tree()

        self.spell_id_entry.delete(0, tk.END)
        self.chance_entry.delete(0, tk.END)


    def delete_selected_spell(self):
        selected = self.spell_tree.selection()

        if not selected:
            self.cont.view.console.print("Select a spell to delete.\n")
            return

        item = selected[0]
        values = self.spell_tree.item(item, "values")
        spell_id = int(values[0])

        new_spells = []

        for spell in self.current_spells:
            if spell["id"] != spell_id:
                new_spells.append(spell)

        self.current_spells = new_spells
        self.refresh_spell_tree()

        self.spell_id_entry.delete(0, tk.END)
        self.chance_entry.delete(0, tk.END)


    def save_spellbook(self):
        if self.cont.sql_data is None:
            self.cont.file_warning()
            return

        wcid = file_helper.get_wcid(self.cont.sql_data)

        independent = []

        for spell in self.current_spells:
            independent.append(spell["chance"])

        stored = spells_module.independent_percents_to_spellbook_stored(independent)

        spells = []

        for spell_data, stored_pr in zip(self.current_spells, stored):
            spells.append(
                spells_module.Spell(
                    spell_data["id"],
                    stored_pr,
                    spell_data["name"]
                )
            )

        new_command = spells_module.make_spellbook(wcid, spells)

        my_list = []

        for command in self.cont.sql_data:
            if "`weenie_properties_spell_book`" not in command:
                if command.strip() != "":
                    my_list.append(command)

        if self.current_spells:
            my_list.append(new_command)

        self.cont.sql_data = my_list

        self.cont.view.console.print("Spellbook saved.\n")
        self.check_spells()


    def upgrade_spells(self):
        if self.cont.sql_data is None:
            self.cont.file_warning()
            return

        wcid = file_helper.get_wcid(self.cont.sql_data)
        name = file_helper.get_name(self.cont.sql_data)
        spells = spells_module.get_spellbook(self.cont.sql_data)

        if spells:
            upgraded = []

            for spell in spells:
                upgraded.append(
                    spells_module.upgrade_spell(
                        spell,
                        self.spell_dict,
                        self.special_names,
                        self.flipped_names
                    )
                )

            new_command = spells_module.make_spellbook(wcid, upgraded)

            my_list = []

            for command in self.cont.sql_data:
                if "`weenie_properties_spell_book`" not in command:
                    if command.strip() != "":
                        my_list.append(command)

            my_list.append(new_command)
            self.cont.sql_data = my_list

            self.cont.view.console.print(
                "\nSpells for " + str(wcid) + "\t" + name + " upgraded.\n"
            )

            self.check_spells()
