import tkinter as tk
from tkinter import messagebox
import sqlite3
import re

# ------------------ App Setup ------------------
root = tk.Tk()
root.title("CinemaHub")
root.geometry("420x650")
root.resizable(False, False)
root.configure(bg="#111827")

selected_movie = {}
selected_seats = []
current_user = None

# ------------------ Database Setup ------------------
def init_db():
    with sqlite3.connect("users.db") as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
        """)

    with sqlite3.connect("tickets.db") as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            movie TEXT,
            date TEXT,
            time TEXT,
            seats TEXT,
            total REAL
        )
        """)

init_db()

# ------------------ UI Helpers ------------------
def clear_screen():
    for widget in root.winfo_children():
        widget.destroy()

def title(text):
    tk.Label(
        root, text=text,
        font=("Segoe UI", 20, "bold"),
        bg="#111827", fg="white"
    ).pack(pady=20)

def button(text, command):
    return tk.Button(
        root, text=text, command=command,
        bg="#2563EB", fg="white",
        activebackground="#1D4ED8",
        font=("Segoe UI", 11),
        relief="flat", padx=14, pady=7
    )

def entry(show=None):
    return tk.Entry(
        root, width=30,
        font=("Segoe UI", 11),
        relief="flat", show=show
    )

# ------------------ Login Screen ------------------
def login_screen():
    clear_screen()
    title("Login")

    username = entry()
    password = entry(show="*")

    username.pack(pady=8)
    password.pack(pady=8)

    def login():
        global current_user
        if not username.get() or not password.get():
            messagebox.showerror("Error", "All fields required")
            return

        with sqlite3.connect("users.db") as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (username.get(), password.get())
            )
            if cur.fetchone():
                current_user = username.get()
                home_screen()
            else:
                messagebox.showerror("Error", "Invalid username or password")

    button("Login", login).pack(pady=12)

    tk.Label(
        root, text="Don't have an account?",
        bg="#111827", fg="#9CA3AF"
    ).pack(pady=10)

    button("Create account", register_screen).pack()

# ------------------ Register Screen ------------------
def register_screen():
    clear_screen()
    title("Register")

    username = entry()
    password = entry(show="*")
    confirm = entry(show="*")

    username.pack(pady=6)
    password.pack(pady=6)
    confirm.pack(pady=6)

    def register():
        if not username.get() or not password.get():
            messagebox.showerror("Error", "All fields required")
            return

        if len(password.get()) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters")
            return

        if password.get() != confirm.get():
            messagebox.showerror("Error", "Passwords do not match")
            return

        try:
            with sqlite3.connect("users.db") as conn:
                conn.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username.get(), password.get())
                )
            messagebox.showinfo("Success", "Account created successfully")
            login_screen()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")

    button("Register", register).pack(pady=12)
    button("Back to login", login_screen).pack()

# ------------------ Home Screen ------------------
def home_screen():
    clear_screen()
    title(f"Welcome, {current_user}")

    movies = [
        ("The Great Adventure", "Action", "2h 10m", 9.99),
        ("Love in London", "Romance", "1h 50m", 8.99),
        ("Space Warriors", "Sci-Fi", "2h 20m", 11.99)
    ]

    for movie in movies:
        frame = tk.Frame(root, bg="#1F2933", padx=10, pady=10)
        frame.pack(fill="x", padx=20, pady=8)

        tk.Label(frame, text=movie[0],
                 font=("Segoe UI", 12, "bold"),
                 bg="#1F2933", fg="white").pack(anchor="w")
        tk.Label(frame, text=f"{movie[1]} • {movie[2]}",
                 bg="#1F2933", fg="#9CA3AF").pack(anchor="w")
        tk.Label(frame, text=f"£{movie[3]:.2f}",
                 bg="#1F2933", fg="#10B981").pack(anchor="w")

        button("Book", lambda m=movie: movie_details(m)).pack(anchor="e")

# ------------------ Movie Details ------------------
def movie_details(movie):
    clear_screen()
    selected_movie.clear()

    selected_movie["title"] = movie[0]
    selected_movie["price"] = movie[3]

    title(movie[0])

    date_var = tk.StringVar(value="Today")
    time_var = tk.StringVar(value="18:30")

    tk.OptionMenu(root, date_var, "Today", "Tomorrow", "Saturday", "Sunday").pack()
    tk.OptionMenu(root, time_var, "16:00", "18:30", "21:00").pack(pady=10)

    def next_step():
        selected_movie["date"] = date_var.get()
        selected_movie["time"] = time_var.get()
        seat_selection()

    button("Select seats", next_step).pack(pady=30)

# ------------------ Seat Selection ------------------
def seat_selection():
    clear_screen()
    selected_seats.clear()

    title("Select Seats")

    frame = tk.Frame(root, bg="#111827")
    frame.pack()

    def toggle(btn, seat):
        if seat in selected_seats:
            selected_seats.remove(seat)
            btn.config(bg="#374151")
        else:
            selected_seats.append(seat)
            btn.config(bg="#10B981")

    rows = "ABCDE"
    for r in range(5):
        for c in range(6):
            seat = f"{rows[r]}{c+1}"
            b = tk.Button(frame, text=seat, width=5,
                          bg="#374151", fg="white")
            b.config(command=lambda s=seat, btn=b: toggle(btn, s))
            b.grid(row=r, column=c, padx=4, pady=4)

    button("Payment", payment_screen).pack(pady=20)

# ------------------ Payment Screen ------------------
def payment_screen():
    if not selected_seats:
        messagebox.showwarning("Error", "Select at least one seat")
        return

    clear_screen()
    title("Payment")

    total = len(selected_seats) * selected_movie["price"]

    tk.Label(
        root, text=f"Total: £{total:.2f}",
        bg="#111827", fg="white",
        font=("Segoe UI", 14, "bold")
    ).pack(pady=10)

    card = entry()
    expiry = entry()
    cvv = entry()

    card.insert(0, "Card Number")
    expiry.insert(0, "MM/YY")
    cvv.insert(0, "CVV")

    card.pack(pady=6)
    expiry.pack(pady=6)
    cvv.pack(pady=6)

    def confirm():
        if not re.fullmatch(r"\d{16}", card.get()):
            messagebox.showerror("Error", "Invalid card number")
            return
        if not re.fullmatch(r"\d{2}/\d{2}", expiry.get()):
            messagebox.showerror("Error", "Invalid expiry")
            return
        if not re.fullmatch(r"\d{3}", cvv.get()):
            messagebox.showerror("Error", "Invalid CVV")
            return

        with sqlite3.connect("tickets.db") as conn:
            conn.execute("""
            INSERT INTO tickets (user, movie, date, time, seats, total)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                current_user,
                selected_movie["title"],
                selected_movie["date"],
                selected_movie["time"],
                ", ".join(selected_seats),
                total
            ))

        messagebox.showinfo("Success", "Booking confirmed 🎉")
        home_screen()

    button("Confirm booking", confirm).pack(pady=20)

# ------------------ Start App ------------------
login_screen()
root.mainloop()
