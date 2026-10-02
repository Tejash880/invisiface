from datetime import datetime
from backend.database import db

class ProcessingHistory(db.Model):
    """
    Quantum InvisiFace SQLite Processing History Table.
    """
    __tablename__ = 'processing_history'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    output_filename = db.Column(db.String(255), nullable=False)
    encrypted_filename = db.Column(db.String(255), nullable=True)
    face_count = db.Column(db.Integer, default=0, nullable=False)
    faces_protected = db.Column(db.Integer, default=0, nullable=False)
    quantum_backend = db.Column(db.String(100), default="Qiskit Aer Simulation", nullable=False)
    quantum_bit_count = db.Column(db.Integer, default=8, nullable=False)
    protection_method = db.Column(db.String(100), default="QRNG Controlled Perturbation & Scrambling", nullable=False)
    ssim = db.Column(db.Float, default=1.0, nullable=False)
    psnr = db.Column(db.Float, default=100.0, nullable=False)
    identity_similarity_after = db.Column(db.Float, default=100.0, nullable=False)
    identity_separation = db.Column(db.Float, default=0.0, nullable=False)
    recognition_resistance_proxy = db.Column(db.Float, default=0.0, nullable=False)
    sha256_hash = db.Column(db.String(64), nullable=False)
    watermark_status = db.Column(db.String(50), default="VALID", nullable=False)
    processing_time = db.Column(db.Float, default=0.0, nullable=False)

    def to_dict(self) -> dict:
        """Convert record to dictionary for REST API responses."""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'original_filename': self.original_filename,
            'output_filename': self.output_filename,
            'encrypted_filename': self.encrypted_filename,
            'face_count': self.face_count,
            'faces_protected': self.faces_protected,
            'quantum_backend': self.quantum_backend,
            'quantum_bit_count': self.quantum_bit_count,
            'protection_method': self.protection_method,
            'ssim': self.ssim,
            'psnr': self.psnr,
            'identity_similarity_after': self.identity_similarity_after,
            'identity_separation': self.identity_separation,
            'recognition_resistance_proxy': self.recognition_resistance_proxy,
            'sha256_hash': self.sha256_hash,
            'watermark_status': self.watermark_status,
            'processing_time': round(self.processing_time, 2)
        }
