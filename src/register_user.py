import cv2
import os
import numpy as np
import pickle
from database import db

def register_user():
    # Get user details
    name = input("Enter user's full name: ")
    user_id = input("Enter User ID: ")
    
    # Create directories if they don't exist
    os.makedirs("images/registered", exist_ok=True)
    os.makedirs("data/encodings", exist_ok=True)
    
    # Initialize camera
    cam = cv2.VideoCapture(0)
    
    # Create window
    cv2.namedWindow("Registration")
    
    while True:
        ret, frame = cam.read()
        if not ret:
            print("❌ Failed to grab frame")
            break
            
        # Create a copy for display
        display_frame = frame.copy()
        
        # Get frame dimensions
        height, width = frame.shape[:2]
        
        # Define face rectangle size and position
        rect_width = int(width * 0.5)
        rect_height = int(height * 0.7)
        x = (width - rect_width) // 2
        y = (height - rect_height) // 2
        
        # Draw rectangle
        cv2.rectangle(display_frame, (x, y), (x + rect_width, y + rect_height), (0, 255, 0), 2)
        
        # Add text instructions
        cv2.putText(display_frame, user_id, (x, y - 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Show frame
        cv2.imshow("Registration", display_frame)
        
        # Handle key events
        key = cv2.waitKey(1)
        if key == 27:  # ESC
            print("\n❌ Registration cancelled")
            break
        elif key == 32:  # SPACE
            # Save the image
            img_path = f"images/registered/{user_id}.jpg"
            cv2.imwrite(img_path, frame)
            
            # Save face encoding
            try:
                # Convert to grayscale for face detection
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Initialize face detector
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                
                # Detect faces with more lenient parameters
                faces = face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=3,
                    minSize=(30, 30)
                )
                
                if len(faces) > 0:
                    # Get the first face
                    (x, y, w, h) = faces[0]
                    face_roi = gray[y:y+h, x:x+w]
                    face_roi = cv2.resize(face_roi, (100, 100))
                    
                    # Store user data in MongoDB
                    if db.add_user(user_id, name, img_path, face_roi):
                        print("\n✅ Successfully saved:")
                        print(f"   - Face image: {img_path}")
                        print(f"   - User data stored in MongoDB")
                    else:
                        print("\n❌ Failed to store user data in MongoDB")
                else:
                    print("\n❌ No face detected in the image")
                    os.remove(img_path)  # Remove the saved image
                    continue
                    
            except Exception as e:
                print(f"\n❌ Error during registration: {str(e)}")
                if os.path.exists(img_path):
                    os.remove(img_path)
                continue
                
            break
    
    # Cleanup
    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    print("\n📸 Instructions:")
    print("1. Position your face in the green rectangle")
    print("2. Press SPACE to capture when ready")
    print("3. Press ESC to cancel\n")
    register_user()
