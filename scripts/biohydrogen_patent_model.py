"""CN116913402A: reproducible toy-circuit study, never a hydrogen-yield model.

The textual CNOT and graphical CZ readings are retained as separate hypotheses.
Angles and Hamiltonian coefficients are dimensionless. No hardware on import/run.
"""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
from scipy.optimize import minimize
from quantumbridge.core import Circuit
from quantumbridge.devices import StatevectorDevice
from quantumbridge.serialization import serialize_circuit

I = np.eye(2)
X = np.array([[0, 1], [1, 0]])
Z = np.diag([1, -1])
H2 = np.kron(Z, Z) + np.kron(X, I) + np.kron(I, X)
H3 = np.kron(I, H2)  # Native statevectors are q0-first.
DEVICE = StatevectorDevice()


def circuit(phi=np.pi / 4, theta=None, interpretation="text_cnot"):
    if interpretation not in ("text_cnot", "figure_cz"):
        raise ValueError("Keep the patent's two gate readings explicit")
    c = Circuit(3, 3, name="patent-biohydrogen-" + interpretation)
    c.h(0).h(1).h(2).phase(float(phi), 0).h(0)
    gate = c.cx if interpretation == "text_cnot" else c.cz
    gate(0, 1); gate(1, 2)
    if theta is not None:
        theta = np.asarray(theta, float)
        if theta.shape != (8,) or not np.isfinite(theta).all():
            raise ValueError("Eight finite angles required")
        # Explicit completion of the opaque eight-angle TwoLocal box in Fig. 2.
        # The patent does not supply its rotation/entangling configuration.
        for offset in (0, 4):
            for j, wire in enumerate((1, 2)):
                c.ry(float(theta[offset + 2*j]), wire)
                c.rz(float(theta[offset + 2*j + 1]), wire)
            if offset == 0:
                c.cx(1, 2)
    return c


def observe(c):
    state = DEVICE.statevector(c)
    probabilities = np.abs(state)**2
    rho0 = state.reshape(2, 4) @ state.reshape(2, 4).conj().T
    return {"energy_dimensionless": float(np.vdot(state, H3 @ state).real),
            "p111": float(probabilities[7]),
            "q0_purity": float(np.trace(rho0 @ rho0).real),
            "probabilities_q0_first": {f"{i:03b}":float(v) for i,v in enumerate(probabilities)}}


def optimize(interpretation, phi=np.pi/4):
    traces, candidates = [], []
    for seed in (17, 43):
        trace = []
        def objective(theta):
            row = observe(circuit(phi, theta, interpretation))
            trace.append({"evaluation":len(trace), "energy_dimensionless":row["energy_dimensionless"], "p111":row["p111"]})
            return row["energy_dimensionless"]
        result = minimize(objective, np.random.default_rng(seed).uniform(-1,1,8),
                          method="BFGS", options={"gtol":1e-7,"maxiter":150})
        theta = result.x.tolist()
        candidates.append({"seed":seed,"theta":theta,"success":bool(result.success),
                           "message":str(result.message),"evaluations":int(result.nfev),
                           **observe(circuit(phi,theta,interpretation))})
        traces.append({"seed":seed,"trace":trace})
    return min(candidates,key=lambda row:row["energy_dimensionless"]), traces


def export(output):
    output = Path(output); output.mkdir(parents=True,exist_ok=True)
    eigenvalues = np.linalg.eigvalsh(H2).tolist()
    evidence = {"schema":"qb-biohydrogen-patent-study-v1", "patent":"CN116913402A",
        "author":"作者：曾祥洪 --QuantumBridge研发组", "source_pdf_sha256":None,
        "model_units":"dimensionless", "qubit_order":"q0_first",
        "hamiltonian":"I(q0) tensor [ZZ + XI + IX](q1,q2)",
        "source_location":"PDF p12, paragraph [0122]; Fig2 on PDF p17",
        "phi":float(np.pi/4), "exact_spectrum":eigenvalues,
        "execution_mode":"local_statevector", "hardware_access":False,"new_cloud_tasks":0,
        "caveats":["No hydrogen production, rate, efficiency, or chemical accuracy inferred.",
          "Patent text names CNOT; Fig2 shows filled-dot pairs consistent with CZ.",
          "Eight-angle TwoLocal configuration explicitly chosen here, not recovered from source.",
          "Phase P(pi/4) comes from Fig2; Pauli Z is a separate limiting case phi=pi.",
          "Local optimized angles evaluated on hardware would be hardware inference, not hardware-in-the-loop VQE."],
        "interpretations":{}}
    patent=Path.home()/"Downloads/基于量子线路模拟生物光电解制氢气的装置、方法、设备及介质.pdf"
    if patent.exists(): evidence["source_pdf_sha256"]=hashlib.sha256(patent.read_bytes()).hexdigest()
    kernels = {}
    for reading in ("text_cnot","figure_cz"):
        best, traces = optimize(reading)
        evidence["interpretations"][reading]={"initial":observe(circuit(interpretation=reading)),
                "best":best, "optimization":traces,
                "phase_scan":[{"phi":float(phi),**observe(circuit(phi,interpretation=reading))}
                              for phi in np.linspace(0,np.pi,13)]}
        for stage, theta in (("initial",None),("optimized",best["theta"])):
            for basis in ("Z","X"):
                c = circuit(theta=theta,interpretation=reading)
                if basis=="X": c.h(1).h(2)
                for q in range(3): c.measure(q,q)
                artifact=serialize_circuit(c,format="qasm2",metadata_policy="external")
                qasm=artifact.data
                key=f"biohydrogen-{reading}-{stage}-{basis}"
                kernels[key]={"num_qubits":3,"logical_depth":c.depth(),"openqasm":qasm,
                              "qasm_sha256":hashlib.sha256(qasm.encode()).hexdigest(),
                              "metadata_sidecar":artifact.sidecar}
                (output/(key+'.qasm')).write_text(qasm)
    # ZZ comes from Z shots, XI and IX share X-basis shots: retain covariance.
    (output/'execution-plan.json').write_text(json.dumps({"schema":"qb-quafu-case-plan-v1","kernels":kernels},indent=2)+'\n')
    (output/'local-evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({"spectrum":eigenvalues,"hardware_results":0,
      "readings":{k:{"initial":v["initial"],"optimized_energy":v["best"]["energy_dimensionless"],"optimized_p111":v["best"]["p111"]} for k,v in evidence['interpretations'].items()}},indent=2))
    return evidence


if __name__ == "__main__":
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    export(parser.parse_args().output)
