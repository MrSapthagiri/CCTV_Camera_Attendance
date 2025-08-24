 # Camera Attendance System

A Python-based facial recognition attendance system that uses your computer's webcam to register users and mark attendance.

## Prerequisites

### Python Version Compatibility
- **Recommended**: Python 3.8 - 3.11
- **Minimum**: Python 3.8
- **Tested on**: Python 3.11.4
- **Not Compatible**: Python 2.x, Python 3.7 or lower

### System Requirements
- **Operating System**:
  - Windows 10/11 (Recommended)
  - Ubuntu 20.04 or higher
  - macOS 10.15 or higher
- **Hardware**:
  - CPU: Intel Core i3/AMD Ryzen 3 or better
  - RAM: 4GB minimum (8GB recommended)
  - Storage: 1GB free space
  - Webcam: 720p or higher resolution
- **Additional Software**:
  - Git (optional, for version control)
  - Visual Studio Code (recommended IDE)

##  Detailed Installation Guide

1. **Check Python Version**
   ```bash
   python --version
   ```
   If Python is not installed or version is incorrect, download from:
   https://www.python.org/downloads/

2. **Create Project Directory**
   ```bash
   # Windows
   mkdir "Camera Attendance System"
   cd "Camera Attendance System"

   # Linux/Mac
   mkdir Camera_Attendance_System
   cd Camera_Attendance_System
   ```

3. **Create and Activate Virtual Environment**
   ```bash
   # Windows
   python -m venv .venv
   .\.venv\Scripts\activate

   # Linux/Mac
   python3 -m venv .venv
   source .venv/bin/activate
   ```
   
   After activation, you should see (.venv) at the start of your command prompt

4. **Verify Pip Version**
   ```bash
   python -m pip --version
   python -m pip install --upgrade pip
   ```

5. **Install Required Packages**
   ```bash
   # Install wheel first (prevents some compilation issues)
   pip install wheel

   # Install all required packages
   pip install -r requirements.txt
   ```

   If you encounter any errors:
   ```bash
   # Try installing packages individually
   pip install opencv-python==4.8.1.78
   pip install opencv-contrib-python==4.8.1.78
   pip install numpy==1.24.3
   pip install pymongo==4.5.0
   pip install Pillow==10.0.0
   ```

### Package Details
- **opencv-python**: Core OpenCV functionality
- **opencv-contrib-python**: Extra OpenCV modules
- **numpy**: Numerical computations
- **pymongo**: MongoDB database operations
- **Pillow**: Image processing

##  MongoDB Setup and Configuration

### Installing MongoDB
1. **Download MongoDB Community Server**
   - Visit: https://www.mongodb.com/try/download/community
   - Select "Windows" as platform
   - Click "Download"

2. **Install MongoDB**
   - Run the downloaded .msi installer
   - Choose "Complete" installation
   - Install MongoDB Compass (GUI tool) when prompted
   - Complete the installation

3. **Verify MongoDB Installation**
   ```bash
   # Check MongoDB service status
   Get-Service MongoDB
   ```
   The status should show as "Running"

### MongoDB Configuration
1. **Default Connection Settings**
   - Host: localhost
   - Port: 27017
   - Database: attendance_system
   - Collections: 
     - users: Stores user information and face encodings
     - attendance: Stores attendance records

2. **Using MongoDB Compass**
   - Launch MongoDB Compass
   - Connect using: `mongodb://localhost:27017`
   - Navigate to `attendance_system` database
   - View/manage users and attendance records

### Data Migration
To migrate existing data from files to MongoDB:
```bash
python src/migrate_to_mongodb.py
```

This will:
- Transfer registered users to MongoDB
- Move attendance records to MongoDB
- Preserve all existing data

### MongoDB Data Structure

1. **Users Collection**
   ```json
   {
     "user_id": "string",
     "name": "string",
     "image_data": "binary",
     "face_encoding": "binary",
     "registered_date": "datetime",
     "last_updated": "datetime"
   }
   ```

2. **Attendance Collection**
   ```json
   {
     "user_id": "string",
     "date": "string (YYYY-MM-DD)",
     "time": "string (HH:MM:SS)",
     "timestamp": "datetime"
   }
   ```

### Troubleshooting MongoDB

1. **MongoDB Service Not Running**
   ```bash
   # Start MongoDB service
   Start-Service MongoDB
   ```

2. **Connection Issues**
   - Verify MongoDB is running
   - Check if port 27017 is available
   - Ensure firewall allows MongoDB connections

3. **Common Error Solutions**
   - "Connection refused": Start MongoDB service
   - "Authentication failed": Check connection string
   - "Duplicate key": Record already exists

##  Detailed Project Structure

```
Camera Attendance System/
├── .venv/                  # Virtual environment directory
├── data/
│   ├── encodings/          # Face encoding files (.pkl)
│   └── trained_model.yml   # Trained face recognition model
├── images/
│   └── registered/         # User face images (.jpg)
├── src/
│   ├── __init__.py
│   ├── register_user.py    # User registration script
│   ├── train_model.py      # Model training script
│   ├── main.py            # Main attendance system
│   ├── camera.py          # Camera handling
│   ├── database.py        # Database operations
│   ├── face_recognition.py # Face recognition logic
│   └── migrate_to_mongodb.py # Data migration script
├── requirements.txt        # Package dependencies
└── README.md              # This documentation
```

##  Detailed Usage Guide

1. **First-Time Setup**
   ```bash
   # 1. Activate virtual environment (if not already activated)
   .\.venv\Scripts\activate  # Windows
   source .venv/bin/activate # Linux/Mac

   # 2. Verify installation
   python -c "import cv2; print(cv2.__version__)"
   ```

2. **Register New Users**
   ```bash
   python src/register_user.py
   ```
   Tips for registration:
   - Use a well-lit room
   - Look directly at the camera
   - Keep a neutral expression
   - Avoid wearing hats or glasses
   - Stay about 2 feet from the camera

3. **Train the Model**
   ```bash
   python src/train_model.py
   ```
   The training process:
   - Loads all registered face images
   - Creates face encodings
   - Saves model to data/trained_model.yml
   - Creates a label mapping file

4. **Run Attendance System**
   ```bash
   python src/main.py
   ```
   The system will:
   - Initialize camera
   - Load trained model
   - Start face detection
   - Record attendance when faces are recognized

##  Common Issues and Solutions

1. **Camera Not Found**
   ```bash
   # Check available cameras
   python -c "import cv2; print([i for i in range(10) if cv2.VideoCapture(i).read()[0]])"
   ```

2. **Package Installation Fails**
   ```bash
   # Update pip
   python -m pip install --upgrade pip

   # Install build tools (Windows)
   pip install --upgrade setuptools wheel
   ```

3. **OpenCV Import Error**
   ```bash
   # Try reinstalling
   pip uninstall opencv-python opencv-contrib-python
   pip install opencv-python==4.8.1.78 opencv-contrib-python==4.8.1.78
   ```

##  Development Tips

- Use Visual Studio Code with Python extension
- Install pylint for code quality
- Use Git for version control
- Keep Python and packages updated
- Test in different lighting conditions

##  Security Notes

- Face images are stored locally
- Encodings are saved as encrypted pickle files
- User data is protected in local storage
- No cloud services are used
- Camera access is required

##  Getting Help

If you encounter issues:
1. Check Python version compatibility
2. Verify all packages are installed correctly
3. Ensure camera permissions are granted
4. Check system requirements
5. Try reinstalling in a new virtual environment

For developers:
- API documentation is in the code comments
- Each module has specific error handling
- Logging is available for debugging
- Test scripts are provided
