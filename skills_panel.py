import tkinter as tk
from functools import partial
import tkinter.messagebox
import file_helper
import settings as st
import view_helper as vh
import stat_helper
import skills_module


class SkillsPanel:

    def __init__(self, parent, cont):
        self.frame = tk.Frame(parent)
        self.cont = cont

        norm_font = st.norm_font

        melee_header = tk.Label(self.frame, text="Melee", font=norm_font, fg='blue')
        magic_header = tk.Label(self.frame, text="Magic", font=norm_font, fg='blue')
        defensive_header = tk.Label(self.frame, text="Defense", font=norm_font, fg='blue')
        other_header = tk.Label(self.frame, text="Other", font=norm_font, fg='blue')

        offensive_labels = ['heavy weapons', 'light weapons', 'finesse weapons', 'two handed combat', 'missile weapons']
        magic_labels = ['war magic', 'life magic', 'creature enchantment', 'item enchantment', 'void magic']
        defensive_labels = ['melee defense', 'missile defense', 'magic defense']
        other_labels = ['sneak attack', 'dirty fighting', 'dual wield', 'deception', 'shield']

        self.offensive_entries = vh.make_int_entry(self.frame, offensive_labels)
        self.magic_entries = vh.make_int_entry(self.frame, magic_labels)
        self.defensive_entries = vh.make_int_entry(self.frame, defensive_labels)
        self.other_entries = vh.make_int_entry(self.frame, other_labels)

        self.all_entries = {
            **self.offensive_entries, **self.magic_entries, **self.defensive_entries, **self.other_entries
        }

        check_attributes_button = tk.Button(self.frame, text="Check", command=self.check_parameters)
        set_button = tk.Button(self.frame, text="Set", bg="lightblue", command=self.set_skills)
        batch_button = tk.Button(self.frame, text="Run Batch",
                                 command=partial(self.cont.run_sql_batch, self.set_skills))

        tooltip = ("All fields optional. Set attributes first and enter desired skill levels. "
                   "Entire skill table is replaced so anything left blank will be deleted. "
                   )

        tooltip_label = tk.Label(self.frame, text=tooltip, font=norm_font, fg="dark green", wraplength=420,
                                 justify=tk.LEFT)

        # layout
        r = 0
        c = 0

        headers = [melee_header, magic_header, defensive_header, other_header]
        content = [self.offensive_entries, self.magic_entries, self.defensive_entries, self.other_entries]
        buttons = [check_attributes_button, set_button, batch_button]

        for i in range(len(headers)):

            headers[i].grid(row=r, column=c, sticky='w')
            r += 1

            for name, entry in content[i].items():
                label = tk.Label(self.frame, text=name, font=norm_font)
                label.grid(row=r, column=c)
                entry.grid(row=r, column=c + 1)
                r += 1

        for button in buttons:
            button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
            r += 1

        tooltip_label.grid(row=r, column=c, columnspan=2)
        r += 1

    def check_parameters(self):
        """Check attributes, base, effective, and pcap skills."""
        if self.cont.sql_commands is not None:

            # clear existing
            for name, entry in self.all_entries.items():
                entry.delete(0, tk.END)  # delete existing

            attributes = stat_helper.get_all_attributes(self.cont.sql_commands)
            skills = skills_module.get_skill_table(self.cont.sql_commands)

            self.cont.view.console.print("\nCurrent Effective Skills\n", "purple")
            for skill in skills:
                attribute_bonus = skills_module.get_attribute_bonus(attributes, skill.name)
                effective_value = skill.value + attribute_bonus

                self.cont.view.console.print(skill.name + "\t" + str(effective_value) + "\n")

                for name, entry in self.all_entries.items():
                    name = name.title().replace(" ", "")
                    if name == skill.name:
                        entry.insert(0, str(effective_value))  # insert new

            self.cont.view.console.print("\nPCAP Effective Skills (mean [min, max])\n", "purple")
            pcap_skills = self.get_skill_pcap()
            for name, v in pcap_skills.items():
                if "defense" in name:
                    self.cont.view.console.print(
                        str(name) + "\t" + str(v[0]) + " [" + str(v[1]) + ", " + str(v[2]) + "]\n", "brown"
                    )
                else:
                    self.cont.view.console.print(
                        str(name) + "\t" + str(v[0]) + " [" + str(v[1]) + ", " + str(v[2]) + "]\n")

    def get_skill_pcap(self):
        if self.cont.sql_commands is not None:
            name = file_helper.get_name(self.cont.sql_commands)
            pcap_skills = skills_module.skill_look_up(name)
            return pcap_skills

    def set_skills(self):

        if self.cont.sql_commands is not None:

            wcid = file_helper.get_wcid(self.cont.sql_commands)
            attributes = stat_helper.get_all_attributes(self.cont.sql_commands)

            skills = {}

            # magic skills
            for k, v in self.magic_entries.items():

                val = v.get()
                if val != "":
                    val_int = int(val)

                    attribute_bonus = round((attributes['focus'] + attributes['self']) / 4)
                    val_int = val_int - attribute_bonus

                    skill_name = k.title().replace(" ", "")
                    skills[skill_name] = val_int

            # melee skills
            for k, v in self.offensive_entries.items():

                val = v.get()
                if val != "":
                    val_int = int(val)

                    attribute_bonus = 0

                    if k == 'heavy weapons' or k == 'light weapons' or k == 'two handed combat':
                        attribute_bonus = round((attributes['strength'] + attributes['coordination']) / 3)
                    elif k == 'finesse weapons':
                        attribute_bonus = round((attributes['coordination'] + attributes['quickness']) / 3)
                    elif k == 'missile weapons':
                        attribute_bonus = round(attributes['coordination'] / 2)
                    else:
                        tk.messagebox.showerror("Error", "A skill label was undefined.")

                    val_int = val_int - attribute_bonus

                    skill_name = k.title().replace(" ", "")
                    skills[skill_name] = val_int

            # defenses
            for k, v in self.defensive_entries.items():

                val = v.get()
                if val != "":
                    val_int = int(val)

                    attribute_bonus = 0

                    if k == 'magic defense':
                        attribute_bonus = round((attributes['focus'] + attributes['self']) / 7)
                    elif k == 'melee defense':
                        attribute_bonus = round((attributes['coordination'] + attributes['quickness']) / 3)
                    elif k == 'missile defense':
                        attribute_bonus = round((attributes['coordination'] + attributes['quickness']) / 5)
                    else:
                        tk.messagebox.showerror("Error", "A skill label was undefined.")

                    val_int = val_int - attribute_bonus

                    skill_name = k.title().replace(" ", "")
                    skills[skill_name] = val_int

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
