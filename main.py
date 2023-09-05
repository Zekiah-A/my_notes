from typing import List
from tkinter import *
import sqlite3
import datetime
import time
import math

window = Tk()
window.title("My notes")
window.geometry("600x400")
sticky_all = (N, S, E, W)
current_frame: Frame = None
frames: List[Frame] = []
main_frame = Frame(window)
main_frame.pack(fill=BOTH, expand=True)
page_history = []

# Will create a singleton of the desired frame
def set_current_frame(new_frame_type: type):
    global current_frame
    global frames
    if current_frame != None:
        current_frame.pack_forget()

    instance = get_frame_singleton(new_frame_type)

    if (instance == None):
        instance = new_frame_type(main_frame)
        frames.append(instance)

    instance.pack(fill=BOTH, expand=True)
    current_frame = instance
    page_history.append(new_frame_type)

def get_frame_singleton(frame_type: type) -> Frame:
    for frame in frames:
        if (frame_type == type(frame)):
            return frame

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

        view_notes = Button(self, text="🔍 Search my notes", command=self.switch_search_page)
        view_notes.grid(column=1, row=1, sticky=sticky_all, padx=10, pady=10)

        recent_title = Label(self, text = "My most recent notes:")
        recent_title.grid(column=0, columnspan=2, row=2, sticky=sticky_all)

        self.recent_notes = Listbox(self)
        self.recent_notes.bind("<<ListboxSelect>>", self.on_recent_notes_selection)
        self.recent_notes.grid(column=0, columnspan=2, row=3, sticky=sticky_all, padx=5, pady=5)

        self.update_recent_notes()

    def switch_create_page(self):
        set_current_frame(CreatePage)

    def switch_search_page(self):
        set_current_frame(SearchPage)

    def on_recent_notes_selection(self, arg):
        selection = self.recent_notes.curselection()
        if not selection:
            return
        set_current_frame(NotePage)

    def update_recent_notes(self):
        cursor.execute("SELECT * FROM Notes ORDER BY date_created DESC")
        notes = cursor.fetchall()
        self.recent_notes.delete(0, END)

        for note in notes:
            date = datetime.datetime.fromtimestamp(note[0])
            content = note[1]
            if (len(content) > 60):
                content = content[:60] + "..."
            self.recent_notes.insert("end", f"{date} | {content} | {note[2]}")

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
        self.grid_rowconfigure(5, weight=1)

        cancel = Button(self, text="❌", font="20", command=self.cancel_create)
        cancel.grid(column=0, row=0, sticky=(N, W), padx=5, pady=5)

        title = Label(self, text="Create new note", font="20")
        title.grid(column=0, row=0, columnspan=2)

        self.name = StringVar()
        name_label = Label(self, text="Author name")
        name_label.grid(column=0, row=1, sticky=W)
        name_entry = HintedEntry(self, hint_text="Enter name", textvariable=self.name)
        name_entry.grid(column=1, row=1, sticky=(N,S,W))

        self.tags = StringVar()
        tags_label = Label(self, text="Note tags:")
        tags_label.grid(column=0, row=2, sticky=W)
        tags_entry = HintedEntry(self, hint_text="Note tags (separated by , or ' ')", textvariable=self.tags)
        tags_entry.grid(column=1, row=2, sticky=(N,S,W))

        content_label = Label(self, text="Note content:")
        content_label.grid(column=0, row=3, sticky=W)
        self.content = StringVar()
        self.content.trace_add("write", self.update_content_entry)
        self.content_entry = Text(self, height=10)
        self.content_entry.grid(column=0, row=4, columnspan=2, sticky=sticky_all, padx=5, pady=5)
        self.content_entry.bind("<KeyRelease>", self.update_content)

        submit = Button(self, text="Create note", command=self.submit_note)
        submit.grid(column=1, row=5, sticky=(N,E,S), padx=5, pady=5)

    def update_content(self, _=None):
        text = self.content_entry.get("1.0", "end-1c")
        self.content.set(text)

    def update_content_entry(self, _=None, _1=None, _2=None):
        self.content_entry.delete("1.0", END)
        self.content_entry.insert("1.0", self.content.get())

    def submit_note(self):
        cursor.execute("INSERT INTO Notes (date_created, content, author) VALUES (?, ?, ?)", 
            (math.floor(time.time()), self.name.get(), self.content.get()))
        db.commit()

        self.name.set("")
        self.tags.set("")
        self.content.set("")
        get_frame_singleton(StartPage).update_recent_notes()
        self.cancel_create()

    def cancel_create(self, _=None):
        set_current_frame(StartPage)

class SearchPage(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_rowconfigure(0, weight=2)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=20)

        cancel = Button(self, text="❌", font="20", command=self.cancel_search)
        cancel.grid(column=0, row=0, sticky=(N, W), padx=5, pady=5)

        title = Label(self, text="Search my notes", font="20")
        title.grid(column=0, row=0, columnspan=4)

        search = HintedEntry(self, hint_text="Search term")
        search.grid(column=0, row=1, sticky=sticky_all, padx=5)
        
        search_by = StringVar(self, "search by")
        search_by_drop = OptionMenu(self, search_by, "by author", "by content")
        search_by_drop.grid(column=1, row=1, sticky=sticky_all, padx=5)

        search_tags = HintedEntry(self, hint_text="Include tags (separate by , or ' ')")
        search_tags.grid(column=2, row=1, sticky=sticky_all)

        search = Button(self, text="Search 🔍")
        search.grid(column=3, row=1, sticky=sticky_all, padx=5)

        found_notes = Listbox(self)
        found_notes.grid(column=0, columnspan=4, row=2, sticky=sticky_all, padx=5, pady=5)

    def cancel_search(self, _=None):
        set_current_frame(StartPage)

class NotePage(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=8)

        cancel = Button(self, text="❌", font="20", command=self.cancel_view)
        cancel.grid(column=0, row=0, sticky=(N, W), padx=5, pady=5)

        title = Label(self, text="Note - NOTENAME", font="20")
        title.grid(column=0, row=0)

        tags = Label(self, text="Tag1, Tag2, Tag3")
        tags.grid(column=0, row=1)

        content = Label(self, text="Content content content")
        content.grid(column=0, row=2, sticky=sticky_all)

    def cancel_view(self, _=None):
        set_current_frame(page_history[len(page_history) - 2])

# DB Initialisation
db = sqlite3.connect("notes.db")
cursor = db.cursor()

# Created (unix epoch offset (s))
cursor.execute("""CREATE TABLE IF NOT EXISTS Notes(
    note_id INTEGER PRIMARY KEY NOT NULL, date_created INTEGER, content TEXT, author TEXT);""")
cursor.execute("""CREATE TABLE IF NOT EXISTS Tags(
        note_id INTEGER, content TEXT, FOREIGN KEY(note_id) REFERENCES Notes(note_id))""")

# Start
set_current_frame(StartPage)
mainloop()