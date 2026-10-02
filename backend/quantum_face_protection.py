import cv2
import numpy as np
from backend.pixel_scrambler import PixelScrambler
from backend.perturbation import ControlledPerturbationEngine
from backend.watermark import WatermarkEngine
from backend.metrics import MetricsEngine

class QuantumFaceProtectionEngine:
    """
    Quantum Face Protection Engine with Iterative Quality Gate (SSIM >= 0.90).
    Applies QRNG-seeded pixel scrambling, controlled high-frequency perturbations,
    and invisible watermarking without using Gaussian blur or visible pixelation.
    """

    @classmethod
    def protect_image(
        cls,
        image: np.ndarray,
        faces: list[dict],
        qrng_data: dict,
        min_ssim_threshold: float = 0.90,
        target_face_ids: list[int] = None
    ) -> tuple[np.ndarray, dict]:
        """
        Executes quantum face protection with Iterative Quality Gate optimization.
        Returns (protected_image, execution_metadata).
        """
        if image is None or not faces:
            return image.copy(), {
                'faces_detected': 0,
                'faces_protected': 0,
                'ssim': 1.0,
                'psnr': 100.0,
                'quality_gate_passed': True,
                'iterations_evaluated': 0,
                'protection_method': 'Quantum QRNG Controlled Perturbation & Scrambling'
            }

        seed = qrng_data.get('seed', 12345)
        params = qrng_data.get('parameter_sequence', [0.5] * 8)

        protected_img = image.copy()
        img_h, img_w = image.shape[:2]

        protected_count = 0
        iterations_total = 0

        for face in faces:
            face_id = face['id']
            if target_face_ids is not None and face_id not in target_face_ids:
                continue

            x, y, w, h = face['x'], face['y'], face['w'], face['h']
            x1, y1, x2, y2 = max(0, x), max(0, y), min(img_w, x + w), min(img_h, y + h)

            if x2 <= x1 or y2 <= y1:
                continue

            orig_roi = image[y1:y2, x1:x2].copy()

            # --- ITERATIVE QUALITY GATE OPTIMIZATION ---
            # Search candidate perturbation strength epsilon in [0.05, 0.03, 0.02, 0.01]
            candidate_epsilons = [0.05, 0.035, 0.02, 0.01]
            best_roi = orig_roi.copy()
            best_ssim = 0.0

            for eps in candidate_epsilons:
                iterations_total += 1
                
                # 1. Apply QRNG-Seeded Controlled Pixel Scrambling
                scrambled_roi = PixelScrambler.scramble_face_roi(
                    orig_roi, seed=seed + face_id, intensity_scale=eps * 0.8
                )

                # 2. Apply Controlled Feature Perturbation
                perturbed_roi = ControlledPerturbationEngine.apply_controlled_perturbation(
                    scrambled_roi, quantum_params=params, epsilon=eps
                )

                # 3. Embed Invisible LSB Watermark
                watermarked_roi = WatermarkEngine.embed_watermark(perturbed_roi)

                # 4. Blend ROI smoothly using Feathered Elliptical Mask
                candidate_blended = cls._blend_roi_feathered(orig_roi, watermarked_roi)

                # 5. Evaluate Quality Gate SSIM on ROI
                roi_ssim = MetricsEngine.calculate_ssim(orig_roi, candidate_blended)

                if roi_ssim >= min_ssim_threshold:
                    best_roi = candidate_blended
                    best_ssim = roi_ssim
                    break
                else:
                    # Keep track of best candidate if none strictly reach min_ssim_threshold
                    if roi_ssim > best_ssim:
                        best_ssim = roi_ssim
                        best_roi = candidate_blended

            protected_img[y1:y2, x1:x2] = best_roi
            protected_count += 1

        # Calculate final overall image metrics
        final_ssim = MetricsEngine.calculate_ssim(image, protected_img)
        final_psnr = MetricsEngine.calculate_psnr(image, protected_img)

        return protected_img, {
            'faces_detected': len(faces),
            'faces_protected': protected_count,
            'ssim': round(final_ssim, 4),
            'psnr': final_psnr,
            'quality_gate_passed': final_ssim >= min_ssim_threshold,
            'min_ssim_threshold': min_ssim_threshold,
            'iterations_evaluated': iterations_total,
            'protection_method': 'Quantum QRNG Controlled Perturbation & Scrambling'
        }

    @staticmethod
    def _blend_roi_feathered(original_roi: np.ndarray, protected_roi: np.ndarray) -> np.ndarray:
        """
        Feathered Elliptical Masking: Blends protected ROI smoothly into surrounding skin.
        """
        h, w = original_roi.shape[:2]
        if h <= 2 or w <= 2:
            return protected_roi

        mask = np.zeros((h, w), dtype=np.float32)
        center = (w // 2, h // 2)
        axes = (int(w * 0.46), int(h * 0.46))
        
        cv2.ellipse(mask, center, axes, 0, 0, 360, 1.0, -1)
        
        # Feather the mask edges
        blur_ksize = max(5, int(min(h, w) * 0.15))
        if blur_ksize % 2 == 0:
            blur_ksize += 1
        feathered_mask = cv2.GaussianBlur(mask, (blur_ksize, blur_ksize), 0)
        feathered_mask = np.expand_dims(feathered_mask, axis=2)

        blended = (protected_roi.astype(np.float32) * feathered_mask + 
                   original_roi.astype(np.float32) * (1.0 - feathered_mask))
        return np.clip(blended, 0, 255).astype(np.uint8)
