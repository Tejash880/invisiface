import pytest
import io
import json
import cv2
import numpy as np
from app import create_app
from config import Config
from backend.database import db
from demo_images.generate_demo_assets import create_synthetic_face_image

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_api_health(client):
    res = client.get('/api/health')
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'healthy'

def test_quantum_status(client):
    res = client.get('/api/quantum/status')
    assert res.status_code == 200
    data = res.get_json()
    assert data['qubits'] == 8

def test_full_quantum_invisiface_api_pipeline(client):
    img = create_synthetic_face_image(1)
    _, buffer = cv2.imencode('.png', img)
    img_bytes = io.BytesIO(buffer.tobytes())

    # 1. Upload
    up_res = client.post(
        '/api/upload',
        data={'image': (img_bytes, 'test_face.png')},
        content_type='multipart/form-data'
    )
    assert up_res.status_code == 200
    up_data = up_res.get_json()
    assert up_data['success'] is True
    filename = up_data['filename']

    # 2. Process
    proc_res = client.post(
        '/api/process',
        data=json.dumps({'filename': filename}),
        content_type='application/json'
    )
    if proc_res.status_code != 200:
        print("PROCESS ERROR JSON:", proc_res.get_json())
    assert proc_res.status_code == 200
    proc_data = proc_res.get_json()
    assert proc_data['success'] is True
    job_id = proc_data['job_id']
    assert proc_data['integrity_report']['ssim'] >= 0.85
    assert proc_data['ai_resistance_report']['recognition_resistance_proxy'] >= 0.0

    # 3. Integrity Report Endpoint
    ir_res = client.get(f'/api/integrity-report/{job_id}')
    assert ir_res.status_code == 200
    ir_data = ir_res.get_json()
    assert ir_data['job_id'] == job_id
    assert 'sha256_hash' in ir_data

    # 4. AI Report Endpoint
    ai_res = client.get(f'/api/ai-report/{job_id}')
    assert ai_res.status_code == 200
    ai_data = ai_res.get_json()
    assert ai_data['job_id'] == job_id
    assert 'recognition_resistance_proxy' in ai_data
