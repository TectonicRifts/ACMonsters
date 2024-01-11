import tkinter as tk
from functools import partial
import file_helper
import settings as st
import spells_module


class SpellsPanel:

    def __init__(self, parent, cont):
        self.frame = tk.Frame(parent, bg=st.base_bg)
        self.cont = cont

        self.spell_dict = spells_module.load_spell_dict()
        self.special_names = spells_module.load_special_dict()
        self.flipped_names = {v: k for k, v in self.special_names.items()}

        norm_font = st.norm_font

        check_button = tk.Button(self.frame, text="Check", command=self.check_spells)
        upgrade_button = tk.Button(self.frame, text="Upgrade", bg=st.button_bg, command=self.upgrade_spells)
        batch_button = tk.Button(self.frame, text="Run Batch",
                                 command=partial(self.cont.run_sql_batch, self.upgrade_spells))

        tooltip = "Use to upgrade the level of all spells. "

        tooltip_label = tk.Label(self.frame, text=tooltip, font=norm_font, fg="dark green", wraplength=420,
                                 justify=tk.LEFT, bg=st.base_bg)

        # layout
        r = 0
        c = 0

        buttons = [check_button, upgrade_button, batch_button]

        for button in buttons:
            button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
            r += 1

        tooltip_label.grid(row=r, column=c, columnspan=2)
        r += 1

    def check_spells(self):
        if self.cont.sql_commands is not None:
            spells = spells_module.get_spellbook(self.cont.sql_commands)

            for spell in spells:
                self.cont.view.console.print(str(spell.id) + "\t" + spell.name + "\n")

    def upgrade_spells(self):
        if self.cont.sql_commands is not None:
            wcid = file_helper.get_wcid(self.cont.sql_commands)
            spells = spells_module.get_spellbook(self.cont.sql_commands)
            upgraded = []
            for spell in spells:
                upgraded.append(spells_module.upgrade_spell(
                    spell, self.spell_dict, self.special_names, self.flipped_names))

            new_command = spells_module.make_spellbook(wcid, upgraded)

            my_list = []

            # delete if already there
            for command in self.cont.sql_commands:
                if str("`weenie_properties_spell_book`") in command:
                    pass
                else:
                    if command.strip() != "":
                        my_list.append(command)

            my_list.append(new_command)
            self.cont.sql_commands = my_list
