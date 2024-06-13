import math
import tkinter as tk
import view_helper as vh
import settings as st
import profiler as pf
import stat_helper
import skills_module


class CalcPanel:

    def __init__(self, parent, cont):
        self.frame = tk.Frame(parent, bg=st.base_bg)
        self.cont = cont

        norm_font = st.norm_font

        skill_check_header = tk.Label(self.frame, text="Skill Calculator", font=norm_font, fg='#221CD9', bg=st.base_bg)
        skill_check_labels = ['player skill', 'skill modifier', 'monster skill']
        self.skill_check_entries = vh.make_float_entry(self.frame, skill_check_labels)

        tooltip = ("All fields required. "
                   "Use a skill mod of 1.6 for missile at full accuracy. "
                   "Use a mod of 1.35 for melee since 35% is the average weapon attack mod. "
                   "Level 200 combat pet attack skill is 693 with a mod of 1. Level 180 pet skill is 653."
                   )

        tooltip_label = tk.Label(self.frame, text=tooltip, font=norm_font, fg="dark green", wraplength=420,
                                 justify=tk.LEFT, bg=st.base_bg)

        check_skill_button = tk.Button(self.frame, text="Check Skill", command=self.check_skill)
        check_range_button = tk.Button(self.frame, text="Check Range", command=self.check_range)

        # layout
        r = 0
        c = 0

        skill_check_header.grid(row=r, column=c, sticky='w')
        r += 1

        for name, entry in self.skill_check_entries.items():
            label = tk.Label(self.frame, text=name, font=norm_font, bg=st.base_bg)
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

    def profile_player(self, label, pmagic_att, pmelee_att, pmissile_att, pmelee_def, pmagic_def, pmelee_def_mod):

        # for max, use 561, 607, 556, 580, 417, 1.55
        # for 150, use 435, 482, 430, 460, 322, 1.45

        if self.cont.sql_commands is not None:

            label = "\n" + label + " Player Profile (% chance)\n"
            self.cont.view.console.print(label, "purple")

            output = {
                "land magic": "NA",
                "land melee": "NA",
                "land missile": "NA",
                "resist magic": "NA",
                "evade melee": "NA",
                # "evade missile": "NA"
            }

            attributes = stat_helper.get_all_attributes(self.cont.sql_commands)
            skills = skills_module.get_skill_table(self.cont.sql_commands)
            for skill in skills:
                attribute_bonus = skills_module.get_attribute_bonus(attributes, skill.name)
                effective_value = skill.value + attribute_bonus

                if skill.name == "MagicDefense":  # this is on the mob
                    result = pf.calc_skill(pmagic_att, 1, effective_value)
                    output["land magic"] = result

                if skill.name == "MeleeDefense":
                    pmelee_att_mod = 1.35
                    result = pf.calc_skill(pmelee_att, pmelee_att_mod, effective_value)
                    output["land melee"] = result

                if skill.name == "MissileDefense":
                    pmissile_att_mod = 1.6  # for full accuracy
                    result = pf.calc_skill(pmissile_att, pmissile_att_mod, effective_value)
                    output["land missile"] = result

                if skill.name == "HeavyWeapons" or skill.name == "LightWeapons" or skill.name == "FinesseWeapons" or skill.name == "TwoHandedCombat":
                    if effective_value > 0:
                        result = pf.calc_skill(pmelee_def, pmelee_def_mod, effective_value)
                        output["evade melee"] = result

                if skill.name == "WarMagic" or skill.name == "VoidMagic":
                    result = pf.calc_skill(pmagic_def, 1, effective_value)
                    output["resist magic"] = result
                elif skill.name == "LifeMagic":
                    # only use if no war or void magic
                    result = pf.calc_skill(pmagic_def, 1, effective_value)
                    output["resist magic"] = result

            for k, v in output.items():
                if v != "NA" and v < 10:
                    self.cont.view.console.print(k + ": " + str(v) + "\n", "red")
                else:
                    self.cont.view.console.print(k + ": " + str(v) + "\n")
