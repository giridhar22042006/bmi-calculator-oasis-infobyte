"""
Project 2: BMI Calculator (Beginner + Advanced)
Oasis Infobyte - Python Programming Internship
<------------------------------------------------>
Features:
  -> Weight (kg) and height (cm or m) input with validation
  -> BMI calculation + WHO category classification
  -> Color-coded result display
  -> History tracking for multiple users (JSON file)
  -> Simple bar chart of last 7 BMI readings (Advanced)
  -> Runs as CLI if tkinter is unavailable

Requirements:
    Python 3.7+  (tkinter is included in standard library)
    pip install matplotlib   (optional — for trend chart)
"""

import json
import os
import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MPL_AVAILABLE = True
except ImportError:
    MPL_AVAILABLE = False

# ── Data Storage ──────────────────────────────────────────────────────────────

DATA_FILE = Path("bmi_history.json")


def load_history() -> dict:
    if DATA_FILE.exists():
        with open(DATA_FILE) as f:
            return json.load(f)
    return {}


def save_history(data: dict) -> None:
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def add_record(name: str, bmi: float, category: str) -> None:
    data = load_history()
    if name not in data:
        data[name] = []
    data[name].append({
        "bmi": round(bmi, 2),
        "category": category,
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    save_history(data)


# ── BMI Logic ─────────────────────────────────────────────────────────────────

def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    height_m = height_cm / 100
    return weight_kg / (height_m ** 2)


def classify_bmi(bmi: float) -> tuple[str, str]:
    """Returns (category label, hex color)."""
    if bmi < 18.5:
        return "Underweight", "#3B8BD4"
    elif bmi < 25.0:
        return "Normal weight", "#1D9E75"
    elif bmi < 30.0:
        return "Overweight", "#EF9F27"
    else:
        return "Obese", "#E24B4A"


# ── GUI Application ───────────────────────────────────────────────────────────

class BMIApp(tk.Tk):
    COLORS = {
        "bg": "#1a1a2e",
        "panel": "#16213e",
        "accent": "#e94560",
        "text": "#eaeaea",
        "muted": "#8892a4",
        "entry_bg": "#0f3460",
        "border": "#2a2a4a",
    }
    FONT_TITLE = ("Helvetica", 22, "bold")
    FONT_LABEL = ("Helvetica", 11)
    FONT_RESULT = ("Helvetica", 38, "bold")
    FONT_SMALL = ("Helvetica", 10)

    def __init__(self):
        super().__init__()
        self.title("BMI Calculator — Oasis Infobyte")
        self.resizable(False, False)
        self.configure(bg=self.COLORS["bg"])
        self._build_ui()
        self._center_window(480, 620)

    def _center_window(self, w: int, h: int):
        self.geometry(f"{w}x{h}")
        self.update_idletasks()
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _label(self, parent, text, font=None, color=None, **kw):
        return tk.Label(
            parent, text=text,
            font=font or self.FONT_LABEL,
            fg=color or self.COLORS["text"],
            bg=parent.cget("bg"), **kw
        )

    def _entry(self, parent):
        e = tk.Entry(
            parent, font=("Helvetica", 13),
            bg=self.COLORS["entry_bg"],
            fg=self.COLORS["text"],
            insertbackground=self.COLORS["text"],
            relief="flat", bd=8
        )
        return e

    def _build_ui(self):
        C = self.COLORS

        # Title
        title_frame = tk.Frame(self, bg=C["bg"], pady=20)
        title_frame.pack(fill="x")
        tk.Label(title_frame, text="⚖  BMI Calculator", font=self.FONT_TITLE,
                 fg=C["accent"], bg=C["bg"]).pack()
        tk.Label(title_frame, text="Body Mass Index", font=self.FONT_SMALL,
                 fg=C["muted"], bg=C["bg"]).pack()

        # Input panel
        panel = tk.Frame(self, bg=C["panel"], padx=30, pady=20,
                         highlightbackground=C["border"], highlightthickness=1)
        panel.pack(fill="x", padx=24)

        self._label(panel, "Your Name").grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.name_var = tk.StringVar()
        name_entry = self._entry(panel)
        name_entry["textvariable"] = self.name_var
        name_entry.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 12))

        self._label(panel, "Weight (kg)").grid(row=2, column=0, sticky="w", pady=(0, 4))
        self._label(panel, "Height (cm)").grid(row=2, column=1, sticky="w", padx=(16, 0), pady=(0, 4))

        self.weight_var = tk.StringVar()
        self.height_var = tk.StringVar()

        w_entry = self._entry(panel)
        w_entry["textvariable"] = self.weight_var
        w_entry.grid(row=3, column=0, sticky="ew", pady=(0, 8))

        h_entry = self._entry(panel)
        h_entry["textvariable"] = self.height_var
        h_entry.grid(row=3, column=1, sticky="ew", padx=(16, 0), pady=(0, 8))

        panel.columnconfigure(0, weight=1)
        panel.columnconfigure(1, weight=1)

        # Calculate button
        btn = tk.Button(
            self, text="Calculate BMI",
            font=("Helvetica", 13, "bold"),
            bg=C["accent"], fg="white",
            activebackground="#c73652", activeforeground="white",
            relief="flat", bd=0, pady=10, cursor="hand2",
            command=self._calculate
        )
        btn.pack(fill="x", padx=24, pady=(16, 0))

        # Result area
        result_frame = tk.Frame(self, bg=C["bg"])
        result_frame.pack(fill="x", padx=24, pady=16)

        self.bmi_label = tk.Label(result_frame, text="—", font=self.FONT_RESULT,
                                  fg=C["muted"], bg=C["bg"])
        self.bmi_label.pack()
        self.cat_label = tk.Label(result_frame, text="Enter your measurements above",
                                  font=("Helvetica", 13), fg=C["muted"], bg=C["bg"])
        self.cat_label.pack()

        # BMI scale bar
        self._build_scale_bar()

        # History button
        tk.Button(
            self, text="📊  View History & Trend",
            font=self.FONT_SMALL,
            bg=C["entry_bg"], fg=C["text"],
            activebackground=C["border"], activeforeground=C["text"],
            relief="flat", bd=0, pady=8, cursor="hand2",
            command=self._show_history
        ).pack(fill="x", padx=24, pady=(0, 16))

    def _build_scale_bar(self):
        canvas = tk.Canvas(self, height=36, bg=self.COLORS["bg"], highlightthickness=0)
        canvas.pack(fill="x", padx=40)

        segments = [
            (0, 18.5, "#3B8BD4", "Under"),
            (18.5, 25, "#1D9E75", "Normal"),
            (25, 30, "#EF9F27", "Over"),
            (30, 40, "#E24B4A", "Obese"),
        ]
        total = 40
        canvas.update_idletasks()
        W = canvas.winfo_reqwidth() or 400
        for lo, hi, color, label in segments:
            x1 = int((lo / total) * W)
            x2 = int((hi / total) * W)
            canvas.create_rectangle(x1, 8, x2, 28, fill=color, outline="")
            canvas.create_text((x1 + x2) // 2, 18, text=label,
                                font=("Helvetica", 8), fill="white")
        self.bmi_canvas = canvas
        self.bmi_marker = None

    def _update_marker(self, bmi: float):
        canvas = self.bmi_canvas
        canvas.update_idletasks()
        W = canvas.winfo_width() or 400
        clamped = max(0, min(bmi, 40))
        x = int((clamped / 40) * W)
        if self.bmi_marker:
            canvas.delete(self.bmi_marker)
        self.bmi_marker = canvas.create_polygon(
            x, 4, x - 6, 0, x + 6, 0, fill="white", outline=""
        )

    def _calculate(self):
        try:
            weight = float(self.weight_var.get())
            height = float(self.height_var.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter numeric values for weight and height.")
            return

        if not (1 <= weight <= 500):
            messagebox.showerror("Invalid Input", "Weight must be between 1 and 500 kg.")
            return
        if not (50 <= height <= 300):
            messagebox.showerror("Invalid Input", "Height must be between 50 and 300 cm.")
            return

        bmi = calculate_bmi(weight, height)
        category, color = classify_bmi(bmi)

        self.bmi_label.config(text=f"{bmi:.1f}", fg=color)
        self.cat_label.config(text=category, fg=color)
        self._update_marker(bmi)

        name = self.name_var.get().strip() or "Anonymous"
        add_record(name, bmi, category)

    def _show_history(self):
        data = load_history()
        if not data:
            messagebox.showinfo("No History", "No BMI records found yet.")
            return

        win = tk.Toplevel(self)
        win.title("BMI History")
        win.configure(bg=self.COLORS["bg"])
        win.geometry("520x460")

        tk.Label(win, text="BMI History", font=self.FONT_TITLE,
                 fg=self.COLORS["accent"], bg=self.COLORS["bg"]).pack(pady=12)

        text = tk.Text(win, bg=self.COLORS["panel"], fg=self.COLORS["text"],
                       font=("Courier", 10), relief="flat", padx=12, pady=8)
        text.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        for user, records in data.items():
            text.insert("end", f"{'─'*44}\n", "sep")
            text.insert("end", f"  {user}\n", "user")
            for r in reversed(records[-5:]):
                line = f"    {r['date']}  BMI {r['bmi']:5.1f}  {r['category']}\n"
                text.insert("end", line)

        text.tag_config("user", foreground=self.COLORS["accent"],
                        font=("Helvetica", 11, "bold"))
        text.tag_config("sep", foreground=self.COLORS["border"])
        text.config(state="disabled")

        if MPL_AVAILABLE:
            self._embed_chart(win, data)

    def _embed_chart(self, parent, data: dict):
        all_records = []
        for user, records in data.items():
            for r in records:
                all_records.append((r["date"], r["bmi"]))
        all_records.sort(key=lambda x: x[0])
        last7 = all_records[-7:]

        fig, ax = plt.subplots(figsize=(4.8, 2.2), facecolor=self.COLORS["panel"])
        ax.set_facecolor(self.COLORS["entry_bg"])
        dates = [r[0][-5:] for r in last7]
        bmis = [r[1] for r in last7]
        bars = ax.bar(dates, bmis, color=self.COLORS["accent"], width=0.5)
        ax.axhline(18.5, color="#3B8BD4", linewidth=0.8, linestyle="--")
        ax.axhline(25.0, color="#1D9E75", linewidth=0.8, linestyle="--")
        ax.axhline(30.0, color="#EF9F27", linewidth=0.8, linestyle="--")
        ax.set_ylabel("BMI", color=self.COLORS["muted"], fontsize=8)
        ax.tick_params(colors=self.COLORS["muted"], labelsize=8)
        ax.spines[:].set_color(self.COLORS["border"])
        fig.tight_layout(pad=0.5)

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", padx=16, pady=(0, 12))


# ── CLI fallback ──────────────────────────────────────────────────────────────

def cli_mode():
    print("\n" + "=" * 50)
    print("  BMI CALCULATOR — Oasis Infobyte (CLI Mode)")
    print("=" * 50)
    name = input("Your name: ").strip() or "User"
    try:
        weight = float(input("Weight (kg): "))
        height = float(input("Height (cm): "))
    except ValueError:
        print("Invalid input. Please enter numbers.")
        return
    bmi = calculate_bmi(weight, height)
    category, _ = classify_bmi(bmi)
    print(f"\n  BMI      : {bmi:.2f}")
    print(f"  Category : {category}")
    add_record(name, bmi, category)
    print("  Record saved to bmi_history.json")


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        app = BMIApp()
        app.mainloop()
    except tk.TclError:
        print("[No display found — running in CLI mode]")
        cli_mode()
