import cv2
import numpy as np
from PIL import Image
from pathlib import Path
from backend.face_detector import FaceDetector

class ImagePreprocessor:
    """
    Image Preprocessing Pipeline:
    1. Read Image
    2. Resize (if max dimension exceeds processing limits while keeping aspect ratio)
    3. Face Detection (Single / Multi-face support)
    4. ROI Extraction & Bounding Box Recording
    """
    def __init__(self):
        self.detector = FaceDetector()

    def preprocess_image(self, file_path: str) -> dict:
        """
        Executes full preprocessing pipeline on input file.
        Returns dict with original image matrix, faces metadata, ROI matrices, and dimensions.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Image at {file_path} not found.")

        # 1. Read Image Matrix
        img_array = np.fromfile(str(path), np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError(f"Failed to decode image at {file_path}")

        h, w = img.shape[:2]

        # 2. Safe Processing Resize (Preserves original dimensions)
        scale_factor = 1.0
        max_dim = 1920
        if max(h, w) > max_dim:
            scale_factor = max_dim / float(max(h, w))
            proc_w, proc_h = int(w * scale_factor), int(h * scale_factor)
            proc_img = cv2.resize(img, (proc_w, proc_h), interpolation=cv2.INTER_AREA)
        else:
            proc_img = img.copy()

        # 3. Face Detection & Bounding Box Coordinates
        faces = self.detector.detect_faces(proc_img)

        # Scale coordinates back if resized
        if scale_factor != 1.0:
            for face in faces:
                face['x'] = int(face['x'] / scale_factor)
                face['y'] = int(face['y'] / scale_factor)
                face['w'] = int(face['w'] / scale_factor)
                face['h'] = int(face['h'] / scale_factor)

        # 4. Extract Face ROIs
        rois = []
        for face in faces:
            x, y, fw, fh = face['x'], face['y'], face['w'], face['h']
            x1, y1 = max(0, x), max(0, y)
            x2, y2 = min(w, x + fw), min(h, y + fh)
            if x2 > x1 and y2 > y1:
                rois.append(img[y1:y2, x1:x2])

        return {
            'image': img,
            'width': w,
            'height': h,
            'faces': faces,
            'face_count': len(faces),
            'rois': rois,
            'scale_factor': scale_factor
        }
