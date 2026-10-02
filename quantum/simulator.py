import time
import numpy as np

class QuantumBackendManager:
    """
    Manages local Qiskit Aer simulator backend execution and optional IBM Quantum Cloud connector.
    """
    def __init__(self, mode: str = "simulation", ibm_token: str = ""):
        self.mode = mode.lower()
        self.ibm_token = ibm_token
        self.backend = None
        self.backend_name = "Qiskit Aer Local Simulator"
        self._initialize_backend()

    def _initialize_backend(self):
        try:
            if self.mode == "ibm" and self.ibm_token:
                try:
                    from qiskit_ibm_provider import IBMProvider
                    provider = IBMProvider(token=self.ibm_token)
                    self.backend = provider.get_backend("ibmq_qasm_simulator")
                    self.backend_name = "IBM Quantum Cloud (ibmq_qasm_simulator)"
                    return
                except Exception as e:
                    print(f"IBM Quantum connection failed, falling back to Aer simulator: {e}")

            # Default to local Qiskit Aer Simulator
            try:
                from qiskit_aer import AerSimulator
                self.backend = AerSimulator()
                self.backend_name = "Qiskit Aer Simulator (Local CPU)"
            except ImportError:
                # Fallback to basic Qiskit simulator if qiskit_aer is not compiled
                from qiskit.providers.basic_provider import BasicProvider
                self.backend = BasicProvider().get_backend('basic_simulator')
                self.backend_name = "Qiskit BasicSimulator (Local CPU)"
        except Exception as e:
            print(f"Failed to initialize Qiskit backend: {e}")
            self.backend = None
            self.backend_name = "Unavailable"

    def execute_circuit(self, circuit, shots: int = 1024) -> dict:
        """
        Execute a Qiskit QuantumCircuit and return measurement outcome statistics.
        """
        if self.backend is None:
            raise RuntimeError("No Qiskit quantum backend available.")

        start_time = time.time()
        
        try:
            from qiskit import transpile
            compiled_circuit = transpile(circuit, self.backend)
            job = self.backend.run(compiled_circuit, shots=shots)
            result = job.result()
            counts = result.get_counts()
        except Exception as e:
            # Fallback for alternative Qiskit execution pathways
            try:
                from qiskit.primitives import StatevectorSampler
                sampler = StatevectorSampler()
                pub_result = sampler.run([circuit], shots=shots).result()[0]
                counts = pub_result.data.meas.get_counts()
            except Exception as ex:
                raise RuntimeError(f"Quantum circuit execution error: {e} / {ex}")

        exec_time_ms = round((time.time() - start_time) * 1000.0, 2)

        # Convert counts to bitstring distribution dictionary
        total_shots = sum(counts.values())
        probabilities = {bitstr: round(cnt / float(total_shots), 4) for bitstr, cnt in counts.items()}

        return {
            'counts': counts,
            'probabilities': probabilities,
            'shots': total_shots,
            'execution_time_ms': exec_time_ms,
            'backend_name': self.backend_name
        }
