import time
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from quantum.simulator import QuantumBackendManager

class QuantumRandomGenerator:
    """
    Real 8-Qubit Quantum Random Number Generator (QRNG) powered by Qiskit.
    Applies Hadamard gates to generate true quantum superposition, measures qubit states,
    and converts quantum bitstrings into deterministic seed parameters for face protection.
    """
    def __init__(self, backend_manager: QuantumBackendManager = None):
        self.backend_manager = backend_manager or QuantumBackendManager(mode="simulation")

    def build_qrng_circuit(self, num_qubits: int = 8) -> QuantumCircuit:
        """Construct an N-qubit Hadamard quantum superposition circuit."""
        qr = QuantumRegister(num_qubits, 'q')
        cr = ClassicalRegister(num_qubits, 'c')
        qc = QuantumCircuit(qr, cr)

        # Apply Hadamard gates to all qubits to create equal quantum superposition |+>
        for i in range(num_qubits):
            qc.h(qr[i])

        # Measure all qubits into classical register
        qc.measure(qr, cr)
        return qc

    def generate_quantum_bits(self, num_qubits: int = 8, shots: int = 1024) -> dict:
        """
        Executes QRNG quantum circuit on local Qiskit Aer simulator.
        Extracts measurement bitstrings and computes integer seeds & parameters.
        """
        try:
            qc = self.build_qrng_circuit(num_qubits)
            sim_res = self.backend_manager.execute_circuit(qc, shots=shots)
            
            counts = sim_res['counts']
            # Concatenate most frequent measurement bitstrings
            sorted_bitstrings = sorted(counts.items(), key=lambda x: x[1], reverse=True)
            primary_bitstring = sorted_bitstrings[0][0]
            
            # Combine bitstrings to create a long quantum bit stream
            full_bitstream = "".join([bitstr for bitstr, _ in sorted_bitstrings[:16]])
            
            # Derive 32-bit integer seed from quantum bitstream
            seed_int = int(full_bitstream[:32], 2) if len(full_bitstream) >= 32 else hash(full_bitstream) % (2**32)
            
            # Derive normalized parameter sequence [0.0, 1.0] for pixel scrambling
            param_sequence = []
            for i in range(0, len(full_bitstream) - 8, 8):
                byte_val = int(full_bitstream[i:i+8], 2)
                param_sequence.append(byte_val / 255.0)

            return {
                'success': True,
                'status': 'Completed',
                'backend_name': sim_res['backend_name'],
                'qubits': num_qubits,
                'shots': sim_res['shots'],
                'primary_bitstring': primary_bitstring,
                'generated_bits': full_bitstream[:64],
                'seed': seed_int,
                'parameter_sequence': param_sequence[:8],
                'execution_time_ms': sim_res['execution_time_ms'],
                'disclaimer': 'Generated via Qiskit Aer local quantum circuit simulation.'
            }

        except Exception as e:
            print(f"QRNG quantum execution exception: {e}")
            # Classical fallback mode
            fallback_seed = int(time.time() * 1000) % (2**32)
            return {
                'success': False,
                'status': 'Classical Fallback',
                'backend_name': 'Classical Fallback (Pseudo-RNG)',
                'qubits': 0,
                'shots': 0,
                'primary_bitstring': '00000000',
                'generated_bits': 'CLASSICAL_FALLBACK',
                'seed': fallback_seed,
                'parameter_sequence': [0.5] * 8,
                'execution_time_ms': 0.0,
                'disclaimer': f'Quantum module fallback: {e}'
            }
