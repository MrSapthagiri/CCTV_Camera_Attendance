import cv2
import dlib
import os
import uuid
from dotenv import load_dotenv
from datetime import datetime
from pymongo import MongoClient
import face_recognition  # Ensure you have this library installed

# Load environment variables
load_dotenv()
database_url = os.getenv("DATABASE_URL")

# Initialize MongoDB client
client = MongoClient(database_url)
db = client['attendance_system']  # Use your database name
collection = db['employees']  # Use your collection name

# Initialize video capture
camera_found = False
for i in range(3):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        camera_found = True
        print(f"Camera opened successfully at index {i}.")
        break
    else:
        print(f"Trying camera index {i}... Camera not found.")

if not camera_found:
    print("❌ Camera not found. Please check the connection and permissions.")
    exit(1)

# Load the face detector
detector = dlib.get_frontal_face_detector()

def register_user():
    employee_name = input("Enter employee's full name: ")
    employee_id = input("Enter employee ID: ")
    attendance_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    user_id = str(uuid.uuid4())

    os.makedirs("images/registered", exist_ok=True)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to capture image from camera.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)
        for face in faces:
            cv2.rectangle(frame, (face.left(), face.top()), (face.right(), face.bottom()), (255, 0, 0), 2)
            cv2.putText(frame, employee_name, (face.left(), face.top() - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        cv2.imshow("Register User", frame)

        key = cv2.waitKey(1)
        if key == 32:  # Press space to confirm registration
            print("User registered!")

            img_path = f"images/registered/{user_id}.jpg"
            cv2.imwrite(img_path, frame)

            # Generate face encoding
            face_image = face_recognition.load_image_file(img_path)
            face_encodings = face_recognition.face_encodings(face_image)
            if not face_encodings:
                print("No face encodings found. Registration failed.")
                break
            elif len(face_encodings) > 1:
                print("Multiple face encodings found. Registration failed.")
                break
            face_encoding = face_encodings[0]  # Get the first face encoding

            # Save employee data to MongoDB
            employee_data = {
                "name": employee_name,
                "employee_id": employee_id,
                "attendance_time": attendance_time,
                "image_path": img_path,
                "face_encoding": face_encoding.tolist()  # Convert to list for MongoDB
            }
            try:
                result = collection.insert_one(employee_data)
                if result.inserted_id:
                    print("Employee data saved successfully.")
                else:
                    print("Error saving employee data: Insertion failed.")
            except MongoClient.InvalidDocument as e:
                print(f"Error saving employee data: Invalid document - {e}")
            except MongoClient.WriteConcernError as e:
                print(f"Error saving employee data: Write concern error - {e}")
            except Exception as e:
                print(f"Error saving employee data: {e}")
            break
        elif key == ord('q'):
            print("Registration canceled.")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    print("\n📸 Instructions:")
    print("1. Position your face in front of the camera.")
    print("2. Press 'space' to capture when ready.")
    print("3. Press 'q' to cancel.\n")
    register_user()