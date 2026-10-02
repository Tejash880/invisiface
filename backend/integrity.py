import os
from pathlib import Path
from backend.security import SecurityManager
from backend.metrics import MetricsEngine
from backend.watermark import WatermarkEngine

class IntegrityVerifier:
    """
    Generates Integrity Verification Report containing actual SHA-256 hashes,
    watermark verification, SSIM, PSNR, and file stats.
    """

    @classmethod
    def verify_integrity(
        cls,
        original_image: object,
        protected_image: object,
        protected_file_path: str,
        faces: list[dict]
    ) -> dict:
        """
        Calculates SHA-256, watermark verification, SSIM, and PSNR for Integrity Report.
        """
        file_path = Path(protected_file_path)
        
        # 1. SHA-256 Hash Calculation
        sha256_hash = SecurityManager.calculate_file_sha256(str(file_path)) if file_path.exists() else "N/A"

        # 2. Actual Watermark Verification
        watermark_valid, watermark_status = WatermarkEngine.verify_watermark(protected_image, faces)

        # 3. Mathematical Quality & Similarity Metrics
        ssim_val = MetricsEngine.calculate_ssim(original_image, protected_image)
        psnr_val = MetricsEngine.calculate_psnr(original_image, protected_image)

        # 4. File Metadata
        img_h, img_w = protected_image.shape[:2]
        file_size_kb = round(file_path.stat().st_size / 1024.0, 2) if file_path.exists() else 0.0
        file_fmt = file_path.suffix.replace('.', '').upper()

        return {
            'sha256': sha256_hash,
            'watermark_status': watermark_status,
            'watermark_valid': watermark_valid,
            'ssim': round(ssim_val, 4),
            'psnr_db': psnr_val,
            'dimensions': f"{img_w} x {img_h} px",
            'width': img_w,
            'height': img_h,
            'file_size_kb': file_size_kb,
            'file_format': file_fmt,
            'integrity_status': 'VERIFIED' if (ssim_val >= 0.85 and sha256_hash != "N/A") else 'WARNING'
        }
