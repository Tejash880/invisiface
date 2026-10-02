import numpy as np
import cv2

class ControlledPerturbationEngine:
    """
    Injects high-frequency, imperceptible adversarial noise into facial ROIs
    guided by Qiskit Quantum Random bit parameters to shift automated identity representations.
    """

    @classmethod
    def apply_controlled_perturbation(
        cls,
        face_roi: np.ndarray,
        quantum_params: list[float],
        epsilon: float = 0.03
    ) -> np.ndarray:
        """
        Applies controlled high-pass feature noise to facial ROI.
        - quantum_params: List of float values derived from Qiskit QRNG measurement bitstream.
        - epsilon: Perturbation magnitude (0.01 to 0.08, keeping visual changes imperceptible).
        """
        if face_roi is None or face_roi.size == 0:
            return face_roi

        h, w, c = face_roi.shape
        roi_float = face_roi.astype(np.float32)

        # 1. Extract High-Pass Feature Gradients (Laplacian / Sobolev edges)
        gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        grad_mag = cv2.magnitude(grad_x, grad_y)
        cv2.normalize(grad_mag, grad_mag, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        grad_mag_3ch = np.expand_dims(grad_mag, axis=2)

        # 2. Derive directional noise pattern from QRNG parameters
        param_factor = float(np.mean(quantum_params)) if quantum_params else 0.5
        noise_pattern = np.sin(grad_x * 0.1 + param_factor * np.pi) * np.cos(grad_y * 0.1 + param_factor * np.pi)
        noise_3ch = np.repeat(np.expand_dims(noise_pattern, axis=2), 3, axis=2)

        # 3. Add noise scaled by gradient magnitude (focuses perturbation on feature edges)
        perturbation = noise_3ch * grad_mag_3ch * (epsilon * 255.0)
        perturbed_roi = np.clip(roi_float + perturbation, 0.0, 255.0).astype(np.uint8)

        return perturbed_roi
