import pandas as pd
from datetime import datetime
from database import db
from tabulate import tabulate

tolerance_value = 0.1  # 10% tolerance

def view_attendance(date=None):
    """View attendance records for a specific date or all dates"""
    records = db.get_attendance(date)
    
    if not records:
        print(f"❌ No attendance records found{' for ' + date if date else ''}!")
        return
    
    # Convert records to DataFrame for better display
    df = pd.DataFrame(records)
    
    if date:
        print(f"\n📊 Attendance for {date}:")
    else:
        print("\n📊 All Attendance Records:")
    
    # Format the DataFrame
    df = df[['date', 'time', 'name', 'user_id']]  # Reorder columns
    df.columns = ['Date', 'Time', 'Name', 'User ID']  # Rename columns
    
    # Display using tabulate for better formatting
    print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))
    print(f"\nTotal Records: {len(df)}")
    
    # Calculate attendance percentage
    expected_attendance = len(db.get_all_users())
    actual_attendance = len(df)
    
    # Check if attendance is within acceptable limits
    if abs(actual_attendance - expected_attendance) <= tolerance_value * expected_attendance:
        print(f"Attendance is within acceptable limits ({(actual_attendance / expected_attendance) * 100:.2f}%).")
    else:
        print(f"Attendance is outside acceptable limits ({(actual_attendance / expected_attendance) * 100:.2f}%).")

def view_users():
    """View all registered users"""
    users = db.get_all_users()
    
    if not users:
        print("❌ No users registered!")
        return
    
    df = pd.DataFrame(users)
    df.columns = ['User ID', 'Name']
    
    print("\n👥 Registered Users:")
    print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))
    print(f"\nTotal Users: {len(df)}")

def main():
    while True:
        print("\n👥 Attendance Management System")
        print("1. View today's attendance")
        print("2. View specific date")
        print("3. View all attendance records")
        print("4. View registered users")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == "1":
            today = datetime.now().strftime("%Y-%m-%d")
            view_attendance(today)
        
        elif choice == "2":
            date = input("Enter date (YYYY-MM-DD): ")
            try:
                datetime.strptime(date, "%Y-%m-%d")
                view_attendance(date)
            except ValueError:
                print("❌ Invalid date format! Use YYYY-MM-DD")
        
        elif choice == "3":
            view_attendance()
        
        elif choice == "4":
            view_users()
        
        elif choice == "5":
            print("\n👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice! Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
