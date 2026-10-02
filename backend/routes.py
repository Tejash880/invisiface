import time
import os
import uuid
from pathlib import Path
from flask import Blueprint, request, jsonify, send_from_directory, render_template, current_app

from config import Config
from backend.image_preprocessing import ImagePreprocessor
from backend.quantum_random import QuantumRandomFacade
from backend.quantum_face_protection import QuantumFaceProtectionEngine
from backend.integrity import IntegrityVerifier
from backend.ai_verification import AIVerificationEngine
from backend.security import SecurityManager
from backend.image_processor import ImageProcessor
from backend.database import db
from backend.models import ProcessingHistory

api = Blueprint('api', __name__)
main_views = Blueprint('main_views', __name__)

preprocessor = ImagePreprocessor()
security_mgr = SecurityManager()

# --- HTML FRONTEND VIEW ROUTERS ---

@main_views.route('/')
def index_page():
    return render_template('index.html')

@main_views.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html')

@main_views.route('/result')
@main_views.route('/result/<int:job_id>')
def result_page(job_id=None):
    return render_template('result.html', job_id=job_id)

@main_views.route('/integrity-report')
@main_views.route('/integrity-report/<int:job_id>')
def integrity_report_page(job_id=None):
    return render_template('integrity_report.html', job_id=job_id)

@main_views.route('/ai-resistance-report')
@main_views.route('/ai-resistance-report/<int:job_id>')
def ai_resistance_report_page(job_id=None):
    return render_template('ai_resistance_report.html', job_id=job_id)

@main_views.route('/security')
def security_page():
    return render_template('security.html')

@main_views.route('/history')
def history_page():
    return render_template('history.html')

@main_views.route('/about')
def about_page():
    return render_template('about.html')


# --- REST API ENDPOINTS ---

@api.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Quantum InvisiFace Engine',
        'version': '2.0.0 QUANTUM',
        'timestamp': time.time()
    }), 200


@api.route('/quantum/status', methods=['GET'])
def quantum_status():
    """Check Qiskit 8-qubit QRNG simulator status."""
    try:
        qrng_facade = QuantumRandomFacade(mode=Config.QUANTUM_MODE, ibm_token=Config.IBM_QUANTUM_TOKEN)
        qrng_res = qrng_facade.generate_protection_seed(num_qubits=8)
        return jsonify({
            'status': 'Completed' if qrng_res['success'] else 'Classical Fallback',
            'backend_name': qrng_res['backend_name'],
            'qubits': qrng_res['qubits'],
            'generated_bits': qrng_res['generated_bits'],
            'label': 'Qiskit Aer Simulation (8 Qubits)'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'Classical Fallback',
            'backend_name': 'Classical Fallback (Pseudo-RNG)',
            'qubits': 0,
            'generated_bits': 'N/A',
            'label': 'Classical Fallback Mode'
        }), 200


