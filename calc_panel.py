import math
import tkinter as tk
import view_helper as vh
import settings as st
import profiler as pf
import stat_helper
import skills_module


class CalcPanel:

    def __init__(self, parent, cont):
        self.frame = tk.Frame(parent)
        self.cont = cont

        norm_font = st.norm_font

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
        max_profile_button = tk.Button(self.frame, text="Max Profile", command=self.max_player)

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
        max_profile_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        r += 1
        tooltip_label.grid(row=r, column=c, columnspan=2)
        r += 1

    def check_skill(self):

        # mod of 1.6 for missile at full accuracy, mod of 1.35 for melee (since 35% is average weapon attack mod)
        player_skill = self.skill_check_entries.get("player skill").get().strip()
        skill_modifier = self.skill_check_entries.get("skill modifier").get().strip()
        monster_skill = self.skill_check_entries.get("monster skill").get().strip()

        if player_skill != "" and skill_modifier != "" and monster_skill != "":

            result = pf.calc_skill(player_skill, skill_modifier, monster_skill)
            self.cont.view.console.print("player skill\t" + str(player_skill) + "\tsuccess\t"
                                         + str(result) + "\n")
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

    def max_player(self):

        if self.cont.sql_commands is not None:

            self.cont.view.console.print("\nMax Player Profile (% chance)\n", "purple")

            attributes = stat_helper.get_all_attributes(self.cont.sql_commands)
            skills = skills_module.get_skill_table(self.cont.sql_commands)
            for skill in skills:
                attribute_bonus = skills_module.get_attribute_bonus(attributes, skill.name)
                effective_value = skill.value + attribute_bonus

                if skill.name == "MagicDefense":  # this is on the mob
                    player_skill = 561
                    result = pf.calc_skill(player_skill, 1, effective_value)
                    self.cont.view.console.print(
                        "magic attack of " + str(player_skill) +
                        " lands:\n" +
                        str(result) + "\n"
                    )
                    if result < 10:
                        self.cont.view.console.print("Warning! Less than 10% chance to land.\n", "red")

                if skill.name == "MeleeDefense":
                    player_skill = 607
                    result = pf.calc_skill(player_skill, 1.35, effective_value)
                    self.cont.view.console.print(
                        "melee attack of " + str(player_skill) +
                        " with +35% to attack hits:\n" +
                        str(result) + "\n"
                    )
                    if result < 10:
                        self.cont.view.console.print("Warning! Less than 10% chance to hit.\n", "red")

                if skill.name == "MissileDefense":
                    player_skill = 556
                    result = pf.calc_skill(player_skill, 1.35, effective_value)
                    self.cont.view.console.print(
                        "missile attack of " + str(player_skill) +
                        " at full accuracy hits:\n" +
                        str(result) + "\n"
                    )
                    if result < 10:
                        self.cont.view.console.print("Warning! Less than 10% chance to hit.\n", "red")
