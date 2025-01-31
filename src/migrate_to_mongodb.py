import os
import csv
from datetime import datetime
from database import db

def migrate_users():
    """Migrate users from images directory to MongoDB"""
    print("\n🔄 Migrating users...")
    images_dir = "images/registered"
    
    if not os.path.exists(images_dir):
        print("❌ No registered users found!")
        return
    
    success_count = 0
    for img_name in os.listdir(images_dir):
        if not img_name.endswith(('.jpg', '.jpeg', '.png')):
            continue
            
        user_id = os.path.splitext(img_name)[0]
        image_path = os.path.join(images_dir, img_name)
        
        # Add user to MongoDB
        if db.add_user(user_id, user_id, image_path):
            success_count += 1
            
    print(f"✅ Successfully migrated {success_count} users to MongoDB")

def migrate_attendance():
    """Migrate attendance records from CSV files to MongoDB"""
    print("\n🔄 Migrating attendance records...")
    attendance_dir = "data/attendance"
    
    if not os.path.exists(attendance_dir):
        print("❌ No attendance records found!")
        return
    
    success_count = 0
    for file_name in os.listdir(attendance_dir):
        if not file_name.startswith('attendance_') or not file_name.endswith('.csv'):
            continue
            
        date = file_name.replace('attendance_', '').replace('.csv', '')
        file_path = os.path.join(attendance_dir, file_name)
        
        try:
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    user_id = row['User ID']
                    time = row['Time']
                    
                    # Create timestamp
                    timestamp = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M:%S")
                    
                    # Add attendance record to MongoDB
                    try:
                        db.attendance.insert_one({
                            'user_id': user_id,
                            'date': date,
                            'time': time,
                            'timestamp': timestamp
                        })
                        success_count += 1
                    except Exception as e:
                        if "duplicate key error" not in str(e).lower():
                            print(f"❌ Error adding attendance for {user_id} on {date}: {str(e)}")
                            
        except Exception as e:
            print(f"❌ Error processing file {file_name}: {str(e)}")
    
    print(f"✅ Successfully migrated {success_count} attendance records to MongoDB")

def main():
    print("📊 Starting data migration to MongoDB...")
    
    try:
        # Test MongoDB connection
        db.users.find_one()
        print("✅ Connected to MongoDB successfully!")
        
        # Migrate data
        migrate_users()
        migrate_attendance()
        
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error connecting to MongoDB: {str(e)}")
        print("\n⚠️ Please make sure MongoDB is installed and running!")
        print("Installation instructions:")
        print("1. Download MongoDB Community Server from:")
        print("   https://www.mongodb.com/try/download/community")
        print("2. Run the installer and follow the installation steps")
        print("3. Make sure the MongoDB service is running")
        print("4. Try running this script again")

if __name__ == "__main__":
    main()
