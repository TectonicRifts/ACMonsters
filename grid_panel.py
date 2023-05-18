import tkinter as tk

import file_helper
import settings as st
import skills_module
import stat_helper
import view_helper as vh


class GridPanel:

    def __init__(self, parent, cont):
        self.frame = tk.Frame(parent, bg=st.base_bg)
        self.cont = cont
        self.all_panels = []
        self.mini_panels = []

        mp1 = MiniPanel(self.frame, self.cont)
        mp2 = MiniPanel(self.frame, self.cont)
        mp3 = MiniPanel(self.frame, self.cont)
        mp4 = MiniPanel(self.frame, self.cont)

        self.mini_panels.append(mp1)
        self.mini_panels.append(mp2)
        self.mini_panels.append(mp3)
        self.mini_panels.append(mp4)

        self.all_panels.append(LabelPanel(self.frame, self.cont))
        self.all_panels.append(mp1)
        self.all_panels.append(mp2)
        self.all_panels.append(LabelPanel(self.frame, self.cont))
        self.all_panels.append(mp3)
        self.all_panels.append(mp4)

        # layout
        r = 0
        c = 0
        for panel in self.all_panels:
            panel.frame.grid(row=r, column=c, padx=5, pady=5)
            c += 1
            if c == 3:
                c = 0
                r += 1

    def show_file(self, counter):
        self.mini_panels[counter].show_parameters()

    def clear(self):
        for panel in self.mini_panels:
            panel.clear()


class LabelPanel:

    def __init__(self, parent, cont):
        self.frame = tk.Frame(parent, bg=st.base_bg)
        self.cont = cont

        norm_font = st.norm_font

        offensive_labels = ['heavy weapons', 'light weapons', 'finesse weapons', 'two handed combat', 'missile weapons']
        magic_labels = ['war magic', 'life magic', 'creature enchantment', 'void magic']
        defensive_labels = ['melee defense', 'missile defense', 'magic defense']

        # layout
        r = 0
        c = 0

        label1 = tk.Label(self.frame, text="wcid", font=norm_font, fg='blue', bg=st.base_bg)
        label1.grid(row=r, column=c)
        r += 1

        label2 = tk.Label(self.frame, text="name", font=norm_font, fg='blue', bg=st.base_bg)
        label2.grid(row=r, column=c)
        r += 1

        for name in offensive_labels:
            if name == "missile weapons":
                label = tk.Label(self.frame, text=name, font=norm_font, fg='brown', bg=st.base_bg)
            else:
                label = tk.Label(self.frame, text=name, font=norm_font, bg=st.base_bg)
            label.grid(row=r, column=c)
            r += 1

        for name in magic_labels:
            label = tk.Label(self.frame, text=name, font=norm_font, fg='purple', bg=st.base_bg)
            label.grid(row=r, column=c)
            r += 1

        for name in defensive_labels:
            label = tk.Label(self.frame, text=name, font=norm_font, fg='darkgreen', bg=st.base_bg)
            label.grid(row=r, column=c)
            r += 1


class MiniPanel:

    def __init__(self, parent, cont):
        self.frame = tk.Frame(parent, bg=st.base_bg)
        self.cont = cont

        offensive_labels = ['heavy weapons', 'light weapons', 'finesse weapons', 'two handed combat', 'missile weapons']
        magic_labels = ['war magic', 'life magic', 'creature enchantment', 'void magic']
        defensive_labels = ['melee defense', 'missile defense', 'magic defense']

        self.wcid_entry = tk.Entry(self.frame, bg=st.entry_bg, font="Arial 12")
        self.name_entry = tk.Entry(self.frame, bg=st.entry_bg, font="Arial 12")

        self.offensive_entries = vh.make_int_entry(self.frame, offensive_labels)
        self.magic_entries = vh.make_int_entry(self.frame, magic_labels)
        self.defensive_entries = vh.make_int_entry(self.frame, defensive_labels)

        self.all_entries = {
            **self.offensive_entries, **self.magic_entries, **self.defensive_entries
        }

        # layout
        r = 0
        c = 0

        self.wcid_entry.configure(width=st.entry_width)
        self.wcid_entry.grid(row=r, column=c + 1, padx=0, pady=1)
        r += 1

        self.name_entry.configure(width=st.entry_width)
        self.name_entry.grid(row=r, column=c + 1, padx=0, pady=1)
        r += 1

        for name, entry in self.offensive_entries.items():
            entry.configure(width=st.entry_width)
            entry.grid(row=r, column=c + 1, padx=0, pady=1)
            r += 1

        for name, entry in self.magic_entries.items():
            entry.configure(width=st.entry_width)
            entry.grid(row=r, column=c + 1, padx=0, pady=1)
            r += 1

        for name, entry in self.defensive_entries.items():
            entry.configure(width=st.entry_width)
            entry.grid(row=r, column=c + 1, padx=0, pady=1)
            r += 1

    def clear(self):
        self.wcid_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        for name, entry in self.all_entries.items():
            entry.delete(0, tk.END)  # delete existing

    def show_parameters(self):
        # clear existing
        if self.cont.sql_commands is not None:
            for name, entry in self.all_entries.items():
                entry.delete(0, tk.END)  # delete existing

            mob_name = file_helper.get_name(self.cont.sql_commands)
            mob_wcid = file_helper.get_wcid(self.cont.sql_commands)

            self.wcid_entry.delete(0, tk.END)
            self.wcid_entry.insert(0, str(mob_wcid))

            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, str(mob_name))

            attributes = stat_helper.get_all_attributes(self.cont.sql_commands)
            skills = skills_module.get_skill_table(self.cont.sql_commands)
            for skill in skills:
                attribute_bonus = skills_module.get_attribute_bonus(attributes, skill.name)
                effective_value = skill.value + attribute_bonus

                for name, entry in self.all_entries.items():
                    name = name.title().replace(" ", "")
                    if name == skill.name:
                        entry.insert(0, str(effective_value))
