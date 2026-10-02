# InvisiFace System Architecture Documentation

## Overview
InvisiFace is a full-stack, privacy-preserving face anonymization and digital identity protection platform combining OpenCV computer vision, Qiskit Quantum Machine Learning (QML) simulations, AES-256-GCM authenticated cryptography, SQLite database history, and a web dashboard.

---

## Technical Component Architecture

```
[ User Browser / Web UI ]
       │
       ▼ (REST APIs)
[ Flask Web Server (app.py) ] ◄──► [ SQLite Database (invisiface.db) ]
       │
       ├───► [ Image Processing & Face Detector (OpenCV Haar/ROI) ]
       ├───► [ Quantum Engine (Qiskit Aer 4-Qubit PQC & VQC) ]
       ├───► [ Quantum-Assisted Parameter Optimizer ]
       ├───► [ Face Anonymizer (Feathered Mask Blending) ]
       ├───► [ Real Metrics Engine (SSIM, PSNR, Privacy Score) ]
       └───► [ Security Module (AES-256-GCM Encryption & SHA-256) ]
```

---

## Key Subsystems

### 1. Computer Vision & Face ROI Extraction (`backend/face_detector.py`)
- Single and multi-face detection using OpenCV multi-scale Haar Cascades (`haarcascade_frontalface_default.xml` & `haarcascade_profileface.xml`).
- Non-Maximum Suppression (NMS) with IoU threshold deduplication.
- Visual bounding box annotation overlays.

### 2. Quantum Engine (`quantum/`)
- Extracts 4-dimensional normalized facial feature vectors $[f_1, f_2, f_3, f_4] \in [0, 1]^4$.
- Encodes feature angles $\theta_i = \pi \cdot f_i$ into a 4-qubit Parameterized Quantum Circuit (PQC).
- Executes ansatz entangling $CZ$ gates on local `Qiskit Aer` simulator.
- Measures state probabilities to classify privacy risk and guide parameter selection.

### 3. Face Anonymization & Feathered Blending (`backend/anonymizer.py`)
- Anonymization algorithms: Adaptive Gaussian Blur, Pixelation, Privacy Dark Shield Mask, and Identity Scrambling (bilateral filtering + noise perturbation).
- Feathered elliptical binary mask blending for seamless cheek, forehead, and skin continuity.

### 4. Cryptographic Security Layer (`backend/security.py`)
- `cryptography.hazmat.primitives.ciphers.aead.AESGCM` strictly enforced for AES-256-GCM authenticated encryption.
- Generates 32-byte (256-bit) keys and 12-byte random nonces (`os.urandom(12)`).
- SHA-256 checksum generation for file integrity validation.

### 5. REST API Specifications (`backend/routes.py`)
- `POST /api/upload`: Validates image MIME/extension/size & detects faces.
- `POST /api/process`: Executes full anonymization pipeline.
- `GET /api/result/<id>`: Returns job record by ID.
- `GET /api/history`: Returns SQLite history log.
- `GET /api/download/<filename>?type=output|encrypted`: Serves output files.
- `POST /api/decrypt`: Verifies and decrypts `.enc` binary package.
