import numpy as np
import cv2

class PixelScrambler:
    """
    QRNG-Seeded Identity-Sensitive ROI Pixel Scrambler.
    Applies controlled micro-scale high-frequency coordinate permutations inside facial ROIs
    guided by Qiskit Quantum Random seeds, disrupting biometric identity features while
    preserving overall human appearance, pose, skin tone, and lighting.
    """

    @classmethod
    def scramble_face_roi(cls, face_roi: np.ndarray, seed: int, intensity_scale: float = 0.05) -> np.ndarray:
        """
        Applies controlled high-frequency micro-displacement to facial ROI pixels.
        - seed: Integer derived from Qiskit QRNG 8-qubit circuit.
        - intensity_scale: 0.01 to 0.10 (keeps perturbations imperceptible).
        """
        if face_roi is None or face_roi.size == 0:
            return face_roi

        h, w, c = face_roi.shape
        scrambled = face_roi.copy().astype(np.float32)

        # Seed pseudo-random generator with true quantum seed
        rng = np.random.RandomState(seed % (2**32 - 1))

        # Generate smooth high-frequency displacement maps
        grid_x, grid_y = np.meshgrid(np.arange(w), np.arange(h))
        
        # Micro displacements bounded by intensity_scale
        max_shift = max(1.0, min(w, h) * intensity_scale)
        shift_x = rng.normal(0, max_shift * 0.3, (h, w)).astype(np.float32)
        shift_y = rng.normal(0, max_shift * 0.3, (h, w)).astype(np.float32)

        # Smooth shift maps with Gaussian filter to prevent hard pixel grid artifacts
        shift_x = cv2.GaussianBlur(shift_x, (5, 5), 0)
        shift_y = cv2.GaussianBlur(shift_y, (5, 5), 0)

        map_x = (grid_x + shift_x).astype(np.float32)
        map_y = (grid_y + shift_y).astype(np.float32)

        # Remap pixels smoothly
        scrambled_roi = cv2.remap(face_roi, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
        return scrambled_roi
