from typing import List
from typing import Union
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
page_history: List[Frame] = []
non_singletons: List[type] = []

# Will make current page the given frame instance. Useful
# in scenarios where you want to hold multiple of a frame to
# preserve state or inject instance-specific data via the frame
# constructor, such as for a specific note page with it's own content.
def set_current_instance(new_frame: Frame):
    global current_frame
    global frames
    if current_frame != None:
        current_frame.pack_forget()

    new_frame.pack(fill=BOTH, expand=True)
    frames.append(new_frame)
    current_frame = new_frame

    if not type(new_frame) in non_singletons:
        non_singletons.append(type(new_frame))

# Will create a singleton of the desired frame. Only one of
# a singleton type can exist in the application at once. Arguments
# can not be used when creating froma  singleton type. Examples of a
# suitable singleton include the start screen, which will never change.
def set_current_singleton(new_frame_type: type):
    global current_frame
    global frames
    global non_singletons
    if current_frame != None:
        current_frame.pack_forget()

    for non_singleton in non_singletons:
        if non_singleton == new_frame_type:
            raise Exception("This frame type has been instanced more than once. Can not get singleton.")

    instance = get_frame_singleton(new_frame_type)

    if (instance == None):
        instance = new_frame_type(main_frame)
        frames.append(instance)

    instance.pack(fill=BOTH, expand=True)
    current_frame = instance

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

        self.recent_note_ids = []
        self.recent_notes = Listbox(self)
        self.recent_notes.bind("<<ListboxSelect>>", self.on_recent_notes_selection)
        self.recent_notes.grid(column=0, columnspan=2, row=3, sticky=sticky_all, padx=5, pady=5)

        self.update_recent_notes()

    def switch_create_page(self):
        set_current_singleton(CreatePage)

    def switch_search_page(self):
        set_current_singleton(SearchPage)

    def on_recent_notes_selection(self, _=None):
        # For some reason self.recent_notes.curselection is boxed in a tuple, probably so it can represent null
        # even though they could have just used an error value for no valid selection, like -1. So this must be handled.
        selection = self.recent_notes.curselection()
        if not selection:
            return
        
        id = self.recent_note_ids[selection[0]]
        note_instance = NotePage(main_frame, id, StartPage)
        set_current_instance(note_instance)

    def update_recent_notes(self):
        cursor.execute("SELECT * FROM Notes ORDER BY date_created DESC")
        notes = cursor.fetchall()
        self.recent_notes.delete(0, END)

        for note in notes:
            self.recent_note_ids.append(note[0])
            date = datetime.datetime.fromtimestamp(note[1])
            title = note[2]
            if (len(title) > 20):
                title = title[:20] + "..."
            self.recent_notes.insert("end", f"{date} | {title} | {note[4]}")

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
        self.grid_rowconfigure(6, weight=1)

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
        tags_entry = HintedEntry(self, hint_text="Note tags (separate with ',')", textvariable=self.tags)
        tags_entry.grid(column=1, row=2, sticky=(N,S,W))

        self.title = StringVar()
        title_label = Label(self, text="Note title:")
        title_label.grid(column=0, row=3, sticky=W)
        title_entry = HintedEntry(self, hint_text="Note title (32 chars max)", textvariable=self.title)
        title_entry.grid(column=1, row=3, sticky=(N,S,W))

        content_label = Label(self, text="Note content:")
        content_label.grid(column=0, row=4, sticky=W)
        self.content = StringVar()
        self.content.trace_add("write", self.update_content_entry)
        self.content_entry = Text(self, height=10)
        self.content_entry.grid(column=0, row=5, columnspan=2, sticky=sticky_all, padx=5, pady=5)
        self.content_entry.bind("<KeyRelease>", self.update_content)

        submit = Button(self, text="Create note", command=self.submit_note)
        submit.grid(column=1, row=6, sticky=(N,E,S), padx=5, pady=5)

    def update_content(self, _=None):
        text = self.content_entry.get("1.0", "end-1c")
        self.content.set(text)

    def update_content_entry(self, _=None, _1=None, _2=None):
        self.content_entry.delete("1.0", END)
        self.content_entry.insert("1.0", self.content.get())

    def submit_note(self):
        cursor.execute("INSERT INTO Notes (date_created, title, content, author) VALUES (?, ?, ?, ?)", 
            (math.floor(time.time()), self.title.get(), self.content.get(), self.name.get()))
        new_id = cursor.lastrowid

        for raw_tag in self.tags.get().split(","):
            cursor.execute("INSERT INTO Tags (note_id, content) VALUES (?, ?)",
                (new_id, raw_tag.strip().lower()))
        db.commit()

        self.name.set("")
        self.tags.set("")
        self.content.set("")
        self.title.set("")
        get_frame_singleton(StartPage).update_recent_notes()
        get_frame_singleton(SearchPage).update_notes()
        self.cancel_create()

    def cancel_create(self, _=None):
        set_current_singleton(StartPage)

