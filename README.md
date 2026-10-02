# InvisiFace – Quantum-Enhanced Face Anonymization & Digital Identity Protection System

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![Qiskit 1.0+](https://img.shields.io/badge/Qiskit-Aer%20Simulator-purple.svg)](https://qiskit.org/)
[![Security AES-256-GCM](https://img.shields.io/badge/Security-AES--256--GCM-green.svg)](https://cryptography.io/)
[![Flask REST API](https://img.shields.io/badge/Flask-REST%20API-black.svg)](https://flask.palletsprojects.com/)

InvisiFace is a full-stack, privacy-preserving face anonymization platform designed to protect individual digital identities in digital imagery. It integrates OpenCV Computer Vision, Qiskit Quantum Machine Learning (QML) circuit simulations, AES-256-GCM authenticated encryption, and a modern web dashboard.

---

## Key Features

1. **AI Face Detection**: Automatic detection of single and multiple faces using OpenCV Haar Cascades and bounding box ROI extraction.
2. **Qiskit Quantum Circuit Simulation**: Feature maps 4D normalized facial features into a 4-qubit parameterized quantum circuit running on local Qiskit Aer.
3. **Quantum-Assisted Parameter Optimization**: Objective optimization function balancing Privacy Gain against Visual Quality (SSIM) Loss.
4. **Natural Appearance Preservation**: Feathered elliptical binary mask blending ensures facial regions are anonymized while preserving surrounding skin, hair, lighting, and background composition.
5. **Real Mathematical Metrics**: Calculated Structural Similarity Index (SSIM), Peak Signal-to-Noise Ratio (PSNR in dB), Privacy Score (0–100), and Facial Recognition Resistance Proxy.
6. **Cryptographic Security**: AES-256-GCM authenticated encryption with 12-byte random nonces and SHA-256 file integrity digests.
7. **Interactive Dashboard**: Futuristic quantum-cyber theme with drag-and-drop upload, animated pipeline timeline, side-by-side interactive split slider before/after comparison, and downloadable `.enc` packages.
8. **SQLite Audit Trail**: SQLite database storing complete processing history.

---

## Installation & Setup

### Prerequisites
- Python 3.10 or 3.11
- Windows 10/11 or macOS/Linux laptop (Runs on CPU with ~8 GB RAM)

### Quick Start Commands

```bash
# 1. Clone or navigate to the project directory
cd invisiface

# 2. Create and activate a Python virtual environment (Windows)
python -m venv venv
venv\Scripts\activate

# 3. Install required dependencies
pip install -r requirements.txt

# 4. Generate demo synthetic test images
python demo_images/generate_demo_assets.py

# 5. Run the automated test suite
pytest

# 6. Launch the Flask application
python app.py
```

Open your browser and navigate to:
👉 **`http://127.0.0.1:5000`**

---

## System Architecture

```
[ Web UI Dashboard ] ──REST API──► [ Flask Server (app.py) ]
                                          │
    ┌───────────────────────────┬─────────┴──────────┬────────────────────────────┐
    ▼                           ▼                    ▼                            ▼
[ OpenCV Detector ]    [ Qiskit Quantum Engine ]  [ Face Anonymizer ]    [ AES-256-GCM Security ]
(Haar / Bounding ROI)  (4-Qubit PQC Simulator)   (Feathered Blending)    (Cryptographic Package)
```

---

## Quantum Component Explanation

All quantum processing executes locally on a **Qiskit Aer Simulator** (CPU) and is labeled as **"Quantum Simulation (Qiskit Aer)"**.

- **Feature Reduction**: Extracts normalized 4D facial feature vector $[f_1, f_2, f_3, f_4]$ (brightness, contrast, face area ratio, edge density).
- **Quantum Circuit**: Builds a 4-qubit Parameterized Quantum Circuit with Hadamard superposition, $R_y(\theta_i)$ feature rotations, and entangling $CZ$ gates.
- **Classifier & Optimizer**: Measures quantum bitstring distributions to classify privacy risk and optimize anonymization intensity.

---

## Security Implementation

- **Encryption**: AES-256-GCM authenticated cipher (`cryptography.hazmat.primitives.ciphers.aead.AESGCM`).
- **Nonce**: 12-byte cryptographically secure random nonce (`os.urandom(12)`).
- **Integrity**: SHA-256 hashing for all inputs, outputs, and encrypted packages.
- **Sanitization**: UUID safe filename generation to prevent path traversal risks.

---

## Automated Test Suite

To run all automated unit and integration tests:

```bash
pytest -v
```

Tests cover:
- OpenCV single/multi/zero-face detection logic (`test_face_detection.py`)
- Gaussian blur, pixelation, and identity scrambling anonymization (`test_anonymization.py`)
- AES-256-GCM encryption, decryption, and tamper detection (`test_security.py`)
- Qiskit quantum circuit construction and simulation (`test_quantum.py`)
- Flask REST API endpoints and database integration (`test_api.py`)

---

## Disclaimers & Limitations

1. **Quantum Mode**: Runs as a Qiskit Aer local simulation on CPU. No claim of quantum advantage or real quantum hardware execution is made.
2. **Recognition Resistance**: Termed strictly as **Facial Recognition Resistance Proxy**. LBP/histogram feature distance evaluates relative feature distortion, not guaranteed immunity against every external AI recognition model.
3. **Hardware**: Designed to run efficiently on a normal laptop without GPU requirements.
