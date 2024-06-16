import tkinter as tk
from tkinter import ttk

from art_panel import ArtPanel
from attributes_panel import AttributesPanel
from calc_panel import CalcPanel
from grid_panel import GridPanel
from ratings_panel import RatingsPanel
from skills_panel import SkillsPanel
from spells_panel import SpellsPanel
from toolbar import Toolbar
from base_panel import BasePanel
from console import ConsolePanel
from mods_panel import ModsPanel
import settings as st


class View:

    def __init__(self, parent, cont):
        self.frame = tk.Frame(parent, bg=st.base_bg)
        self.cont = cont

        self.right_nb = ttk.Notebook(self.frame)
        left_nb = ttk.Notebook(self.frame)

        # make panels
        self.console = ConsolePanel(left_nb, cont)
        self.attributes_panel = AttributesPanel(self.right_nb, cont)
        self.skills_panel = SkillsPanel(self.right_nb, cont)
        self.calc_panel = CalcPanel(self.right_nb, cont)
        self.mods_panel = ModsPanel(self.right_nb, cont)
        self.grid_panel = GridPanel(self.right_nb, cont)
        art_panel = ArtPanel(self.right_nb, cont)
        spells_panel = SpellsPanel(self.right_nb, cont)
        ratings_panel = RatingsPanel(self.right_nb, cont)

        # left
        left_nb.add(self.console.frame, text="Console")

        # right
        base_panel = BasePanel(self.right_nb, cont)

        self.right_nb.add(base_panel.frame, text="Base")
        self.right_nb.add(self.attributes_panel.frame, text="Attr")
        self.right_nb.add(self.skills_panel.frame, text="Skill")
        self.right_nb.add(self.grid_panel.frame, text="Grid")
        self.right_nb.add(self.calc_panel.frame, text="Calc")
        self.right_nb.add(self.mods_panel.frame, text="Mods")
        self.right_nb.add(art_panel.frame, text="Art")
        self.right_nb.add(spells_panel.frame, text="Spell")
        self.right_nb.add(ratings_panel.frame, text="Rate")

        left_nb.grid(row=0, column=0)
        self.right_nb.grid(row=0, column=1, sticky="ns")

        toolbar = Toolbar(self.frame, cont)
        toolbar.frame.grid(row=1, column=0, columnspan=2)

        self.frame.grid()

    def get_current_tab_name(self):
        current_tab_index = self.right_nb.index(self.right_nb.select())
        return self.right_nb.tab(current_tab_index, option="text")
