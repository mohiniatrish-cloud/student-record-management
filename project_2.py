import customtkinter as ctk
from tkinter import ttk, messagebox
import tkinter as tk
from datetime import datetime
import sqlite3

# ─────────────────────────────────────────────
#  Theme / Color constants
# ─────────────────────────────────────────────
LIGHT = {
    "bg":          "#F3F4F6",
    "sidebar_bg":  "#FFFFFF",
    "header_bg":   "#2061CB",
    "card_bg":     "#FFFFFF",
    "btn_add":     "#22C55E",
    "btn_edit":    "#2061CB",
    "btn_del":     "#F59E0B",
    "btn_ref":     "#799BFA",
    "btn_find":    "#2061CB",
    "btn_update":  "#22C55E",
    "btn_delete2": "#F59E0B",
    "btn_cancel":  "#EF4444",
    "btn_submit":  "#22C55E",
    "btn_clear":   "#EF4444",
    "tbl_header":  "#2061CB",
    "tbl_row1":    "#FFFFFF",
    "tbl_row2":    "#F0F4FF",
    "sidebar_sel": "#2061CB",
    "sidebar_txt": "#374151",
    "text_main":   "#111827",
    "text_sub":    "#6B7280",
    "border":      "#E5E7EB",
    "entry_bg":    "#FFFFFF",
    "entry_fg":    "#111827",
    "status_bg":   "#F3F4F6",
}

DARK = {
    "bg":          "#1E1E1E",
    "sidebar_bg":  "#2A2A2A",
    "header_bg":   "#1A3A6B",
    "card_bg":     "#2A2A2A",
    "btn_add":     "#22C55E",
    "btn_edit":    "#2061CB",
    "btn_del":     "#F59E0B",
    "btn_ref":     "#799BFA",
    "btn_find":    "#2061CB",
    "btn_update":  "#22C55E",
    "btn_delete2": "#F59E0B",
    "btn_cancel":  "#EF4444",
    "btn_submit":  "#22C55E",
    "btn_clear":   "#EF4444",
    "tbl_header":  "#1A3A6B",
    "tbl_row1":    "#2A2A2A",
    "tbl_row2":    "#333333",
    "sidebar_sel": "#2061CB",
    "sidebar_txt": "#D1D5DB",
    "text_main":   "#F9FAFB",
    "text_sub":    "#9CA3AF",
    "border":      "#374151",
    "entry_bg":    "#374151",
    "entry_fg":    "#F9FAFB",
    "status_bg":   "#1A1A1A",
}

C = LIGHT  # active color dict (mutable reference updated on toggle)


# ─────────────────────────────────────────────
#  Database Setup & Fetching
# ─────────────────────────────────────────────
DB_NAME = "student_data.db"

