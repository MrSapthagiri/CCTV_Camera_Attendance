import cv2
import numpy as np
import pickle
from datetime import datetime
from database import db

MODEL_PATH = 'data/trained_model.yml'
LABEL_MAP_PATH = 'data/label_map.pkl'

# Load the trained model and label map
recognizer = cv2.face.LBPHFaceRecognizer.create()
recognizer.read(MODEL_PATH)
with open(LABEL_MAP_PATH, 'rb') as f:
    label_map = pickle.load(f)

# Initialize face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Start video capture
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture image")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    detected_faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    for (x, y, w, h) in detected_faces:
        face_roi = gray[y:y+h, x:x+w]
        label_id, confidence = recognizer.predict(face_roi)

        if confidence < 100:
            user_id = list(label_map.keys())[list(label_map.values()).index(label_id)]
            attendance_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            db.mark_attendance(user_id, attendance_time)  # Function to mark attendance in the database
            cv2.putText(frame, f'{user_id} - Present', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        else:
            cv2.putText(frame, 'Unknown', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    cv2.imshow('Real-Time Attendance Monitoring', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