class SearchPage(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.note_ids = []

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

        self.search = StringVar()
        search_entry = HintedEntry(self, hint_text="Search term", textvariable=self.search)
        search_entry.grid(column=0, row=1, sticky=sticky_all, padx=5)
        
        self.search_by = StringVar(self, "search by")
        search_by_drop = OptionMenu(self, self.search_by, "by author", "by title")
        search_by_drop.grid(column=1, row=1, sticky=sticky_all, padx=5)

        self.search_tags = StringVar()
        search_tags_entry = HintedEntry(self, hint_text="Include tags (separate by , or ' ')", textvariable=self.search_tags)
        search_tags_entry.grid(column=2, row=1, sticky=sticky_all)

        search_button = Button(self, text="Search 🔍", command=self.update_notes)
        search_button.grid(column=3, row=1, sticky=sticky_all, padx=5)

        self.notes = Listbox(self)
        self.notes.grid(column=0, columnspan=4, row=2, sticky=sticky_all, padx=5, pady=5)
        self.notes.bind("<<ListboxSelect>>", self.on_notes_selection)
        self.update_notes()

    def on_notes_selection(self, _=None):
        selection = self.notes.curselection()
        if not selection:
            return
        
        id = self.note_ids[selection[0]]
        note_instance = NotePage(main_frame, id, SearchPage)
        set_current_instance(note_instance)

    def get_searchcolumn_notes(self, search_column):
        cursor.execute("SELECT * FROM Notes WHERE ? LIKE ?", search_column, self.search) 
        return cursor.fetchall()

    def get_recent_notes(self):
        cursor.execute("SELECT * FROM Notes ORDER BY date_created DESC")
        return cursor.fetchall()

    def update_notes(self, _=None):
        notes = []
        if self.search_by == "by author":
            notes = self.get_searchcolumn_notes("author")
        elif self.search_by == "by title":
            notes = self.get_searchcolumn_notes("title")
        else:
            notes = self.get_recent_notes()

        self.notes.delete(0, END)

        for note in notes:
            self.note_ids.append(note[0])
            date = datetime.datetime.fromtimestamp(note[1])
            title = note[2]
            if (len(title) > 20):
                title = title[:20] + "..."
            self.notes.insert("end", f"{date} | {title} | {note[4]}")        

    def cancel_search(self, _=None):
        set_current_singleton(StartPage)

class NotePage(Frame):
    # return_to -> Page the current view will return to after this note instance is closed.
    # Will either attempt a singleton type or a frame instance
    def __init__(self, parent, note_id: int, return_to: Union[type, Frame]):
        super().__init__(parent)
        self.return_to = return_to
        
        # Load injected note ID from the DB
        cursor.execute("SELECT date_created, title, content, author FROM Notes WHERE note_id = ?",
            (note_id,))
        note_data = cursor.fetchone()
        self.note_created = note_data[0]
        self.note_title = note_data[1]
        self.note_content = note_data[2]
        self.note_author = note_data[3]

        self.note_tags = []
        cursor.execute("SELECT content FROM Tags WHERE note_id = ?",
            (note_id,))
        for tag_tuple in cursor.fetchall():
            self.note_tags.append(tag_tuple[0])

        # Ui
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=8)

        cancel = Button(self, text="❌", font="20", command=self.cancel_view)
        cancel.grid(column=0, row=0, sticky=(N, W), padx=5, pady=5)

        title = Label(self, text=f"{self.note_title} - By {self.note_author}", font="20")
        title.grid(column=0, row=0)

        tags_text = StringVar()
        tags = Label(self, textvariable=tags_text)
        tags.grid(column=0, row=1)

        for tag in self.note_tags:
            pre = ""
            if tags_text.get():
                pre = tags_text.get() + ", "
            else:
                pre = "Tags: "
            tags_text.set(pre + tag)
        tags_text.set(tags_text.get() + f" | Created on: {datetime.datetime.fromtimestamp(self.note_created)}")

        content = Label(self, text=self.note_content)
        content.grid(column=0, row=2, sticky=sticky_all)

    def cancel_view(self, _=None):
        # Instance return
        if type(self.return_to) is type:
            set_current_singleton(self.return_to)
        else:
            set_current_instance(self.return_to)

# DB Initialisation
db = sqlite3.connect("notes.db")
cursor = db.cursor()

# Created (unix epoch offset (s))
cursor.execute("""CREATE TABLE IF NOT EXISTS Notes(
    note_id INTEGER PRIMARY KEY NOT NULL, date_created INTEGER, title TEXT, content TEXT, author TEXT);""")
cursor.execute("""CREATE TABLE IF NOT EXISTS Tags(
        note_id INTEGER, content TEXT, FOREIGN KEY(note_id) REFERENCES Notes(note_id))""")

# Start
set_current_singleton(StartPage)
mainloop()