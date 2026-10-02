class DeepFaceEvaluator:
    """
    Evaluation module measuring facial identity representation similarity using DeepFace.
    Returns 'NOT AVAILABLE' status cleanly if deepface package is uninstalled.
    """

    @classmethod
    def evaluate(cls, original_img: object, protected_img: object, faces: list[dict]) -> dict:
        """
        Executes DeepFace identity embedding comparison if deepface library is installed.
        """
        try:
            from deepface import DeepFace
            # If DeepFace is installed, perform evaluation
            # (Runs DeepFace.represent / verify on cropped ROIs)
            if not faces or original_img is None or protected_img is None:
                return {'status': 'Completed', 'available': True, 'similarity': 100.0, 'separation': 0.0}

            # Crop primary face ROI
            face = faces[0]
            x, y, w, h = face['x'], face['y'], face['w'], face['h']
            orig_crop = original_img[y:y+h, x:x+w]
            prot_crop = protected_img[y:y+h, x:x+w]

            res = DeepFace.verify(orig_crop, prot_crop, enforce_detection=False)
            dist = float(res.get('distance', 0.4))
            sim = float(round(max(0.0, (1.0 - dist) * 100.0), 1))

            return {
                'status': 'Completed',
                'available': True,
                'model_name': res.get('model', 'VGG-Face'),
                'similarity': sim,
                'separation': round(100.0 - sim, 1),
                'verified_same_identity': res.get('verified', False)
            }
        except ImportError:
            return {
                'status': 'NOT AVAILABLE',
                'available': False,
                'model_name': 'DeepFace Framework',
                'similarity': None,
                'separation': None,
                'note': 'DeepFace library not installed. Add deepface to requirements.txt for DeepFace evaluations.'
            }
        except Exception as e:
            return {
                'status': 'NOT AVAILABLE',
                'available': False,
                'model_name': 'DeepFace Framework',
                'similarity': None,
                'separation': None,
                'note': f'DeepFace evaluation notice: {e}'
            }
