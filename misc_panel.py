from tkinter import ttk

import view_helper as vh
import sql_helper as sh
import settings as st
import tkinter as tk


class MiscPanel(tk.Frame):

    def __init__(self, parent, cont):
        super().__init__(parent, bg=st.base_bg)
        self.cont = cont

        norm_font = st.norm_font

        # quest
        quest_header_label = tk.Label(self, text="Quest", font=norm_font, fg=st.label_text, bg=st.base_bg)
        str_labels = ["quest name", "description", "min delta", "max delta"]
        self.quest_entries = vh.make_str_entry(self, str_labels)

        self.quest_entries["min delta"].insert(0, "72000")
        self.quest_entries["max delta"].insert(0, "-1")

        # kill task
        task_header_label = tk.Label(self, text="Kill Task", font=norm_font, fg=st.label_text, bg=st.base_bg)
        str_labels = ["task name", "kill total"]
        self.task_entries = vh.make_str_entry(self, str_labels)

        # event
        event_header_label = tk.Label(self, text="Event", font=norm_font, fg=st.label_text, bg=st.base_bg)
        str_labels = ["event name"]
        self.event_entries = vh.make_str_entry(self, str_labels)

        event_state_label = tk.Label(self, text="state", font=norm_font, bg=st.base_bg)
        event_state_options = ["Off", "On"]
        self.event_state_combo = ttk.Combobox(self, values=event_state_options, font=norm_font, state="readonly")
        self.event_state_combo.current(0)

        make_event_button = tk.Button(self, text="Make Event", command=self.make_event)
        make_quest_button = tk.Button(self, text="Make Quest", command=self.make_quest)
        make_task_button = tk.Button(self, text="Make Task", command=self.make_kill_task)

        # layout
        r = 0
        c = 0

        quest_header_label.grid(row=r, column=c, sticky="w", padx=2)
        r += 1
        for name, entry in self.quest_entries.items():
            label = tk.Label(self, text=name, font=norm_font, bg=st.base_bg)
            label.grid(row=r, column=c, sticky="e", padx=2)
            entry.grid(row=r, column=c + 1, sticky="ew", padx=2)
            r += 1
        make_quest_button.grid(row=r, column=c, columnspan=2, padx=2, pady=5, sticky="ew")
        r += 1

        task_header_label.grid(row=r, column=c, sticky="w", padx=2)
        r += 1
        for name, entry in self.task_entries.items():
            label = tk.Label(self, text=name, font=norm_font, bg=st.base_bg)
            label.grid(row=r, column=c, sticky="e", padx=2)
            entry.grid(row=r, column=c + 1, sticky="ew", padx=2)
            r += 1
        make_task_button.grid(row=r, column=c, columnspan=2, padx=2, pady=5, sticky="ew")
        r += 1

        event_header_label.grid(row=r, column=c, sticky="w", padx=2)
        r += 1
        for name, entry in self.event_entries.items():
            label = tk.Label(self, text=name, font=norm_font, bg=st.base_bg)
            label.grid(row=r, column=c, sticky="e", padx=2)
            entry.grid(row=r, column=c + 1, sticky="ew", padx=2)
            r += 1
        event_state_label.grid(row=r, column=c, sticky="e", padx=2)
        self.event_state_combo.grid(row=r, column=c + 1, sticky="ew", padx=2)
        r += 1
        make_event_button.grid(row=r, column=c, columnspan=2, padx=2, pady=5, sticky="ew")

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)


    def make_quest(self, name: str = None):
        if name is None:
            quest_name = str.strip(self.quest_entries["quest name"].get())
            description = str.strip(self.quest_entries["description"].get())
        else:
            quest_name = str.strip(self.task_entries["task name"].get())
            description = "task timer"

        quest_name = quest_name.replace("'", "''")
        description = description.replace("'", "''")

        min_delta = str.strip(self.quest_entries["min delta"].get())
        max_delta = str.strip(self.quest_entries["max delta"].get())

        if quest_name and description and min_delta and max_delta:
            print("this ran")
            commands = [
                f"DELETE FROM `quest` WHERE `name` = '{quest_name}';\n\n",
                "INSERT INTO `quest` (`name`, `min_Delta`, `max_Solves`, `message`, `last_Modified`)\n",
                f"VALUES ('{quest_name}', {min_delta}, {max_delta}, '{description}', '2024-09-07 06:01:47');\n"
            ]

            sh.write_sql_file(quest_name, "quests", ''.join(commands))

    def make_kill_task(self):
        counter_name = str.strip(self.task_entries["task name"].get())
        counter_name = counter_name.replace("'", "''")

        self.make_quest(name=counter_name)
        
        counter_name = counter_name + "KillCount"

        kill_total = str.strip(self.task_entries["kill total"].get())

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


