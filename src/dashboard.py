import tkinter as tk
from tkinter import ttk, messagebox
from database import db
from datetime import datetime, timedelta
import pandas as pd

class AttendanceDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Attendance System Dashboard")
        self.root.geometry("800x600")
        
        # Create main container
        self.main_container = ttk.Frame(self.root, padding="10")
        self.main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create tabs
        self.tab_control = ttk.Notebook(self.main_container)
        
        # Attendance Tab
        self.attendance_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.attendance_tab, text='Attendance Records')
        
        # Users Tab
        self.users_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.users_tab, text='Registered Users')
        
        self.tab_control.pack(expand=1, fill="both")
        
        # Initialize tabs
        self.setup_attendance_tab()
        self.setup_users_tab()
        
        # Load initial data
        self.load_attendance_data()
        self.load_users_data()

    def setup_attendance_tab(self):
        # Date Filter Frame
        filter_frame = ttk.LabelFrame(self.attendance_tab, text="Filter", padding="5")
        filter_frame.pack(fill="x", padx=5, pady=5)
        
        # Date selection
        ttk.Label(filter_frame, text="Date:").pack(side="left", padx=5)
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.date_entry = ttk.Entry(filter_frame, textvariable=self.date_var)
        self.date_entry.pack(side="left", padx=5)
        
        # Filter buttons
        ttk.Button(filter_frame, text="Today", command=lambda: self.set_date_filter("today")).pack(side="left", padx=2)
        ttk.Button(filter_frame, text="Yesterday", command=lambda: self.set_date_filter("yesterday")).pack(side="left", padx=2)
        ttk.Button(filter_frame, text="This Week", command=lambda: self.set_date_filter("week")).pack(side="left", padx=2)
        ttk.Button(filter_frame, text="All", command=lambda: self.set_date_filter("all")).pack(side="left", padx=2)
        ttk.Button(filter_frame, text="Refresh", command=self.load_attendance_data).pack(side="right", padx=5)
        
        # Attendance Table
        table_frame = ttk.Frame(self.attendance_tab)
        table_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create Treeview
        self.attendance_tree = ttk.Treeview(table_frame, columns=("Date", "Time", "User ID", "Name"), show="headings")
        
        # Set column headings
        self.attendance_tree.heading("Date", text="Date")
        self.attendance_tree.heading("Time", text="Time")
        self.attendance_tree.heading("User ID", text="User ID")
        self.attendance_tree.heading("Name", text="Name")
        
        # Set column widths
        self.attendance_tree.column("Date", width=100)
        self.attendance_tree.column("Time", width=100)
        self.attendance_tree.column("User ID", width=100)
        self.attendance_tree.column("Name", width=200)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.attendance_tree.yview)
        self.attendance_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack the table and scrollbar
        self.attendance_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def setup_users_tab(self):
        # Users Table Frame
        table_frame = ttk.Frame(self.users_tab)
        table_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create Treeview
        self.users_tree = ttk.Treeview(table_frame, columns=("User ID", "Name", "Registration Date"), show="headings")
        
        # Set column headings
        self.users_tree.heading("User ID", text="User ID")
        self.users_tree.heading("Name", text="Name")
        self.users_tree.heading("Registration Date", text="Registration Date")
        
        # Set column widths
        self.users_tree.column("User ID", width=100)
        self.users_tree.column("Name", width=200)
        self.users_tree.column("Registration Date", width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack the table and scrollbar
        self.users_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Refresh button
        ttk.Button(self.users_tab, text="Refresh", command=self.load_users_data).pack(pady=5)

    def set_date_filter(self, filter_type):
        today = datetime.now()
        if filter_type == "today":
            self.date_var.set(today.strftime("%Y-%m-%d"))
        elif filter_type == "yesterday":
            yesterday = today - timedelta(days=1)
            self.date_var.set(yesterday.strftime("%Y-%m-%d"))
        elif filter_type == "week":
            self.date_var.set("week")
        elif filter_type == "all":
            self.date_var.set("")
        self.load_attendance_data()

    def load_attendance_data(self):
        # Clear existing items
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)
        
        try:
            # Get date filter
            date_filter = self.date_var.get()
            if date_filter == "week":
                # Get this week's attendance
                today = datetime.now()
                week_start = today - timedelta(days=today.weekday())
                records = []
                for i in range(7):
                    date = week_start + timedelta(days=i)
                    date_str = date.strftime("%Y-%m-%d")
                    records.extend(db.get_attendance(date_str))
            else:
                # Get attendance for specific date or all dates
                records = db.get_attendance(date_filter if date_filter else None)
            
            # Insert records into tree
            for record in records:
                self.attendance_tree.insert("", "end", values=(
                    record.get('date', ''),
                    record.get('time', ''),
                    record.get('user_id', ''),
                    record.get('name', '')
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load attendance data: {str(e)}")

    def load_users_data(self):
        # Clear existing items
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        try:
            # Get all users
            users = db.get_all_users()
            
            # Insert users into tree
            for user in users:
                self.users_tree.insert("", "end", values=(
                    user.get('user_id', ''),
                    user.get('name', ''),
                    user.get('registered_date', '').strftime("%Y-%m-%d %H:%M") if user.get('registered_date') else ''
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load users data: {str(e)}")

def main():
    root = tk.Tk()
    app = AttendanceDashboard(root)
    root.mainloop()

if __name__ == "__main__":
    main()
