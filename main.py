from typing import List
from tkinter import *
import sqlite3

window = Tk()
window.title("My notes")
window.geometry("600x400")
sticky_all = (N, S, E, W)
current_frame: Frame = None
frames: List[Frame] = []
main_frame = Frame(window)
main_frame.pack(fill=BOTH, expand=True)

# Will create a singleton of the desired frame
def set_current_frame(new_frame: type):
    global current_frame
    global frames
    if current_frame != None:
        current_frame.pack_forget()

    instance = None
    for frame in frames:
        if (new_frame == type(frame)):
            instance = frame

    if (instance == None):
        instance = new_frame(main_frame)
        frames.append(instance)

    instance.pack(fill=BOTH, expand=True)
    current_frame = instance

class HintedEntry(Entry):
    def __init__(self, parent=None, hint_text="", *args, **kw):
        super().__init__(parent, *args, **kw)
        self.fg = "black"
        self.fg_hint_style = "grey30"
        self.placeholder = hint_text
        self.bind("<FocusOut>", self.show_hint)
        self.bind("<FocusIn>", self.clear_hint)
        self.show_hint()

    def clear_hint(self, _=None):
        if not self.get() and super().get():
            self.config(fg=self.fg)
            self.delete(0, END)

    def show_hint(self, _=None):
        if not super().get():
            self.config(fg=self.fg_hint_style)
            self.insert(0, self.placeholder)

    def get(self):
        content = super().get()
        if content == self.placeholder:
            return ""
        return content

class StartPage(Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=2)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=4)

        title = Label(self, text = "My notes - by Zekiah-A", font="30")
        title.grid(column = 0, row = 0, columnspan = 2)

        create_new = Button(self, text="➕ Create new note", command=self.switch_create_page)
        create_new.grid(column=0, row=1, sticky=sticky_all, padx=10, pady=10)

        view_notes = Button(self, text="🔍 Search my notes")
        view_notes.grid(column=1, row=1, sticky=sticky_all, padx=10, pady=10)

        recent_title = Label(self, text = "My most recent notes:")
        recent_title.grid(column=0, columnspan=2, row=2, sticky=sticky_all)

        recent_notes = Listbox(self)
        recent_notes.grid(column=0, columnspan=2, row=3, sticky=sticky_all, padx=5, pady=5)

    def switch_create_page(self):
        set_current_frame(CreatePage)

    def search():
        pass

class CreatePage(Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)

        cancel = Button(self, text="❌", font="20", command=self.cancel_create)
        cancel.grid(column=0, row=0, sticky=(N, W), padx=5, pady=5)

        title = Label(self, text="Create note", font="20")
        title.grid(column=0, row=0, columnspan=2)

        name_label = Label(self, text="Notetaker name")
        name_label.grid(column=0, row=1)
        name_entry = HintedEntry(self, hint_text="Enter name")
        name_entry.grid(column=1, row=1)

        tags_label = Label(self, text="Note tags:")
        tags_label.grid(column=0, row=2)
        tags_entry = HintedEntry(self, hint_text="Note tags (separated by , or ' ')")
        tags_entry.grid(column=1, row=2)

        content_label = Label(self, text="Note content:")
        content_label.grid(column=0, row=3)

        content_entry = Text(self, height=10)
        content_entry.grid(column=0, row=4, columnspan=2, sticky=sticky_all, padx=5, pady=5)
    
    def cancel_create(self, _=None):
        set_current_frame(StartPage)

    
# DB Initialisation
connection = sqlite3.connect("notes.db")
cursor = connection.cursor()

# Created (unix epoch offset (s))
cursor.execute("CREATE TABLE IF NOT EXISTS Notes(date_created INTEGER, content TEXT, author TEXT)")

# Start
set_current_frame(StartPage)
mainloop()