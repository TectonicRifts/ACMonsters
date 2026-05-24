import tkinter as tk
from functools import partial
from tkinter import scrolledtext

import file_helper
import settings as st
import spells_module


class SpellsPanel(tk.Frame):

    def __init__(self, parent, cont):
        super().__init__(parent, bg=st.base_bg)
        self.cont = cont

        self.spell_dict = spells_module.load_spell_dict()
        self.special_names = spells_module.load_special_dict()
        self.flipped_names = {v: k for k, v in self.special_names.items()}

        norm_font = st.norm_font

        check_button = tk.Button(self, text="Check", command=self.check_spells)
        upgrade_button = tk.Button(self, text="Upgrade", bg=st.button_bg, command=self.upgrade_spells)
        batch_button = tk.Button(self, text="Run Batch",
                                 command=partial(self.cont.run_sql_batch, self.upgrade_spells))

        # read-only spell display
        self.spell_text = scrolledtext.ScrolledText(
            self,
            width=20,
            height=15,
            wrap=tk.WORD,
            font=norm_font,
            bg=st.entry_bg
        )
        self.spell_text.config(state="disabled")

        # layout
        r = 0
        c = 0

        buttons = [check_button, upgrade_button, batch_button]

        for button in buttons:
            button.grid(row=r, column=c, padx=2, pady=5, sticky="ew")
            r += 1

        self.spell_text.grid(row=r, column=c, columnspan=2, padx=2, pady=2, sticky="nsew")

        self.grid_rowconfigure(r, weight=1)
        self.grid_columnconfigure(c, weight=1)


    def show_spell_text(self, text: str):
        """Replace the spell display contents."""
        self.spell_text.config(state="normal")
        self.spell_text.delete("1.0", tk.END)
        self.spell_text.insert(tk.END, text)
        self.spell_text.config(state="disabled")


    def check_spells(self):
        if self.cont.sql_data is not None:
            wcid = file_helper.get_wcid(self.cont.sql_data)
            name = file_helper.get_name(self.cont.sql_data)
            # self.cont.view.console.print("\n" + str(wcid) + "\t" + name + "\n\n")
            spells = spells_module.get_spellbook(self.cont.sql_data)
            lines = [f"{wcid} {name}", ""]

            stored = []
            if spells:
                for spell in spells:
                    stored.append(spell.pr)

                independent = spells_module.spellbook_stored_to_independent_percents(stored)

                for spell, pct in zip(spells, independent):
                    lines.append(f"{spell.id} {spell.short_name} ({pct:.2f}%)")

                total_pct = sum(independent)
                lines.append("")
                lines.append(f"Total cast chance: {total_pct:.2f}%")
            else:
                lines.append("No spells found.")

            display_text = "\n".join(lines)
            self.show_spell_text(display_text)

        else:
            self.cont.file_warning()


    def upgrade_spells(self):
        if self.cont.sql_data is not None:
            wcid = file_helper.get_wcid(self.cont.sql_data)
            name = file_helper.get_name(self.cont.sql_data)
            spells = spells_module.get_spellbook(self.cont.sql_data)
            if spells:
                upgraded = []
                for spell in spells:
                    upgraded.append(spells_module.upgrade_spell(
                        spell, self.spell_dict, self.special_names, self.flipped_names))

                new_command = spells_module.make_spellbook(wcid, upgraded)

                my_list = []

                # delete if already there
                for command in self.cont.sql_data:
                    if str("`weenie_properties_spell_book`") in command:
                        pass
                    else:
                        if command.strip() != "":
                            my_list.append(command)

                my_list.append(new_command)
                self.cont.sql_data = my_list

                self.cont.view.console.print("\nSpells for " + str(wcid) + "\t" + name + " upgraded.\n")


    def show_help(self):
        help_text = [
            ("title", "Spell Help\n\n"),
            ("body", "Use to upgrade the level of all spells.\n\n")
        ]

        self.cont.view.console.show_help(help_text)

