from quantum.random_generator import QuantumRandomGenerator
from quantum.simulator import QuantumBackendManager

class QuantumRandomFacade:
    """
    Backend facade connecting Quantum Random Number Generator (QRNG) to the face protection pipeline.
    """
    def __init__(self, mode: str = "simulation", ibm_token: str = ""):
        self.backend_manager = QuantumBackendManager(mode=mode, ibm_token=ibm_token)
        self.qrng = QuantumRandomGenerator(self.backend_manager)

    def generate_protection_seed(self, num_qubits: int = 8) -> dict:
        """
        Executes 8-qubit Qiskit QRNG circuit and returns quantum bitstream & parameters.
        """
        return self.qrng.generate_quantum_bits(num_qubits=num_qubits, shots=1024)
