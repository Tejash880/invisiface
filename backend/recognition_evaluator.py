import cv2
import numpy as np

class ControlledRecognitionEvaluator:
    """
    Evaluates controlled recognition similarity attempt between original and protected facial ROIs
    using Local Binary Pattern (LBP) histogram and structural gradient distance.
    """

    @classmethod
    def evaluate_recognition_attempt(cls, original_img: np.ndarray, protected_img: np.ndarray, faces: list[dict]) -> dict:
        """
        Calculates Identity Similarity Before (100%), Identity Similarity After (%),
        Identity Separation (%), Similarity Reduction %, and Recognition Resistance Proxy (0-100).
        """
        if not faces or original_img is None or protected_img is None:
            return {
                'status': 'Completed',
                'identity_similarity_before': 100.0,
                'identity_similarity_after': 100.0,
                'identity_separation': 0.0,
                'similarity_reduction_pct': 0.0,
                'recognition_resistance_proxy': 0.0,
                'note': 'No faces detected for recognition evaluation.'
            }

        distances = []
        img_h, img_w = original_img.shape[:2]

        for face in faces:
            x, y, w, h = face['x'], face['y'], face['w'], face['h']
            x1, y1, x2, y2 = max(0, x), max(0, y), min(img_w, x + w), min(img_h, y + h)

            if x2 <= x1 or y2 <= y1:
                continue

            orig_roi = original_img[y1:y2, x1:x2]
            prot_roi = protected_img[y1:y2, x1:x2]

            # 1. Color Space HSV Histogram Correlation Distance
            hsv_orig = cv2.cvtColor(orig_roi, cv2.COLOR_BGR2HSV)
            hsv_prot = cv2.cvtColor(prot_roi, cv2.COLOR_BGR2HSV)

            hist_orig = cv2.calcHist([hsv_orig], [0, 1], None, [16, 16], [0, 180, 0, 256])
            hist_prot = cv2.calcHist([hsv_prot], [0, 1], None, [16, 16], [0, 180, 0, 256])

            cv2.normalize(hist_orig, hist_orig, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
            cv2.normalize(hist_prot, hist_prot, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)

            corr = cv2.compareHist(hist_orig, hist_prot, cv2.HISTCMP_CORREL)
            color_dist = max(0.0, 1.0 - corr)

            # 2. High-Frequency Structural Gradient Distance
            gray_orig = cv2.cvtColor(orig_roi, cv2.COLOR_BGR2GRAY)
            gray_prot = cv2.cvtColor(prot_roi, cv2.COLOR_BGR2GRAY)

            sobel_orig = cv2.Sobel(gray_orig, cv2.CV_32F, 1, 1, ksize=3)
            sobel_prot = cv2.Sobel(gray_prot, cv2.CV_32F, 1, 1, ksize=3)

            diff_grad = np.abs(sobel_orig - sobel_prot)
            grad_dist = float(np.mean(diff_grad) / 255.0)

            # Combined identity feature distance
            combined_dist = color_dist * 0.3 + grad_dist * 0.7
            distances.append(combined_dist)

        avg_dist = float(np.mean(distances)) if distances else 0.0

        sim_before = 100.0
        sim_after = float(round(max(20.0, (1.0 - avg_dist * 2.5) * 100.0), 1))
        separation = float(round(100.0 - sim_after, 1))
        reduction_pct = float(round((separation / sim_before) * 100.0, 1))
        resistance_proxy = float(round(np.clip(separation * 1.25, 0.0, 100.0), 1))

        return {
            'status': 'Completed',
            'identity_similarity_before': sim_before,
            'identity_similarity_after': sim_after,
            'identity_separation': separation,
            'similarity_reduction_pct': reduction_pct,
            'recognition_resistance_proxy': resistance_proxy,
            'evaluation_method': 'Structural Feature Gradient & Color Space Distance'
        }
