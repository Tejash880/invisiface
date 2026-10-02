import os
import cv2
import numpy as np
from PIL import Image
from pathlib import Path

class ImageProcessor:
    """
    Image validation, reading, metadata extraction, and safety helper.
    """
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}

    @classmethod
    def validate_file(cls, file_path: str, max_size_bytes: int = 16777216) -> tuple[bool, str]:
        """
        Validate file extension, file existence, size, and header format.
        """
        path = Path(file_path)
        if not path.exists():
            return False, "File does not exist."

        if path.suffix.lower() not in cls.ALLOWED_EXTENSIONS:
            return False, f"Unsupported file extension '{path.suffix}'. Allowed: JPG, PNG, WEBP."

        if path.stat().st_size > max_size_bytes:
            return False, f"File size exceeds limit ({max_size_bytes / (1024*1024):.1f} MB)."

        try:
            with Image.open(file_path) as img:
                img.verify()  # Verify image integrity
            return True, "Valid image."
        except Exception as e:
            return False, f"Corrupted or invalid image header: {str(e)}"

    @staticmethod
    def read_image(file_path: str) -> np.ndarray:
        """
        Read image file into OpenCV BGR numpy matrix safely.
        Handles unicode paths on Windows via np.fromfile.
        """
        try:
            img_array = np.fromfile(file_path, np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError("cv2.imdecode returned None.")
            return img
        except Exception as e:
            raise ValueError(f"Failed to read image at {file_path}: {e}")

    @staticmethod
    def save_image(img: np.ndarray, output_path: str) -> bool:
        """
        Save OpenCV image matrix to disk safely.
        """
        try:
            ext = Path(output_path).suffix.lower()
            if not ext:
                ext = '.png'
            is_success, buffer = cv2.imencode(ext, img)
            if is_success:
                with open(output_path, 'wb') as f:
                    f.write(buffer)
                return True
            return False
        except Exception as e:
            print(f"Error saving image: {e}")
            return False

    @staticmethod
    def get_metadata(file_path: str) -> dict:
        """
        Get image dimensions, format, and file size stats.
        """
        path = Path(file_path)
        file_size_kb = round(path.stat().st_size / 1024.0, 2)
        
        with Image.open(file_path) as img:
            width, height = img.size
            fmt = img.format
            mode = img.mode

        return {
            'width': width,
            'height': height,
            'size_kb': file_size_kb,
            'format': fmt,
            'mode': mode,
            'aspect_ratio': round(width / max(height, 1), 2)
        }

    @staticmethod
    def resize_for_processing(img: np.ndarray, max_dim: int = 1920) -> tuple[np.ndarray, float]:
        """
        Resize image if dimensions exceed max_dim for memory & CPU optimization.
        Returns (resized_img, scale_factor).
        """
        h, w = img.shape[:2]
        if max(h, w) <= max_dim:
            return img, 1.0

        scale = max_dim / float(max(h, w))
        new_w, new_h = int(w * scale), int(h * scale)
        resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        return resized, scale
