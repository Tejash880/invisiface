import pytest
import numpy as np
import cv2
from pathlib import Path
from backend.face_detector import FaceDetector
from demo_images.generate_demo_assets import create_synthetic_face_image

@pytest.fixture
def detector():
    return FaceDetector()

def test_detect_single_face(detector):
    img = create_synthetic_face_image(1)
    faces = detector.detect_faces(img)
    assert isinstance(faces, list)
    if len(faces) > 0:
        face = faces[0]
        assert 'id' in face
        assert 'x' in face and 'y' in face and 'w' in face and 'h' in face
        assert face['w'] > 0 and face['h'] > 0

def test_detect_no_face(detector):
    blank_img = np.ones((400, 400, 3), dtype=np.uint8) * 128
    faces = detector.detect_faces(blank_img)
    assert len(faces) == 0

def test_reject_false_positive_chest_candidate(detector):
    img = np.ones((981, 736, 3), dtype=np.uint8) * 128
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    existing_head = [(200, 100, 250, 280)]  # Valid head face
    
    # Chest candidate directly below head with wide aspect ratio
    x, y, w, h = 180, 500, 320, 200  # Aspect ratio 1.6
    is_valid, reason = detector._validate_face_candidate(x, y, w, h, img, gray, existing_head)
    
    assert is_valid is False
    assert ("aspect ratio" in reason.lower() or "chest" in reason.lower())

def test_draw_bounding_boxes(detector):
    img = create_synthetic_face_image(1)
    faces = [{'id': 1, 'x': 100, 'y': 100, 'w': 50, 'h': 50, 'confidence': 0.95}]
    annotated = detector.draw_bounding_boxes(img, faces)
    assert annotated is not None
    assert annotated.shape == img.shape
    assert not np.array_equal(img, annotated)
