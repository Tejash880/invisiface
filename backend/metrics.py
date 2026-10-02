import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim_fn

class MetricsEngine:
    """
    Calculates actual mathematical metrics for image quality, SSIM, PSNR,
    and Privacy Protection Score.
    """

    @classmethod
    def calculate_ssim(cls, img1: np.ndarray, img2: np.ndarray) -> float:
        """
        Calculate Structural Similarity Index (SSIM) between two BGR images.
        Returns value between 0.0 and 1.0.
        """
        if img1.shape != img2.shape:
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

        score, _ = ssim_fn(gray1, gray2, full=True)
        return float(np.clip(score, 0.0, 1.0))

    @classmethod
    def calculate_psnr(cls, img1: np.ndarray, img2: np.ndarray) -> float:
        """
        Calculate Peak Signal-to-Noise Ratio (PSNR) in decibels (dB).
        """
        if img1.shape != img2.shape:
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

        mse = np.mean((img1.astype(np.float64) - img2.astype(np.float64)) ** 2)
        if mse == 0:
            return 100.0  # Infinite PSNR (identical images)

        max_pixel = 255.0
        psnr = 20.0 * np.log10(max_pixel / np.sqrt(mse))
        return float(round(psnr, 2))

    @classmethod
    def calculate_quality_preservation(cls, original: np.ndarray, anonymized: np.ndarray, faces: list[dict]) -> float:
        """
        Calculate visual quality preservation percentage.
        Evaluates background similarity outside facial bounding boxes combined with overall SSIM.
        """
        ssim_val = cls.calculate_ssim(original, anonymized)
        
        # If no faces were detected, quality preservation is 100%
        if not faces:
            return 100.0

        # Calculate non-face background SSIM
        bg_mask = np.ones(original.shape[:2], dtype=np.uint8)
        for face in faces:
            x, y, w, h = face['x'], face['y'], face['w'], face['h']
            cv2.rectangle(bg_mask, (x, y), (x + w, y + h), 0, -1)

        bg_orig = cv2.bitwise_and(original, original, mask=bg_mask)
        bg_anon = cv2.bitwise_and(anonymized, anonymized, mask=bg_mask)
        
        bg_ssim = cls.calculate_ssim(bg_orig, bg_anon)
        
        # Weighted overall quality score (80% background fidelity, 20% overall SSIM)
        quality_score = (bg_ssim * 0.8 + ssim_val * 0.2) * 100.0
        return float(round(np.clip(quality_score, 0.0, 100.0), 1))

    @classmethod
    def calculate_privacy_score(
        cls,
        original: np.ndarray,
        anonymized: np.ndarray,
        faces: list[dict],
        quantum_factor: float = 0.5,
        anonymization_method: str = "gaussian_blur"
    ) -> float:
        """
        Calculate Privacy Score from 0 to 100 based on:
        1. Facial region pixel variance difference before and after.
        2. Percentage of facial area modified.
        3. Quantum classification confidence weight.
        4. Selected anonymization algorithm strength.
        """
        if not faces:
            return 0.0  # 0 faces detected = 0 privacy modification required

        face_scores = []
        img_h, img_w = original.shape[:2]

        method_weight = {
            'mask': 1.0,
            'pixelate': 0.85,
            'identity_scramble': 0.90,
            'gaussian_blur': 0.80
        }.get(anonymization_method, 0.80)

        for face in faces:
            x, y, w, h = face['x'], face['y'], face['w'], face['h']
            x1, y1, x2, y2 = max(0, x), max(0, y), min(img_w, x + w), min(img_h, y + h)

            if x2 <= x1 or y2 <= y1:
                continue

            orig_crop = original[y1:y2, x1:x2]
            anon_crop = anonymized[y1:y2, x1:x2]

            # 1. Structural Difference in Facial ROI
            crop_ssim = cls.calculate_ssim(orig_crop, anon_crop)
            distortion = (1.0 - crop_ssim)

            # 2. Gradient / Edge alteration
            g_orig = cv2.Laplacian(cv2.cvtColor(orig_crop, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()
            g_anon = cv2.Laplacian(cv2.cvtColor(anon_crop, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()
            grad_diff = abs(g_orig - g_anon) / max(g_orig, 1.0)
            grad_factor = min(1.0, grad_diff)

            # Combined single face privacy metric
            face_privacy = (distortion * 0.7 + grad_factor * 0.3) * method_weight * 100.0
            face_scores.append(face_privacy)

        avg_face_privacy = np.mean(face_scores) if face_scores else 50.0

        # Incorporate Quantum classification weight (0.0 to 1.0)
        final_privacy = avg_face_privacy * 0.85 + (quantum_factor * 100.0) * 0.15
        return float(round(np.clip(final_privacy, 0.0, 100.0), 1))
