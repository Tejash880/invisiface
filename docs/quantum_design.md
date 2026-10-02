# Qiskit Quantum Module Design Specifications

## Overview
InvisiFace incorporates a Qiskit quantum circuit simulator to analyze facial feature distributions, classify privacy risk levels, and assist in optimizing parameter intensity (blur kernel / block size).

> [!NOTE]
> All quantum operations run on a local **Qiskit Aer Simulator (CPU)** or **Qiskit BasicSimulator** and are labeled in the UI as **"Quantum Simulation (Qiskit Aer)"** or **"Quantum-Assisted Prototype"**.

---

## 1. Feature Representation & Quantum Mapping

Facial Regions of Interest (ROI) are mapped into a 4-dimensional normalized feature vector:

$$\vec{f} = \begin{bmatrix} f_1 & f_2 & f_3 & f_4 \end{bmatrix}^T \in [0, 1]^4$$

Where:
- $f_1$: Mean ROI Brightness (Normalized $[0, 1]$)
- $f_2$: Spatial Contrast (Normalized Laplacian Variance)
- $f_3$: Face Area Ratio relative to Image Dimensions
- $f_4$: Edge Density (Canny Gradient Magnitude Ratio)

The rotation angles $\theta_i$ for each qubit $q_i$ are derived via:

$$\theta_i = \pi \cdot f_i \quad \text{for } i \in \{0, 1, 2, 3\}$$

---

## 2. 4-Qubit Parameterized Quantum Circuit (PQC) Structure

```
q_0: ──[H]──[Ry(θ_0)]──────■──────────────────────────[Rz(θ_0/2)]──[Ry(π/4)]──[M]
                           │
q_1: ──[H]──[Ry(θ_1)]──────■──────■───────────────────[Rz(θ_1/2)]──[Ry(π/4)]──[M]
                                  │
q_2: ──[H]──[Ry(θ_2)]─────────────■──────■────────────[Rz(θ_2/2)]──[Ry(π/4)]──[M]
                                         │
q_3: ──[H]──[Ry(θ_3)]──────■─────────────■────────────[Rz(θ_3/2)]──[Ry(π/4)]──[M]
                           │
                           └──────────────────────────┘
```

1. **Superposition Layer**: Hadamard gates ($H$) applied to all 4 qubits.
2. **Rotation Encoding**: Parameterized $R_y(\theta_i)$ rotation gates.
3. **Quantum Entanglement Layer**: Controlled-$Z$ ($CZ$) entangling gates between adjacent qubit pairs $(q_0, q_1), (q_1, q_2), (q_2, q_3), (q_3, q_0)$.
4. **Ansatz Layer**: Parameterized $R_z(\theta_i / 2)$ and fixed $R_y(\pi/4)$ rotation gates.
5. **Measurement Layer**: Measure all 4 qubits into classical bits.

---

## 3. Quantum-Assisted Parameter Optimization Objective Function

Parameter search evaluates intensity candidates $I \in \{30, 50, 75, 90\}$ by executing a 2-qubit parameter state search circuit.

The objective score to maximize is:

$$\text{Objective}(I) = 0.7 \cdot \text{PrivacyGain}(I, P_{11}) - 0.3 \cdot \text{QualityLoss}(I, P_{00})$$

Where $P_{11}$ is the quantum state $|11\rangle$ measurement probability.

---

## 4. Robust Classical Fallback Strategy
If Qiskit Aer encounters an unexpected hardware or compilation error:
- The system catches the exception cleanly.
- Falls back to **Classical Optimization Fallback**.
- UI updates the status badge to **"Classical Fallback Mode"** without interrupting user workflow.
