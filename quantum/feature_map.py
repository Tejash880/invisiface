import numpy as np
import cv2

class QuantumFeatureExtractor:
    """
    Extracts normalized 4-dimensional facial feature vectors from image & face ROIs
    for encoding into Qiskit quantum circuits.
    """

    @classmethod
    def extract_face_features(cls, image: np.ndarray, faces: list[dict]) -> np.ndarray:
        """
        Extracts 4 normalized feature values in range [0, 1]:
        1. f1: Mean brightness of face ROI
        2. f2: Normalized spatial contrast (Laplacian variance)
        3. f3: Face area ratio relative to overall image
        4. f4: Normalized edge density
        """
        if image is None or image.size == 0:
            return np.array([0.5, 0.5, 0.1, 0.5], dtype=np.float64)

        img_h, img_w = image.shape[:2]
        total_area = float(img_h * img_w)

        if not faces:
            # If no face, compute whole image global stats
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            f1 = float(np.mean(gray)) / 255.0
            f2 = float(min(1.0, cv2.Laplacian(gray, cv2.CV_64F).var() / 1000.0))
            f3 = 0.05
            f4 = float(np.mean(cv2.Canny(gray, 100, 200))) / 255.0
            return np.array([f1, f2, f3, f4], dtype=np.float64)

        # Primary face analysis
        primary_face = max(faces, key=lambda f: f['w'] * f['h'])
        x, y, w, h = primary_face['x'], primary_face['y'], primary_face['w'], primary_face['h']
        
        x1, y1, x2, y2 = max(0, x), max(0, y), min(img_w, x + w), min(img_h, y + h)
        roi = image[y1:y2, x1:x2]

        if roi.size == 0:
            return np.array([0.5, 0.5, 0.1, 0.5], dtype=np.float64)

        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        # f1: Brightness
        f1 = float(np.mean(gray_roi)) / 255.0

        # f2: Spatial contrast (Laplacian var)
        lap_var = cv2.Laplacian(gray_roi, cv2.CV_64F).var()
        f2 = float(min(1.0, lap_var / 800.0))

        # f3: Face coverage ratio
        face_area = float(w * h)
        f3 = float(min(1.0, face_area / (total_area * 0.5)))

        # f4: Edge density
        edges = cv2.Canny(gray_roi, 80, 180)
        f4 = float(np.mean(edges)) / 255.0

        return np.array([f1, f2, f3, f4], dtype=np.float64)
