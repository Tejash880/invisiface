import cv2
import numpy as np

class FaceAnonymizer:
    """
    Privacy-preserving face anonymization engine with natural appearance preservation.
    Supports Gaussian Blur, Pixelation, Masking, and Identity Transformation.
    Uses elliptical feather-blended masks for seamless skin/lighting continuity.
    """

    @classmethod
    def anonymize_image(
        cls,
        image: np.ndarray,
        faces: list[dict],
        method: str = "gaussian_blur",
        intensity: int = 75,
        target_face_ids: list[int] = None
    ) -> np.ndarray:
        """
        Anonymize specified faces in the image matrix.
        - method: 'gaussian_blur', 'pixelate', 'mask', 'identity_scramble'
        - intensity: 1 to 100 (maps to kernel/block sizes)
        - target_face_ids: None means anonymize all detected faces.
        """
        if image is None or not faces:
            return image.copy()

        output = image.copy()
        
        for face in faces:
            face_id = face['id']
            if target_face_ids is not None and face_id not in target_face_ids:
                continue

            x, y, w, h = face['x'], face['y'], face['w'], face['h']

            # Ensure bounding box is strictly within image boundaries
            img_h, img_w = image.shape[:2]
            x1, y1 = max(0, x), max(0, y)
            x2, y2 = min(img_w, x + w), min(img_h, y + h)

            if x2 <= x1 or y2 <= y1:
                continue

            face_roi = output[y1:y2, x1:x2]

            # Apply requested anonymization transform to ROI
            if method == "pixelate":
                anonymized_roi = cls._apply_pixelation(face_roi, intensity)
            elif method == "mask":
                anonymized_roi = cls._apply_masking(face_roi)
            elif method == "identity_scramble":
                anonymized_roi = cls._apply_identity_scramble(face_roi, intensity)
            else:  # Default to gaussian_blur
                anonymized_roi = cls._apply_gaussian_blur(face_roi, intensity)

            # Feathered Elliptical Mask Blending for Natural Skin & Lighting Preservation
            output[y1:y2, x1:x2] = cls._blend_roi_feathered(face_roi, anonymized_roi)

        return output

    @staticmethod
    def _apply_gaussian_blur(roi: np.ndarray, intensity: int) -> np.ndarray:
        """Apply adaptive Gaussian blur based on intensity (1-100)."""
        h, w = roi.shape[:2]
        # Map intensity 1-100 to odd kernel size between 15 and 99
        k_size = int(15 + (intensity / 100.0) * (min(h, w, 150) - 15))
        if k_size % 2 == 0:
            k_size += 1
        k_size = max(15, k_size)
        return cv2.GaussianBlur(roi, (k_size, k_size), 0)

    @staticmethod
    def _apply_pixelation(roi: np.ndarray, intensity: int) -> np.ndarray:
        """Apply block pixelation based on intensity (1-100)."""
        h, w = roi.shape[:2]
        # Map intensity 1-100 to block size
        blocks = max(4, int(35 - (intensity / 100.0) * 30))
        # Downscale then upscale
        small = cv2.resize(roi, (max(1, w // blocks), max(1, h // blocks)), interpolation=cv2.INTER_LINEAR)
        return cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)

    @staticmethod
    def _apply_masking(roi: np.ndarray) -> np.ndarray:
        """Apply a sleek privacy dark shield mask over ROI."""
        mask_color = np.array([25, 20, 15], dtype=np.uint8)
        return np.full_like(roi, mask_color)

    @staticmethod
    def _apply_identity_scramble(roi: np.ndarray, intensity: int) -> np.ndarray:
        """
        Advanced Identity Scrambling Transformation:
        Combines edge-preserving bilateral filtering, high-frequency noise injection,
        and localized color-space perturbation to distort identity embeddings while preserving
        overall head geometry and lighting cues.
        """
        h, w = roi.shape[:2]
        # 1. Bilateral filter to smooth fine biometric features
        d = int(9 + (intensity / 100.0) * 15)
        sigma = int(75 + (intensity / 100.0) * 75)
        smooth = cv2.bilateralFilter(roi, d, sigma, sigma)

        # 2. Inject controlled feature noise
        noise_level = (intensity / 100.0) * 35.0
        noise = np.random.normal(0, noise_level, smooth.shape).astype(np.float32)
        scrambled = np.clip(smooth.astype(np.float32) + noise, 0, 255).astype(np.uint8)

        # 3. Micro-blur for edge harmonization
        return cv2.GaussianBlur(scrambled, (7, 7), 0)

    @staticmethod
    def _blend_roi_feathered(original_roi: np.ndarray, anonymized_roi: np.ndarray) -> np.ndarray:
        """
        Feathered Elliptical Masking:
        Creates an ellipse mask inside ROI and applies Gaussian blur to the mask boundary,
        ensuring smooth, natural blending into surrounding cheeks, forehead, and hair.
        """
        h, w = original_roi.shape[:2]
        if h <= 2 or w <= 2:
            return anonymized_roi

        mask = np.zeros((h, w), dtype=np.float32)
        center = (w // 2, h // 2)
        axes = (int(w * 0.48), int(h * 0.48))
        
        cv2.ellipse(mask, center, axes, 0, 0, 360, 1.0, -1)
        
        # Feather the mask edges using blur
        blur_ksize = max(5, int(min(h, w) * 0.2))
        if blur_ksize % 2 == 0:
            blur_ksize += 1
        feathered_mask = cv2.GaussianBlur(mask, (blur_ksize, blur_ksize), 0)
        feathered_mask = np.expand_dims(feathered_mask, axis=2)

        blended = (anonymized_roi.astype(np.float32) * feathered_mask + 
                   original_roi.astype(np.float32) * (1.0 - feathered_mask))
        return np.clip(blended, 0, 255).astype(np.uint8)
