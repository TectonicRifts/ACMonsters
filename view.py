import tkinter as tk
from tkinter import ttk

from art_panel import ArtPanel
from attributes_panel import AttributesPanel
from calc_panel import CalcPanel
from port_panel import PortPanel
from skills_panel import SkillsPanel
from spells_panel import SpellsPanel
from misc_panel import MiscPanel
from toolbar import Toolbar
from base_panel import BasePanel
from gen_panel import GenPanel
from console import ConsolePanel
from mods_panel import ModsPanel
from recipe_panel import RecipePanel
import settings as st


class View(tk.Frame):

    def __init__(self, parent, cont):
        super().__init__(parent, bg=st.base_bg)
        self.cont = cont

        self.right_nb = ttk.Notebook(self)
        left_nb = ttk.Notebook(self)

        # make panels
        self.console = ConsolePanel(left_nb, cont)
        self.attributes_panel = AttributesPanel(self.right_nb, cont)
        self.skills_panel = SkillsPanel(self.right_nb, cont)
        self.calc_panel = CalcPanel(self.right_nb, cont)
        self.mods_panel = ModsPanel(self.right_nb, cont)
        art_panel = ArtPanel(self.right_nb, cont)
        self.spells_panel = SpellsPanel(self.right_nb, cont)
        misc_panel = MiscPanel(self.right_nb, cont)
        recipe_panel = RecipePanel(self.right_nb, cont)
        port_panel = PortPanel(self.right_nb, cont)

        # left
        left_nb.add(self.console, text="Console")

        # right
        base_panel = BasePanel(self.right_nb, cont)
        gen_panel = GenPanel(self.right_nb, cont)

        self.right_nb.add(base_panel, text="Base")
        self.right_nb.add(gen_panel, text="Gen")
        self.right_nb.add(self.attributes_panel, text="Attr")
        self.right_nb.add(self.skills_panel, text="Skill")
        self.right_nb.add(self.calc_panel, text="Calc")
        self.right_nb.add(self.mods_panel, text="Mods")
        self.right_nb.add(art_panel, text="Art")
        self.right_nb.add(self.spells_panel, text="Spell")
        self.right_nb.add(recipe_panel, text="Recp")
        self.right_nb.add(port_panel, text="Port")
        self.right_nb.add(misc_panel, text="Misc")

        left_nb.grid(row=0, column=0, sticky="ns")
        self.right_nb.grid(row=0, column=1, sticky="ns")

        toolbar = Toolbar(self, cont)
        toolbar.grid(row=1, column=0, columnspan=2)

        self.grid()


    def show_help(self):
        self.console.print("For help, visit the ACM Wiki: https://github.com/TectonicRifts/ACMonsters/wiki")
