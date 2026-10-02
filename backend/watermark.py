import cv2
import numpy as np

class WatermarkEngine:
    """
    Invisible Spatial Least Significant Bit (LSB) Watermark Embedding & Verification.
    Embeds an imperceptible binary watermark signature into the center region of facial ROIs
    (unaffected by boundary mask feathering) to verify image provenance and integrity.
    """
    # 32-bit signature bitstream for InvisiFace ("INVI")
    WATERMARK_SIGNATURE = [0, 1, 0, 0, 1, 0, 0, 1,   # 'I'
                           0, 1, 0, 0, 1, 1, 1, 0,   # 'N'
                           0, 1, 0, 1, 0, 1, 1, 0,   # 'V'
                           0, 1, 0, 0, 1, 0, 0, 1]   # 'I'

    @classmethod
    def embed_watermark(cls, face_roi: np.ndarray) -> np.ndarray:
        """
        Embeds the 32-bit watermark signature into the Least Significant Bit (LSB)
        of the blue channel in the center of the facial ROI matrix.
        """
        if face_roi is None or face_roi.size < 32 * 3:
            return face_roi

        watermarked_roi = face_roi.copy()
        h, w = face_roi.shape[:2]
        
        sig_idx = 0
        sig_len = len(cls.WATERMARK_SIGNATURE)

        # Center offset to avoid boundary feathering alterations
        start_y = max(0, h // 4)
        start_x = max(0, w // 4)

        for y in range(start_y, h):
            for x in range(start_x, w):
                if sig_idx < sig_len:
                    blue_val = int(watermarked_roi[y, x, 0])
                    bit = cls.WATERMARK_SIGNATURE[sig_idx]
                    watermarked_roi[y, x, 0] = (blue_val & ~1) | bit
                    sig_idx += 1
                else:
                    break
            if sig_idx >= sig_len:
                break

        return watermarked_roi

    @classmethod
    def verify_watermark(cls, image: np.ndarray, faces: list[dict]) -> tuple[bool, str]:
        """
        Verifies if the embedded LSB watermark signature is intact in facial ROIs.
        Returns (is_valid, status_text).
        """
        if image is None or not faces:
            return False, "NOT DETECTED"

        img_h, img_w = image.shape[:2]
        sig_len = len(cls.WATERMARK_SIGNATURE)

        for face in faces:
            x, y, w, h = face['x'], face['y'], face['w'], face['h']
            x1, y1, x2, y2 = max(0, x), max(0, y), min(img_w, x + w), min(img_h, y + h)

            if x2 <= x1 or y2 <= y1 or (y2 - y1) * (x2 - x1) < sig_len:
                continue

            roi = image[y1:y2, x1:x2]
            roi_h, roi_w = roi.shape[:2]

            start_y = max(0, roi_h // 4)
            start_x = max(0, roi_w // 4)

            extracted_bits = []
            for ry in range(start_y, roi_h):
                for rx in range(start_x, roi_w):
                    if len(extracted_bits) < sig_len:
                        bit = int(roi[ry, rx, 0]) & 1
                        extracted_bits.append(bit)
                    else:
                        break
                if len(extracted_bits) >= sig_len:
                    break

            if len(extracted_bits) == sig_len and extracted_bits == cls.WATERMARK_SIGNATURE:
                return True, "VALID"

        return False, "NOT DETECTED"
