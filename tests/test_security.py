import pytest
import os
from pathlib import Path
from backend.security import SecurityManager

@pytest.fixture
def security():
    return SecurityManager()

def test_aes256_gcm_encrypt_decrypt_bytes(security):
    data = b"InvisiFace Quantum Security Test Payload 2026"
    encrypted = security.encrypt_data(data)
    
    assert 'ciphertext_b64' in encrypted
    assert 'nonce_b64' in encrypted
    assert 'sha256' in encrypted
    assert encrypted['algorithm'] == 'AES-256-GCM'

    decrypted = security.decrypt_data(encrypted['ciphertext_b64'], encrypted['nonce_b64'])
    assert decrypted == data

def test_aes256_gcm_file_encryption_decryption(security, tmp_path):
    input_file = tmp_path / "original.txt"
    input_file.write_bytes(b"Secret image binary payload content for testing.")

    encrypted_file = tmp_path / "protected.enc"
    decrypted_file = tmp_path / "restored.txt"

    enc_meta = security.encrypt_file(str(input_file), str(encrypted_file))
    assert Path(encrypted_file).exists()
    assert 'sha256' in enc_meta

    success = security.decrypt_file(str(encrypted_file), str(decrypted_file))
    assert success is True
    assert decrypted_file.read_bytes() == b"Secret image binary payload content for testing."

def test_aes256_gcm_tamper_detection(security, tmp_path):
    input_file = tmp_path / "data.bin"
    input_file.write_bytes(b"Original untampered data")

    enc_file = tmp_path / "payload.enc"
    dec_file = tmp_path / "out.bin"

    security.encrypt_file(str(input_file), str(enc_file))

    # Tamper with encrypted bytes
    raw_enc = bytearray(enc_file.read_bytes())
    raw_enc[15] ^= 0xFF  # Flip bits
    enc_file.write_bytes(bytes(raw_enc))

    # Decryption must fail due to tag mismatch
    success = security.decrypt_file(str(enc_file), str(dec_file))
    assert success is False

def test_sha256_hash(security):
    data = b"InvisiFace Hash Test"
    h1 = security.calculate_sha256(data)
    h2 = security.calculate_sha256(data)
    assert len(h1) == 64
    assert h1 == h2
