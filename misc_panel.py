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
        quest_labels = ["quest name", "description", "min delta", "max solves"]
        self.quest_entries = vh.make_str_entry(self, quest_labels)

        self.quest_entries["min delta"].insert(0, "72000")
        self.quest_entries["max solves"].insert(0, "-1")

        # quest bits
        bits_header_label = tk.Label(self, text="Quest Bits", font=norm_font, fg=st.label_text, bg=st.base_bg)
        bits_labels = ["total bits"]
        self.bits_entries = vh.make_int_entry(self, bits_labels)

        # kill task
        task_header_label = tk.Label(self, text="Kill Task", font=norm_font, fg=st.label_text, bg=st.base_bg)
        task_labels = ["kill total"]
        self.task_entries = vh.make_int_entry(self, task_labels)

        # event
        event_header_label = tk.Label(self, text="Event", font=norm_font, fg=st.label_text, bg=st.base_bg)
        str_labels = ["event name"]
        self.event_entries = vh.make_str_entry(self, str_labels)

        event_state_label = tk.Label(self, text="state", font=norm_font, bg=st.base_bg)
        event_state_options = ["Off", "On"]
        self.event_state_combo = ttk.Combobox(self, values=event_state_options, font=norm_font, state="readonly")
        self.event_state_combo.current(0)

        make_quest_button = tk.Button(self, text="Make Quest", command=self.make_quest)
        make_bits_button = tk.Button(self, text="Make Bits", command=self.make_quest_bits)
        make_task_button = tk.Button(self, text="Make Task", command=self.make_kill_task)
        make_event_button = tk.Button(self, text="Make Event", command=self.make_event)

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

        bits_header_label.grid(row=r, column=c, sticky="w", padx=2)
        r += 1
        for name, entry in self.bits_entries.items():
            label = tk.Label(self, text=name, font=norm_font, bg=st.base_bg)
            label.grid(row=r, column=c, sticky="e", padx=2)
            entry.grid(row=r, column=c + 1, sticky="ew", padx=2)
            r += 1
        make_bits_button.grid(row=r, column=c, columnspan=2, padx=2, sticky="ew")
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


    def make_quest(self):

        quest_name = self.quest_entries["quest name"].get().strip()
        if not quest_name:
            self.cont.view.console.print("Enter a quest name.\n")
            return

        description = self.quest_entries["description"].get().strip()
        if not description:
            description = "Placeholder description"

        quest_name = quest_name.replace("'", "''")
        description = description.replace("'", "''")

        min_delta = self.quest_entries["min delta"].get().strip()
        max_solves = self.quest_entries["max solves"].get().strip()
        if not min_delta:
            self.quest_entries["min delta"].insert(0, "72000")
            min_delta = "72000"

        if not max_solves:
            self.quest_entries["max solves"].insert(0, "-1")
            max_solves = "-1"

        write_quest_sql(quest_name, min_delta, max_solves, description)


    def make_quest_bits(self):

        quest_name = self.quest_entries["quest name"].get().strip()
        if not quest_name:
            self.cont.view.console.print("Enter a quest name.\n")
            return

        description = self.quest_entries["description"].get().strip()
        if not description:
            description = "Placeholder description"

        total_bits = self.bits_entries["total bits"].get().strip()
        if not total_bits:
            self.cont.view.console.print("Enter a total number of bits.\n")
            return

        try:
            total_bits = int(total_bits)
        except ValueError:
            self.cont.view.console.print("Total bits must be a whole number.\n")
            return

        min_delta = 0
        # max solves = 2^number of bits - 1
        # e.g., for 10 bits, do 2^10 = 1024 - 1 = 1023
        max_solves = 2 ** total_bits - 1

        # print list of bit flags
        for i in range(total_bits):
            value = 2 ** i
            self.cont.view.console.print(f"{hex(value)} = {value}\n")

        write_quest_sql(quest_name, min_delta, max_solves, description)


    def make_kill_task(self):
        # make quest file first
        self.make_quest()

        # make kill counter file
        counter_name = self.quest_entries["quest name"].get().strip()
        counter_name = counter_name.replace("'", "''")
        counter_name = counter_name + "KillCount"
        description = "Kill counter"

        min_delta = 0
        # max solves are equal to kill total
        kill_total = self.task_entries["kill total"].get().strip()

        if not kill_total:
            self.cont.view.console.print("Enter a kill total.\n")
            return

        write_quest_sql(counter_name, min_delta, kill_total, description)


    def make_event(self):
        event_name = self.event_entries["event name"].get().strip()
        if not event_name:
            self.cont.view.console.print("Enter an event name.\n")
            return

        selected = self.event_state_combo.get()
        if selected == "Off":
            state = 3
            comment = "/* GameEventState.On */"
        else:
            state = 4
            comment = "/* GameEventState.Off */"

        write_event_sql(event_name, state, comment)


def write_quest_sql(name, min_delta, max_solves, description):
    commands = [
        f"DELETE FROM `quest` WHERE `name` = '{name}';\n\n",
        "INSERT INTO `quest` (`name`, `min_Delta`, `max_Solves`, `message`, `last_Modified`)\n",
        f"VALUES ('{name}', {min_delta}, {max_solves}, '{description}', '2024-09-07 06:01:47');\n"
    ]
    sh.write_sql_file(name, "quests", ''.join(commands))


def write_event_sql(name, state, comment):
    commands = [
        f"DELETE FROM `event` WHERE `name` = '{name}';\n\n",
        "INSERT INTO `event` (`name`, `start_Time`, `end_Time`, `state`, `last_Modified`)\n",
        f"VALUES ('{name}', -1, -1, {state} {comment}, '2020-01-24 19:57:17');\n"
    ]
    sh.write_sql_file(name, "events", ''.join(commands))