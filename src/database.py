import os
from datetime import datetime
from pymongo import MongoClient, ASCENDING
from bson import Binary
import pickle
import numpy as np

class Database:
    def __init__(self):
        try:
            # Connect to MongoDB
            self.client = MongoClient('mongodb://localhost:27017/')
            
            # Create/Get database
            self.db = self.client['attendance_system']
            
            # Get collections
            self.users = self.db['users']
            self.attendance = self.db['attendance']
            
            # Drop existing indexes to avoid conflicts
            self.users.drop_indexes()
            self.attendance.drop_indexes()
            
            # Create new indexes
            self.users.create_index([('user_id', ASCENDING)], unique=True)
            self.attendance.create_index(
                [('date', ASCENDING), ('user_id', ASCENDING)], 
                unique=True
            )
            
            print("✅ Connected to MongoDB successfully!")
            
        except Exception as e:
            print(f"❌ Error connecting to MongoDB: {str(e)}")
            print("⚠️ Please make sure MongoDB is installed and running!")

    def add_user(self, user_id, name, image_path, face_encoding=None):
        """Add a new user to the database"""
        try:
            # Read the image file as binary
            with open(image_path, 'rb') as f:
                image_data = Binary(f.read())
            
            # Convert face encoding to bytes if it exists
            if face_encoding is not None:
                if isinstance(face_encoding, np.ndarray):
                    face_encoding_bytes = Binary(pickle.dumps(face_encoding))
                else:
                    face_encoding_bytes = None
            else:
                face_encoding_bytes = None
            
            # Create user document
            user_doc = {
                'user_id': user_id,
                'name': name,
                'image_data': image_data,
                'face_encoding': face_encoding_bytes,
                'registered_date': datetime.now(),
                'last_updated': datetime.now()
            }
            
            # Check if user exists
            existing_user = self.users.find_one({'user_id': user_id})
            if existing_user:
                # Update existing user
                self.users.update_one(
                    {'user_id': user_id},
                    {'$set': user_doc}
                )
                print(f"✅ User {user_id} updated in MongoDB")
            else:
                # Insert new user
                self.users.insert_one(user_doc)
                print(f"✅ User {user_id} added to MongoDB")
            return True
            
        except Exception as e:
            print(f"❌ Error adding user to MongoDB: {str(e)}")
            return False

    def get_user(self, user_id):
        """Get user information"""
        try:
            user = self.users.find_one({'user_id': user_id})
            if user:
                # Convert Binary face_encoding back to numpy array if it exists
                if user.get('face_encoding'):
                    user['face_encoding'] = pickle.loads(user['face_encoding'])
            return user
        except Exception as e:
            print(f"❌ Error retrieving user: {str(e)}")
            return None

    def mark_attendance(self, user_id):
        """Mark attendance for a user"""
        try:
            # Get current date and time
            now = datetime.now()
            date = now.strftime("%Y-%m-%d")
            
            # Check if user exists
            user = self.get_user(user_id)
            if not user:
                print(f"❌ User {user_id} not found!")
                return False
            
            # Try to insert attendance record
            try:
                self.attendance.insert_one({
                    'user_id': user_id,
                    'date': date,
                    'time': now.strftime("%H:%M:%S"),
                    'timestamp': now
                })
                print(f"✅ Attendance marked for {user_id}")
                return True
                
            except Exception as e:
                if "duplicate key error" in str(e).lower():
                    print(f"ℹ️ Attendance already marked for {user_id} today")
                    return False
                raise e
                
        except Exception as e:
            print(f"❌ Error marking attendance: {str(e)}")
            return False

    def get_attendance(self, date=None):
        """Get attendance records for a specific date or all dates"""
        try:
            query = {'date': date} if date else {}
            
            # Get attendance records and sort by date and time
            records = list(self.attendance.aggregate([
                {'$match': query},
                {'$lookup': {
                    'from': 'users',
                    'localField': 'user_id',
                    'foreignField': 'user_id',
                    'as': 'user_info'
                }},
                {'$unwind': {'path': '$user_info', 'preserveNullAndEmptyArrays': True}},
                {'$project': {
                    'user_id': 1,
                    'date': 1,
                    'time': 1,
                    'name': '$user_info.name'
                }},
                {'$sort': {'date': -1, 'time': 1}}
            ]))
            
            return records
            
        except Exception as e:
            print(f"❌ Error retrieving attendance records: {str(e)}")
            return []

    def get_all_users(self):
        """Get all registered users"""
        try:
            return list(self.users.find({}, {
                'user_id': 1,
                'name': 1,
                'registered_date': 1,
                '_id': 0
            }).sort('registered_date', -1))
        except Exception as e:
            print(f"❌ Error retrieving users: {str(e)}")
            return []

    def get_user_stats(self, user_id):
        """Get attendance statistics for a user"""
        try:
            # Get total attendance count
            total_attendance = self.attendance.count_documents({'user_id': user_id})
            
            # Get first and last attendance
            first_attendance = self.attendance.find_one(
                {'user_id': user_id},
                sort=[('timestamp', 1)]
            )
            last_attendance = self.attendance.find_one(
                {'user_id': user_id},
                sort=[('timestamp', -1)]
            )
            
            return {
                'total_attendance': total_attendance,
                'first_attendance': first_attendance['timestamp'] if first_attendance else None,
                'last_attendance': last_attendance['timestamp'] if last_attendance else None
            }
            
        except Exception as e:
            print(f"❌ Error retrieving user stats: {str(e)}")
            return None

    def get_daily_stats(self, date=None):
        """Get daily attendance statistics"""
        try:
            query = {'date': date} if date else {}
            
            # Get total attendance for the day
            total_attendance = self.attendance.count_documents(query)
            
            # Get unique users who attended
            unique_users = len(self.attendance.distinct('user_id', query))
            
            # Get first and last attendance of the day
            first_attendance = self.attendance.find_one(
                query,
                sort=[('timestamp', 1)]
            )
            last_attendance = self.attendance.find_one(
                query,
                sort=[('timestamp', -1)]
            )
            
            return {
                'total_attendance': total_attendance,
                'unique_users': unique_users,
                'first_attendance': first_attendance['timestamp'] if first_attendance else None,
                'last_attendance': last_attendance['timestamp'] if last_attendance else None
            }
            
        except Exception as e:
            print(f"❌ Error retrieving daily stats: {str(e)}")
            return None

    def update_user(self, user_id, updates):
        """Update user information"""
        try:
            updates['last_updated'] = datetime.now()
            result = self.users.update_one(
                {'user_id': user_id},
                {'$set': updates}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"❌ Error updating user: {str(e)}")
            return False

    def get_user_attendance(self, user_id):
        """Get all attendance records for a specific user"""
        try:
            records = list(self.attendance.aggregate([
                {'$match': {'user_id': user_id}},
                {'$lookup': {
                    'from': 'users',
                    'localField': 'user_id',
                    'foreignField': 'user_id',
                    'as': 'user_info'
                }},
                {'$unwind': {'path': '$user_info', 'preserveNullAndEmptyArrays': True}},
                {'$project': {
                    'user_id': 1,
                    'date': 1,
                    'time': 1,
                    'name': '$user_info.name'
                }},
                {'$sort': {'date': -1, 'time': 1}}
            ]))
            return records
        except Exception as e:
            print(f"❌ Error retrieving user attendance: {str(e)}")
            return []

    def get_attendance_range(self, start_date, end_date):
        """Get attendance records within a date range"""
        try:
            records = list(self.attendance.aggregate([
                {'$match': {
                    'date': {
                        '$gte': start_date,
                        '$lte': end_date
                    }
                }},
                {'$lookup': {
                    'from': 'users',
                    'localField': 'user_id',
                    'foreignField': 'user_id',
                    'as': 'user_info'
                }},
                {'$unwind': {'path': '$user_info', 'preserveNullAndEmptyArrays': True}},
                {'$project': {
                    'user_id': 1,
                    'date': 1,
                    'time': 1,
                    'name': '$user_info.name'
                }},
                {'$sort': {'date': -1, 'time': 1}}
            ]))
            return records
        except Exception as e:
            print(f"❌ Error retrieving attendance range: {str(e)}")
            return []

    def get_attendance_summary(self, start_date=None, end_date=None):
        """Get attendance summary statistics"""
        try:
            match_query = {}
            if start_date and end_date:
                match_query['date'] = {
                    '$gte': start_date,
                    '$lte': end_date
                }
            
            summary = self.attendance.aggregate([
                {'$match': match_query},
                {'$group': {
                    '_id': '$date',
                    'total_attendance': {'$sum': 1},
                    'unique_users': {'$addToSet': '$user_id'}
                }},
                {'$project': {
                    'date': '$_id',
                    'total_attendance': 1,
                    'unique_users': {'$size': '$unique_users'}
                }},
                {'$sort': {'date': -1}}
            ])
            
            return list(summary)
        except Exception as e:
            print(f"❌ Error retrieving attendance summary: {str(e)}")
            return []

# Initialize database instance
db = Database()