@api.route('/upload', methods=['POST'])
def upload_image():
    """
    Validate and save uploaded image. Preprocess and return face detection metadata.
    """
    print("\n[1] Upload request received")
    if 'image' not in request.files:
        print("[ERR] No 'image' field in request.files")
        return jsonify({'success': False, 'error': 'No image file received in request.'}), 400

    file = request.files['image']
    if not file or file.filename == '':
        print("[ERR] Empty file or empty filename selected")
        return jsonify({'success': False, 'error': 'Empty image file selected.'}), 400

    safe_name = SecurityManager.generate_safe_filename(file.filename)
    upload_path = Config.UPLOAD_FOLDER / safe_name

    try:
        file.save(upload_path)
        print(f"[2] File saved safely to {upload_path}")
    except Exception as e:
        print(f"[ERR] Failed to save file: {e}")
        return jsonify({'success': False, 'error': f'Failed to save uploaded file: {e}'}), 500

    is_valid, err_msg = ImageProcessor.validate_file(str(upload_path), Config.MAX_CONTENT_LENGTH)
    if not is_valid:
        print(f"[ERR] File validation failed: {err_msg}")
        if upload_path.exists():
            upload_path.unlink()
        return jsonify({'success': False, 'error': err_msg}), 400

    print("[3] File validated successfully")

    try:
        prep_res = preprocessor.preprocess_image(str(upload_path))
        faces = prep_res['faces']
        img = prep_res['image']

        if img is None or img.size == 0:
            print("[ERR] Image decoding returned empty or None image")
            return jsonify({'success': False, 'error': 'Unable to decode uploaded image.'}), 400

        print(f"[4] Image decoded successfully. Dimensions: {prep_res['width']}x{prep_res['height']}, Faces detected: {len(faces)}")

        # Extract file metadata stats
        meta = ImageProcessor.get_metadata(str(upload_path))

        # Generate annotated preview
        annotated = preprocessor.detector.draw_bounding_boxes(img, faces)
        annotated_name = f"detected_{safe_name}"
        annotated_path = Config.OUTPUT_FOLDER / annotated_name
        ImageProcessor.save_image(annotated, str(annotated_path))

        return jsonify({
            'success': True,
            'filename': safe_name,
            'original_name': file.filename,
            'detected_preview': annotated_name,
            'metadata': meta,
            'width': prep_res['width'],
            'height': prep_res['height'],
            'faces': faces,
            'face_count': prep_res['face_count']
        }), 200

    except Exception as e:
        print(f"[ERR] Preprocessing exception: {e}")
        if upload_path.exists():
            upload_path.unlink()
        return jsonify({'success': False, 'error': f'Preprocessing exception: {str(e)}'}), 500


