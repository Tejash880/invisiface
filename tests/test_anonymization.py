import pytest
import numpy as np
from backend.quantum_face_protection import QuantumFaceProtectionEngine
from backend.watermark import WatermarkEngine
from backend.metrics import MetricsEngine
from demo_images.generate_demo_assets import create_synthetic_face_image

@pytest.fixture
def test_data():
    img = create_synthetic_face_image(1)
    faces = [{'id': 1, 'x': 200, 'y': 200, 'w': 100, 'h': 100, 'confidence': 0.9}]
    qrng_data = {
        'seed': 987654321,
        'parameter_sequence': [0.4, 0.7, 0.2, 0.9, 0.1, 0.5, 0.8, 0.3]
    }
    return img, faces, qrng_data

def test_imperceptible_quantum_face_protection(test_data):
    img, faces, qrng_data = test_data
    protected_img, meta = QuantumFaceProtectionEngine.protect_image(
        img, faces, qrng_data, min_ssim_threshold=0.90
    )

    assert protected_img is not None
    assert protected_img.shape == img.shape
    assert meta['faces_protected'] == 1
    assert meta['ssim'] >= 0.90  # Quality Gate enforced
    assert meta['quality_gate_passed'] is True

def test_invisible_watermark_embed_and_verify(test_data):
    img, faces, qrng_data = test_data
    protected_img, _ = QuantumFaceProtectionEngine.protect_image(
        img, faces, qrng_data, min_ssim_threshold=0.90
    )

    is_valid, status = WatermarkEngine.verify_watermark(protected_img, faces)
    assert is_valid is True
    assert status == "VALID"

def test_watermark_not_detected_on_original(test_data):
    img, faces, _ = test_data
    is_valid, status = WatermarkEngine.verify_watermark(img, faces)
    assert is_valid is False
    assert status == "NOT DETECTED"
