from quantum.optimizer import QuantumAssistedOptimizer
from quantum.feature_map import QuantumFeatureExtractor
from quantum.simulator import QuantumBackendManager

class QuantumOptimizerFacade:
    """
    Facade connecting quantum-assisted parameter optimization to backend pipeline.
    """
    def __init__(self, backend_manager: QuantumBackendManager = None):
        self.backend_manager = backend_manager or QuantumBackendManager()
        self.optimizer = QuantumAssistedOptimizer(self.backend_manager)

    def optimize_anonymization_settings(self, image, faces, base_method: str = "gaussian_blur") -> dict:
        """
        Runs quantum-assisted optimization to select optimal anonymization intensity.
        """
        try:
            features = QuantumFeatureExtractor.extract_face_features(image, faces)
            res = self.optimizer.optimize_parameters(features, base_method=base_method)
            return res
        except Exception as e:
            return {
                'success': False,
                'optimal_intensity': 75,
                'optimal_blur_ksize': 45,
                'optimal_pixel_block': 8,
                'evaluations': [],
                'optimization_label': 'Classical Fallback Optimization',
                'backend': 'Classical Fallback'
            }
