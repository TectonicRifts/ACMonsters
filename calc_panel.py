import math
import tkinter as tk

import profiler as pf
import settings as st
import skills_module
import stat_helper
import view_helper as vh


class CalcPanel(tk.Frame):

    def __init__(self, parent, cont):
        super().__init__(parent, bg=st.base_bg)
        self.cont = cont
        self.canvas = None

        norm_font = st.norm_font

        skill_check_header = tk.Label(self, text="Skill Calculator", font=norm_font, fg="#221CD9", bg=st.base_bg)

        skill_check_labels = ["player skill", "skill modifier", "monster skill"]
        self.skill_check_entries = vh.make_float_entry(self, skill_check_labels)

        check_skill_button = tk.Button(self, text="Check Skill", command=self.check_skill)
        plot_player_button = tk.Button(self, text="Plot Player Range", command=self.plot_player_perspective)
        plot_monster_button = tk.Button(self, text="Plot Monster Range", command=self.plot_monster_perspective)

        # layout
        r = 0
        c = 0

        skill_check_header.grid(row=r, column=c, sticky="w")
        r += 1

        for name, entry in self.skill_check_entries.items():
            label = tk.Label(self, text=name, font=norm_font, bg=st.base_bg)
            label.grid(row=r, column=c, sticky="e", padx=2)
            entry.grid(row=r, column=c + 1, sticky="ew", padx=2)
            r += 1

        check_skill_button.grid(row=r, column=c, columnspan=2, padx=2, pady=5, sticky="ew")
        r += 1
        plot_player_button.grid(row=r, column=c, columnspan=1, padx=2, pady=5, sticky="ew")
        r += 1
        plot_monster_button.grid(row=r, column=c, columnspan=1, padx=2, pady=5, sticky="ew")
        r += 1

        self.plot_frame = tk.Frame(self, bg=st.base_bg)
        self.plot_frame.grid(row=r, column=c, columnspan=2, sticky="nsew", padx=2, pady=2)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(r, weight=1)

        self._init_plot()

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)


    def _print(self, text, color=None):
        if color is None:
            self.cont.view.console.print(text)
        else:
            self.cont.view.console.print(text, color)

    def _get_entry_value(self, key, required_message=None, as_int=False, as_float=False):
        raw = self.skill_check_entries.get(key).get().strip()

        if raw == "":
            if required_message:
                self._print(required_message + "\n")
            return None

        try:
            if as_int:
                return int(float(raw))
            if as_float:
                return float(raw)
            return raw
        except ValueError:
            self._print(f"Invalid value for {key}.\n")
            return None

    @staticmethod
    def _calc_success_percent(player_skill, monster_skill):
        y = 1 - 1 / (1 + math.exp(0.03 * (player_skill - monster_skill)))
        return round(y * 100, 2)

    def _clear_plot(self):
        if self.canvas is not None:
            self.canvas.delete("all")

    def _init_plot(self):
        self.plot_width = 360
        self.plot_height = 300

        # margins for labels/axes
        self.left_pad = 45
        self.right_pad = 15
        self.top_pad = 25
        self.bottom_pad = 40

        self.canvas = tk.Canvas(
            self.plot_frame,
            width=self.plot_width,
            height=self.plot_height,
            bg="white",
            highlightthickness=1,
            highlightbackground="gray"
        )
        self.canvas.grid(row=0, column=0)

        self.plot_frame.grid_rowconfigure(0, weight=1)
        self.plot_frame.grid_columnconfigure(0, weight=1)

        self._draw_blank_plot("Skill Comparison", "Monster Skill")


    def check_skill(self):
        player_skill = self._get_entry_value(
            "player skill",
            "Enter a value for player skill.",
            as_int=True
        )
        player_mod = self._get_entry_value(
            "skill modifier",
            "Enter a value for player skill modifier.",
            as_float=True
        )
        monster_skill = self._get_entry_value(
            "monster skill",
            "Enter a value for monster skill.",
            as_int=True
        )

        if player_skill is None or player_mod is None or monster_skill is None:
            return

        result = pf.calc_skill(player_skill, player_mod, monster_skill)
        self._print(f"player skill\t{player_skill}\tsuccess\t{result}\n")


    def profile_player(self, player_profile):

        if self.cont.sql_data is None:
            return

        self._print(f"\n{player_profile.name} Player Profile (% chance)\n", "purple")

        output = {
            "land magic": "NA",
            "land melee": "NA",
            "land missile": "NA",
            "resist magic": "NA",
            "evade melee": "NA",
        }

        attributes = stat_helper.get_all_attributes(self.cont.sql_data)
        skills = skills_module.get_skill_table(self.cont.sql_data)

        found_war_or_void = False

        for skill in skills:
            attribute_bonus = skills_module.get_attribute_bonus(attributes, skill.name)
            effective_value = skill.value + attribute_bonus

            if skill.name == "MagicDefense":
                output["land magic"] = pf.calc_skill(player_profile.magic_a, 1, effective_value)

            elif skill.name == "MeleeDefense":
                output["land melee"] = pf.calc_skill(player_profile.melee_a, 1.35, effective_value)

            elif skill.name == "MissileDefense":
                output["land missile"] = pf.calc_skill(player_profile.missile_a, 1.6, effective_value)

            elif skill.name in ("HeavyWeapons", "LightWeapons", "FinesseWeapons", "TwoHandedCombat"):
                if effective_value > 0:
                    output["evade melee"] = pf.calc_skill(player_profile.melee_d, player_profile.melee_d_mod, effective_value)

            elif skill.name in ("WarMagic", "VoidMagic"):
                output["resist magic"] = pf.calc_skill(player_profile.magic_d, 1, effective_value)
                found_war_or_void = True

            elif skill.name == "LifeMagic" and not found_war_or_void:
                output["resist magic"] = pf.calc_skill(player_profile.magic_d, 1, effective_value)

        for key, value in output.items():
            if value != "NA" and value < 10:
                self._print(f"{key}: {value}\n", "red")
            else:
                self._print(f"{key}: {value}\n")


    def _draw_blank_plot(self, title, x_label):
        self._clear_plot()

        x0 = self.left_pad
        y0 = self.plot_height - self.bottom_pad
        x1 = self.plot_width - self.right_pad
        y1 = self.top_pad

        # title
        self.canvas.create_text(
            self.plot_width / 2,
            12,
            text=title,
            font=("Arial", 10, "bold")
        )

        # axes
        self.canvas.create_line(x0, y0, x1, y0, width=2)  # x-axis
        self.canvas.create_line(x0, y0, x0, y1, width=2)  # y-axis

        # y-axis ticks and labels
        for val in range(0, 101, 20):
            y = self._scale_y(val)
            self.canvas.create_line(x0 - 5, y, x0, y)
            self.canvas.create_text(x0 - 5, y, text=str(val), anchor="e", font=("Arial", 8))

        # axis labels
        self.canvas.create_text(
            (x0 + x1) / 2,
            self.plot_height - 12,
            text=x_label,
            font=("Arial", 9)
        )

        self.canvas.create_text(
            15,
            (y0 + y1) / 2,
            text="Player Success (%)",
            angle=90,
            font=("Arial", 9)
        )

    def _scale_x(self, value, x_min, x_max):
        x0 = self.left_pad
        x1 = self.plot_width - self.right_pad

        if x_max == x_min:
            return x0

        return x0 + (value - x_min) / (x_max - x_min) * (x1 - x0)

    def _scale_y(self, value):
        y0 = self.plot_height - self.bottom_pad
        y1 = self.top_pad

        return y0 - (value / 100) * (y0 - y1)

    def _draw_plot(self, x_values, y_values, title, x_label):
        self._draw_blank_plot(title, x_label)

        if not x_values or not y_values:
            return

        x_min = min(x_values)
        x_max = max(x_values)

        # x-axis ticks
        tick_count = 5
        if x_max == x_min:
            ticks = [x_min]
        else:
            step = max(10, ((x_max - x_min) // tick_count // 10) * 10)
            if step == 0:
                step = 10
            ticks = list(range(int(x_min), int(x_max) + 1, step))

        for tick in ticks:
            x = self._scale_x(tick, x_min, x_max)
            y0 = self.plot_height - self.bottom_pad
            self.canvas.create_line(x, y0, x, y0 + 5)
            self.canvas.create_text(x, y0 + 5, text=str(tick), anchor="n", font=("Arial", 8))

        # build line points
        points = []
        for x_val, y_val in zip(x_values, y_values):
            px = self._scale_x(x_val, x_min, x_max)
            py = self._scale_y(y_val)
            points.extend([px, py])

        if len(points) >= 4:
            self.canvas.create_line(points, width=2, fill="blue", smooth=False)

        # optional: draw small points
        for x_val, y_val in zip(x_values, y_values):
            px = self._scale_x(x_val, x_min, x_max)
            py = self._scale_y(y_val)
            self.canvas.create_oval(px - 2, py - 2, px + 2, py + 2, fill="blue", outline="blue")

    def plot_monster_perspective(self):

        player_skill = self._get_entry_value(
            "player skill",
            "Enter a value for player skill.",
            as_int=True
        )
        player_mod = self._get_entry_value(
            "skill modifier",
            "Enter a value for player skill modifier.",
            as_float=True
        )

        if player_skill is None or player_mod is None:
            return

        player_skill = player_skill * player_mod

        monster_skills = []
        success_values = []

        for ms in range(0, 1010, 10):
            success = self._calc_success_percent(player_skill, ms)

            if success < 98:
                monster_skills.append(ms)
                success_values.append(success)

            if success < 2:
                break

        self._draw_plot(
            monster_skills,
            success_values,
            title=f"Player Skill = {int(player_skill)}",
            x_label="Monster Skill"
        )

    def plot_player_perspective(self):

        monster_skill = self._get_entry_value(
            "monster skill",
            "Enter a value for monster skill.",
            as_int=True
        )
        if monster_skill is None:
            return

        player_skills = []
        success_values = []

        for ps in range(0, 1010, 10):
            success = self._calc_success_percent(ps, monster_skill)

            if success > 2:
                player_skills.append(ps)
                success_values.append(success)

            if success > 98:
                break

        self._draw_plot(
            player_skills,
            success_values,
            title=f"Monster Skill = {monster_skill}",
            x_label="Player Skill"
        )

