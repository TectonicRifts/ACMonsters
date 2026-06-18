import os
import tkinter as tk
from ctypes import windll

from controller import Controller


def main():
    # if on Windows, fix blurry font
    if os.name == 'nt':
        windll.shcore.SetProcessDpiAwareness(1) # type: ignore

    version = 1.7
    root = tk.Tk()
    root.title("AC Monsters " + str(version))
    Controller(root)
    root.mainloop()


if __name__ == '__main__':
    main()
