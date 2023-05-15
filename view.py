import tkinter as tk
from tkinter import ttk

from art_panel import ArtPanel
from attributes_panel import AttributesPanel
from calc_panel import CalcPanel
from skills_panel import SkillsPanel
from toolbar import Toolbar
from base_panel import BasePanel
from console import ConsolePanel
from mods_panel import ModsPanel


class View:

    def __init__(self, parent, cont):
        self.frame = tk.Frame(parent)
        self.cont = cont

        right_nb = ttk.Notebook(self.frame)
        left_nb = ttk.Notebook(self.frame)

        # make panels
        self.console = ConsolePanel(left_nb, cont)
        self.attributes_panel = AttributesPanel(right_nb, cont)
        self.skills_panel = SkillsPanel(right_nb, cont)
        self.calc_panel = CalcPanel(right_nb, cont)
        self.mods_panel = ModsPanel(right_nb, cont)
        art_panel = ArtPanel(right_nb, cont)

        # left
        left_nb.add(self.console.frame, text="Console")

        # right
        base_panel = BasePanel(right_nb, cont)

        right_nb.add(base_panel.frame, text="Base")
        right_nb.add(self.attributes_panel.frame, text="Attr")
        right_nb.add(self.skills_panel.frame, text="Skill")
        right_nb.add(self.calc_panel.frame, text="Calc")
        right_nb.add(self.mods_panel.frame, text="Mods")
        right_nb.add(art_panel.frame, text="Art")

        left_nb.grid(row=0, column=0)
        right_nb.grid(row=0, column=1, sticky="ns")

        toolbar = Toolbar(self.frame, cont)
        toolbar.frame.grid(row=1, column=0, columnspan=2)

        self.frame.grid()