# ─────────────────────────────────────────────
#  Database Setup & Fetching
# ─────────────────────────────────────────────
DB_NAME = "student_data.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            roll INTEGER PRIMARY KEY, name TEXT NOT NULL, age INTEGER, course TEXT,
            sem1 REAL, sem2 REAL, sem3 REAL, sem4 REAL, sem5 REAL, sem6 REAL
        )
    ''')
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        # None represents an empty/incomplete semester
        initial_data = [
            (101, "Mohini Atrish", 20, "BCA", 92.5, 88.0, 95.0, None, None, None),
            (102, "Anjali Sharma", 19, "BCA", 85.0, 90.0, None, None, None, None),
            (103, "Rahul Verma", 21, "BCA", 78.0, 82.0, 88.0, 86.0, 80.0, 85.0),
        ]
        cursor.executemany("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", initial_data)
    conn.commit()
    conn.close()

init_db()

def get_all_students():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    rows = cursor.fetchall()
    conn.close()
    return [
        {"roll": r[0], "name": r[1], "age": r[2], "course": r[3],
         "sem1": r[4], "sem2": r[5], "sem3": r[6], "sem4": r[7], "sem5": r[8], "sem6": r[9]}
        for r in rows
    ]

def get_recent_students(limit=5):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM students ORDER BY rowid DESC LIMIT {limit}")
    rows = cursor.fetchall()
    conn.close()
    return [
        {"roll": r[0], "name": r[1], "age": r[2], "course": r[3],
         "sem1": r[4], "sem2": r[5], "sem3": r[6], "sem4": r[7], "sem5": r[8], "sem6": r[9]}
        for r in rows
    ]



def calc_percentage(s):
    # Gather all semesters, filtering out None or empty strings
    sems = [s[f"sem{i}"] for i in range(1, 7)]
    valid_sems = [float(val) for val in sems if val not in ("", None)]
    
    if not valid_sems:  # If no semesters are filled yet
        return 0.0
    return round(sum(valid_sems) / len(valid_sems), 1)

def calc_grade(pct):
    if pct == 0.0: return "-"  # No grade if no semesters filled
    if pct >= 90: return "A+"
    if pct >= 80: return "A"
    if pct >= 70: return "B"
    if pct >= 60: return "C"
    if pct >= 50: return "D"
    return "F"


# ─────────────────────────────────────────────
#  Helper: rounded rectangle button
# ─────────────────────────────────────────────
def make_btn(parent, text, color, cmd, width=140, height=36, icon=""):
    label = f"{icon}  {text}" if icon else text
    btn = ctk.CTkButton(
        parent, text=label, fg_color=color, hover_color=_darken(color),
        text_color="#FFFFFF", font=ctk.CTkFont(size=13, weight="bold"),
        corner_radius=8, width=width, height=height, command=cmd
    )
    return btn

def _darken(hex_color):
    """Darken a hex color by ~15% for hover."""
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    r, g, b = max(0, r - 30), max(0, g - 30), max(0, b - 30)
    return f"#{r:02x}{g:02x}{b:02x}"


# ─────────────────────────────────────────────
#  Main Application
# ─────────────────────────────────────────────
class StudentApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Student Management System")
        self.geometry("1100x680")
        self.minsize(900, 600)
        self.resizable(True, True)

        self._dark_mode = False
        self._active_nav = "Dashboard"

        # configure ctk appearance
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self._build_ui()
        self.refresh_table()
        self._update_status()
        self._clock_tick()

    # ── LAYOUT ──────────────────────────────────────────────
    def _build_ui(self):
        self.configure(fg_color=C["bg"])
        self.grid_rowconfigure(0, weight=0)  # header
        self.grid_rowconfigure(1, weight=1)  # content
        self.grid_rowconfigure(2, weight=0)  # status bar
        self.grid_columnconfigure(0, weight=0)  # sidebar
        self.grid_columnconfigure(1, weight=1)  # main

        self._build_header()
        self._build_sidebar()
        self._build_main()
        self._build_statusbar()

    # ── HEADER ──────────────────────────────────────────────
    def _build_header(self):
        self.header = ctk.CTkFrame(self, fg_color=C["header_bg"],
                                   corner_radius=0, height=65)
        self.header.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.header.grid_propagate(False)
        self.header.grid_columnconfigure(1, weight=1)

        # icon + title
        icon_lbl = ctk.CTkLabel(self.header, text="🎓",
                                 font=ctk.CTkFont(size=30), text_color="#FFFFFF")
        icon_lbl.grid(row=0, column=0, padx=(18, 6), pady=10)

        title_lbl = ctk.CTkLabel(
            self.header, text="STUDENT MANAGEMENT SYSTEM",
            font=ctk.CTkFont(size=20, weight="bold"), text_color="#FFFFFF"
        )
        title_lbl.grid(row=0, column=1, sticky="w", pady=10)

        # dark mode toggle
        toggle_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        toggle_frame.grid(row=0, column=2, padx=18, pady=10)

        self.mode_label = ctk.CTkLabel(
            toggle_frame, text="🌙 Dark Mode",
            font=ctk.CTkFont(size=12), text_color="#FFFFFF"
        )
        self.mode_label.pack(side="left", padx=(0, 8))

        self.toggle_switch = ctk.CTkSwitch(
            toggle_frame, text="", command=self._toggle_mode,
            onvalue=True, offvalue=False,
            fg_color="#374151", progress_color="#799BFA",
            button_color="#FFFFFF", button_hover_color="#E5E7EB",
            width=46, height=24
        )
        self.toggle_switch.pack(side="left")

    # ── SIDEBAR ─────────────────────────────────────────────
    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, fg_color=C["sidebar_bg"],
                                    corner_radius=0, width=180)
        self.sidebar.grid(row=1, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)

        nav_items = [
            ("🏠", "Dashboard"),
            ("👤", "Add Student"),
            ("✏️", "Edit Record"),
            ("🗑️", "Delete Student"),
            ("📋", "Show All Records"),
        ]

        self._nav_buttons = {}
        for i, (icon, label) in enumerate(nav_items):
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"  {icon}  {label}",
                anchor="w",
                fg_color=C["sidebar_sel"] if label == self._active_nav else "transparent",
                text_color="#FFFFFF" if label == self._active_nav else C["sidebar_txt"],
                hover_color=C["sidebar_sel"],
                font=ctk.CTkFont(size=13),
                corner_radius=8,
                height=42,
                width=164,
                command=lambda l=label: self._nav_click(l)
            )
            btn.grid(row=i, column=0, padx=8, pady=(6 if i == 0 else 2, 0))
            self._nav_buttons[label] = btn

        # decorative illustration at bottom
        art = ctk.CTkLabel(self.sidebar, text="📚\n📖\n🎓",
                            font=ctk.CTkFont(size=30), text_color=C["text_sub"])
        art.grid(row=10, column=0, pady=30, sticky="s")
        self.sidebar.grid_rowconfigure(10, weight=1)

    # ── MAIN AREA ───────────────────────────────────────────
    def _build_main(self):
        self.main = ctk.CTkFrame(self, fg_color=C["bg"], corner_radius=0)
        self.main.grid(row=1, column=1, sticky="nsew", padx=0, pady=0)
        self.main.grid_rowconfigure(1, weight=1)
        self.main.grid_columnconfigure(0, weight=1)

        # ── Search bar row
        search_row = ctk.CTkFrame(self.main, fg_color="transparent")
        search_row.grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 0))
        search_row.grid_columnconfigure(0, weight=1)

        self.search_var = tk.StringVar()
        self.search_entry = ctk.CTkEntry(
            search_row, textvariable=self.search_var,
            placeholder_text="Search by Roll Number or Name",
            fg_color=C["entry_bg"], text_color=C["entry_fg"],
            border_color=C["border"], corner_radius=8, height=38,
            font=ctk.CTkFont(size=13)
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.search_entry.bind("<Return>", lambda event: self._quick_search())

        srch_btn = make_btn(search_row, "Search", C["btn_edit"],
                            self._quick_search, width=100, height=38, icon="🔍")
        srch_btn.grid(row=0, column=1)

        # ── Action buttons row
        btn_row = ctk.CTkFrame(self.main, fg_color="transparent")
        btn_row.grid(row=1, column=0, sticky="ew", padx=18, pady=10)

        make_btn(btn_row, "Add Student",    C["btn_add"],  self._open_add,  icon="＋").pack(side="left", padx=(0, 8))
        make_btn(btn_row, "Edit Record",    C["btn_edit"], self._open_edit, icon="✏️").pack(side="left", padx=(0, 8))
        make_btn(btn_row, "Delete Student", C["btn_del"],  self._open_del,  icon="🗑").pack(side="left", padx=(0, 8))
        make_btn(btn_row, "Refresh",        C["btn_ref"],  self._refresh_all, icon="↻").pack(side="left")

        # ── Table card
        card = ctk.CTkFrame(self.main, fg_color=C["card_bg"],
                             corner_radius=10, border_width=1,
                             border_color=C["border"])
        card.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 10))
        card.grid_rowconfigure(1, weight=1)
        card.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(2, weight=1)

        card_title = ctk.CTkLabel(card, text="📋  Recent Student Records",
                                  font=ctk.CTkFont(size=14, weight="bold"),
                                  text_color=C["text_main"])
        card_title.grid(row=0, column=0, sticky="w", padx=14, pady=(10, 6))
        self.card_title_ref = card_title

        # Treeview for table
        tree_frame = ctk.CTkFrame(card, fg_color="transparent")
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        cols = ("Roll No.", "Name", "Age", "Course",
                "Sem 1", "Sem 2", "Sem 3", "Sem 4", "Sem 5", "Sem 6", "%", "Grade")
        col_widths = [70, 130, 50, 70, 55, 55, 55, 55, 55, 55, 55, 55]

        style = ttk.Style()
        style.theme_use("clam")
        self._apply_tree_style(style)

        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings",
                                  selectmode="browse", style="Custom.Treeview")
        for col, w in zip(cols, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center", minwidth=40)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical",
                             command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        self.tree.tag_configure("odd",  background=C["tbl_row1"])
        self.tree.tag_configure("even", background=C["tbl_row2"])

    def _apply_tree_style(self, style):
        style.configure(
            "Custom.Treeview",
            background=C["tbl_row1"],
            foreground=C["text_main"],
            rowheight=32,
            fieldbackground=C["tbl_row1"],
            bordercolor=C["border"],
            font=("Segoe UI", 11),
        )
        style.configure(
            "Custom.Treeview.Heading",
            background=C["tbl_header"],
            foreground="#FFFFFF",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
        )
        style.map("Custom.Treeview",
                  background=[("selected", C["btn_edit"])],
                  foreground=[("selected", "#FFFFFF")])
        style.map("Custom.Treeview.Heading",
                  background=[("active", _darken(C["tbl_header"]))])

    # ── STATUS BAR ──────────────────────────────────────────
    def _build_statusbar(self):
        bar = ctk.CTkFrame(self, fg_color=C["status_bg"],
                            corner_radius=0, height=36, border_width=1,
                            border_color=C["border"])
        bar.grid(row=2, column=0, columnspan=2, sticky="ew")
        bar.grid_propagate(False)
        bar.grid_columnconfigure(1, weight=1)

        self.lbl_total = ctk.CTkLabel(bar, text="👥  Total Students: 0",
                                       font=ctk.CTkFont(size=12),
                                       text_color=C["text_sub"])
        self.lbl_total.grid(row=0, column=0, padx=18, pady=4)

        self.lbl_welcome = ctk.CTkLabel(bar, text="👤  Welcome, Mohini",
                                         font=ctk.CTkFont(size=12),
                                         text_color=C["text_sub"])
        self.lbl_welcome.grid(row=0, column=1, pady=4)

        self.lbl_time = ctk.CTkLabel(bar, text="",
                                      font=ctk.CTkFont(size=12),
                                      text_color=C["text_sub"])
        self.lbl_time.grid(row=0, column=2, padx=18, pady=4)

    # ─────────────────────────────────────────
    #  DATA / TABLE helpers
    # ─────────────────────────────────────────
    def refresh_table(self, data=None):
        for item in self.tree.get_children():
            self.tree.delete(item)
        rows = data if data is not None else get_recent_students(5)
        
        # Helper to format empty semesters as "-"
        def fmt(val): return val if val not in (None, "") else "-"

        for i, s in enumerate(rows):
            pct = calc_percentage(s)
            grade = calc_grade(pct)
            tag = "even" if i % 2 == 0 else "odd"
            self.tree.insert("", "end", values=(
                s["roll"], s["name"], s["age"], s["course"],
                fmt(s["sem1"]), fmt(s["sem2"]), fmt(s["sem3"]),
                fmt(s["sem4"]), fmt(s["sem5"]), fmt(s["sem6"]), pct, grade
            ), tags=(tag,))
        self._update_status()

    def _update_status(self):
        self.lbl_total.configure(text=f"👥  Total Students: {len(get_all_students())}")

    def _clock_tick(self):
        now = datetime.now().strftime("%I:%M %p")
        self.lbl_time.configure(text=f"🕐  {now}")
        self.after(10000, self._clock_tick)

    # ─────────────────────────────────────────
    #  Navigation
    # ─────────────────────────────────────────
    def _nav_click(self, label):
        # update button styles
        for lbl, btn in self._nav_buttons.items():
            if lbl == label:
                btn.configure(fg_color=C["sidebar_sel"], text_color="#FFFFFF")
            else:
                btn.configure(fg_color="transparent", text_color=C["sidebar_txt"])
        self._active_nav = label

        if label == "Add Student":
            self._open_add()
        elif label == "Edit Record":
            self._open_edit()
        elif label == "Delete Student":
            self._open_del()
        elif label == "Show All Records":
            self.refresh_table(get_all_students())
            self.card_title_ref.configure(text="📋  All Student Records")
        elif label == "Dashboard":
            self.refresh_table(get_recent_students(5))
            self.card_title_ref.configure(text="📋  Recent 5 Records")
        # Dashboard just shows main view (already visible)

    # ─────────────────────────────────────────
    #  Quick search (top bar)
    # ─────────────────────────────────────────
    def _quick_search(self):
        q = self.search_var.get().strip().lower()
        if not q:
            self.refresh_table(get_recent_students(5))
            self.card_title_ref.configure(text="📋  Recent 5 Records")
            return
        results = [s for s in get_all_students()
                   if q in str(s["roll"]).lower() or q in s["name"].lower()]
        self.refresh_table(results)
        self.card_title_ref.configure(text=f"🔍  Search Results for '{q}'")

    def _refresh_all(self):
        self.search_var.set("")
        self.refresh_table()

    # ─────────────────────────────────────────
    #  Modal base
    # ─────────────────────────────────────────
    def _make_modal(self, title, width=440, height=480):
        win = ctk.CTkToplevel(self)
        win.title(title)
        win.geometry(f"{width}x{height}")
        win.resizable(False, False)
        win.grab_set()
        win.configure(fg_color=C["bg"])
        # center on parent
        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - width) // 2
        y = self.winfo_y() + (self.winfo_height() - height) // 2
        win.geometry(f"+{x}+{y}")
        return win

    def _modal_header(self, parent, icon, title):
        hdr = ctk.CTkFrame(parent, fg_color=C["header_bg"], corner_radius=0, height=54)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text=f"{icon}  {title}",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color="#FFFFFF").pack(side="left", padx=18)
        return hdr

    # ─────────────────────────────────────────
    #  ADD STUDENT window
    # ─────────────────────────────────────────
    def _open_add(self):
        win = self._make_modal("Add New Student", 480, 500)
        self._modal_header(win, "👤", "Add New Student")

        body = ctk.CTkFrame(win, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=24, pady=16)

        fields_left = [
            ("Roll Number", "roll"), ("Name", "name"),
            ("Age", "age"),         ("Course (e.g. BCA)", "course"),
        ]
        marks_right = [
            ("Sem 1 %", "sem1"), ("Sem 2 %", "sem2"), ("Sem 3 %", "sem3"),
            ("Sem 4 %", "sem4"), ("Sem 5 %", "sem5"), ("Sem 6 %", "sem6")
        ]

        entries = {}

        left_col  = ctk.CTkFrame(body, fg_color="transparent")
        right_col = ctk.CTkFrame(body, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nw", padx=(0, 20))
        right_col.grid(row=0, column=1, sticky="nw")

        def make_field(parent, label, key, default="", row=0):
            ctk.CTkLabel(parent, text=label,
                         font=ctk.CTkFont(size=12),
                         text_color=C["text_main"]).grid(
                row=row, column=0, sticky="w", pady=(6, 1))
            e = ctk.CTkEntry(parent, fg_color=C["entry_bg"],
                              text_color=C["entry_fg"],
                              border_color=C["border"],
                              placeholder_text=f"Enter {label.lower()}",
                              width=160, height=32, corner_radius=6,
                              font=ctk.CTkFont(size=12))
            if default:
                e.insert(0, default)
            e.grid(row=row + 1, column=0, sticky="w")
            entries[key] = e

        for i, (lbl, key) in enumerate(fields_left):
            make_field(left_col, lbl, key, row=i * 2)

        for i, (lbl, key) in enumerate(marks_right):
            make_field(right_col, lbl, key, row=i * 2)

        # illustration
        ctk.CTkLabel(left_col, text="📚", font=ctk.CTkFont(size=48)).grid(
            row=9, column=0, pady=(10, 0))
        
        focus_order = ["roll", "name", "age", "course", "sem1", "sem2", "sem3", "sem4", "sem5", "sem6"]
        
        for i, key in enumerate(focus_order):
            if i < len(focus_order) - 1:
                next_key = focus_order[i+1]
                # Bind Enter to focus the next entry in the list
                entries[key].bind("<Return>", lambda event, nk=next_key: entries[nk].focus_set())
            else:
                # Bind Enter on the last entry (sst) to submit the form
                entries[key].bind("<Return>", lambda event: submit())
                
        # Automatically put the text cursor in the first box when the window opens
        entries["roll"].focus_set()

        # buttons
        btn_row = ctk.CTkFrame(win, fg_color="transparent")
        btn_row.pack(pady=10)

        def submit():
            try:
                roll = int(entries["roll"].get())
                name = entries["name"].get().strip()
                age  = int(entries["age"].get())
                course = entries["course"].get().strip()
                if not name or not course:
                    raise ValueError("Name/course empty")
                if any(s["roll"] == roll for s in get_all_students()):
                    messagebox.showerror("Duplicate", f"Roll {roll} already exists.", parent=win)
                    return
                
                # Handle empty semester inputs
                marks = {}
                for k in ("sem1", "sem2", "sem3", "sem4", "sem5", "sem6"):
                    val = entries[k].get().strip()
                    marks[k] = float(val) if val else None
                
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO students (roll, name, age, course, sem1, sem2, sem3, sem4, sem5, sem6)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (roll, name, age, course, marks["sem1"], marks["sem2"], marks["sem3"], marks["sem4"], marks["sem5"], marks["sem6"]))
                conn.commit()
                conn.close()
                
                self.refresh_table()
                win.destroy()
            except ValueError as ex:
                messagebox.showerror("Invalid Input", f"Please fill fields correctly (Semesters must be numbers or left blank).\n{ex}", parent=win)

        def clear_fields():
            for e in entries.values():
                e.delete(0, "end")

        make_btn(btn_row, "Submit", C["btn_submit"], submit, icon="✓").pack(
            side="left", padx=8)
        make_btn(btn_row, "Clear",  C["btn_cancel"], clear_fields, icon="✕").pack(
            side="left", padx=8)

    # ─────────────────────────────────────────
    #  EDIT RECORD — two-step
    # ─────────────────────────────────────────
    def _open_edit(self):
        # Step 1: find roll number
        win = self._make_modal("Edit Student Record", 420, 320)
        self._modal_header(win, "✏️", "Edit Student Record")

        body = ctk.CTkFrame(win, fg_color="transparent")
        body.pack(expand=True, fill="both", padx=30, pady=20)

        ctk.CTkLabel(body, text="🎓", font=ctk.CTkFont(size=60)).pack()
        ctk.CTkLabel(body, text="Enter Roll Number",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=C["text_main"]).pack(pady=(10, 4))

        roll_var = tk.StringVar()
        roll_entry = ctk.CTkEntry(body, textvariable=roll_var,
                                   placeholder_text="Enter roll number here",
                                   fg_color=C["entry_bg"], text_color=C["entry_fg"],
                                   border_color=C["border"], width=260, height=38,
                                   corner_radius=8)
        roll_entry.pack(pady=6)

        roll_entry.focus_set()
        roll_entry.bind("<Return>", lambda event: find_student())

        def find_student():
            try:
                roll = int(roll_var.get())
            except ValueError:
                messagebox.showerror("Error", "Enter a valid roll number.", parent=win)
                return
            student = next((s for s in get_all_students() if s["roll"] == roll), None)
            if not student:
                messagebox.showerror("Not Found",
                                     f"No student with Roll #{roll}.", parent=win)
                return
            win.destroy()
            self._open_edit_detail(student)

        make_btn(body, "Find Student", C["btn_find"],
                 find_student, width=180, height=38, icon="🔍").pack(pady=12)

    def _open_edit_detail(self, student):
        win = self._make_modal("Edit Student Details", 480, 440)
        self._modal_header(win, "✏️", "Edit Student Details")

        body = ctk.CTkFrame(win, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=24, pady=12)

        left = ctk.CTkFrame(body, fg_color="transparent")
        right = ctk.CTkFrame(body, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nw", padx=(0, 20))
        right.grid(row=0, column=1, sticky="nw")

        entries = {}

        def lbl_entry(parent, label, key, value, row):
            ctk.CTkLabel(parent, text=label,
                          font=ctk.CTkFont(size=12, weight="bold"),
                          text_color=C["text_sub"]).grid(
                row=row, column=0, sticky="w")
            e = ctk.CTkEntry(parent, fg_color=C["entry_bg"],
                              text_color=C["entry_fg"],
                              border_color=C["border"],
                              width=150, height=30, corner_radius=6)
            e.insert(0, str(value))
            e.grid(row=row + 1, column=0, sticky="w", pady=(0, 6))
            entries[key] = e

        def val_fmt(val): return val if val is not None else "-"

        left_fields = [
            ("Roll Number", "roll",   student["roll"]),
            ("Name",        "name",   student["name"]),
            ("Age",         "age",    student["age"]),
            ("Course",      "course", student["course"]),
        ]
        right_fields = [
            ("Sem 1 %", "sem1", val_fmt(student["sem1"])),
            ("Sem 2 %", "sem2", val_fmt(student["sem2"])),
            ("Sem 3 %", "sem3", val_fmt(student["sem3"])),
            ("Sem 4 %", "sem4", val_fmt(student["sem4"])),
            ("Sem 5 %", "sem5", val_fmt(student["sem5"])),
            ("Sem 6 %", "sem6", val_fmt(student["sem6"])),
        ]

        for i, (lbl, key, val) in enumerate(left_fields):
            lbl_entry(left, lbl, key, val, i * 2)

        for i, (lbl, key, val) in enumerate(right_fields):
            lbl_entry(right, lbl, key, val, i * 2)

        # make roll read-only
        entries["roll"].configure(state="disabled",
                                   fg_color=C["border"])
        
        edit_order = ["name", "age", "course", "sem1", "sem2", "sem3", "sem4", "sem5", "sem6"]
        
        for i, key in enumerate(edit_order):
            if i < len(edit_order) - 1:
                next_key = edit_order[i+1]
                entries[key].bind("<Return>", lambda event, nk=next_key: entries[nk].focus_set())
            else:
                entries[key].bind("<Return>", lambda event: update())
                
        # Automatically focus the first editable box
        entries["name"].focus_set()

        btn_row = ctk.CTkFrame(win, fg_color="transparent")
        btn_row.pack(pady=8)

        def update():
            try:
                name   = entries["name"].get().strip()
                age    = int(entries["age"].get())
                course = entries["course"].get().strip()
                if not name or not course:
                    raise ValueError
                # --- UPDATE SQLITE DATABASE ---
                marks = {}
                for k in ("sem1", "sem2", "sem3", "sem4", "sem5", "sem6"):
                    val = entries[k].get().strip()
                    marks[k] = float(val) if val else None
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE students SET name=?, age=?, course=?, sem1=?, sem2=?, sem3=?, sem4=?, sem5=?, sem6=?
                    WHERE roll=?
                ''', (name, age, course, marks["sem1"], marks["sem2"], marks["sem3"], marks["sem4"], marks["sem5"], marks["sem6"], student["roll"]))
                conn.commit()
                conn.close()
                
                self.refresh_table()
                win.destroy()
            except ValueError:
                messagebox.showerror("Error", "Check all fields.", parent=win)

        def delete_from_edit():
            if messagebox.askyesno("Confirm", f"Delete {student['name']}?", parent=win):
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM students WHERE roll=?", (student['roll'],))
                conn.commit()
                conn.close()
                
                self.refresh_table()
                win.destroy()

        make_btn(btn_row, "Update", C["btn_update"], update,    icon="✓").pack(side="left", padx=6)
        make_btn(btn_row, "Delete", C["btn_delete2"], delete_from_edit, icon="🗑").pack(side="left", padx=6)
        make_btn(btn_row, "Cancel", C["btn_cancel"], win.destroy, icon="✕").pack(side="left", padx=6)

    # ─────────────────────────────────────────
    #  DELETE STUDENT window
    # ─────────────────────────────────────────
    def _open_del(self):
        win = self._make_modal("Delete Student", 420, 300)
        self._modal_header(win, "🗑️", "Delete Student")

        body = ctk.CTkFrame(win, fg_color="transparent")
        body.pack(expand=True, fill="both", padx=30, pady=20)

        ctk.CTkLabel(body, text="🗑️", font=ctk.CTkFont(size=48)).pack()
        ctk.CTkLabel(body, text="Enter Roll Number to Delete",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=C["text_main"]).pack(pady=(8, 4))

        roll_var = tk.StringVar()
        del_entry = ctk.CTkEntry(body, textvariable=roll_var,
                     placeholder_text="Enter roll number",
                     fg_color=C["entry_bg"], text_color=C["entry_fg"],
                     border_color=C["border"], width=240, height=36,
                     corner_radius=8)
        del_entry.pack(pady=6)
        
        #Focus immediately and trigger delete on Enter
        del_entry.focus_set()
        del_entry.bind("<Return>", lambda event: delete())

        def delete():
            try:
                roll = int(roll_var.get())
            except ValueError:
                messagebox.showerror("Error", "Enter a valid roll number.", parent=win)
                return
            student = next((s for s in get_all_students() if s["roll"] == roll), None)
            if not student:
                messagebox.showerror("Not Found", f"No student with Roll #{roll}.", parent=win)
                return
            if messagebox.askyesno("Confirm", f"Delete '{student['name']}'?", parent=win):
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM students WHERE roll=?", (roll,))
                conn.commit()
                conn.close()
                
                self.refresh_table()
                win.destroy()

        make_btn(body, "Delete", C["btn_del"], delete,
                 width=160, height=38, icon="🗑").pack(pady=10)

    
        

    # ─────────────────────────────────────────
    #  DARK MODE TOGGLE
    # ─────────────────────────────────────────
    def _toggle_mode(self):
        global C
        self._dark_mode = not self._dark_mode
        C = DARK if self._dark_mode else LIGHT

        if self._dark_mode:
            ctk.set_appearance_mode("dark")
            self.mode_label.configure(text="☀️ Light Mode")
        else:
            ctk.set_appearance_mode("light")
            self.mode_label.configure(text="🌙 Dark Mode")

        # Rebuild UI (simplest way to recolor everything)
        for widget in self.winfo_children():
            widget.destroy()
        self._build_ui()
        self.refresh_table()
        self._update_status()
        self._clock_tick()

        if self._dark_mode:
            self.toggle_switch.select()


# ─────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = StudentApp()
    app.mainloop()