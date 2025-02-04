import cv2
import os
import numpy as np
import pickle

DATASET_DIR = "images/registered"
MODEL_PATH = "data/trained_model.yml"

def train_model():
    # Initialize face detector
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Initialize face recognizer
    recognizer = cv2.face_LBPHFaceRecognizer.create()
    
    faces = []
    labels = []
    label_map = {}
    current_label = 0
    
    print("Training model...")
    
    # Check if dataset directory exists
    if not os.path.exists(DATASET_DIR):
        print(f"Dataset directory not found: {DATASET_DIR}")
        return
    
    # Load and process images
    for img_name in os.listdir(DATASET_DIR):
        if not img_name.endswith(('.jpg', '.jpeg', '.png')):
            continue
            
        user_id = os.path.splitext(img_name)[0]
        img_path = os.path.join(DATASET_DIR, img_name)
        
        print(f"Processing image: {img_path}")
        
        # Read and convert image to grayscale
        image = cv2.imread(img_path)
        if image is None:
            print(f"Failed to load image: {img_path}")
            continue
            
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect faces with more lenient parameters
        detected_faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,  # More gradual scaling
            minNeighbors=3,   # Fewer neighbors required
            minSize=(30, 30)  # Smaller minimum face size
        )
        
        if len(detected_faces) > 0:
            (x, y, w, h) = detected_faces[0]  # Use the first detected face
            face_roi = gray[y:y+h, x:x+w]
            face_roi = cv2.resize(face_roi, (100, 100))  # Normalize size
            
            # Add face and label
            faces.append(face_roi)
            
            if user_id not in label_map:
                label_map[user_id] = current_label
                current_label += 1
                
            labels.append(label_map[user_id])
            print(f"Successfully processed user: {user_id}")
    
    if not faces:
        print("No faces found in the dataset!")
        return
    
    # Convert lists to numpy arrays
    faces = np.array(faces)
    labels = np.array(labels)
    
    print(f"Training with {len(faces)} faces...")
    
    try:
        # Train the recognizer
        recognizer.train(faces, labels)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        
        # Save the model
        recognizer.save(MODEL_PATH)
        
        # Save the label mapping
        label_map_path = os.path.join(os.path.dirname(MODEL_PATH), 'label_map.pkl')
        with open(label_map_path, 'wb') as f:
            pickle.dump(label_map, f)
        
        print(" Model trained successfully!")
        print(f"Model saved to: {MODEL_PATH}")
        print(f"Label map saved to: {label_map_path}")
        print(f"Total users trained: {len(label_map)}")
        
    except Exception as e:
        print(f"Error during training: {str(e)}")

if __name__ == "__main__":
    train_model()
    input("Press Enter to exit...")