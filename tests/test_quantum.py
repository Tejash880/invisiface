import pytest
import numpy as np
from quantum.random_generator import QuantumRandomGenerator
from quantum.simulator import QuantumBackendManager
from backend.quantum_random import QuantumRandomFacade

def test_qrng_circuit_construction():
    qrng = QuantumRandomGenerator()
    qc = qrng.build_qrng_circuit(num_qubits=8)
    assert qc.num_qubits == 8
    assert qc.num_clbits == 8

def test_qrng_bit_generation_on_aer_simulator():
    backend_mgr = QuantumBackendManager(mode="simulation")
    qrng = QuantumRandomGenerator(backend_mgr)
    res = qrng.generate_quantum_bits(num_qubits=8, shots=1024)

    assert res['success'] is True
    assert res['status'] == 'Completed'
    assert res['qubits'] == 8
    assert len(res['primary_bitstring']) == 8
    assert isinstance(res['seed'], int)
    assert len(res['parameter_sequence']) == 8

def test_quantum_random_facade():
    facade = QuantumRandomFacade(mode="simulation")
    res = facade.generate_protection_seed(num_qubits=8)
    assert res['success'] is True
    assert 'Qiskit Aer' in res['backend_name']
