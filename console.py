import tkinter as tk
import tkinter.scrolledtext as scrolledtext
import settings as st


class ConsolePanel:

    def __init__(self, parent, cont):
        self.frame = tk.Frame(parent, bg=st.base_bg)
        self.cont = cont

        self.text = scrolledtext.ScrolledText(self.frame, height=30, width=40, undo=True, font=st.norm_font,
                                              bg=st.entry_bg)
        self.text.configure(state='disabled', wrap=tk.WORD)
        self.text.tag_config('field', foreground="dark green")
        self.text.tag_config('warning', foreground="red")

        # configure colors
        self.text.tag_configure("red", foreground="red")
        self.text.tag_configure("blue", foreground="blue")
        self.text.tag_configure("green", foreground="dark green")
        self.text.tag_configure("purple", foreground="purple")
        self.text.tag_configure("brown", foreground="brown")

        clear_button = tk.Button(self.frame, text="Clear", command=self.clear)

        # layout
        self.text.grid(row=0, column=0)
        clear_button.grid(row=1, column=0)

    def clear(self):
        self.text.configure(state='normal')
        self.text.delete('1.0', tk.END)
        self.text.configure(state='disabled')

    def print(self, line, color="black"):
        """Color is an optional parameter."""
        self.text.configure(state='normal')
        self.text.insert(tk.END, line, color)
        self.text.yview_moveto(1)
        self.text.configure(state='disabled')
