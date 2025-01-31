import cv2

class Camera:
    def __init__(self, camera_id=0):
        """Initialize camera with specified ID (default is 0 for primary camera)"""
        self.camera_id = camera_id
        self.cam = None
        self.is_running = False

    def start(self):
        """Start the camera"""
        if not self.is_running:
            self.cam = cv2.VideoCapture(self.camera_id)
            if not self.cam.isOpened():
                raise Exception("Failed to open camera")
            self.is_running = True
            return True
        return False

    def stop(self):
        """Stop the camera"""
        if self.is_running:
            self.cam.release()
            cv2.destroyAllWindows()
            self.is_running = False
            return True
        return False

    def get_frame(self):
        """Get a frame from the camera"""
        if not self.is_running:
            return None

        ret, frame = self.cam.read()
        if not ret:
            return None
        return frame

    def show_frame(self, frame, window_name='Camera'):
        """Display a frame in a window"""
        cv2.imshow(window_name, frame)
        return cv2.waitKey(1) & 0xFF

    def capture_image(self):
        """Capture a single image"""
        if not self.is_running:
            self.start()
        
        ret, frame = self.cam.read()
        if not ret:
            return None
        return frame

    @staticmethod
    def save_image(image, path):
        """Save an image to specified path"""
        return cv2.imwrite(path, image)

    @staticmethod
    def list_cameras():
        """List available cameras"""
        available_cameras = []
        for i in range(10):  # Check first 10 camera indices
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available_cameras.append(i)
                cap.release()
        return available_cameras

    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()
