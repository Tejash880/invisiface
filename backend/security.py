import os
import hashlib
import base64
import uuid
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class SecurityManager:
    """
    AES-256-GCM Cryptographic Security Engine & SHA-256 Integrity Verification.
    Uses cryptography.hazmat.primitives.ciphers.aead.AESGCM strictly.
    """
    def __init__(self, key: bytes = None):
        if key is None:
            # Generate a true 256-bit (32-byte) key
            self.key = AESGCM.generate_key(bit_length=256)
        else:
            if len(key) != 32:
                raise ValueError("AES-256 key must be exactly 32 bytes (256 bits).")
            self.key = key
        
        self.aesgcm = AESGCM(self.key)

    @staticmethod
    def generate_256bit_key() -> bytes:
        """Generate a cryptographically secure 256-bit key."""
        return AESGCM.generate_key(bit_length=256)

    @staticmethod
    def calculate_sha256(data: bytes) -> str:
        """Calculate SHA-256 checksum of raw bytes."""
        hasher = hashlib.sha256()
        hasher.update(data)
        return hasher.hexdigest()

    @staticmethod
    def calculate_file_sha256(file_path: str) -> str:
        """Calculate SHA-256 checksum of a file on disk."""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()

    def encrypt_data(self, data: bytes, associated_data: bytes = None) -> dict:
        """
        Encrypt raw bytes using AES-256-GCM with a 12-byte secure random nonce.
        Returns dict with base64 ciphertext, nonce, key_b64, and sha256 checksum.
        """
        nonce = os.urandom(12)  # Recommended 96-bit nonce for AES-GCM
        ciphertext = self.aesgcm.encrypt(nonce, data, associated_data)
        
        return {
            'ciphertext_b64': base64.b64encode(ciphertext).decode('utf-8'),
            'nonce_b64': base64.b64encode(nonce).decode('utf-8'),
            'key_b64': base64.b64encode(self.key).decode('utf-8'),
            'sha256': self.calculate_sha256(data),
            'algorithm': 'AES-256-GCM'
        }

    def decrypt_data(self, ciphertext_b64: str, nonce_b64: str, associated_data: bytes = None) -> bytes:
        """
        Decrypt base64 ciphertext using AES-256-GCM and base64 nonce.
        """
        ciphertext = base64.b64decode(ciphertext_b64)
        nonce = base64.b64decode(nonce_b64)
        return self.aesgcm.decrypt(nonce, ciphertext, associated_data)

    def encrypt_file(self, input_path: str, output_path: str) -> dict:
        """
        Encrypt file from input_path to binary format at output_path.
        Binary Format: [12-byte Nonce] + [AES-256-GCM Ciphertext with Tag]
        """
        with open(input_path, 'rb') as f:
            raw_data = f.read()

        sha256_hash = self.calculate_sha256(raw_data)
        nonce = os.urandom(12)
        ciphertext = self.aesgcm.encrypt(nonce, raw_data, None)

        # Write binary package [12-byte nonce][ciphertext]
        with open(output_path, 'wb') as f:
            f.write(nonce + ciphertext)

        return {
            'output_file': str(output_path),
            'nonce_b64': base64.b64encode(nonce).decode('utf-8'),
            'sha256': sha256_hash,
            'key_b64': base64.b64encode(self.key).decode('utf-8'),
            'algorithm': 'AES-256-GCM'
        }

    def decrypt_file(self, encrypted_path: str, output_path: str) -> bool:
        """
        Decrypt binary file [12-byte nonce][ciphertext] back to original unencrypted file.
        """
        try:
            with open(encrypted_path, 'rb') as f:
                content = f.read()

            if len(content) < 13:
                return False  # Invalid encrypted format

            nonce = content[:12]
            ciphertext = content[12:]

            decrypted_data = self.aesgcm.decrypt(nonce, ciphertext, None)

            with open(output_path, 'wb') as f:
                f.write(decrypted_data)

            return True
        except Exception as e:
            print(f"AES-GCM Decryption Error: {e}")
            return False

    @staticmethod
    def generate_safe_filename(original_filename: str) -> str:
        """
        Generate safe UUID-based filename preserving valid extensions.
        Prevents Path Traversal and Command Injection risks.
        """
        ext = Path(original_filename).suffix.lower()
        if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
            ext = '.png'
        return f"{uuid.uuid4().hex}{ext}"