@api.route('/process', methods=['POST'])
def process_face_protection():
    """
    Execute Quantum InvisiFace Pipeline:
    1. Preprocessing (Image read & face detection)
    2. Quantum Random Number Generator (Qiskit 8-qubit QRNG)
    3. Quantum Face Protection Module (Scrambling + Perturbation + Watermarking + Quality Gate)
    4. Protected Image Generation
    5. Integrity Verification (SHA-256, Watermark Check, SSIM, PSNR)
    6. AI Verification Test (DeepFace, FaceNet, Recognition Proxy)
    7. AES-256-GCM Cryptographic Storage Protection
    8. SQLite Database Logging
    """
    start_time = time.time()
    data = request.get_json() or {}
    filename = data.get('filename')

    if not filename:
        return jsonify({'success': False, 'error': 'Filename is required.'}), 400

    upload_path = Config.UPLOAD_FOLDER / filename
    if not upload_path.exists():
        return jsonify({'success': False, 'error': f'File {filename} not found.'}), 404

    print(f"\n[5] Pipeline execution started for: {filename}")

    try:
        # STAGE 1: Image Preprocessing
        prep_res = preprocessor.preprocess_image(str(upload_path))
        orig_img = prep_res['image']
        faces = prep_res['faces']
        print(f"[6] Preprocessing complete. Dimensions: {prep_res['width']}x{prep_res['height']}, Faces detected: {len(faces)}")

        # STAGE 2: Quantum Random Number Generator (QRNG)
        print("[7] Quantum QRNG execution started (Qiskit Aer 8-Qubit Circuit)")
        qrng_facade = QuantumRandomFacade(mode=Config.QUANTUM_MODE, ibm_token=Config.IBM_QUANTUM_TOKEN)
        qrng_data = qrng_facade.generate_protection_seed(num_qubits=8)
        print(f"[8] QRNG complete. Bitstream: {qrng_data.get('generated_bits', 'N/A')[:16]}..., Seed: {qrng_data.get('seed')}")

        # STAGE 3: Quantum Face Protection Module (Iterative Quality Gate SSIM >= 0.90)
        print("[9] Quantum face protection module started (Controlled Perturbation & Scrambling)")
        protected_img, prot_meta = QuantumFaceProtectionEngine.protect_image(
            orig_img,
            faces,
            qrng_data,
            min_ssim_threshold=0.90
        )
        print(f"[10] Face protection complete. Protected faces: {prot_meta['faces_protected']}, SSIM: {prot_meta['ssim']}")

        # STAGE 4: Save Protected Image
        output_filename = f"protected_{filename}"
        output_path = Config.OUTPUT_FOLDER / output_filename
        ImageProcessor.save_image(protected_img, str(output_path))

        # STAGE 5: Integrity Verification
        print("[11] Integrity verification started (SHA-256, Watermark Check, SSIM, PSNR)")
        integrity_report = IntegrityVerifier.verify_integrity(
            orig_img, protected_img, str(output_path), faces
        )
        print(f"[12] Integrity verification complete. Watermark: {integrity_report['watermark_status']}, SHA-256: {integrity_report['sha256'][:16]}...")

        # STAGE 6: AI Verification Test
        print("[13] AI verification test suite started (DeepFace, FaceNet, Recognition Proxy)")
        ai_resistance_report = AIVerificationEngine.run_ai_verification_suite(
            orig_img, protected_img, faces
        )
        print(f"[14] AI verification complete. Recognition Resistance Proxy: {ai_resistance_report['recognition_resistance_proxy']}/100")

        # STAGE 7: AES-256-GCM Storage Encryption
        encrypted_filename = f"encrypted_{Path(filename).stem}.enc"
        encrypted_path = Config.ENCRYPTED_FOLDER / encrypted_filename
        enc_meta = security_mgr.encrypt_file(str(output_path), str(encrypted_path))
        print("[15] AES-256-GCM storage package encrypted")

        exec_time = time.time() - start_time

        # STAGE 8: SQLite Database Logging
        record = ProcessingHistory(
            original_filename=filename,
            output_filename=output_filename,
            encrypted_filename=encrypted_filename,
            face_count=len(faces),
            faces_protected=prot_meta['faces_protected'],
            quantum_backend=qrng_data['backend_name'],
            quantum_bit_count=qrng_data['qubits'],
            protection_method=prot_meta['protection_method'],
            ssim=integrity_report['ssim'],
            psnr=integrity_report['psnr_db'],
            identity_similarity_after=ai_resistance_report['identity_similarity_after'],
            identity_separation=ai_resistance_report['identity_separation'],
            recognition_resistance_proxy=ai_resistance_report['recognition_resistance_proxy'],
            sha256_hash=integrity_report['sha256'],
            watermark_status=integrity_report['watermark_status'],
            processing_time=exec_time
        )
        db.session.add(record)
        db.session.commit()
        print(f"[16] Final result logged to SQLite database. Job ID: #{record.id}. Total time: {round(exec_time, 2)}s\n")

        # Build complete three-report response
        return jsonify({
            'success': True,
            'job_id': record.id,
            'original_filename': filename,
            'output_filename': output_filename,
            'encrypted_filename': encrypted_filename,
            'face_count': len(faces),
            'faces_protected': prot_meta['faces_protected'],
            'qrng_status': qrng_data,
            'protected_image_metadata': prot_meta,
            'integrity_report': integrity_report,
            'ai_resistance_report': ai_resistance_report,
            'security': {
                'algorithm': 'AES-256-GCM',
                'sha256': integrity_report['sha256'],
                'encrypted_file': encrypted_filename
            },
            'processing_time': round(exec_time, 2)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Quantum InvisiFace pipeline error: {str(e)}'}), 500


@api.route('/result/<int:job_id>', methods=['GET'])
def get_result(job_id):
    """Retrieve full result payload for job_id."""
    record = db.session.get(ProcessingHistory, job_id)
    if not record:
        return jsonify({'error': f'Job ID {job_id} not found.'}), 404
    return jsonify(record.to_dict()), 200


@api.route('/integrity-report/<int:job_id>', methods=['GET'])
def get_integrity_report(job_id):
    """Retrieve standalone Integrity Report payload."""
    record = db.session.get(ProcessingHistory, job_id)
    if not record:
        return jsonify({'error': f'Job ID {job_id} not found.'}), 404

    data = record.to_dict()
    return jsonify({
        'report_name': 'Integrity Verification Report',
        'job_id': data['id'],
        'sha256_hash': data['sha256_hash'],
        'watermark_status': data['watermark_status'],
        'ssim': data['ssim'],
        'psnr_db': data['psnr'],
        'original_filename': data['original_filename'],
        'protected_filename': data['output_filename'],
        'processing_time': data['processing_time'],
        'integrity_status': 'VERIFIED' if data['ssim'] >= 0.85 else 'WARNING'
    }), 200


@api.route('/ai-report/<int:job_id>', methods=['GET'])
def get_ai_report(job_id):
    """Retrieve standalone AI Resistance Evaluation Report payload."""
    record = db.session.get(ProcessingHistory, job_id)
    if not record:
        return jsonify({'error': f'Job ID {job_id} not found.'}), 404

    data = record.to_dict()
    return jsonify({
        'report_name': 'AI Resistance Evaluation Report',
        'job_id': data['id'],
        'identity_similarity_before': 100.0,
        'identity_similarity_after': data['identity_similarity_after'],
        'identity_separation': data['identity_separation'],
        'recognition_resistance_proxy': data['recognition_resistance_proxy'],
        'models_evaluated': {
            'deepface': {'status': 'NOT AVAILABLE', 'similarity': None},
            'facenet': {'status': 'NOT AVAILABLE', 'similarity': None},
            'recognition_attempt': {
                'status': 'Completed',
                'identity_similarity_after': data['identity_similarity_after'],
                'identity_separation': data['identity_separation']
            }
        },
        'disclaimer': 'Evaluated against selected recognition models. Does not claim guaranteed immunity against all external facial recognition systems.'
    }), 200


@api.route('/history', methods=['GET'])
def get_history():
    records = ProcessingHistory.query.order_by(ProcessingHistory.timestamp.desc()).limit(50).all()
    return jsonify([r.to_dict() for r in records]), 200


@api.route('/download/<path:filename>', methods=['GET'])
def download_file(filename):
    file_type = request.args.get('type', 'output')
    folder = Config.ENCRYPTED_FOLDER if file_type == 'encrypted' else (Config.UPLOAD_FOLDER if file_type == 'upload' else Config.OUTPUT_FOLDER)

    file_path = folder / filename
    if not file_path.exists():
        return jsonify({'error': f'File {filename} not found.'}), 404

    return send_from_directory(folder, filename, as_attachment=True)


@api.route('/decrypt', methods=['POST'])
def decrypt_file_endpoint():
    if 'file' not in request.files:
        return jsonify({'error': 'No encrypted file provided.'}), 400

    file = request.files['file']
    temp_enc_path = Config.ENCRYPTED_FOLDER / f"temp_{uuid.uuid4().hex}.enc"
    temp_dec_path = Config.OUTPUT_FOLDER / f"decrypted_{uuid.uuid4().hex}.png"

    try:
        file.save(temp_enc_path)
        success = security_mgr.decrypt_file(str(temp_enc_path), str(temp_dec_path))
        
        if temp_enc_path.exists():
            temp_enc_path.unlink()

        if success:
            dec_sha256 = SecurityManager.calculate_file_sha256(str(temp_dec_path))
            return jsonify({
                'success': True,
                'message': 'AES-256-GCM Authenticated Decryption Successful!',
                'decrypted_filename': temp_dec_path.name,
                'sha256': dec_sha256
            }), 200
        else:
            return jsonify({'error': 'AES-256-GCM Tag verification or decryption failed.'}), 400

    except Exception as e:
        return jsonify({'error': f'Decryption exception: {e}'}), 500
