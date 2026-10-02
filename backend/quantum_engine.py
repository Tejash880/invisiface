from quantum.feature_map import QuantumFeatureExtractor
from quantum.simulator import QuantumBackendManager
from quantum.quantum_classifier import VariationalQuantumClassifier

class QuantumEngine:
    """
    Facade connecting quantum feature extraction, simulation backend,
    and Variational Quantum Classifier (VQC) to the main InvisiFace pipeline.
    """

    def __init__(self, mode: str = "simulation", ibm_token: str = ""):
        self.backend_manager = QuantumBackendManager(mode=mode, ibm_token=ibm_token)
        self.classifier = VariationalQuantumClassifier(self.backend_manager)

    def process_quantum_pipeline(self, image, faces) -> dict:
        """
        Runs complete quantum analysis pipeline:
        Image/Face ROI -> Feature Reduction -> Quantum Encoding -> VQC Execution -> Privacy Score.
        """
        try:
            # 1. Extract 4D normalized facial features
            features = QuantumFeatureExtractor.extract_face_features(image, faces)

            # 2. Run Variational Quantum Classifier
            qml_result = self.classifier.classify_privacy_level(features)

            return {
                'status': 'Quantum Simulation Completed' if qml_result['success'] else 'Classical Fallback',
                'feature_vector': [round(float(f), 4) for f in features],
                'privacy_class': qml_result['privacy_class'],
                'quantum_confidence': qml_result['quantum_confidence'],
                'class_description': qml_result['class_description'],
                'quantum_probabilities': qml_result['quantum_probabilities'],
                'circuit_qubits': qml_result['circuit_qubits'],
                'circuit_depth': qml_result['circuit_depth'],
                'execution_time_ms': qml_result['execution_time_ms'],
                'backend_name': qml_result['backend_name'],
                'mode_label': qml_result['mode_label']
            }
        except Exception as e:
            return {
                'status': 'Unavailable - Classical Fallback',
                'feature_vector': [0.5, 0.5, 0.1, 0.5],
                'privacy_class': 'MEDIUM_PRIVACY',
                'quantum_confidence': 0.50,
                'class_description': f'Quantum module fallback: {e}',
                'quantum_probabilities': {},
                'circuit_qubits': 0,
                'circuit_depth': 0,
                'execution_time_ms': 0.0,
                'backend_name': 'Classical Fallback',
                'mode_label': 'Classical Optimization Fallback'
            }
