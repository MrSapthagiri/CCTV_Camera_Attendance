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
                return False
    
    # Mark attendance
    with open(attendance_file, 'a') as f:
        if os.path.getsize(attendance_file) == 0:
            f.write("User ID,Time\n")
        f.write(f"{user_id},{time}\n")
    return True

def main():
    # Load the face detection classifier
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Load the trained model and label mapping
    recognizer, id_map = load_model_and_labels()
    if recognizer is None:
        return
    
    # Initialize camera
    cam = cv2.VideoCapture(0)
    print("\n🎥 Starting attendance system...")
    print("Press 'q' to quit\n")
    
    while True:
        ret, frame = cam.read()
        if not ret:
            print("❌ Failed to grab frame")
            break
            
        # Create a copy for display
        display_frame = frame.copy()
        
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        # Process each detected face
        for (x, y, w, h) in faces:
            # Draw rectangle around face
            cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Get face ROI
            face_roi = gray[y:y+h, x:x+w]
            face_roi = cv2.resize(face_roi, (100, 100))
            
            # Predict the face
            label, confidence = recognizer.predict(face_roi)
            
            if confidence < 100:  # Lower confidence is better
                user_id = id_map.get(label, "Unknown")
                confidence_text = f"{100 - confidence:.1f}%"
                color = (0, 255, 0)  # Green
                
                # Try to mark attendance
                if mark_attendance(user_id):
                    print(f"✅ Attendance marked for {user_id}")
            else:
                user_id = "Unknown"
                confidence_text = "Unknown"
                color = (0, 0, 255)  # Red
            
            # Display name and confidence
            cv2.putText(display_frame, f"ID: {user_id}", (x, y-30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
            cv2.putText(display_frame, f"Conf: {confidence_text}", (x, y-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        # Show the frame
        cv2.imshow('Attendance System', display_frame)
        
        # Check for 'q' key to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Cleanup
    cam.release()
    cv2.destroyAllWindows()
    print("\n👋 Attendance system stopped")

if __name__ == "__main__":
    main()
