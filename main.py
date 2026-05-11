"""
main.py
-------
Entry point for the AI-Powered Face Attendance System.

Run:
    python main.py

Flow:
  1. Ensure folders exist
  2. Init SQLite database
  3. Show login window
  4. On success, open the main dashboard
"""

import os
import sys
import tkinter as tk
from tkinter import ttk

# ── Ensure project root is in path ──────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from modules.utils     import (ensure_folders, get_theme, set_theme,
                                toggle_theme, ensure_logo, styled_button,
                                notify_warning)
from modules.database  import init_db
from modules.login     import LoginWindow
from modules.register  import RegisterWindow
from modules.train_model import TrainModelWindow
from modules.attendance  import AttendanceWindow
from modules.reports     import ReportsWindow


# ════════════════════════════════════════════════════════════════════════
#  Dashboard
# ════════════════════════════════════════════════════════════════════════
class Dashboard:
    """
    Main application window.
    Shown after successful admin login.
    """

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI Face Attendance System")
        self.root.geometry("900x640")
        self.root.minsize(760, 560)
        self._apply_theme()
        self._center()
        self._build_ui()

    # ─────────────────────────────────────────
    #  Theme
    # ─────────────────────────────────────────
    def _apply_theme(self):
        t = get_theme()
        self.root.configure(bg=t["bg"])

    def _toggle_theme(self):
        new_theme = toggle_theme()
        # Simple restart-notify (full live re-theme is complex in Tkinter)
        notify_warning(
            "Theme Changed",
            f"Theme set to '{new_theme}'.\n"
            "Restart the application to apply changes fully."
        )

    # ─────────────────────────────────────────
    #  Build UI
    # ─────────────────────────────────────────
    def _build_ui(self):
        t = get_theme()

        # ── Sidebar ──────────────────────────────────────────────────
        self.sidebar = tk.Frame(self.root, bg=t["header_bg"], width=230)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo + app name
        logo_frame = tk.Frame(self.sidebar, bg=t["accent"], height=90)
        logo_frame.pack(fill="x")
        logo_frame.pack_propagate(False)

        logo_path = ensure_logo()
        try:
            from PIL import Image, ImageTk
            img = Image.open(logo_path).resize((46, 46))
            self._logo_img = ImageTk.PhotoImage(img)
            tk.Label(logo_frame, image=self._logo_img,
                     bg=t["accent"]).pack(side="left", padx=12, pady=10)
        except Exception:
            tk.Label(logo_frame, text="🎓", bg=t["accent"],
                     font=("Segoe UI", 28)).pack(side="left", padx=12)

        title_frame = tk.Frame(logo_frame, bg=t["accent"])
        title_frame.pack(side="left", fill="y", pady=12)
        tk.Label(title_frame, text="FaceAttend",
                 bg=t["accent"], fg="#FFFFFF",
                 font=("Segoe UI Semibold", 14)).pack(anchor="w")
        tk.Label(title_frame, text="Admin Panel",
                 bg=t["accent"], fg="#CCDDFF",
                 font=("Segoe UI", 9)).pack(anchor="w")

        # Navigation buttons
        nav_buttons = [
            ("📋  Register Student",  self._open_register,  t["accent"]),
            ("🧠  Train Model",        self._open_train,     "#3D3680"),
            ("📷  Mark Attendance",    self._open_attendance, t["success"]),
            ("📊  View Attendance",    self._open_reports,   "#1a6a8a"),
            ("📁  Export Reports",     self._open_reports,   "#7a3d7a"),
        ]

        tk.Label(self.sidebar, text="NAVIGATION",
                 bg=t["header_bg"], fg=t["text_muted"],
                 font=("Segoe UI", 8)).pack(anchor="w", padx=18, pady=(16, 4))

        for label, cmd, color in nav_buttons:
            b = tk.Button(
                self.sidebar, text=label, command=cmd,
                bg=t["header_bg"], fg=t["text"],
                activebackground=color,
                activeforeground="#FFFFFF",
                font=("Segoe UI", 11), relief="flat",
                cursor="hand2", anchor="w",
                padx=18, pady=10, bd=0,
            )
            b.pack(fill="x")
            b.bind("<Enter>", lambda e, b=b, c=color: b.config(bg=c, fg="#FFFFFF"))
            b.bind("<Leave>", lambda e, b=b: b.config(bg=t["header_bg"], fg=t["text"]))

        # Spacer
        tk.Frame(self.sidebar, bg=t["header_bg"]).pack(fill="both", expand=True)

        # Theme toggle
        tk.Button(
            self.sidebar, text="🌙  Toggle Theme",
            command=self._toggle_theme,
            bg=t["header_bg"], fg=t["text_muted"],
            activebackground=t["surface"],
            font=("Segoe UI", 10), relief="flat",
            cursor="hand2", anchor="w", padx=18, pady=8, bd=0,
        ).pack(fill="x")

        # Exit button
        tk.Button(
            self.sidebar, text="🚪  Exit",
            command=self.root.quit,
            bg=t["error"], fg="#FFFFFF",
            activebackground="#CC0000",
            font=("Segoe UI Semibold", 11), relief="flat",
            cursor="hand2", pady=12, bd=0,
        ).pack(fill="x")

        # ── Main content area ─────────────────────────────────────
        self.main = tk.Frame(self.root, bg=t["bg"])
        self.main.pack(side="right", fill="both", expand=True)

        self._build_home()

    def _build_home(self):
        """Welcome / stats panel."""
        t = get_theme()

        # Top bar
        topbar = tk.Frame(self.main, bg=t["surface"],
                          height=52,
                          highlightthickness=1, highlightbackground=t["border"])
        topbar.pack(fill="x")
        topbar.pack_propagate(False)
        tk.Label(topbar, text="Dashboard  /  Home",
                 bg=t["surface"], fg=t["text_muted"],
                 font=("Segoe UI", 11)).pack(side="left", padx=18)

        from datetime import datetime
        tk.Label(topbar,
                 text=datetime.now().strftime("%A, %d %B %Y"),
                 bg=t["surface"], fg=t["text_muted"],
                 font=("Segoe UI", 10)).pack(side="right", padx=18)

        # Welcome card
        content = tk.Frame(self.main, bg=t["bg"])
        content.pack(fill="both", expand=True, padx=24, pady=20)

        welcome = tk.Frame(content, bg=t["card"], pady=26, padx=30,
                           highlightthickness=1, highlightbackground=t["border"])
        welcome.pack(fill="x")

        tk.Label(welcome, text="👋  Welcome to Face Attendance System",
                 bg=t["card"], fg=t["accent"],
                 font=("Segoe UI Semibold", 16)).pack(anchor="w")
        tk.Label(welcome,
                 text=(
                     "An AI-powered attendance solution using real-time face recognition.\n"
                     "Use the sidebar to Register students, Train the model, and Mark attendance."
                 ),
                 bg=t["card"], fg=t["text_muted"],
                 font=("Segoe UI", 11), justify="left").pack(anchor="w", pady=(6, 0))

        # ── Stats cards ──
        stats_frame = tk.Frame(content, bg=t["bg"])
        stats_frame.pack(fill="x", pady=20)

        self._stat_card(stats_frame, "👤  Students", self._count_students(), t["accent"])
        self._stat_card(stats_frame, "✅  Today's Present", self._count_today(), t["success"])
        self._stat_card(stats_frame, "📅  Total Records", self._count_total(), t["warning"])

        # ── Quick action buttons ──
        qa_label = tk.Label(content, text="Quick Actions",
                            bg=t["bg"], fg=t["text"],
                            font=("Segoe UI Semibold", 13))
        qa_label.pack(anchor="w", pady=(10, 8))

        qa_frame = tk.Frame(content, bg=t["bg"])
        qa_frame.pack(fill="x")

        actions = [
            ("📋\nRegister\nStudent",  self._open_register,   t["accent"]),
            ("🧠\nTrain\nModel",        self._open_train,      "#3D3680"),
            ("📷\nMark\nAttendance",    self._open_attendance, t["success"]),
            ("📊\nView\nAttendance",    self._open_reports,    "#1a6a8a"),
            ("📁\nExport\nReports",     self._open_reports,    "#7a3d7a"),
            ("🚪\nExit",               self.root.quit,         t["error"]),
        ]

        for label, cmd, color in actions:
            b = tk.Button(
                qa_frame, text=label, command=cmd,
                bg=color, fg="#FFFFFF",
                activebackground=t["accent2"],
                activeforeground="#FFFFFF",
                font=("Segoe UI Semibold", 10),
                relief="flat", cursor="hand2",
                width=10, height=4, bd=0,
                wraplength=90,
            )
            b.pack(side="left", padx=6)

        # ── Recent attendance ──
        rec_label = tk.Label(content, text="Recent Attendance",
                             bg=t["bg"], fg=t["text"],
                             font=("Segoe UI Semibold", 13))
        rec_label.pack(anchor="w", pady=(18, 6))

        self._build_mini_table(content, t)

    def _stat_card(self, parent, label, value, color):
        t = get_theme()
        card = tk.Frame(parent, bg=t["card"], padx=20, pady=16,
                        highlightthickness=2, highlightbackground=color)
        card.pack(side="left", padx=8, expand=True, fill="x")
        tk.Label(card, text=str(value), bg=t["card"], fg=color,
                 font=("Segoe UI Semibold", 28)).pack()
        tk.Label(card, text=label, bg=t["card"], fg=t["text_muted"],
                 font=("Segoe UI", 10)).pack()

    def _build_mini_table(self, parent, t):
        from modules.database import get_attendance
        from modules.utils    import today_str

        cols    = ("Time", "Student ID", "Name", "Department")
        records = get_attendance(date=today_str())[:8]

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Mini.Treeview",
                        background=t["table_odd"],
                        foreground=t["text"],
                        rowheight=24,
                        fieldbackground=t["table_odd"],
                        font=("Segoe UI", 10))
        style.configure("Mini.Treeview.Heading",
                        background=t["card"],
                        foreground=t["accent"],
                        font=("Segoe UI Semibold", 10))
        style.map("Mini.Treeview",
                  background=[("selected", t["table_sel"])],
                  foreground=[("selected", "#FFFFFF")])

        tree = ttk.Treeview(parent, columns=cols, show="headings",
                             height=7, style="Mini.Treeview")
        col_widths = [80, 100, 180, 160]
        for col, w in zip(cols, col_widths):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor="center")

        for r in records:
            tree.insert("", "end", values=(
                r["time"], r["student_id"], r["name"], r["department"]
            ))

        if not records:
            tree.insert("", "end", values=("—", "—",
                                            "No attendance marked today", "—"))

        tree.pack(fill="x")

    # ─────────────────────────────────────────
    #  Stats helpers
    # ─────────────────────────────────────────
    def _count_students(self) -> int:
        from modules.database import get_all_students
        return len(get_all_students())

    def _count_today(self) -> int:
        from modules.database import get_attendance
        from modules.utils    import today_str
        return len(get_attendance(date=today_str()))

    def _count_total(self) -> int:
        from modules.database import get_all_attendance
        return len(get_all_attendance())

    # ─────────────────────────────────────────
    #  Window launchers
    # ─────────────────────────────────────────
    def _open_register(self):
        RegisterWindow(self.root)

    def _open_train(self):
        TrainModelWindow(self.root)

    def _open_attendance(self):
        AttendanceWindow(self.root)

    def _open_reports(self):
        ReportsWindow(self.root)

    # ─────────────────────────────────────────
    #  Helpers
    # ─────────────────────────────────────────
    def _center(self):
        self.root.update_idletasks()
        w, h = 900, 640
        x = (self.root.winfo_screenwidth()  - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def run(self):
        self.root.mainloop()


# ════════════════════════════════════════════════════════════════════════
#  Bootstrap
# ════════════════════════════════════════════════════════════════════════
def main():
    # 1. Create folders
    ensure_folders()

    # 2. Init DB
    init_db()

    # 3. Login
    login_root = tk.Tk()
    login      = LoginWindow(login_root)

    if not login.authenticated:
        # Login window was closed without authenticating
        sys.exit(0)

    # 4. Dashboard
    dashboard = Dashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
