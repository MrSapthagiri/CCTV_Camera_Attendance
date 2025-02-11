import cv2
import numpy as np
import os
import pickle
from datetime import datetime

def load_model_and_labels():
    # Load the trained model
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    model_path = "data/trained_model.yml"
    
    if not os.path.exists(model_path):
        print("❌ No trained model found! Please train the model first.")
        return None, None
        
    recognizer.read(model_path)
    
    # Load the label mapping
    label_map_path = os.path.join(os.path.dirname(model_path), 'label_map.pkl')
    with open(label_map_path, 'rb') as f:
        label_map = pickle.load(f)
        
    # Invert the label map for recognition
    id_map = {v: k for k, v in label_map.items()}
    return recognizer, id_map

def mark_attendance(user_id):
    # Create attendance directory if it doesn't exist
    attendance_dir = "data/attendance"
    os.makedirs(attendance_dir, exist_ok=True)
    
    # Get current date for filename
    date = datetime.now().strftime("%Y-%m-%d")
    attendance_file = os.path.join(attendance_dir, f"attendance_{date}.csv")
    
    # Get current time
    time = datetime.now().strftime("%H:%M:%S")
    
    # Check if user already marked attendance today
    if os.path.exists(attendance_file):
        with open(attendance_file, 'r') as f:
            if user_id in f.read():
                print(f"❌ Attendance already marked for {user_id} today.")
                return False
    
    # Mark attendance
    with open(attendance_file, 'a') as f:
        if os.path.getsize(attendance_file) == 0:
            f.write("User ID,Time\n")
            print(f"✅ Created new attendance file for {date}.")
        f.write(f"{user_id},{time}\n")
        print(f"✅ Attendance marked for {user_id} at {time}.")
    return True

def main():
    # Load the face detection classifier
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Load the trained model and label mapping
    recognizer, id_map = load_model_and_labels()
    if recognizer is None:
        return
    
    # Initialize IP cameras (replace with your actual IP addresses and credentials)
    camera_streams = [
        
        "rtsp://Admin:Admin123@192.168.0.184:8080/h264_pcm.sdp",
    ]

    for i, stream in enumerate(camera_streams):
        try:
            cap = cv2.VideoCapture(stream)
            if not cap.isOpened():
                print(f'❌ Failed to open camera stream: {stream}')
                continue
            while True:
                try:
                    ret, frame = cap.read()
                    if not ret:
                        print("❌ Failed to grab frame from stream.")
                        break
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

                    print(f"Faces detected: {len(faces)}")

                    for (x, y, w, h) in faces:
                        # Draw rectangle around face
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        face_roi = gray[y:y+h, x:x+w]
                        face_roi = cv2.resize(face_roi, (100, 100))
                        label, confidence = recognizer.predict(face_roi)

                        user_id = id_map.get(label, "Unknown")
                        print(f"Recognized: {user_id} with confidence: {confidence}")

                        if confidence < 100:
                            print(f"Checking attendance for {user_id} with confidence: {confidence}")
                            if mark_attendance(user_id):
                                print(f"✅ Attendance marked for {user_id} with confidence: {confidence}")
                            else:
                                print(f"❌ Attendance already marked for {user_id} with confidence: {confidence}")

                    # Display the resulting frame
                    cv2.imshow(f'Camera Feed {i}', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                except Exception as e:
                    print(f"❌ Error processing frame: {e}")
        except Exception as e:
            print(f"❌ Error processing camera stream: {e}")
        finally:
            if 'cap' in locals() and cap.isOpened():
                cap.release()
    cv2.destroyAllWindows()
    print("\n👋 Attendance system stopped")

if __name__ == "__main__":
    main()