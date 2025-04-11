from tkinter import ttk

import view_helper as vh
import sql_helper as sh
import settings as st
import tkinter as tk


class MiscPanel:

    def __init__(self, parent, cont):
        self.frame = tk.Frame(parent, bg=st.base_bg)
        self.cont = cont

        norm_font = st.norm_font

        # quest
        quest_header_label = tk.Label(self.frame, text="Quest", font=norm_font, fg=st.label_text, bg=st.base_bg)
        str_labels = ["quest name", "description", "min delta", "max delta"]
        self.quest_entries = vh.make_str_entry(self.frame, str_labels)

        # kill task
        task_header_label = tk.Label(self.frame, text="Kill Task", font=norm_font, fg=st.label_text, bg=st.base_bg)
        str_labels = ["counter name", "kill total"]
        self.task_entries = vh.make_str_entry(self.frame, str_labels)

        # event
        event_header_label = tk.Label(self.frame, text="Event", font=norm_font, fg=st.label_text, bg=st.base_bg)
        str_labels = ["event name"]
        self.event_entries = vh.make_str_entry(self.frame, str_labels)

        event_state_label = tk.Label(self.frame, text="state", font=norm_font, bg=st.base_bg)
        event_state_options = ["Off", "On"]
        self.event_state_combo = ttk.Combobox(self.frame, values=event_state_options, font=norm_font, state="readonly")
        self.event_state_combo.current(0)

        tooltip = ("If repeatable, min delta is the timer in milliseconds (e.g., 72000), and max delta should be -1. "
                   "For a one time flag, min and max delta should be 0 and 1. "
                   )

        tooltip_label = tk.Label(self.frame, text=tooltip, font=norm_font, fg="dark green", wraplength=420,
                                 justify=tk.LEFT, bg=st.base_bg)

        make_event_button = tk.Button(self.frame, text="Make Event", command=self.make_event)
        make_quest_button = tk.Button(self.frame, text="Make Quest", command=self.make_quest)
        make_task_button = tk.Button(self.frame, text="Make Task", command=self.make_kill_task)

        # layout
        r = 0
        c = 0

        quest_header_label.grid(row=r, column=c)
        r += 1
        for name, entry in self.quest_entries.items():
            label = tk.Label(self.frame, text=name, font=norm_font, bg=st.base_bg)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1
        make_quest_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        r += 1
        tooltip_label.grid(row=r, column=c, columnspan=2, sticky="w")
        r += 1

        task_header_label.grid(row=r, column=c)
        r += 1
        for name, entry in self.task_entries.items():
            label = tk.Label(self.frame, text=name, font=norm_font, bg=st.base_bg)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1
        make_task_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        r += 1

        event_header_label.grid(row=r, column=c)
        r += 1
        for name, entry in self.event_entries.items():
            label = tk.Label(self.frame, text=name, font=norm_font, bg=st.base_bg)
            label.grid(row=r, column=c)
            entry.grid(row=r, column=c + 1)
            r += 1
        event_state_label.grid(row=r, column=c)
        self.event_state_combo.grid(row=r, column=c + 1)
        r += 1
        make_event_button.grid(row=r, column=c, padx=5, pady=5, sticky="ew")

    def make_quest(self):
        quest_name = str.strip(self.quest_entries["quest name"].get())
        description = str.strip(self.quest_entries["description"].get())
        if quest_name.__contains__("'"):
            quest_name.replace("'", "''")
        if description.__contains__("'"):
            description.replace("'", "''")

        min_delta = str.strip(self.quest_entries["min delta"].get())
        max_delta = str.strip(self.quest_entries["max delta"].get())

        if quest_name and description and min_delta and max_delta:
            commands = [
                f"DELETE FROM `quest` WHERE `name` = '{quest_name}';\n\n",
                "INSERT INTO `quest` (`name`, `min_Delta`, `max_Solves`, `message`, `last_Modified`)\n",
                f"VALUES ('{quest_name}', {min_delta}, {max_delta}, '{description}', '2024-09-07 06:01:47');\n"
            ]

            sh.write_sql_file(quest_name, "quests", ''.join(commands))

    def make_kill_task(self):
        self.make_quest()
        counter_name = str.strip(self.quest_entries["counter name"].get())
        kill_total = str.strip(self.quest_entries["kill total"].get())

        if counter_name and kill_total:
            commands = [
                f"DELETE FROM `quest` WHERE `name` = '{counter_name}';\n\n",
                "INSERT INTO `quest` (`name`, `min_Delta`, `max_Solves`, `message`, `last_Modified`)\n",
                f"VALUES ('{counter_name}', 0, {kill_total}, 'kill counter', '2024-09-07 06:01:47');\n"
            ]

            sh.write_sql_file(counter_name, "quests", ''.join(commands))

    def make_event(self):
        event_name = str.strip(self.event_entries["event name"].get())
        selected = self.event_state_combo.get()
        if selected == "Off":
            state = 3
            comment = "/* GameEventState.On */"
        else:
            state = 4
            comment = "/* GameEventState.Off */"

        if event_name and state:
            commands = [
                f"DELETE FROM `event` WHERE `name` = '{event_name}';\n\n",
                "INSERT INTO `event` (`name`, `start_Time`, `end_Time`, `state`, `last_Modified`)\n",
                f"VALUES ('{event_name}', -1, -1, {state} {comment}, '2020-01-24 19:57:17');\n"
            ]
            sh.write_sql_file(event_name, "events", ''.join(commands))
