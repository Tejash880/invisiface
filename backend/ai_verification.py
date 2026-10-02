from backend.deepface_evaluator import DeepFaceEvaluator
from backend.facenet_evaluator import FaceNetEvaluator
from backend.recognition_evaluator import ControlledRecognitionEvaluator

class AIVerificationEngine:
    """
    Master AI Verification Test orchestrator producing the AI Resistance Evaluation Report.
    Runs DeepFace, FaceNet, and Controlled Recognition Attempt evaluations.
    """

    @classmethod
    def run_ai_verification_suite(cls, original_img: object, protected_img: object, faces: list[dict]) -> dict:
        """
        Executes evaluation suite across DeepFace, FaceNet, and Controlled Recognition attempt.
        Returns complete AI Resistance Evaluation Report payload.
        """
        # 1. DeepFace Evaluation
        deepface_res = DeepFaceEvaluator.evaluate(original_img, protected_img, faces)

        # 2. FaceNet Evaluation
        facenet_res = FaceNetEvaluator.evaluate(original_img, protected_img, faces)

        # 3. Controlled Recognition Attempt
        rec_res = ControlledRecognitionEvaluator.evaluate_recognition_attempt(original_img, protected_img, faces)

        return {
            'report_name': 'AI Resistance Evaluation Report',
            'models_evaluated': {
                'deepface': deepface_res,
                'facenet': facenet_res,
                'recognition_attempt': rec_res
            },
            'identity_similarity_before': rec_res['identity_similarity_before'],
            'identity_similarity_after': rec_res['identity_similarity_after'],
            'identity_separation': rec_res['identity_separation'],
            'similarity_reduction_pct': rec_res['similarity_reduction_pct'],
            'recognition_resistance_proxy': rec_res['recognition_resistance_proxy'],
            'disclaimer': 'Evaluated against selected recognition models. Does not claim guaranteed immunity against all external facial recognition systems.'
        }
