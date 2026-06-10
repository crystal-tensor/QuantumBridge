// This file is generated from QuantumBridge-owned Stage 10C backend API outputs.

// It contains local prototype seed data only: no secrets, credentials, cloud calls, or hardware access.

export const sampleCatalog = {
  "notices": [
    "QuantumBridge Studio is an independent local prototype.",
    "No official endorsement is claimed.",
    "Local-only: no cloud execution, credential reading, or hardware access.",
    "Third-party package names are used only for compatibility identification.",
    "This prototype is not production-ready."
  ],
  "projects": [
    {
      "capability_level": 3,
      "category": "QML",
      "executable_workflows": [
        "native educational quantum kernel",
        "native educational kernel classifier",
        "native educational QNN classifier",
        "optional upstream qiskit-machine-learning passthrough"
      ],
      "project_id": "qiskit-machine-learning",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qiskit-machine-learning",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": null
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "partial",
      "title": "Qiskit Machine Learning",
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-machine-learning; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow is local-only: no cloud, token, credential, or hardware access.",
        "not full Qiskit Machine Learning replacement",
        "not production ML",
        "no high-risk decision use",
        "no cloud/token/hardware access"
      ]
    },
    {
      "capability_level": 3,
      "category": "QML",
      "executable_workflows": [
        "TorchQuantum-like native educational quantum layer",
        "tensor and batch forward",
        "native educational classifier training",
        "optional torch tensor compatibility",
        "optional upstream TorchQuantum passthrough"
      ],
      "project_id": "torchquantum",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "torchquantum",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": null
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "partial",
      "title": "TorchQuantum",
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for torchquantum; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow is local-only: no cloud, token, credential, or hardware access.",
        "not full TorchQuantum replacement",
        "not full PyTorch replacement",
        "not production QML",
        "no high-risk ML decision use",
        "no cloud/token/hardware access"
      ]
    },
    {
      "capability_level": 3,
      "category": "Error mitigation",
      "executable_workflows": [
        "native educational ZNE",
        "native educational readout mitigation",
        "optional upstream mitiq passthrough"
      ],
      "project_id": "mitiq",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "mitiq",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": null
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "partial",
      "title": "Mitiq",
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for mitiq; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow is local-only: no cloud, token, credential, or hardware access.",
        "not full Mitiq replacement",
        "not production error mitigation",
        "no hardware calibration parity",
        "no cloud/token/hardware access"
      ]
    },
    {
      "capability_level": 3,
      "category": "Framework bridge",
      "executable_workflows": [
        "Qiskit to QuantumBridge IR to PennyLane executable spec",
        "PennyLane operation/tape metadata to QuantumBridge IR to Qiskit QuantumCircuit",
        "bidirectional Bell circuit equivalence proof",
        "optional upstream pennylane-qiskit passthrough metadata"
      ],
      "project_id": "pennylane-qiskit",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "pennylane-qiskit",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": null
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "partial",
      "title": "PennyLane-Qiskit",
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for pennylane-qiskit; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow is local-only: no cloud, token, credential, or hardware access.",
        "not full PennyLane-Qiskit replacement",
        "not full Qiskit parity",
        "not full PennyLane parity",
        "no advanced device, transform, or gradient parity",
        "no cloud/token/hardware access"
      ]
    },
    {
      "capability_level": 3,
      "category": "Experiments and calibration",
      "executable_workflows": [
        "native educational Rabi experiment",
        "native educational T1 experiment",
        "native educational Ramsey experiment",
        "optional upstream qiskit-experiments passthrough"
      ],
      "project_id": "qiskit-experiments",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qiskit-experiments",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": null
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "partial",
      "title": "Qiskit Experiments",
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-experiments; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow is local-only: no cloud, token, credential, or hardware access.",
        "not full Qiskit Experiments replacement",
        "not hardware calibration",
        "not production experiment analysis",
        "no cloud/token/hardware access"
      ]
    },
    {
      "capability_level": 3,
      "category": "Dynamics",
      "executable_workflows": [
        "native educational Z precession",
        "native educational Rabi drive dynamics",
        "native educational dephasing metadata simulation",
        "optional upstream qiskit-dynamics passthrough"
      ],
      "project_id": "qiskit-dynamics",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qiskit-dynamics",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": null
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "partial",
      "title": "Qiskit Dynamics",
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-dynamics; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow is local-only: no cloud, token, credential, or hardware access.",
        "not full Qiskit Dynamics replacement",
        "not production dynamics",
        "no full Lindblad solver",
        "no cloud/token/hardware access"
      ]
    },
    {
      "capability_level": 3,
      "category": "Circuit / IR compatibility",
      "executable_workflows": [
        "QuantumBridge IR to MQT Core-like circuit dict",
        "MQT Core-like dict to QuantumBridge IR",
        "QASM subset compatibility artifact",
        "optional upstream MQT Core passthrough boundary"
      ],
      "project_id": "mqt-core",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "mqt-core",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": null
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "partial",
      "title": "MQT Core",
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for mqt-core; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow is local-only: no cloud, token, credential, or hardware access.",
        "not full MQT Core replacement",
        "no official MQT endorsement",
        "no cloud/token/hardware access"
      ]
    },
    {
      "capability_level": 3,
      "category": "Simulation",
      "executable_workflows": [
        "native DDSIM-like statevector simulation",
        "native DDSIM-like counts simulation",
        "decision-diagram-inspired metadata",
        "optional upstream MQT DDSIM passthrough boundary"
      ],
      "project_id": "mqt-ddsim",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "mqt-ddsim",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": null
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "partial",
      "title": "MQT DDSIM",
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for mqt-ddsim; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow is local-only: no cloud, token, credential, or hardware access.",
        "not full DDSIM replacement",
        "no full decision diagram parity",
        "no production simulator parity",
        "no cloud/token/hardware access"
      ]
    },
    {
      "capability_level": 3,
      "category": "Mapping / routing",
      "executable_workflows": [
        "topology validation",
        "greedy routing",
        "SWAP insertion",
        "mapping cost",
        "original vs mapped simulation comparison",
        "optional upstream MQT QMAP passthrough boundary"
      ],
      "project_id": "mqt-qmap",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "mqt-qmap",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": null
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "partial",
      "title": "MQT QMAP",
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for mqt-qmap; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow is local-only: no cloud, token, credential, or hardware access.",
        "not full QMAP replacement",
        "no optimal mapping claim",
        "no production compiler parity",
        "no cloud/token/hardware access"
      ]
    },
    {
      "capability_level": 3,
      "category": "Backend / QOS compatibility",
      "executable_workflows": [
        "QuantumBridge IR to UQCI IR",
        "UQCI job spec",
        "offline mock runtime",
        "DeviceSpec / CalSet / Manifest",
        "OpenQASM compatibility artifact",
        "optional upstream QOS-UQCI passthrough boundary"
      ],
      "project_id": "qos-uqci",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qos-uqci",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": null
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "partial",
      "title": "QOS-UQCI",
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qos-uqci; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow is local-only: no cloud, token, credential, or hardware access.",
        "not production QOS runtime",
        "no cloud access",
        "no token access",
        "no hardware access",
        "no official endorsement"
      ]
    },
    {
      "capability_level": 3,
      "category": "Backend compatibility",
      "executable_workflows": [
        "QuantumBridge IR to Quafu-compatible payload",
        "Quafu job spec",
        "offline mock backend",
        "optional pyquafu passthrough boundary"
      ],
      "project_id": "quafu",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "quafu",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": null
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "partial",
      "title": "Quafu / pyquafu",
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for quafu; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow is local-only: no cloud, token, credential, or hardware access.",
        "not full pyquafu replacement",
        "not production backend",
        "no cloud access",
        "no token access",
        "no hardware access",
        "no official endorsement"
      ]
    },
    {
      "capability_level": 3,
      "category": "Benchmarking",
      "executable_workflows": [
        "basic circuit benchmark suite",
        "simulator benchmark suite",
        "algorithms benchmark suite",
        "finance / optimization benchmark suite",
        "chemistry benchmark suite",
        "qml benchmark suite",
        "mitigation benchmark suite",
        "backend benchmark suite",
        "bridge benchmark suite",
        "JSON / Markdown report generation",
        "optional upstream Benchpress passthrough boundary"
      ],
      "project_id": "benchpress",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "benchpress",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": null
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "partial",
      "title": "Benchpress",
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for benchpress; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow is local-only: no cloud, token, credential, or hardware access.",
        "not full Benchpress replacement",
        "not official benchmark",
        "not production performance ranking",
        "no cloud access",
        "no token access",
        "no hardware access",
        "no official endorsement"
      ]
    }
  ],
  "summary": {
    "cloud_access": false,
    "hardware_access": false,
    "official_endorsement": false,
    "project_count": 12,
    "studio_ready": {
      "partial": 12
    },
    "token_access": false
  }
};

export const sampleWorkflows = {
  "details": [
    {
      "category": "finance",
      "cloud_access": false,
      "default_inputs": {
        "budget": 2
      },
      "description": "Local-only QuantumBridge Studio workflow for Portfolio Optimization.",
      "examples": [
        {
          "inputs": {
            "budget": 2
          }
        }
      ],
      "executable": true,
      "hardware_access": false,
      "input_schema": {
        "defaults": {
          "budget": 2
        },
        "fields": [
          {
            "default": 2,
            "description": "",
            "enum": [],
            "field_type": "integer",
            "maximum": null,
            "minimum": null,
            "name": "budget",
            "required": false
          }
        ],
        "provenance": {
          "cloud_access": false,
          "copied_upstream_source": false,
          "hardware_access": false,
          "metadata": {
            "api_layer": "quantumbridge.studio",
            "frontend_ui_implementation": false,
            "local_router": true
          },
          "official_endorsement": false,
          "production_ready": false,
          "project_id": "qiskit-finance",
          "source": "quantumbridge",
          "token_access": false,
          "workflow_id": "finance.portfolio_optimization_native"
        },
        "schema_version": "quantumbridge-studio-api-v0.1",
        "unsupported_reason": null,
        "warnings": [
          "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
          "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
          "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
          "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
          "QuantumBridge Studio uses clean-room local metadata for qiskit-finance; no third-party source, UI, prose, or branding is copied.",
          "Studio workflow finance.portfolio_optimization_native is local-only: no cloud, token, credential, or hardware access."
        ],
        "workflow_id": "finance.portfolio_optimization_native"
      },
      "local_only": true,
      "output_schema": {
        "result_schema": "PortfolioOptimizationResult",
        "type": "object"
      },
      "production_ready": false,
      "project_id": "qiskit-finance",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qiskit-finance",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "finance.portfolio_optimization_native"
      },
      "result_schema": "PortfolioOptimizationResult",
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "Portfolio Optimization",
      "token_access": false,
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-finance; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow finance.portfolio_optimization_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "finance.portfolio_optimization_native"
    },
    {
      "category": "optimization",
      "cloud_access": false,
      "default_inputs": {},
      "description": "Local-only QuantumBridge Studio workflow for Quadratic Program.",
      "examples": [
        {
          "inputs": {}
        }
      ],
      "executable": true,
      "hardware_access": false,
      "input_schema": {
        "defaults": {},
        "fields": [],
        "provenance": {
          "cloud_access": false,
          "copied_upstream_source": false,
          "hardware_access": false,
          "metadata": {
            "api_layer": "quantumbridge.studio",
            "frontend_ui_implementation": false,
            "local_router": true
          },
          "official_endorsement": false,
          "production_ready": false,
          "project_id": "qiskit-optimization",
          "source": "quantumbridge",
          "token_access": false,
          "workflow_id": "optimization.quadratic_program_native"
        },
        "schema_version": "quantumbridge-studio-api-v0.1",
        "unsupported_reason": null,
        "warnings": [
          "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
          "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
          "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
          "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
          "QuantumBridge Studio uses clean-room local metadata for qiskit-optimization; no third-party source, UI, prose, or branding is copied.",
          "Studio workflow optimization.quadratic_program_native is local-only: no cloud, token, credential, or hardware access."
        ],
        "workflow_id": "optimization.quadratic_program_native"
      },
      "local_only": true,
      "output_schema": {
        "result_schema": "NativeOptimizationResult",
        "type": "object"
      },
      "production_ready": false,
      "project_id": "qiskit-optimization",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qiskit-optimization",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "optimization.quadratic_program_native"
      },
      "result_schema": "NativeOptimizationResult",
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "Quadratic Program",
      "token_access": false,
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-optimization; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow optimization.quadratic_program_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "optimization.quadratic_program_native"
    },
    {
      "category": "algorithms",
      "cloud_access": false,
      "default_inputs": {},
      "description": "Local-only QuantumBridge Studio workflow for VQE Native.",
      "examples": [
        {
          "inputs": {}
        }
      ],
      "executable": true,
      "hardware_access": false,
      "input_schema": {
        "defaults": {},
        "fields": [],
        "provenance": {
          "cloud_access": false,
          "copied_upstream_source": false,
          "hardware_access": false,
          "metadata": {
            "api_layer": "quantumbridge.studio",
            "frontend_ui_implementation": false,
            "local_router": true
          },
          "official_endorsement": false,
          "production_ready": false,
          "project_id": "qiskit-algorithms",
          "source": "quantumbridge",
          "token_access": false,
          "workflow_id": "algorithms.vqe_native"
        },
        "schema_version": "quantumbridge-studio-api-v0.1",
        "unsupported_reason": null,
        "warnings": [
          "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
          "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
          "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
          "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
          "QuantumBridge Studio uses clean-room local metadata for qiskit-algorithms; no third-party source, UI, prose, or branding is copied.",
          "Studio workflow algorithms.vqe_native is local-only: no cloud, token, credential, or hardware access."
        ],
        "workflow_id": "algorithms.vqe_native"
      },
      "local_only": true,
      "output_schema": {
        "result_schema": "VQEResult",
        "type": "object"
      },
      "production_ready": false,
      "project_id": "qiskit-algorithms",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qiskit-algorithms",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "algorithms.vqe_native"
      },
      "result_schema": "VQEResult",
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "VQE Native",
      "token_access": false,
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-algorithms; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow algorithms.vqe_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "algorithms.vqe_native"
    },
    {
      "category": "algorithms",
      "cloud_access": false,
      "default_inputs": {
        "p": 1
      },
      "description": "Local-only QuantumBridge Studio workflow for QAOA MaxCut Native.",
      "examples": [
        {
          "inputs": {
            "p": 1
          }
        }
      ],
      "executable": true,
      "hardware_access": false,
      "input_schema": {
        "defaults": {
          "p": 1
        },
        "fields": [
          {
            "default": 1,
            "description": "",
            "enum": [],
            "field_type": "integer",
            "maximum": null,
            "minimum": null,
            "name": "p",
            "required": false
          }
        ],
        "provenance": {
          "cloud_access": false,
          "copied_upstream_source": false,
          "hardware_access": false,
          "metadata": {
            "api_layer": "quantumbridge.studio",
            "frontend_ui_implementation": false,
            "local_router": true
          },
          "official_endorsement": false,
          "production_ready": false,
          "project_id": "qiskit-algorithms",
          "source": "quantumbridge",
          "token_access": false,
          "workflow_id": "algorithms.qaoa_native"
        },
        "schema_version": "quantumbridge-studio-api-v0.1",
        "unsupported_reason": null,
        "warnings": [
          "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
          "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
          "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
          "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
          "QuantumBridge Studio uses clean-room local metadata for qiskit-algorithms; no third-party source, UI, prose, or branding is copied.",
          "Studio workflow algorithms.qaoa_native is local-only: no cloud, token, credential, or hardware access."
        ],
        "workflow_id": "algorithms.qaoa_native"
      },
      "local_only": true,
      "output_schema": {
        "result_schema": "QAOAResult",
        "type": "object"
      },
      "production_ready": false,
      "project_id": "qiskit-algorithms",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qiskit-algorithms",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "algorithms.qaoa_native"
      },
      "result_schema": "QAOAResult",
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "QAOA MaxCut Native",
      "token_access": false,
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-algorithms; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow algorithms.qaoa_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "algorithms.qaoa_native"
    },
    {
      "category": "algorithms",
      "cloud_access": false,
      "default_inputs": {
        "marked_bitstrings": [
          "11"
        ]
      },
      "description": "Local-only QuantumBridge Studio workflow for Grover Native.",
      "examples": [
        {
          "inputs": {
            "marked_bitstrings": [
              "11"
            ]
          }
        }
      ],
      "executable": true,
      "hardware_access": false,
      "input_schema": {
        "defaults": {
          "marked_bitstrings": [
            "11"
          ]
        },
        "fields": [
          {
            "default": [
              "11"
            ],
            "description": "",
            "enum": [],
            "field_type": "list",
            "maximum": null,
            "minimum": null,
            "name": "marked_bitstrings",
            "required": false
          }
        ],
        "provenance": {
          "cloud_access": false,
          "copied_upstream_source": false,
          "hardware_access": false,
          "metadata": {
            "api_layer": "quantumbridge.studio",
            "frontend_ui_implementation": false,
            "local_router": true
          },
          "official_endorsement": false,
          "production_ready": false,
          "project_id": "qiskit-algorithms",
          "source": "quantumbridge",
          "token_access": false,
          "workflow_id": "algorithms.grover_native"
        },
        "schema_version": "quantumbridge-studio-api-v0.1",
        "unsupported_reason": null,
        "warnings": [
          "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
          "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
          "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
          "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
          "QuantumBridge Studio uses clean-room local metadata for qiskit-algorithms; no third-party source, UI, prose, or branding is copied.",
          "Studio workflow algorithms.grover_native is local-only: no cloud, token, credential, or hardware access."
        ],
        "workflow_id": "algorithms.grover_native"
      },
      "local_only": true,
      "output_schema": {
        "result_schema": "GroverResult",
        "type": "object"
      },
      "production_ready": false,
      "project_id": "qiskit-algorithms",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qiskit-algorithms",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "algorithms.grover_native"
      },
      "result_schema": "GroverResult",
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "Grover Native",
      "token_access": false,
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-algorithms; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow algorithms.grover_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "algorithms.grover_native"
    },
    {
      "category": "chemistry",
      "cloud_access": false,
      "default_inputs": {
        "bond_length": 0.735
      },
      "description": "Local-only QuantumBridge Studio workflow for H2 Chemistry Native.",
      "examples": [
        {
          "inputs": {
            "bond_length": 0.735
          }
        }
      ],
      "executable": true,
      "hardware_access": false,
      "input_schema": {
        "defaults": {
          "bond_length": 0.735
        },
        "fields": [
          {
            "default": 0.735,
            "description": "",
            "enum": [],
            "field_type": "float",
            "maximum": null,
            "minimum": null,
            "name": "bond_length",
            "required": false
          }
        ],
        "provenance": {
          "cloud_access": false,
          "copied_upstream_source": false,
          "hardware_access": false,
          "metadata": {
            "api_layer": "quantumbridge.studio",
            "frontend_ui_implementation": false,
            "local_router": true
          },
          "official_endorsement": false,
          "production_ready": false,
          "project_id": "qiskit-nature",
          "source": "quantumbridge",
          "token_access": false,
          "workflow_id": "nature.h2_native"
        },
        "schema_version": "quantumbridge-studio-api-v0.1",
        "unsupported_reason": null,
        "warnings": [
          "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
          "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
          "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
          "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
          "QuantumBridge Studio uses clean-room local metadata for qiskit-nature; no third-party source, UI, prose, or branding is copied.",
          "Studio workflow nature.h2_native is local-only: no cloud, token, credential, or hardware access."
        ],
        "workflow_id": "nature.h2_native"
      },
      "local_only": true,
      "output_schema": {
        "result_schema": "H2WorkflowResult",
        "type": "object"
      },
      "production_ready": false,
      "project_id": "qiskit-nature",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qiskit-nature",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "nature.h2_native"
      },
      "result_schema": "H2WorkflowResult",
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "H2 Chemistry Native",
      "token_access": false,
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-nature; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow nature.h2_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "nature.h2_native"
    },
    {
      "category": "chemistry",
      "cloud_access": false,
      "default_inputs": {
        "bond_length": 1.6
      },
      "description": "Local-only QuantumBridge Studio workflow for LiH Chemistry Native.",
      "examples": [
        {
          "inputs": {
            "bond_length": 1.6
          }
        }
      ],
      "executable": true,
      "hardware_access": false,
      "input_schema": {
        "defaults": {
          "bond_length": 1.6
        },
        "fields": [
          {
            "default": 1.6,
            "description": "",
            "enum": [],
            "field_type": "float",
            "maximum": null,
            "minimum": null,
            "name": "bond_length",
            "required": false
          }
        ],
        "provenance": {
          "cloud_access": false,
          "copied_upstream_source": false,
          "hardware_access": false,
          "metadata": {
            "api_layer": "quantumbridge.studio",
            "frontend_ui_implementation": false,
            "local_router": true
          },
          "official_endorsement": false,
          "production_ready": false,
          "project_id": "qiskit-nature",
          "source": "quantumbridge",
          "token_access": false,
          "workflow_id": "nature.lih_native"
        },
        "schema_version": "quantumbridge-studio-api-v0.1",
        "unsupported_reason": null,
        "warnings": [
          "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
          "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
          "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
          "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
          "QuantumBridge Studio uses clean-room local metadata for qiskit-nature; no third-party source, UI, prose, or branding is copied.",
          "Studio workflow nature.lih_native is local-only: no cloud, token, credential, or hardware access."
        ],
        "workflow_id": "nature.lih_native"
      },
      "local_only": true,
      "output_schema": {
        "result_schema": "LiHWorkflowResult",
        "type": "object"
      },
      "production_ready": false,
      "project_id": "qiskit-nature",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qiskit-nature",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "nature.lih_native"
      },
      "result_schema": "LiHWorkflowResult",
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "LiH Chemistry Native",
      "token_access": false,
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-nature; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow nature.lih_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "nature.lih_native"
    },
    {
      "category": "machine-learning",
      "cloud_access": false,
      "default_inputs": {},
      "description": "Local-only QuantumBridge Studio workflow for Quantum Kernel Native.",
      "examples": [
        {
          "inputs": {}
        }
      ],
      "executable": true,
      "hardware_access": false,
      "input_schema": {
        "defaults": {},
        "fields": [],
        "provenance": {
          "cloud_access": false,
          "copied_upstream_source": false,
          "hardware_access": false,
          "metadata": {
            "api_layer": "quantumbridge.studio",
            "frontend_ui_implementation": false,
            "local_router": true
          },
          "official_endorsement": false,
          "production_ready": false,
          "project_id": "qiskit-machine-learning",
          "source": "quantumbridge",
          "token_access": false,
          "workflow_id": "ml.quantum_kernel_native"
        },
        "schema_version": "quantumbridge-studio-api-v0.1",
        "unsupported_reason": null,
        "warnings": [
          "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
          "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
          "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
          "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
          "QuantumBridge Studio uses clean-room local metadata for qiskit-machine-learning; no third-party source, UI, prose, or branding is copied.",
          "Studio workflow ml.quantum_kernel_native is local-only: no cloud, token, credential, or hardware access."
        ],
        "workflow_id": "ml.quantum_kernel_native"
      },
      "local_only": true,
      "output_schema": {
        "result_schema": "QuantumKernelResult",
        "type": "object"
      },
      "production_ready": false,
      "project_id": "qiskit-machine-learning",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qiskit-machine-learning",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "ml.quantum_kernel_native"
      },
      "result_schema": "QuantumKernelResult",
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "Quantum Kernel Native",
      "token_access": false,
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-machine-learning; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow ml.quantum_kernel_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "ml.quantum_kernel_native"
    },
    {
      "category": "machine-learning",
      "cloud_access": false,
      "default_inputs": {},
      "description": "Local-only QuantumBridge Studio workflow for Kernel Classifier Native.",
      "examples": [
        {
          "inputs": {}
        }
      ],
      "executable": true,
      "hardware_access": false,
      "input_schema": {
        "defaults": {},
        "fields": [],
        "provenance": {
          "cloud_access": false,
          "copied_upstream_source": false,
          "hardware_access": false,
          "metadata": {
            "api_layer": "quantumbridge.studio",
            "frontend_ui_implementation": false,
            "local_router": true
          },
          "official_endorsement": false,
          "production_ready": false,
          "project_id": "qiskit-machine-learning",
          "source": "quantumbridge",
          "token_access": false,
          "workflow_id": "ml.kernel_classifier_native"
        },
        "schema_version": "quantumbridge-studio-api-v0.1",
        "unsupported_reason": null,
        "warnings": [
          "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
          "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
          "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
          "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
          "QuantumBridge Studio uses clean-room local metadata for qiskit-machine-learning; no third-party source, UI, prose, or branding is copied.",
          "Studio workflow ml.kernel_classifier_native is local-only: no cloud, token, credential, or hardware access."
        ],
        "workflow_id": "ml.kernel_classifier_native"
      },
      "local_only": true,
      "output_schema": {
        "result_schema": "KernelClassifierResult",
        "type": "object"
      },
      "production_ready": false,
      "project_id": "qiskit-machine-learning",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qiskit-machine-learning",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "ml.kernel_classifier_native"
      },
      "result_schema": "KernelClassifierResult",
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "Kernel Classifier Native",
      "token_access": false,
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-machine-learning; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow ml.kernel_classifier_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "ml.kernel_classifier_native"
    },
    {
      "category": "machine-learning",
      "cloud_access": false,
      "default_inputs": {},
      "description": "Local-only QuantumBridge Studio workflow for QNN Classifier Native.",
      "examples": [
        {
          "inputs": {}
        }
      ],
      "executable": true,
      "hardware_access": false,
      "input_schema": {
        "defaults": {},
        "fields": [],
        "provenance": {
          "cloud_access": false,
          "copied_upstream_source": false,
          "hardware_access": false,
          "metadata": {
            "api_layer": "quantumbridge.studio",
            "frontend_ui_implementation": false,
            "local_router": true
          },
          "official_endorsement": false,
          "production_ready": false,
          "project_id": "qiskit-machine-learning",
          "source": "quantumbridge",
          "token_access": false,
          "workflow_id": "ml.qnn_classifier_native"
        },
        "schema_version": "quantumbridge-studio-api-v0.1",
        "unsupported_reason": null,
        "warnings": [
          "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
          "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
          "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
          "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
          "QuantumBridge Studio uses clean-room local metadata for qiskit-machine-learning; no third-party source, UI, prose, or branding is copied.",
          "Studio workflow ml.qnn_classifier_native is local-only: no cloud, token, credential, or hardware access."
        ],
        "workflow_id": "ml.qnn_classifier_native"
      },
      "local_only": true,
      "output_schema": {
        "result_schema": "QNNClassifierResult",
        "type": "object"
      },
      "production_ready": false,
      "project_id": "qiskit-machine-learning",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qiskit-machine-learning",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "ml.qnn_classifier_native"
      },
      "result_schema": "QNNClassifierResult",
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "QNN Classifier Native",
      "token_access": false,
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-machine-learning; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow ml.qnn_classifier_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "ml.qnn_classifier_native"
    },
    {
      "category": "simulator",
      "cloud_access": false,
      "default_inputs": {},
      "description": "Local-only QuantumBridge Studio workflow for Statevector Simulator Native.",
      "examples": [
        {
          "inputs": {}
        }
      ],
      "executable": true,
      "hardware_access": false,
      "input_schema": {
        "defaults": {},
        "fields": [],
        "provenance": {
          "cloud_access": false,
          "copied_upstream_source": false,
          "hardware_access": false,
          "metadata": {
            "api_layer": "quantumbridge.studio",
            "frontend_ui_implementation": false,
            "local_router": true
          },
          "official_endorsement": false,
          "production_ready": false,
          "project_id": "qiskit-aer",
          "source": "quantumbridge",
          "token_access": false,
          "workflow_id": "aer.statevector_native"
        },
        "schema_version": "quantumbridge-studio-api-v0.1",
        "unsupported_reason": null,
        "warnings": [
          "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
          "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
          "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
          "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
          "QuantumBridge Studio uses clean-room local metadata for qiskit-aer; no third-party source, UI, prose, or branding is copied.",
          "Studio workflow aer.statevector_native is local-only: no cloud, token, credential, or hardware access."
        ],
        "workflow_id": "aer.statevector_native"
      },
      "local_only": true,
      "output_schema": {
        "result_schema": "StatevectorSimulationResult",
        "type": "object"
      },
      "production_ready": false,
      "project_id": "qiskit-aer",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qiskit-aer",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "aer.statevector_native"
      },
      "result_schema": "StatevectorSimulationResult",
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "Statevector Simulator Native",
      "token_access": false,
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-aer; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow aer.statevector_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "aer.statevector_native"
    },
    {
      "category": "simulator",
      "cloud_access": false,
      "default_inputs": {
        "seed": 7,
        "shots": 128
      },
      "description": "Local-only QuantumBridge Studio workflow for QASM Counts Native.",
      "examples": [
        {
          "inputs": {
            "seed": 7,
            "shots": 128
          }
        }
      ],
      "executable": true,
      "hardware_access": false,
      "input_schema": {
        "defaults": {
          "seed": 7,
          "shots": 128
        },
        "fields": [
          {
            "default": 128,
            "description": "",
            "enum": [],
            "field_type": "integer",
            "maximum": null,
            "minimum": null,
            "name": "shots",
            "required": false
          },
          {
            "default": 7,
            "description": "",
            "enum": [],
            "field_type": "integer",
            "maximum": null,
            "minimum": null,
            "name": "seed",
            "required": false
          }
        ],
        "provenance": {
          "cloud_access": false,
          "copied_upstream_source": false,
          "hardware_access": false,
          "metadata": {
            "api_layer": "quantumbridge.studio",
            "frontend_ui_implementation": false,
            "local_router": true
          },
          "official_endorsement": false,
          "production_ready": false,
          "project_id": "qiskit-aer",
          "source": "quantumbridge",
          "token_access": false,
          "workflow_id": "aer.qasm_counts_native"
        },
        "schema_version": "quantumbridge-studio-api-v0.1",
        "unsupported_reason": null,
        "warnings": [
          "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
          "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
          "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
          "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
          "QuantumBridge Studio uses clean-room local metadata for qiskit-aer; no third-party source, UI, prose, or branding is copied.",
          "Studio workflow aer.qasm_counts_native is local-only: no cloud, token, credential, or hardware access."
        ],
        "workflow_id": "aer.qasm_counts_native"
      },
      "local_only": true,
      "output_schema": {
        "result_schema": "QasmSimulationResult",
        "type": "object"
      },
      "production_ready": false,
      "project_id": "qiskit-aer",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qiskit-aer",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "aer.qasm_counts_native"
      },
      "result_schema": "QasmSimulationResult",
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "QASM Counts Native",
      "token_access": false,
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-aer; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow aer.qasm_counts_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "aer.qasm_counts_native"
    },
    {
      "category": "simulator",
      "cloud_access": false,
      "default_inputs": {
        "seed": 7,
        "shots": 128
      },
      "description": "Local-only QuantumBridge Studio workflow for Noisy Counts Native.",
      "examples": [
        {
          "inputs": {
            "seed": 7,
            "shots": 128
          }
        }
      ],
      "executable": true,
      "hardware_access": false,
      "input_schema": {
        "defaults": {
          "seed": 7,
          "shots": 128
        },
        "fields": [
          {
            "default": 128,
            "description": "",
            "enum": [],
            "field_type": "integer",
            "maximum": null,
            "minimum": null,
            "name": "shots",
            "required": false
          },
          {
            "default": 7,
            "description": "",
            "enum": [],
            "field_type": "integer",
            "maximum": null,
            "minimum": null,
            "name": "seed",
            "required": false
          }
        ],
        "provenance": {
          "cloud_access": false,
          "copied_upstream_source": false,
          "hardware_access": false,
          "metadata": {
            "api_layer": "quantumbridge.studio",
            "frontend_ui_implementation": false,
            "local_router": true
          },
          "official_endorsement": false,
          "production_ready": false,
          "project_id": "qiskit-aer",
          "source": "quantumbridge",
          "token_access": false,
          "workflow_id": "aer.noisy_counts_native"
        },
        "schema_version": "quantumbridge-studio-api-v0.1",
        "unsupported_reason": null,
        "warnings": [
          "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
          "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
          "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
          "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
          "QuantumBridge Studio uses clean-room local metadata for qiskit-aer; no third-party source, UI, prose, or branding is copied.",
          "Studio workflow aer.noisy_counts_native is local-only: no cloud, token, credential, or hardware access."
        ],
        "workflow_id": "aer.noisy_counts_native"
      },
      "local_only": true,
      "output_schema": {
        "result_schema": "NoisySimulationResult",
        "type": "object"
      },
      "production_ready": false,
      "project_id": "qiskit-aer",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qiskit-aer",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "aer.noisy_counts_native"
      },
      "result_schema": "NoisySimulationResult",
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "Noisy Counts Native",
      "token_access": false,
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-aer; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow aer.noisy_counts_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "aer.noisy_counts_native"
    },
    {
      "category": "mitigation",
      "cloud_access": false,
      "default_inputs": {
        "seed": 13,
        "shots": 256
      },
      "description": "Local-only QuantumBridge Studio workflow for ZNE Native.",
      "examples": [
        {
          "inputs": {
            "seed": 13,
            "shots": 256
          }
        }
      ],
      "executable": true,
      "hardware_access": false,
      "input_schema": {
        "defaults": {
          "seed": 13,
          "shots": 256
        },
        "fields": [
          {
            "default": 256,
            "description": "",
            "enum": [],
            "field_type": "integer",
            "maximum": null,
            "minimum": null,
            "name": "shots",
            "required": false
          },
          {
            "default": 13,
            "description": "",
            "enum": [],
            "field_type": "integer",
            "maximum": null,
            "minimum": null,
            "name": "seed",
            "required": false
          }
        ],
        "provenance": {
          "cloud_access": false,
          "copied_upstream_source": false,
          "hardware_access": false,
          "metadata": {
            "api_layer": "quantumbridge.studio",
            "frontend_ui_implementation": false,
            "local_router": true
          },
          "official_endorsement": false,
          "production_ready": false,
          "project_id": "mitiq",
          "source": "quantumbridge",
          "token_access": false,
          "workflow_id": "mitiq.zne_native"
        },
        "schema_version": "quantumbridge-studio-api-v0.1",
        "unsupported_reason": null,
        "warnings": [
          "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
          "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
          "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
          "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
          "QuantumBridge Studio uses clean-room local metadata for mitiq; no third-party source, UI, prose, or branding is copied.",
          "Studio workflow mitiq.zne_native is local-only: no cloud, token, credential, or hardware access."
        ],
        "workflow_id": "mitiq.zne_native"
      },
      "local_only": true,
      "output_schema": {
        "result_schema": "ZNEResult",
        "type": "object"
      },
      "production_ready": false,
      "project_id": "mitiq",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "mitiq",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "mitiq.zne_native"
      },
      "result_schema": "ZNEResult",
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "ZNE Native",
      "token_access": false,
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for mitiq; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow mitiq.zne_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "mitiq.zne_native"
    },
    {
      "category": "mitigation",
      "cloud_access": false,
      "default_inputs": {
        "seed": 21,
        "shots": 256
      },
      "description": "Local-only QuantumBridge Studio workflow for Readout Mitigation Native.",
      "examples": [
        {
          "inputs": {
            "seed": 21,
            "shots": 256
          }
        }
      ],
      "executable": true,
      "hardware_access": false,
      "input_schema": {
        "defaults": {
          "seed": 21,
          "shots": 256
        },
        "fields": [
          {
            "default": 256,
            "description": "",
            "enum": [],
            "field_type": "integer",
            "maximum": null,
            "minimum": null,
            "name": "shots",
            "required": false
          },
          {
            "default": 21,
            "description": "",
            "enum": [],
            "field_type": "integer",
            "maximum": null,
            "minimum": null,
            "name": "seed",
            "required": false
          }
        ],
        "provenance": {
          "cloud_access": false,
          "copied_upstream_source": false,
          "hardware_access": false,
          "metadata": {
            "api_layer": "quantumbridge.studio",
            "frontend_ui_implementation": false,
            "local_router": true
          },
          "official_endorsement": false,
          "production_ready": false,
          "project_id": "mitiq",
          "source": "quantumbridge",
          "token_access": false,
          "workflow_id": "mitiq.readout_mitigation_native"
        },
        "schema_version": "quantumbridge-studio-api-v0.1",
        "unsupported_reason": null,
        "warnings": [
          "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
          "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
          "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
          "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
          "QuantumBridge Studio uses clean-room local metadata for mitiq; no third-party source, UI, prose, or branding is copied.",
          "Studio workflow mitiq.readout_mitigation_native is local-only: no cloud, token, credential, or hardware access."
        ],
        "workflow_id": "mitiq.readout_mitigation_native"
      },
      "local_only": true,
      "output_schema": {
        "result_schema": "ReadoutMitigationResult",
        "type": "object"
      },
      "production_ready": false,
      "project_id": "mitiq",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "mitiq",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "mitiq.readout_mitigation_native"
      },
      "result_schema": "ReadoutMitigationResult",
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "Readout Mitigation Native",
      "token_access": false,
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for mitiq; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow mitiq.readout_mitigation_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "mitiq.readout_mitigation_native"
    },
    {
      "category": "bridge",
      "cloud_access": false,
      "default_inputs": {},
      "description": "Local-only QuantumBridge Studio workflow for Qiskit to PennyLane Bridge.",
      "examples": [
        {
          "inputs": {}
        }
      ],
      "executable": true,
      "hardware_access": false,
      "input_schema": {
        "defaults": {},
        "fields": [],
        "provenance": {
          "cloud_access": false,
          "copied_upstream_source": false,
          "hardware_access": false,
          "metadata": {
            "api_layer": "quantumbridge.studio",
            "frontend_ui_implementation": false,
            "local_router": true
          },
          "official_endorsement": false,
          "production_ready": false,
          "project_id": "pennylane-qiskit",
          "source": "quantumbridge",
          "token_access": false,
          "workflow_id": "pennylane_qiskit.qiskit_to_pennylane"
        },
        "schema_version": "quantumbridge-studio-api-v0.1",
        "unsupported_reason": null,
        "warnings": [
          "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
          "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
          "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
          "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
          "QuantumBridge Studio uses clean-room local metadata for pennylane-qiskit; no third-party source, UI, prose, or branding is copied.",
          "Studio workflow pennylane_qiskit.qiskit_to_pennylane is local-only: no cloud, token, credential, or hardware access."
        ],
        "workflow_id": "pennylane_qiskit.qiskit_to_pennylane"
      },
      "local_only": true,
      "output_schema": {
        "result_schema": "QiskitToPennyLaneResult",
        "type": "object"
      },
      "production_ready": false,
      "project_id": "pennylane-qiskit",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "pennylane-qiskit",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "pennylane_qiskit.qiskit_to_pennylane"
      },
      "result_schema": "QiskitToPennyLaneResult",
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "Qiskit to PennyLane Bridge",
      "token_access": false,
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for pennylane-qiskit; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow pennylane_qiskit.qiskit_to_pennylane is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "pennylane_qiskit.qiskit_to_pennylane"
    },
    {
      "category": "bridge",
      "cloud_access": false,
      "default_inputs": {},
      "description": "Local-only QuantumBridge Studio workflow for PennyLane to Qiskit Bridge.",
      "examples": [
        {
          "inputs": {}
        }
      ],
      "executable": true,
      "hardware_access": false,
      "input_schema": {
        "defaults": {},
        "fields": [],
        "provenance": {
          "cloud_access": false,
          "copied_upstream_source": false,
          "hardware_access": false,
          "metadata": {
            "api_layer": "quantumbridge.studio",
            "frontend_ui_implementation": false,
            "local_router": true
          },
          "official_endorsement": false,
          "production_ready": false,
          "project_id": "pennylane-qiskit",
          "source": "quantumbridge",
          "token_access": false,
          "workflow_id": "pennylane_qiskit.pennylane_to_qiskit"
        },
        "schema_version": "quantumbridge-studio-api-v0.1",
        "unsupported_reason": null,
        "warnings": [
          "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
          "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
          "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
          "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
          "QuantumBridge Studio uses clean-room local metadata for pennylane-qiskit; no third-party source, UI, prose, or branding is copied.",
          "Studio workflow pennylane_qiskit.pennylane_to_qiskit is local-only: no cloud, token, credential, or hardware access."
        ],
        "workflow_id": "pennylane_qiskit.pennylane_to_qiskit"
      },
      "local_only": true,
      "output_schema": {
        "result_schema": "PennyLaneToQiskitResult",
        "type": "object"
      },
      "production_ready": false,
      "project_id": "pennylane-qiskit",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "pennylane-qiskit",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "pennylane_qiskit.pennylane_to_qiskit"
      },
      "result_schema": "PennyLaneToQiskitResult",
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "PennyLane to Qiskit Bridge",
      "token_access": false,
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for pennylane-qiskit; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow pennylane_qiskit.pennylane_to_qiskit is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "pennylane_qiskit.pennylane_to_qiskit"
    },
    {
      "category": "experiments",
      "cloud_access": false,
      "default_inputs": {},
      "description": "Local-only QuantumBridge Studio workflow for Rabi Experiment Native.",
      "examples": [
        {
          "inputs": {}
        }
      ],
      "executable": true,
      "hardware_access": false,
      "input_schema": {
        "defaults": {},
        "fields": [],
        "provenance": {
          "cloud_access": false,
          "copied_upstream_source": false,
          "hardware_access": false,
          "metadata": {
            "api_layer": "quantumbridge.studio",
            "frontend_ui_implementation": false,
            "local_router": true
          },
          "official_endorsement": false,
          "production_ready": false,
          "project_id": "qiskit-experiments",
          "source": "quantumbridge",
          "token_access": false,
          "workflow_id": "experiments.rabi_native"
        },
        "schema_version": "quantumbridge-studio-api-v0.1",
        "unsupported_reason": null,
        "warnings": [
          "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
          "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
          "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
          "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
          "QuantumBridge Studio uses clean-room local metadata for qiskit-experiments; no third-party source, UI, prose, or branding is copied.",
          "Studio workflow experiments.rabi_native is local-only: no cloud, token, credential, or hardware access."
        ],
        "workflow_id": "experiments.rabi_native"
      },
      "local_only": true,
      "output_schema": {
        "result_schema": "RabiExperimentResult",
        "type": "object"
      },
      "production_ready": false,
      "project_id": "qiskit-experiments",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qiskit-experiments",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "experiments.rabi_native"
      },
      "result_schema": "RabiExperimentResult",
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "Rabi Experiment Native",
      "token_access": false,
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-experiments; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow experiments.rabi_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "experiments.rabi_native"
    },
    {
      "category": "experiments",
      "cloud_access": false,
      "default_inputs": {},
      "description": "Local-only QuantumBridge Studio workflow for T1 Experiment Native.",
      "examples": [
        {
          "inputs": {}
        }
      ],
      "executable": true,
      "hardware_access": false,
      "input_schema": {
        "defaults": {},
        "fields": [],
        "provenance": {
          "cloud_access": false,
          "copied_upstream_source": false,
          "hardware_access": false,
          "metadata": {
            "api_layer": "quantumbridge.studio",
            "frontend_ui_implementation": false,
            "local_router": true
          },
          "official_endorsement": false,
          "production_ready": false,
          "project_id": "qiskit-experiments",
          "source": "quantumbridge",
          "token_access": false,
          "workflow_id": "experiments.t1_native"
        },
        "schema_version": "quantumbridge-studio-api-v0.1",
        "unsupported_reason": null,
        "warnings": [
          "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
          "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
          "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
          "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
          "QuantumBridge Studio uses clean-room local metadata for qiskit-experiments; no third-party source, UI, prose, or branding is copied.",
          "Studio workflow experiments.t1_native is local-only: no cloud, token, credential, or hardware access."
        ],
        "workflow_id": "experiments.t1_native"
      },
      "local_only": true,
      "output_schema": {
        "result_schema": "T1ExperimentResult",
        "type": "object"
      },
      "production_ready": false,
      "project_id": "qiskit-experiments",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qiskit-experiments",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "experiments.t1_native"
      },
      "result_schema": "T1ExperimentResult",
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "T1 Experiment Native",
      "token_access": false,
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-experiments; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow experiments.t1_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "experiments.t1_native"
    },
    {
      "category": "experiments",
      "cloud_access": false,
      "default_inputs": {},
      "description": "Local-only QuantumBridge Studio workflow for Ramsey Experiment Native.",
      "examples": [
        {
          "inputs": {}
        }
      ],
      "executable": true,
      "hardware_access": false,
      "input_schema": {
        "defaults": {},
        "fields": [],
        "provenance": {
          "cloud_access": false,
          "copied_upstream_source": false,
          "hardware_access": false,
          "metadata": {
            "api_layer": "quantumbridge.studio",
            "frontend_ui_implementation": false,
            "local_router": true
          },
          "official_endorsement": false,
          "production_ready": false,
          "project_id": "qiskit-experiments",
          "source": "quantumbridge",
          "token_access": false,
          "workflow_id": "experiments.ramsey_native"
        },
        "schema_version": "quantumbridge-studio-api-v0.1",
        "unsupported_reason": null,
        "warnings": [
          "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
          "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
          "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
          "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
          "QuantumBridge Studio uses clean-room local metadata for qiskit-experiments; no third-party source, UI, prose, or branding is copied.",
          "Studio workflow experiments.ramsey_native is local-only: no cloud, token, credential, or hardware access."
        ],
        "workflow_id": "experiments.ramsey_native"
      },
      "local_only": true,
      "output_schema": {
        "result_schema": "RamseyExperimentResult",
        "type": "object"
      },
      "production_ready": false,
      "project_id": "qiskit-experiments",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qiskit-experiments",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "experiments.ramsey_native"
      },
      "result_schema": "RamseyExperimentResult",
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "Ramsey Experiment Native",
      "token_access": false,
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-experiments; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow experiments.ramsey_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "experiments.ramsey_native"
    },
    {
      "category": "dynamics",
      "cloud_access": false,
      "default_inputs": {},
      "description": "Local-only QuantumBridge Studio workflow for Z Precession Dynamics Native.",
      "examples": [
        {
          "inputs": {}
        }
      ],
      "executable": true,
      "hardware_access": false,
      "input_schema": {
        "defaults": {},
        "fields": [],
        "provenance": {
          "cloud_access": false,
          "copied_upstream_source": false,
          "hardware_access": false,
          "metadata": {
            "api_layer": "quantumbridge.studio",
            "frontend_ui_implementation": false,
            "local_router": true
          },
          "official_endorsement": false,
          "production_ready": false,
          "project_id": "qiskit-dynamics",
          "source": "quantumbridge",
          "token_access": false,
          "workflow_id": "dynamics.z_precession_native"
        },
        "schema_version": "quantumbridge-studio-api-v0.1",
        "unsupported_reason": null,
        "warnings": [
          "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
          "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
          "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
          "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
          "QuantumBridge Studio uses clean-room local metadata for qiskit-dynamics; no third-party source, UI, prose, or branding is copied.",
          "Studio workflow dynamics.z_precession_native is local-only: no cloud, token, credential, or hardware access."
        ],
        "workflow_id": "dynamics.z_precession_native"
      },
      "local_only": true,
      "output_schema": {
        "result_schema": "SingleQubitDynamicsResult",
        "type": "object"
      },
      "production_ready": false,
      "project_id": "qiskit-dynamics",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qiskit-dynamics",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "dynamics.z_precession_native"
      },
      "result_schema": "SingleQubitDynamicsResult",
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "Z Precession Dynamics Native",
      "token_access": false,
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-dynamics; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow dynamics.z_precession_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "dynamics.z_precession_native"
    },
    {
      "category": "dynamics",
      "cloud_access": false,
      "default_inputs": {},
      "description": "Local-only QuantumBridge Studio workflow for Rabi Drive Dynamics Native.",
      "examples": [
        {
          "inputs": {}
        }
      ],
      "executable": true,
      "hardware_access": false,
      "input_schema": {
        "defaults": {},
        "fields": [],
        "provenance": {
          "cloud_access": false,
          "copied_upstream_source": false,
          "hardware_access": false,
          "metadata": {
            "api_layer": "quantumbridge.studio",
            "frontend_ui_implementation": false,
            "local_router": true
          },
          "official_endorsement": false,
          "production_ready": false,
          "project_id": "qiskit-dynamics",
          "source": "quantumbridge",
          "token_access": false,
          "workflow_id": "dynamics.rabi_drive_native"
        },
        "schema_version": "quantumbridge-studio-api-v0.1",
        "unsupported_reason": null,
        "warnings": [
          "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
          "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
          "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
          "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
          "QuantumBridge Studio uses clean-room local metadata for qiskit-dynamics; no third-party source, UI, prose, or branding is copied.",
          "Studio workflow dynamics.rabi_drive_native is local-only: no cloud, token, credential, or hardware access."
        ],
        "workflow_id": "dynamics.rabi_drive_native"
      },
      "local_only": true,
      "output_schema": {
        "result_schema": "SingleQubitDynamicsResult",
        "type": "object"
      },
      "production_ready": false,
      "project_id": "qiskit-dynamics",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qiskit-dynamics",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "dynamics.rabi_drive_native"
      },
      "result_schema": "SingleQubitDynamicsResult",
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "Rabi Drive Dynamics Native",
      "token_access": false,
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-dynamics; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow dynamics.rabi_drive_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "dynamics.rabi_drive_native"
    },
    {
      "category": "compiler",
      "cloud_access": false,
      "default_inputs": {},
      "description": "Local-only QuantumBridge Studio workflow for MQT Core-like Circuit.",
      "examples": [
        {
          "inputs": {}
        }
      ],
      "executable": true,
      "hardware_access": false,
      "input_schema": {
        "defaults": {},
        "fields": [],
        "provenance": {
          "cloud_access": false,
          "copied_upstream_source": false,
          "hardware_access": false,
          "metadata": {
            "api_layer": "quantumbridge.studio",
            "frontend_ui_implementation": false,
            "local_router": true
          },
          "official_endorsement": false,
          "production_ready": false,
          "project_id": "mqt",
          "source": "quantumbridge",
          "token_access": false,
          "workflow_id": "mqt.core_like_circuit"
        },
        "schema_version": "quantumbridge-studio-api-v0.1",
        "unsupported_reason": null,
        "warnings": [
          "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
          "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
          "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
          "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
          "QuantumBridge Studio uses clean-room local metadata for mqt; no third-party source, UI, prose, or branding is copied.",
          "Studio workflow mqt.core_like_circuit is local-only: no cloud, token, credential, or hardware access."
        ],
        "workflow_id": "mqt.core_like_circuit"
      },
      "local_only": true,
      "output_schema": {
        "result_schema": "MQTCoreLikeCircuit",
        "type": "object"
      },
      "production_ready": false,
      "project_id": "mqt",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "mqt",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "mqt.core_like_circuit"
      },
      "result_schema": "MQTCoreLikeCircuit",
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "MQT Core-like Circuit",
      "token_access": false,
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for mqt; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow mqt.core_like_circuit is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "mqt.core_like_circuit"
    },
    {
      "category": "simulator",
      "cloud_access": false,
      "default_inputs": {},
      "description": "Local-only QuantumBridge Studio workflow for DDSIM-like Simulation.",
      "examples": [
        {
          "inputs": {}
        }
      ],
      "executable": true,
      "hardware_access": false,
      "input_schema": {
        "defaults": {},
        "fields": [],
        "provenance": {
          "cloud_access": false,
          "copied_upstream_source": false,
          "hardware_access": false,
          "metadata": {
            "api_layer": "quantumbridge.studio",
            "frontend_ui_implementation": false,
            "local_router": true
          },
          "official_endorsement": false,
          "production_ready": false,
          "project_id": "mqt",
          "source": "quantumbridge",
          "token_access": false,
          "workflow_id": "mqt.ddsim_like_simulation"
        },
        "schema_version": "quantumbridge-studio-api-v0.1",
        "unsupported_reason": null,
        "warnings": [
          "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
          "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
          "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
          "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
          "QuantumBridge Studio uses clean-room local metadata for mqt; no third-party source, UI, prose, or branding is copied.",
          "Studio workflow mqt.ddsim_like_simulation is local-only: no cloud, token, credential, or hardware access."
        ],
        "workflow_id": "mqt.ddsim_like_simulation"
      },
      "local_only": true,
      "output_schema": {
        "result_schema": "MQTDDLikeResult",
        "type": "object"
      },
      "production_ready": false,
      "project_id": "mqt",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "mqt",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "mqt.ddsim_like_simulation"
      },
      "result_schema": "MQTDDLikeResult",
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "DDSIM-like Simulation",
      "token_access": false,
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for mqt; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow mqt.ddsim_like_simulation is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "mqt.ddsim_like_simulation"
    },
    {
      "category": "routing",
      "cloud_access": false,
      "default_inputs": {},
      "description": "Local-only QuantumBridge Studio workflow for QMAP-like Routing.",
      "examples": [
        {
          "inputs": {}
        }
      ],
      "executable": true,
      "hardware_access": false,
      "input_schema": {
        "defaults": {},
        "fields": [],
        "provenance": {
          "cloud_access": false,
          "copied_upstream_source": false,
          "hardware_access": false,
          "metadata": {
            "api_layer": "quantumbridge.studio",
            "frontend_ui_implementation": false,
            "local_router": true
          },
          "official_endorsement": false,
          "production_ready": false,
          "project_id": "mqt",
          "source": "quantumbridge",
          "token_access": false,
          "workflow_id": "mqt.qmap_like_routing"
        },
        "schema_version": "quantumbridge-studio-api-v0.1",
        "unsupported_reason": null,
        "warnings": [
          "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
          "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
          "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
          "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
          "QuantumBridge Studio uses clean-room local metadata for mqt; no third-party source, UI, prose, or branding is copied.",
          "Studio workflow mqt.qmap_like_routing is local-only: no cloud, token, credential, or hardware access."
        ],
        "workflow_id": "mqt.qmap_like_routing"
      },
      "local_only": true,
      "output_schema": {
        "result_schema": "MQTQMAPLikeResult",
        "type": "object"
      },
      "production_ready": false,
      "project_id": "mqt",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "mqt",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "mqt.qmap_like_routing"
      },
      "result_schema": "MQTQMAPLikeResult",
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "QMAP-like Routing",
      "token_access": false,
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for mqt; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow mqt.qmap_like_routing is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "mqt.qmap_like_routing"
    },
    {
      "category": "qml",
      "cloud_access": false,
      "default_inputs": {},
      "description": "Local-only QuantumBridge Studio workflow for TorchQuantum-like Layer.",
      "examples": [
        {
          "inputs": {}
        }
      ],
      "executable": true,
      "hardware_access": false,
      "input_schema": {
        "defaults": {},
        "fields": [],
        "provenance": {
          "cloud_access": false,
          "copied_upstream_source": false,
          "hardware_access": false,
          "metadata": {
            "api_layer": "quantumbridge.studio",
            "frontend_ui_implementation": false,
            "local_router": true
          },
          "official_endorsement": false,
          "production_ready": false,
          "project_id": "torchquantum",
          "source": "quantumbridge",
          "token_access": false,
          "workflow_id": "torchquantum.layer_native"
        },
        "schema_version": "quantumbridge-studio-api-v0.1",
        "unsupported_reason": null,
        "warnings": [
          "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
          "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
          "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
          "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
          "QuantumBridge Studio uses clean-room local metadata for torchquantum; no third-party source, UI, prose, or branding is copied.",
          "Studio workflow torchquantum.layer_native is local-only: no cloud, token, credential, or hardware access."
        ],
        "workflow_id": "torchquantum.layer_native"
      },
      "local_only": true,
      "output_schema": {
        "result_schema": "TorchQuantumLayerResult",
        "type": "object"
      },
      "production_ready": false,
      "project_id": "torchquantum",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "torchquantum",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "torchquantum.layer_native"
      },
      "result_schema": "TorchQuantumLayerResult",
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "TorchQuantum-like Layer",
      "token_access": false,
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for torchquantum; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow torchquantum.layer_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "torchquantum.layer_native"
    },
    {
      "category": "qml",
      "cloud_access": false,
      "default_inputs": {},
      "description": "Local-only QuantumBridge Studio workflow for TorchQuantum-like Batch Forward.",
      "examples": [
        {
          "inputs": {}
        }
      ],
      "executable": true,
      "hardware_access": false,
      "input_schema": {
        "defaults": {},
        "fields": [],
        "provenance": {
          "cloud_access": false,
          "copied_upstream_source": false,
          "hardware_access": false,
          "metadata": {
            "api_layer": "quantumbridge.studio",
            "frontend_ui_implementation": false,
            "local_router": true
          },
          "official_endorsement": false,
          "production_ready": false,
          "project_id": "torchquantum",
          "source": "quantumbridge",
          "token_access": false,
          "workflow_id": "torchquantum.batch_forward_native"
        },
        "schema_version": "quantumbridge-studio-api-v0.1",
        "unsupported_reason": null,
        "warnings": [
          "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
          "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
          "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
          "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
          "QuantumBridge Studio uses clean-room local metadata for torchquantum; no third-party source, UI, prose, or branding is copied.",
          "Studio workflow torchquantum.batch_forward_native is local-only: no cloud, token, credential, or hardware access."
        ],
        "workflow_id": "torchquantum.batch_forward_native"
      },
      "local_only": true,
      "output_schema": {
        "result_schema": "TorchQuantumBatchResult",
        "type": "object"
      },
      "production_ready": false,
      "project_id": "torchquantum",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "torchquantum",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "torchquantum.batch_forward_native"
      },
      "result_schema": "TorchQuantumBatchResult",
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "TorchQuantum-like Batch Forward",
      "token_access": false,
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for torchquantum; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow torchquantum.batch_forward_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "torchquantum.batch_forward_native"
    },
    {
      "category": "qml",
      "cloud_access": false,
      "default_inputs": {},
      "description": "Local-only QuantumBridge Studio workflow for TorchQuantum-like Classifier.",
      "examples": [
        {
          "inputs": {}
        }
      ],
      "executable": true,
      "hardware_access": false,
      "input_schema": {
        "defaults": {},
        "fields": [],
        "provenance": {
          "cloud_access": false,
          "copied_upstream_source": false,
          "hardware_access": false,
          "metadata": {
            "api_layer": "quantumbridge.studio",
            "frontend_ui_implementation": false,
            "local_router": true
          },
          "official_endorsement": false,
          "production_ready": false,
          "project_id": "torchquantum",
          "source": "quantumbridge",
          "token_access": false,
          "workflow_id": "torchquantum.classifier_native"
        },
        "schema_version": "quantumbridge-studio-api-v0.1",
        "unsupported_reason": null,
        "warnings": [
          "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
          "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
          "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
          "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
          "QuantumBridge Studio uses clean-room local metadata for torchquantum; no third-party source, UI, prose, or branding is copied.",
          "Studio workflow torchquantum.classifier_native is local-only: no cloud, token, credential, or hardware access."
        ],
        "workflow_id": "torchquantum.classifier_native"
      },
      "local_only": true,
      "output_schema": {
        "result_schema": "TorchQuantumClassifierResult",
        "type": "object"
      },
      "production_ready": false,
      "project_id": "torchquantum",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "torchquantum",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "torchquantum.classifier_native"
      },
      "result_schema": "TorchQuantumClassifierResult",
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "TorchQuantum-like Classifier",
      "token_access": false,
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for torchquantum; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow torchquantum.classifier_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "torchquantum.classifier_native"
    },
    {
      "category": "backend",
      "cloud_access": false,
      "default_inputs": {},
      "description": "Local-only QuantumBridge Studio workflow for QOS-UQCI Bell Job Spec.",
      "examples": [
        {
          "inputs": {}
        }
      ],
      "executable": true,
      "hardware_access": false,
      "input_schema": {
        "defaults": {},
        "fields": [],
        "provenance": {
          "cloud_access": false,
          "copied_upstream_source": false,
          "hardware_access": false,
          "metadata": {
            "api_layer": "quantumbridge.studio",
            "frontend_ui_implementation": false,
            "local_router": true
          },
          "official_endorsement": false,
          "production_ready": false,
          "project_id": "qos-uqci",
          "source": "quantumbridge",
          "token_access": false,
          "workflow_id": "qos_uqci.bell_job_spec"
        },
        "schema_version": "quantumbridge-studio-api-v0.1",
        "unsupported_reason": null,
        "warnings": [
          "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
          "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
          "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
          "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
          "QuantumBridge Studio uses clean-room local metadata for qos-uqci; no third-party source, UI, prose, or branding is copied.",
          "Studio workflow qos_uqci.bell_job_spec is local-only: no cloud, token, credential, or hardware access."
        ],
        "workflow_id": "qos_uqci.bell_job_spec"
      },
      "local_only": true,
      "output_schema": {
        "result_schema": "QOSUQCIJobSpec",
        "type": "object"
      },
      "production_ready": false,
      "project_id": "qos-uqci",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qos-uqci",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "qos_uqci.bell_job_spec"
      },
      "result_schema": "QOSUQCIJobSpec",
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "QOS-UQCI Bell Job Spec",
      "token_access": false,
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qos-uqci; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow qos_uqci.bell_job_spec is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "qos_uqci.bell_job_spec"
    },
    {
      "category": "backend",
      "cloud_access": false,
      "default_inputs": {},
      "description": "Local-only QuantumBridge Studio workflow for QOS-UQCI Mock Runtime.",
      "examples": [
        {
          "inputs": {}
        }
      ],
      "executable": true,
      "hardware_access": false,
      "input_schema": {
        "defaults": {},
        "fields": [],
        "provenance": {
          "cloud_access": false,
          "copied_upstream_source": false,
          "hardware_access": false,
          "metadata": {
            "api_layer": "quantumbridge.studio",
            "frontend_ui_implementation": false,
            "local_router": true
          },
          "official_endorsement": false,
          "production_ready": false,
          "project_id": "qos-uqci",
          "source": "quantumbridge",
          "token_access": false,
          "workflow_id": "qos_uqci.mock_runtime"
        },
        "schema_version": "quantumbridge-studio-api-v0.1",
        "unsupported_reason": null,
        "warnings": [
          "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
          "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
          "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
          "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
          "QuantumBridge Studio uses clean-room local metadata for qos-uqci; no third-party source, UI, prose, or branding is copied.",
          "Studio workflow qos_uqci.mock_runtime is local-only: no cloud, token, credential, or hardware access."
        ],
        "workflow_id": "qos_uqci.mock_runtime"
      },
      "local_only": true,
      "output_schema": {
        "result_schema": "BackendExecutionResult",
        "type": "object"
      },
      "production_ready": false,
      "project_id": "qos-uqci",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qos-uqci",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "qos_uqci.mock_runtime"
      },
      "result_schema": "BackendExecutionResult",
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "QOS-UQCI Mock Runtime",
      "token_access": false,
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qos-uqci; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow qos_uqci.mock_runtime is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "qos_uqci.mock_runtime"
    },
    {
      "category": "backend",
      "cloud_access": false,
      "default_inputs": {},
      "description": "Local-only QuantumBridge Studio workflow for Quafu Bell Payload.",
      "examples": [
        {
          "inputs": {}
        }
      ],
      "executable": true,
      "hardware_access": false,
      "input_schema": {
        "defaults": {},
        "fields": [],
        "provenance": {
          "cloud_access": false,
          "copied_upstream_source": false,
          "hardware_access": false,
          "metadata": {
            "api_layer": "quantumbridge.studio",
            "frontend_ui_implementation": false,
            "local_router": true
          },
          "official_endorsement": false,
          "production_ready": false,
          "project_id": "quafu",
          "source": "quantumbridge",
          "token_access": false,
          "workflow_id": "quafu.bell_payload"
        },
        "schema_version": "quantumbridge-studio-api-v0.1",
        "unsupported_reason": null,
        "warnings": [
          "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
          "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
          "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
          "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
          "QuantumBridge Studio uses clean-room local metadata for quafu; no third-party source, UI, prose, or branding is copied.",
          "Studio workflow quafu.bell_payload is local-only: no cloud, token, credential, or hardware access."
        ],
        "workflow_id": "quafu.bell_payload"
      },
      "local_only": true,
      "output_schema": {
        "result_schema": "QuafuPayload",
        "type": "object"
      },
      "production_ready": false,
      "project_id": "quafu",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "quafu",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "quafu.bell_payload"
      },
      "result_schema": "QuafuPayload",
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "Quafu Bell Payload",
      "token_access": false,
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for quafu; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow quafu.bell_payload is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "quafu.bell_payload"
    },
    {
      "category": "backend",
      "cloud_access": false,
      "default_inputs": {},
      "description": "Local-only QuantumBridge Studio workflow for Quafu Mock Backend.",
      "examples": [
        {
          "inputs": {}
        }
      ],
      "executable": true,
      "hardware_access": false,
      "input_schema": {
        "defaults": {},
        "fields": [],
        "provenance": {
          "cloud_access": false,
          "copied_upstream_source": false,
          "hardware_access": false,
          "metadata": {
            "api_layer": "quantumbridge.studio",
            "frontend_ui_implementation": false,
            "local_router": true
          },
          "official_endorsement": false,
          "production_ready": false,
          "project_id": "quafu",
          "source": "quantumbridge",
          "token_access": false,
          "workflow_id": "quafu.mock_backend"
        },
        "schema_version": "quantumbridge-studio-api-v0.1",
        "unsupported_reason": null,
        "warnings": [
          "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
          "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
          "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
          "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
          "QuantumBridge Studio uses clean-room local metadata for quafu; no third-party source, UI, prose, or branding is copied.",
          "Studio workflow quafu.mock_backend is local-only: no cloud, token, credential, or hardware access."
        ],
        "workflow_id": "quafu.mock_backend"
      },
      "local_only": true,
      "output_schema": {
        "result_schema": "BackendExecutionResult",
        "type": "object"
      },
      "production_ready": false,
      "project_id": "quafu",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "quafu",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "quafu.mock_backend"
      },
      "result_schema": "BackendExecutionResult",
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "Quafu Mock Backend",
      "token_access": false,
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for quafu; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow quafu.mock_backend is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "quafu.mock_backend"
    },
    {
      "category": "benchmark",
      "cloud_access": false,
      "default_inputs": {},
      "description": "Local-only QuantumBridge Studio workflow for Benchpress Basic Suite.",
      "examples": [
        {
          "inputs": {}
        }
      ],
      "executable": true,
      "hardware_access": false,
      "input_schema": {
        "defaults": {},
        "fields": [],
        "provenance": {
          "cloud_access": false,
          "copied_upstream_source": false,
          "hardware_access": false,
          "metadata": {
            "api_layer": "quantumbridge.studio",
            "frontend_ui_implementation": false,
            "local_router": true
          },
          "official_endorsement": false,
          "production_ready": false,
          "project_id": "benchpress",
          "source": "quantumbridge",
          "token_access": false,
          "workflow_id": "benchpress.basic_suite"
        },
        "schema_version": "quantumbridge-studio-api-v0.1",
        "unsupported_reason": null,
        "warnings": [
          "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
          "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
          "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
          "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
          "QuantumBridge Studio uses clean-room local metadata for benchpress; no third-party source, UI, prose, or branding is copied.",
          "Studio workflow benchpress.basic_suite is local-only: no cloud, token, credential, or hardware access."
        ],
        "workflow_id": "benchpress.basic_suite"
      },
      "local_only": true,
      "output_schema": {
        "result_schema": "BenchmarkSuiteResult",
        "type": "object"
      },
      "production_ready": false,
      "project_id": "benchpress",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "benchpress",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "benchpress.basic_suite"
      },
      "result_schema": "BenchmarkSuiteResult",
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "Benchpress Basic Suite",
      "token_access": false,
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for benchpress; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow benchpress.basic_suite is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "benchpress.basic_suite"
    },
    {
      "category": "benchmark",
      "cloud_access": false,
      "default_inputs": {},
      "description": "Local-only QuantumBridge Studio workflow for Benchpress Algorithms Suite.",
      "examples": [
        {
          "inputs": {}
        }
      ],
      "executable": true,
      "hardware_access": false,
      "input_schema": {
        "defaults": {},
        "fields": [],
        "provenance": {
          "cloud_access": false,
          "copied_upstream_source": false,
          "hardware_access": false,
          "metadata": {
            "api_layer": "quantumbridge.studio",
            "frontend_ui_implementation": false,
            "local_router": true
          },
          "official_endorsement": false,
          "production_ready": false,
          "project_id": "benchpress",
          "source": "quantumbridge",
          "token_access": false,
          "workflow_id": "benchpress.algorithms_suite"
        },
        "schema_version": "quantumbridge-studio-api-v0.1",
        "unsupported_reason": null,
        "warnings": [
          "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
          "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
          "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
          "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
          "QuantumBridge Studio uses clean-room local metadata for benchpress; no third-party source, UI, prose, or branding is copied.",
          "Studio workflow benchpress.algorithms_suite is local-only: no cloud, token, credential, or hardware access."
        ],
        "workflow_id": "benchpress.algorithms_suite"
      },
      "local_only": true,
      "output_schema": {
        "result_schema": "BenchmarkSuiteResult",
        "type": "object"
      },
      "production_ready": false,
      "project_id": "benchpress",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "benchpress",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "benchpress.algorithms_suite"
      },
      "result_schema": "BenchmarkSuiteResult",
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "Benchpress Algorithms Suite",
      "token_access": false,
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for benchpress; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow benchpress.algorithms_suite is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "benchpress.algorithms_suite"
    },
    {
      "category": "benchmark",
      "cloud_access": false,
      "default_inputs": {},
      "description": "Local-only QuantumBridge Studio workflow for Benchpress Backend Suite.",
      "examples": [
        {
          "inputs": {}
        }
      ],
      "executable": true,
      "hardware_access": false,
      "input_schema": {
        "defaults": {},
        "fields": [],
        "provenance": {
          "cloud_access": false,
          "copied_upstream_source": false,
          "hardware_access": false,
          "metadata": {
            "api_layer": "quantumbridge.studio",
            "frontend_ui_implementation": false,
            "local_router": true
          },
          "official_endorsement": false,
          "production_ready": false,
          "project_id": "benchpress",
          "source": "quantumbridge",
          "token_access": false,
          "workflow_id": "benchpress.backend_suite"
        },
        "schema_version": "quantumbridge-studio-api-v0.1",
        "unsupported_reason": null,
        "warnings": [
          "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
          "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
          "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
          "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
          "QuantumBridge Studio uses clean-room local metadata for benchpress; no third-party source, UI, prose, or branding is copied.",
          "Studio workflow benchpress.backend_suite is local-only: no cloud, token, credential, or hardware access."
        ],
        "workflow_id": "benchpress.backend_suite"
      },
      "local_only": true,
      "output_schema": {
        "result_schema": "BenchmarkSuiteResult",
        "type": "object"
      },
      "production_ready": false,
      "project_id": "benchpress",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "benchpress",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "benchpress.backend_suite"
      },
      "result_schema": "BenchmarkSuiteResult",
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "Benchpress Backend Suite",
      "token_access": false,
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for benchpress; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow benchpress.backend_suite is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "benchpress.backend_suite"
    },
    {
      "category": "benchmark",
      "cloud_access": false,
      "default_inputs": {},
      "description": "Local-only QuantumBridge Studio workflow for Benchpress Full Smoke Suite.",
      "examples": [
        {
          "inputs": {}
        }
      ],
      "executable": true,
      "hardware_access": false,
      "input_schema": {
        "defaults": {},
        "fields": [],
        "provenance": {
          "cloud_access": false,
          "copied_upstream_source": false,
          "hardware_access": false,
          "metadata": {
            "api_layer": "quantumbridge.studio",
            "frontend_ui_implementation": false,
            "local_router": true
          },
          "official_endorsement": false,
          "production_ready": false,
          "project_id": "benchpress",
          "source": "quantumbridge",
          "token_access": false,
          "workflow_id": "benchpress.full_smoke_suite"
        },
        "schema_version": "quantumbridge-studio-api-v0.1",
        "unsupported_reason": null,
        "warnings": [
          "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
          "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
          "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
          "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
          "QuantumBridge Studio uses clean-room local metadata for benchpress; no third-party source, UI, prose, or branding is copied.",
          "Studio workflow benchpress.full_smoke_suite is local-only: no cloud, token, credential, or hardware access."
        ],
        "workflow_id": "benchpress.full_smoke_suite"
      },
      "local_only": true,
      "output_schema": {
        "result_schema": "BenchmarkSuiteResult",
        "type": "object"
      },
      "production_ready": false,
      "project_id": "benchpress",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "benchpress",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "benchpress.full_smoke_suite"
      },
      "result_schema": "BenchmarkSuiteResult",
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "Benchpress Full Smoke Suite",
      "token_access": false,
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for benchpress; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow benchpress.full_smoke_suite is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "benchpress.full_smoke_suite"
    }
  ],
  "notices": [
    "QuantumBridge Studio is an independent local prototype.",
    "No official endorsement is claimed.",
    "Local-only: no cloud execution, credential reading, or hardware access.",
    "Third-party package names are used only for compatibility identification.",
    "This prototype is not production-ready."
  ],
  "workflows": [
    {
      "category": "finance",
      "cloud_access": false,
      "executable": true,
      "hardware_access": false,
      "local_only": true,
      "production_ready": false,
      "project_id": "qiskit-finance",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qiskit-finance",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "finance.portfolio_optimization_native"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "Portfolio Optimization",
      "token_access": false,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-finance; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow finance.portfolio_optimization_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "finance.portfolio_optimization_native"
    },
    {
      "category": "optimization",
      "cloud_access": false,
      "executable": true,
      "hardware_access": false,
      "local_only": true,
      "production_ready": false,
      "project_id": "qiskit-optimization",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qiskit-optimization",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "optimization.quadratic_program_native"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "Quadratic Program",
      "token_access": false,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-optimization; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow optimization.quadratic_program_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "optimization.quadratic_program_native"
    },
    {
      "category": "algorithms",
      "cloud_access": false,
      "executable": true,
      "hardware_access": false,
      "local_only": true,
      "production_ready": false,
      "project_id": "qiskit-algorithms",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qiskit-algorithms",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "algorithms.vqe_native"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "VQE Native",
      "token_access": false,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-algorithms; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow algorithms.vqe_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "algorithms.vqe_native"
    },
    {
      "category": "algorithms",
      "cloud_access": false,
      "executable": true,
      "hardware_access": false,
      "local_only": true,
      "production_ready": false,
      "project_id": "qiskit-algorithms",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qiskit-algorithms",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "algorithms.qaoa_native"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "QAOA MaxCut Native",
      "token_access": false,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-algorithms; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow algorithms.qaoa_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "algorithms.qaoa_native"
    },
    {
      "category": "algorithms",
      "cloud_access": false,
      "executable": true,
      "hardware_access": false,
      "local_only": true,
      "production_ready": false,
      "project_id": "qiskit-algorithms",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qiskit-algorithms",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "algorithms.grover_native"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "Grover Native",
      "token_access": false,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-algorithms; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow algorithms.grover_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "algorithms.grover_native"
    },
    {
      "category": "chemistry",
      "cloud_access": false,
      "executable": true,
      "hardware_access": false,
      "local_only": true,
      "production_ready": false,
      "project_id": "qiskit-nature",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qiskit-nature",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "nature.h2_native"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "H2 Chemistry Native",
      "token_access": false,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-nature; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow nature.h2_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "nature.h2_native"
    },
    {
      "category": "chemistry",
      "cloud_access": false,
      "executable": true,
      "hardware_access": false,
      "local_only": true,
      "production_ready": false,
      "project_id": "qiskit-nature",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qiskit-nature",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "nature.lih_native"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "LiH Chemistry Native",
      "token_access": false,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-nature; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow nature.lih_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "nature.lih_native"
    },
    {
      "category": "machine-learning",
      "cloud_access": false,
      "executable": true,
      "hardware_access": false,
      "local_only": true,
      "production_ready": false,
      "project_id": "qiskit-machine-learning",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qiskit-machine-learning",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "ml.quantum_kernel_native"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "Quantum Kernel Native",
      "token_access": false,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-machine-learning; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow ml.quantum_kernel_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "ml.quantum_kernel_native"
    },
    {
      "category": "machine-learning",
      "cloud_access": false,
      "executable": true,
      "hardware_access": false,
      "local_only": true,
      "production_ready": false,
      "project_id": "qiskit-machine-learning",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qiskit-machine-learning",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "ml.kernel_classifier_native"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "Kernel Classifier Native",
      "token_access": false,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-machine-learning; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow ml.kernel_classifier_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "ml.kernel_classifier_native"
    },
    {
      "category": "machine-learning",
      "cloud_access": false,
      "executable": true,
      "hardware_access": false,
      "local_only": true,
      "production_ready": false,
      "project_id": "qiskit-machine-learning",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qiskit-machine-learning",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "ml.qnn_classifier_native"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "QNN Classifier Native",
      "token_access": false,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-machine-learning; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow ml.qnn_classifier_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "ml.qnn_classifier_native"
    },
    {
      "category": "simulator",
      "cloud_access": false,
      "executable": true,
      "hardware_access": false,
      "local_only": true,
      "production_ready": false,
      "project_id": "qiskit-aer",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qiskit-aer",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "aer.statevector_native"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "Statevector Simulator Native",
      "token_access": false,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-aer; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow aer.statevector_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "aer.statevector_native"
    },
    {
      "category": "simulator",
      "cloud_access": false,
      "executable": true,
      "hardware_access": false,
      "local_only": true,
      "production_ready": false,
      "project_id": "qiskit-aer",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qiskit-aer",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "aer.qasm_counts_native"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "QASM Counts Native",
      "token_access": false,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-aer; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow aer.qasm_counts_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "aer.qasm_counts_native"
    },
    {
      "category": "simulator",
      "cloud_access": false,
      "executable": true,
      "hardware_access": false,
      "local_only": true,
      "production_ready": false,
      "project_id": "qiskit-aer",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qiskit-aer",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "aer.noisy_counts_native"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "Noisy Counts Native",
      "token_access": false,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-aer; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow aer.noisy_counts_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "aer.noisy_counts_native"
    },
    {
      "category": "mitigation",
      "cloud_access": false,
      "executable": true,
      "hardware_access": false,
      "local_only": true,
      "production_ready": false,
      "project_id": "mitiq",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "mitiq",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "mitiq.zne_native"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "ZNE Native",
      "token_access": false,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for mitiq; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow mitiq.zne_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "mitiq.zne_native"
    },
    {
      "category": "mitigation",
      "cloud_access": false,
      "executable": true,
      "hardware_access": false,
      "local_only": true,
      "production_ready": false,
      "project_id": "mitiq",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "mitiq",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "mitiq.readout_mitigation_native"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "Readout Mitigation Native",
      "token_access": false,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for mitiq; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow mitiq.readout_mitigation_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "mitiq.readout_mitigation_native"
    },
    {
      "category": "bridge",
      "cloud_access": false,
      "executable": true,
      "hardware_access": false,
      "local_only": true,
      "production_ready": false,
      "project_id": "pennylane-qiskit",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "pennylane-qiskit",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "pennylane_qiskit.qiskit_to_pennylane"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "Qiskit to PennyLane Bridge",
      "token_access": false,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for pennylane-qiskit; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow pennylane_qiskit.qiskit_to_pennylane is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "pennylane_qiskit.qiskit_to_pennylane"
    },
    {
      "category": "bridge",
      "cloud_access": false,
      "executable": true,
      "hardware_access": false,
      "local_only": true,
      "production_ready": false,
      "project_id": "pennylane-qiskit",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "pennylane-qiskit",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "pennylane_qiskit.pennylane_to_qiskit"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "PennyLane to Qiskit Bridge",
      "token_access": false,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for pennylane-qiskit; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow pennylane_qiskit.pennylane_to_qiskit is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "pennylane_qiskit.pennylane_to_qiskit"
    },
    {
      "category": "experiments",
      "cloud_access": false,
      "executable": true,
      "hardware_access": false,
      "local_only": true,
      "production_ready": false,
      "project_id": "qiskit-experiments",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qiskit-experiments",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "experiments.rabi_native"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "Rabi Experiment Native",
      "token_access": false,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-experiments; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow experiments.rabi_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "experiments.rabi_native"
    },
    {
      "category": "experiments",
      "cloud_access": false,
      "executable": true,
      "hardware_access": false,
      "local_only": true,
      "production_ready": false,
      "project_id": "qiskit-experiments",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qiskit-experiments",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "experiments.t1_native"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "T1 Experiment Native",
      "token_access": false,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-experiments; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow experiments.t1_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "experiments.t1_native"
    },
    {
      "category": "experiments",
      "cloud_access": false,
      "executable": true,
      "hardware_access": false,
      "local_only": true,
      "production_ready": false,
      "project_id": "qiskit-experiments",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qiskit-experiments",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "experiments.ramsey_native"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "Ramsey Experiment Native",
      "token_access": false,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-experiments; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow experiments.ramsey_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "experiments.ramsey_native"
    },
    {
      "category": "dynamics",
      "cloud_access": false,
      "executable": true,
      "hardware_access": false,
      "local_only": true,
      "production_ready": false,
      "project_id": "qiskit-dynamics",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qiskit-dynamics",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "dynamics.z_precession_native"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "Z Precession Dynamics Native",
      "token_access": false,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-dynamics; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow dynamics.z_precession_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "dynamics.z_precession_native"
    },
    {
      "category": "dynamics",
      "cloud_access": false,
      "executable": true,
      "hardware_access": false,
      "local_only": true,
      "production_ready": false,
      "project_id": "qiskit-dynamics",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qiskit-dynamics",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "dynamics.rabi_drive_native"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "Rabi Drive Dynamics Native",
      "token_access": false,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-dynamics; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow dynamics.rabi_drive_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "dynamics.rabi_drive_native"
    },
    {
      "category": "compiler",
      "cloud_access": false,
      "executable": true,
      "hardware_access": false,
      "local_only": true,
      "production_ready": false,
      "project_id": "mqt",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "mqt",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "mqt.core_like_circuit"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "MQT Core-like Circuit",
      "token_access": false,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for mqt; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow mqt.core_like_circuit is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "mqt.core_like_circuit"
    },
    {
      "category": "simulator",
      "cloud_access": false,
      "executable": true,
      "hardware_access": false,
      "local_only": true,
      "production_ready": false,
      "project_id": "mqt",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "mqt",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "mqt.ddsim_like_simulation"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "DDSIM-like Simulation",
      "token_access": false,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for mqt; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow mqt.ddsim_like_simulation is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "mqt.ddsim_like_simulation"
    },
    {
      "category": "routing",
      "cloud_access": false,
      "executable": true,
      "hardware_access": false,
      "local_only": true,
      "production_ready": false,
      "project_id": "mqt",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "mqt",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "mqt.qmap_like_routing"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "QMAP-like Routing",
      "token_access": false,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for mqt; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow mqt.qmap_like_routing is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "mqt.qmap_like_routing"
    },
    {
      "category": "qml",
      "cloud_access": false,
      "executable": true,
      "hardware_access": false,
      "local_only": true,
      "production_ready": false,
      "project_id": "torchquantum",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "torchquantum",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "torchquantum.layer_native"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "TorchQuantum-like Layer",
      "token_access": false,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for torchquantum; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow torchquantum.layer_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "torchquantum.layer_native"
    },
    {
      "category": "qml",
      "cloud_access": false,
      "executable": true,
      "hardware_access": false,
      "local_only": true,
      "production_ready": false,
      "project_id": "torchquantum",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "torchquantum",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "torchquantum.batch_forward_native"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "TorchQuantum-like Batch Forward",
      "token_access": false,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for torchquantum; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow torchquantum.batch_forward_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "torchquantum.batch_forward_native"
    },
    {
      "category": "qml",
      "cloud_access": false,
      "executable": true,
      "hardware_access": false,
      "local_only": true,
      "production_ready": false,
      "project_id": "torchquantum",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "torchquantum",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "torchquantum.classifier_native"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "TorchQuantum-like Classifier",
      "token_access": false,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for torchquantum; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow torchquantum.classifier_native is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "torchquantum.classifier_native"
    },
    {
      "category": "backend",
      "cloud_access": false,
      "executable": true,
      "hardware_access": false,
      "local_only": true,
      "production_ready": false,
      "project_id": "qos-uqci",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qos-uqci",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "qos_uqci.bell_job_spec"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "QOS-UQCI Bell Job Spec",
      "token_access": false,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qos-uqci; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow qos_uqci.bell_job_spec is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "qos_uqci.bell_job_spec"
    },
    {
      "category": "backend",
      "cloud_access": false,
      "executable": true,
      "hardware_access": false,
      "local_only": true,
      "production_ready": false,
      "project_id": "qos-uqci",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qos-uqci",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "qos_uqci.mock_runtime"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "QOS-UQCI Mock Runtime",
      "token_access": false,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qos-uqci; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow qos_uqci.mock_runtime is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "qos_uqci.mock_runtime"
    },
    {
      "category": "backend",
      "cloud_access": false,
      "executable": true,
      "hardware_access": false,
      "local_only": true,
      "production_ready": false,
      "project_id": "quafu",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "quafu",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "quafu.bell_payload"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "Quafu Bell Payload",
      "token_access": false,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for quafu; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow quafu.bell_payload is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "quafu.bell_payload"
    },
    {
      "category": "backend",
      "cloud_access": false,
      "executable": true,
      "hardware_access": false,
      "local_only": true,
      "production_ready": false,
      "project_id": "quafu",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "quafu",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "quafu.mock_backend"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "Quafu Mock Backend",
      "token_access": false,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for quafu; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow quafu.mock_backend is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "quafu.mock_backend"
    },
    {
      "category": "benchmark",
      "cloud_access": false,
      "executable": true,
      "hardware_access": false,
      "local_only": true,
      "production_ready": false,
      "project_id": "benchpress",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "benchpress",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "benchpress.basic_suite"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "Benchpress Basic Suite",
      "token_access": false,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for benchpress; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow benchpress.basic_suite is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "benchpress.basic_suite"
    },
    {
      "category": "benchmark",
      "cloud_access": false,
      "executable": true,
      "hardware_access": false,
      "local_only": true,
      "production_ready": false,
      "project_id": "benchpress",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "benchpress",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "benchpress.algorithms_suite"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "Benchpress Algorithms Suite",
      "token_access": false,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for benchpress; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow benchpress.algorithms_suite is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "benchpress.algorithms_suite"
    },
    {
      "category": "benchmark",
      "cloud_access": false,
      "executable": true,
      "hardware_access": false,
      "local_only": true,
      "production_ready": false,
      "project_id": "benchpress",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "benchpress",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "benchpress.backend_suite"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "Benchpress Backend Suite",
      "token_access": false,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for benchpress; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow benchpress.backend_suite is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "benchpress.backend_suite"
    },
    {
      "category": "benchmark",
      "cloud_access": false,
      "executable": true,
      "hardware_access": false,
      "local_only": true,
      "production_ready": false,
      "project_id": "benchpress",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "benchpress",
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "benchpress.full_smoke_suite"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "studio_ready": "true",
      "title": "Benchpress Full Smoke Suite",
      "token_access": false,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for benchpress; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow benchpress.full_smoke_suite is local-only: no cloud, token, credential, or hardware access."
      ],
      "workflow_id": "benchpress.full_smoke_suite"
    }
  ]
};

export const sampleResults = {
  "exports": {
    "json": {
      "content": "{\n  \"error\": null,\n  \"execution_id\": \"studio-exec-000001\",\n  \"provenance\": {\n    \"cloud_access\": false,\n    \"copied_upstream_source\": false,\n    \"hardware_access\": false,\n    \"metadata\": {\n      \"api_layer\": \"quantumbridge.studio\",\n      \"frontend_ui_implementation\": false,\n      \"local_router\": true\n    },\n    \"official_endorsement\": false,\n    \"production_ready\": false,\n    \"project_id\": \"qiskit-aer\",\n    \"result_provenance\": {\n      \"adapter\": \"quantumbridge.compat.qiskit_aer\",\n      \"cloud_access\": false,\n      \"hardware_access\": false,\n      \"ibm_branding_copied\": false,\n      \"official_endorsement\": false,\n      \"source_code_copied\": false,\n      \"stage\": \"9F\",\n      \"token_read\": false,\n      \"upstream_source_copied\": false,\n      \"workflow\": \"qasm_simulator_native\"\n    },\n    \"source\": \"quantumbridge\",\n    \"token_access\": false,\n    \"workflow_id\": \"aer.qasm_counts_native\"\n  },\n  \"result\": {\n    \"backend\": \"qasm\",\n    \"capability_level\": 3,\n    \"counts\": {\n      \"00\": 32,\n      \"11\": 32\n    },\n    \"data\": null,\n    \"ecosystem\": \"quantumbridge_native_simulator\",\n    \"final_statevector\": [],\n    \"metadata\": {\n      \"backend\": \"qasm\",\n      \"cloud_access\": false,\n      \"hardware_access\": false,\n      \"measurement_count\": 2,\n      \"operation_count\": 2,\n      \"production_simulator\": false,\n      \"qiskit_aer_parity_claim\": false,\n      \"supported_gates\": [\n        \"cx\",\n        \"cz\",\n        \"h\",\n        \"phase\",\n        \"rx\",\n        \"ry\",\n        \"rz\",\n        \"swap\",\n        \"x\",\n        \"y\",\n        \"z\"\n      ],\n      \"token_read\": false\n    },\n    \"mode\": \"native_minimal\",\n    \"native_implementation\": true,\n    \"noise_model\": null,\n    \"num_qubits\": 2,\n    \"probabilities\": {\n      \"00\": 0.5,\n      \"11\": 0.5\n    },\n    \"production_ready\": false,\n    \"provenance\": {\n      \"adapter\": \"quantumbridge.compat.qiskit_aer\",\n      \"cloud_access\": false,\n      \"hardware_access\": false,\n      \"ibm_branding_copied\": false,\n      \"official_endorsement\": false,\n      \"source_code_copied\": false,\n      \"stage\": \"9F\",\n      \"token_read\": false,\n      \"upstream_source_copied\": false,\n      \"workflow\": \"qasm_simulator_native\"\n    },\n    \"quantumbridge_version\": null,\n    \"raw_type\": \"QuantumBridgeQasmCounts\",\n    \"schema_version\": \"0.1\",\n    \"seed\": 5,\n    \"shots\": 64,\n    \"unsupported_reason\": null,\n    \"upstream_package\": null,\n    \"upstream_version\": null,\n    \"warnings\": [\n      \"QuantumBridge Qiskit Aer support is an optional passthrough/schema bridge plus minimal educational native simulator workflows. It is not a full Qiskit Aer replacement and is not production simulator software.\",\n      \"Native simulator support is a minimal deterministic educational simulator for small circuits.\"\n    ],\n    \"workflow\": \"qasm_simulator_native\"\n  },\n  \"schema_version\": \"quantumbridge-studio-api-v0.1\",\n  \"status\": \"succeeded\",\n  \"unsupported_reason\": null,\n  \"warnings\": [\n    \"QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.\",\n    \"Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.\",\n    \"This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.\",\n    \"This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.\",\n    \"QuantumBridge Studio uses clean-room local metadata for qiskit-aer; no third-party source, UI, prose, or branding is copied.\",\n    \"Studio workflow aer.qasm_counts_native is local-only: no cloud, token, credential, or hardware access.\",\n    \"QuantumBridge Qiskit Aer support is an optional passthrough/schema bridge plus minimal educational native simulator workflows. It is not a full Qiskit Aer replacement and is not production simulator software.\",\n    \"Native simulator support is a minimal deterministic educational simulator for small circuits.\"\n  ],\n  \"workflow_id\": \"aer.qasm_counts_native\"\n}",
      "execution_id": null,
      "export_type": "json",
      "provenance": {},
      "schema_version": "quantumbridge-studio-api-v0.1",
      "unsupported_reason": null,
      "warnings": [],
      "workflow_id": null
    },
    "markdown": {
      "content": "# QuantumBridge Studio Result\\n\\n- execution_id: `studio-exec-000001`\\n- workflow_id: `aer.qasm_counts_native`\\n\\n```json\\n{\n  \"error\": null,\n  \"execution_id\": \"studio-exec-000001\",\n  \"provenance\": {\n    \"cloud_access\": false,\n    \"copied_upstream_source\": false,\n    \"hardware_access\": false,\n    \"metadata\": {\n      \"api_layer\": \"quantumbridge.studio\",\n      \"frontend_ui_implementation\": false,\n      \"local_router\": true\n    },\n    \"official_endorsement\": false,\n    \"production_ready\": false,\n    \"project_id\": \"qiskit-aer\",\n    \"result_provenance\": {\n      \"adapter\": \"quantumbridge.compat.qiskit_aer\",\n      \"cloud_access\": false,\n      \"hardware_access\": false,\n      \"ibm_branding_copied\": false,\n      \"official_endorsement\": false,\n      \"source_code_copied\": false,\n      \"stage\": \"9F\",\n      \"token_read\": false,\n      \"upstream_source_copied\": false,\n      \"workflow\": \"qasm_simulator_native\"\n    },\n    \"source\": \"quantumbridge\",\n    \"token_access\": false,\n    \"workflow_id\": \"aer.qasm_counts_native\"\n  },\n  \"result\": {\n    \"backend\": \"qasm\",\n    \"capability_level\": 3,\n    \"counts\": {\n      \"00\": 32,\n      \"11\": 32\n    },\n    \"data\": null,\n    \"ecosystem\": \"quantumbridge_native_simulator\",\n    \"final_statevector\": [],\n    \"metadata\": {\n      \"backend\": \"qasm\",\n      \"cloud_access\": false,\n      \"hardware_access\": false,\n      \"measurement_count\": 2,\n      \"operation_count\": 2,\n      \"production_simulator\": false,\n      \"qiskit_aer_parity_claim\": false,\n      \"supported_gates\": [\n        \"cx\",\n        \"cz\",\n        \"h\",\n        \"phase\",\n        \"rx\",\n        \"ry\",\n        \"rz\",\n        \"swap\",\n        \"x\",\n        \"y\",\n        \"z\"\n      ],\n      \"token_read\": false\n    },\n    \"mode\": \"native_minimal\",\n    \"native_implementation\": true,\n    \"noise_model\": null,\n    \"num_qubits\": 2,\n    \"probabilities\": {\n      \"00\": 0.5,\n      \"11\": 0.5\n    },\n    \"production_ready\": false,\n    \"provenance\": {\n      \"adapter\": \"quantumbridge.compat.qiskit_aer\",\n      \"cloud_access\": false,\n      \"hardware_access\": false,\n      \"ibm_branding_copied\": false,\n      \"official_endorsement\": false,\n      \"source_code_copied\": false,\n      \"stage\": \"9F\",\n      \"token_read\": false,\n      \"upstream_source_copied\": false,\n      \"workflow\": \"qasm_simulator_native\"\n    },\n    \"quantumbridge_version\": null,\n    \"raw_type\": \"QuantumBridgeQasmCounts\",\n    \"schema_version\": \"0.1\",\n    \"seed\": 5,\n    \"shots\": 64,\n    \"unsupported_reason\": null,\n    \"upstream_package\": null,\n    \"upstream_version\": null,\n    \"warnings\": [\n      \"QuantumBridge Qiskit Aer support is an optional passthrough/schema bridge plus minimal educational native simulator workflows. It is not a full Qiskit Aer replacement and is not production simulator software.\",\n      \"Native simulator support is a minimal deterministic educational simulator for small circuits.\"\n    ],\n    \"workflow\": \"qasm_simulator_native\"\n  },\n  \"schema_version\": \"quantumbridge-studio-api-v0.1\",\n  \"status\": \"succeeded\",\n  \"unsupported_reason\": null,\n  \"warnings\": [\n    \"QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.\",\n    \"Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.\",\n    \"This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.\",\n    \"This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.\",\n    \"QuantumBridge Studio uses clean-room local metadata for qiskit-aer; no third-party source, UI, prose, or branding is copied.\",\n    \"Studio workflow aer.qasm_counts_native is local-only: no cloud, token, credential, or hardware access.\",\n    \"QuantumBridge Qiskit Aer support is an optional passthrough/schema bridge plus minimal educational native simulator workflows. It is not a full Qiskit Aer replacement and is not production simulator software.\",\n    \"Native simulator support is a minimal deterministic educational simulator for small circuits.\"\n  ],\n  \"workflow_id\": \"aer.qasm_counts_native\"\n}\\n```\\n",
      "execution_id": "studio-exec-000001",
      "export_type": "markdown",
      "provenance": {},
      "schema_version": "quantumbridge-studio-api-v0.1",
      "unsupported_reason": null,
      "warnings": [],
      "workflow_id": "aer.qasm_counts_native"
    },
    "notebook_stub": {
      "content": "{\n  \"metadata\": {\n    \"quantumbridge\": \"studio-notebook-stub-v0.1\"\n  },\n  \"cells\": [\n    {\n      \"cell_type\": \"markdown\",\n      \"source\": [\n        \"# QuantumBridge Studio workflow: aer.qasm_counts_native\\\\n\"\n      ]\n    },\n    {\n      \"cell_type\": \"code\",\n      \"source\": [\n        \"from quantumbridge.studio.execution_service import execute_workflow\\\\n\\\\nresult = execute_workflow('aer.qasm_counts_native', inputs={'shots': 64, 'seed': 5})\\\\nprint(result.to_json())\\\\n\"\n      ],\n      \"outputs\": []\n    }\n  ],\n  \"nbformat\": 4,\n  \"nbformat_minor\": 5\n}",
      "execution_id": null,
      "export_type": "notebook_stub",
      "provenance": {},
      "schema_version": "quantumbridge-studio-api-v0.1",
      "unsupported_reason": null,
      "warnings": [],
      "workflow_id": "aer.qasm_counts_native"
    },
    "python": {
      "content": "from quantumbridge.studio.execution_service import execute_workflow\\n\\nresult = execute_workflow('aer.qasm_counts_native', inputs={'shots': 64, 'seed': 5})\\nprint(result.to_json())\\n",
      "execution_id": null,
      "export_type": "python",
      "provenance": {},
      "schema_version": "quantumbridge-studio-api-v0.1",
      "unsupported_reason": null,
      "warnings": [],
      "workflow_id": "aer.qasm_counts_native"
    }
  },
  "notices": [
    "QuantumBridge Studio is an independent local prototype.",
    "No official endorsement is claimed.",
    "Local-only: no cloud execution, credential reading, or hardware access.",
    "Third-party package names are used only for compatibility identification.",
    "This prototype is not production-ready."
  ],
  "results": [
    {
      "error": null,
      "execution_id": "studio-exec-000001",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qiskit-aer",
        "result_provenance": {
          "adapter": "quantumbridge.compat.qiskit_aer",
          "cloud_access": false,
          "hardware_access": false,
          "ibm_branding_copied": false,
          "official_endorsement": false,
          "source_code_copied": false,
          "stage": "9F",
          "token_read": false,
          "upstream_source_copied": false,
          "workflow": "qasm_simulator_native"
        },
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "aer.qasm_counts_native"
      },
      "result": {
        "backend": "qasm",
        "capability_level": 3,
        "counts": {
          "00": 32,
          "11": 32
        },
        "data": null,
        "ecosystem": "quantumbridge_native_simulator",
        "final_statevector": [],
        "metadata": {
          "backend": "qasm",
          "cloud_access": false,
          "hardware_access": false,
          "measurement_count": 2,
          "operation_count": 2,
          "production_simulator": false,
          "qiskit_aer_parity_claim": false,
          "supported_gates": [
            "cx",
            "cz",
            "h",
            "phase",
            "rx",
            "ry",
            "rz",
            "swap",
            "x",
            "y",
            "z"
          ],
          "token_read": false
        },
        "mode": "native_minimal",
        "native_implementation": true,
        "noise_model": null,
        "num_qubits": 2,
        "probabilities": {
          "00": 0.5,
          "11": 0.5
        },
        "production_ready": false,
        "provenance": {
          "adapter": "quantumbridge.compat.qiskit_aer",
          "cloud_access": false,
          "hardware_access": false,
          "ibm_branding_copied": false,
          "official_endorsement": false,
          "source_code_copied": false,
          "stage": "9F",
          "token_read": false,
          "upstream_source_copied": false,
          "workflow": "qasm_simulator_native"
        },
        "quantumbridge_version": null,
        "raw_type": "QuantumBridgeQasmCounts",
        "schema_version": "0.1",
        "seed": 5,
        "shots": 64,
        "unsupported_reason": null,
        "upstream_package": null,
        "upstream_version": null,
        "warnings": [
          "QuantumBridge Qiskit Aer support is an optional passthrough/schema bridge plus minimal educational native simulator workflows. It is not a full Qiskit Aer replacement and is not production simulator software.",
          "Native simulator support is a minimal deterministic educational simulator for small circuits."
        ],
        "workflow": "qasm_simulator_native"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "status": "succeeded",
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-aer; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow aer.qasm_counts_native is local-only: no cloud, token, credential, or hardware access.",
        "QuantumBridge Qiskit Aer support is an optional passthrough/schema bridge plus minimal educational native simulator workflows. It is not a full Qiskit Aer replacement and is not production simulator software.",
        "Native simulator support is a minimal deterministic educational simulator for small circuits."
      ],
      "workflow_id": "aer.qasm_counts_native"
    },
    {
      "error": null,
      "execution_id": "studio-exec-000002",
      "provenance": {
        "cloud_access": false,
        "copied_upstream_source": false,
        "hardware_access": false,
        "metadata": {
          "api_layer": "quantumbridge.studio",
          "frontend_ui_implementation": false,
          "local_router": true
        },
        "official_endorsement": false,
        "production_ready": false,
        "project_id": "qiskit-finance",
        "result_provenance": {
          "adapter_package": "qiskit-finance",
          "copied_upstream_source": false,
          "native_subset": "binary mean-variance exact enumeration",
          "official_endorsement": false
        },
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "finance.portfolio_optimization_native"
      },
      "result": {
        "budget": 2,
        "covariances": [
          [
            0.001,
            0.0002,
            0.0001,
            0.0001
          ],
          [
            0.0002,
            0.0015,
            0.0002,
            0.0001
          ],
          [
            0.0001,
            0.0002,
            0.0011,
            0.0003
          ],
          [
            0.0001,
            0.0001,
            0.0003,
            0.0012
          ]
        ],
        "expected_returns": [
          0.014,
          0.0008,
          0.0001,
          0.015
        ],
        "metadata": {
          "constraint": "sum(selection) == budget",
          "example": "tutorial-synthetic-four-asset",
          "input_source": "deterministic synthetic data unless explicitly provided",
          "objective": "minimize risk_factor * x^T Sigma x - expected_returns^T x"
        },
        "method": "exact-enumeration",
        "objective_value": -0.0278,
        "path": "quantumbridge-native",
        "probabilities": {
          "1001": 1.0
        },
        "provenance": {
          "adapter_package": "qiskit-finance",
          "copied_upstream_source": false,
          "native_subset": "binary mean-variance exact enumeration",
          "official_endorsement": false
        },
        "risk_factor": 0.5,
        "samples": [
          {
            "bitstring": "1001",
            "feasible": true,
            "objective_value": -0.0278,
            "selection": [
              1,
              0,
              0,
              1
            ]
          },
          {
            "bitstring": "0101",
            "feasible": true,
            "objective_value": -0.014349999999999998,
            "selection": [
              0,
              1,
              0,
              1
            ]
          },
          {
            "bitstring": "0011",
            "feasible": true,
            "objective_value": -0.013649999999999999,
            "selection": [
              0,
              0,
              1,
              1
            ]
          },
          {
            "bitstring": "1100",
            "feasible": true,
            "objective_value": -0.01335,
            "selection": [
              1,
              1,
              0,
              0
            ]
          },
          {
            "bitstring": "1010",
            "feasible": true,
            "objective_value": -0.01295,
            "selection": [
              1,
              0,
              1,
              0
            ]
          },
          {
            "bitstring": "0110",
            "feasible": true,
            "objective_value": 0.0006,
            "selection": [
              0,
              1,
              1,
              0
            ]
          }
        ],
        "schema_version": "0.1",
        "selection": [
          1,
          0,
          0,
          1
        ],
        "upstream_package": "qiskit-finance",
        "upstream_version": null,
        "warnings": [
          "This is an educational portfolio-optimization compatibility path. It is not production finance, investment advice, pricing support, or a complete Qiskit Finance replacement."
        ]
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "status": "succeeded",
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-finance; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow finance.portfolio_optimization_native is local-only: no cloud, token, credential, or hardware access.",
        "This is an educational portfolio-optimization compatibility path. It is not production finance, investment advice, pricing support, or a complete Qiskit Finance replacement."
      ],
      "workflow_id": "finance.portfolio_optimization_native"
    }
  ]
};

export const sampleBenchmarkReport = {
  "benchmark": {
    "provenance": {
      "adapter_package": "benchpress",
      "clean_room": true,
      "cloud_access": false,
      "copied_upstream_source": false,
      "copied_upstream_text": false,
      "hardware_access": false,
      "official_benchmark": false,
      "official_endorsement": false,
      "production_benchmark_parity": false,
      "token_access": false
    },
    "report_json": "{\"capability_level\": 2, \"case_id\": \"studio_circuit_basic\", \"case_name\": \"studio_circuit_basic\", \"category\": \"suite\", \"ecosystem\": \"quantumbridge_native_benchmarking\", \"elapsed_seconds\": 0.0006572080000069036, \"expected_summary\": {\"case_count\": 3}, \"metadata\": {}, \"metrics\": {\"failed\": 0, \"passed\": 3, \"skipped\": 0, \"total\": 3, \"unsupported\": 0}, \"mode\": \"native_minimal\", \"native_implementation\": true, \"output_summary\": {\"cases\": [{\"capability_level\": 2, \"case_id\": \"circuit_basic.h_circuit_statevector\", \"case_name\": \"H circuit statevector\", \"category\": \"circuit_basic\", \"ecosystem\": \"quantumbridge_native_benchmarking\", \"elapsed_seconds\": 0.00017137500000785622, \"expected_summary\": {\"0\": 0.5, \"1\": 0.5}, \"metadata\": {\"case\": {\"case_id\": \"circuit_basic.h_circuit_statevector\", \"category\": \"circuit_basic\", \"deterministic\": true, \"expected_summary\": {\"probabilities\": {\"0\": 0.5, \"1\": 0.5}}, \"input_summary\": {\"circuit\": \"single-qubit H\", \"runner\": \"Stage 9F statevector\"}, \"metadata\": {\"cloud_access\": false, \"hardware_access\": false, \"official_benchmark_claim\": false, \"production_benchmark_parity_claim\": false, \"token_access\": false}, \"name\": \"H circuit statevector\", \"production_ready\": false, \"provenance\": {\"adapter_package\": \"benchpress\", \"clean_room\": true, \"cloud_access\": false, \"copied_upstream_source\": false, \"copied_upstream_text\": false, \"hardware_access\": false, \"official_benchmark\": false, \"official_endorsement\": false, \"production_benchmark_parity\": false, \"token_access\": false}, \"runner\": \"_run_h_statevector_case\", \"seed\": 7, \"tags\": [\"circuit\", \"statevector\"], \"timeout_seconds\": 10.0, \"warnings\": [\"QuantumBridge Benchpress compatibility support is a clean-room educational benchmarking adapter. It is not a full Benchpress replacement and does not provide production benchmark parity.\", \"QuantumBridge benchmark results are deterministic local validation results for small educational workloads, not official performance rankings.\"], \"workload_type\": \"callable\"}}, \"metrics\": {\"max_probability_delta\": 1.1102230246251565e-16}, \"mode\": \"native_minimal\", \"native_implementation\": true, \"output_summary\": {\"backend\": \"statevector\", \"capability_level\": 3, \"counts\": {}, \"data\": null, \"ecosystem\": \"quantumbridge_native_simulator\", \"final_statevector\": [{\"imag\": 0.0, \"real\": 0.7071067811865475}, {\"imag\": 0.0, \"real\": 0.7071067811865475}], \"metadata\": {\"backend\": \"statevector\", \"cloud_access\": false, \"hardware_access\": false, \"measurement_count\": 0, \"operation_count\": 1, \"production_simulator\": false, \"qiskit_aer_parity_claim\": false, \"supported_gates\": [\"cx\", \"cz\", \"h\", \"phase\", \"rx\", \"ry\", \"rz\", \"swap\", \"x\", \"y\", \"z\"], \"token_read\": false}, \"mode\": \"native_minimal\", \"native_implementation\": true, \"noise_model\": null, \"num_qubits\": 1, \"probabilities\": {\"0\": 0.4999999999999999, \"1\": 0.4999999999999999}, \"production_ready\": false, \"provenance\": {\"adapter\": \"quantumbridge.compat.qiskit_aer\", \"cloud_access\": false, \"hardware_access\": false, \"ibm_branding_copied\": false, \"official_endorsement\": false, \"source_code_copied\": false, \"stage\": \"9F\", \"token_read\": false, \"upstream_source_copied\": false, \"workflow\": \"statevector_simulator_native\"}, \"quantumbridge_version\": null, \"raw_type\": \"QuantumBridgeStatevector\", \"schema_version\": \"0.1\", \"seed\": null, \"shots\": null, \"unsupported_reason\": null, \"upstream_package\": null, \"upstream_version\": null, \"warnings\": [\"QuantumBridge Qiskit Aer support is an optional passthrough/schema bridge plus minimal educational native simulator workflows. It is not a full Qiskit Aer replacement and is not production simulator software.\", \"Native simulator support is a minimal deterministic educational simulator for small circuits.\"], \"workflow\": \"statevector_simulator_native\"}, \"passed\": true, \"production_ready\": false, \"provenance\": {\"adapter_package\": \"benchpress\", \"clean_room\": true, \"cloud_access\": false, \"copied_upstream_source\": false, \"copied_upstream_text\": false, \"hardware_access\": false, \"official_benchmark\": false, \"official_endorsement\": false, \"production_benchmark_parity\": false, \"token_access\": false}, \"quantumbridge_version\": null, \"raw_type\": \"dict\", \"report\": {}, \"schema_version\": \"0.1\", \"skipped\": false, \"status\": \"passed\", \"tags\": [\"circuit\", \"statevector\"], \"unsupported\": false, \"unsupported_reason\": null, \"upstream_package\": null, \"upstream_version\": null, \"warnings\": [\"QuantumBridge Benchpress compatibility support is a clean-room educational benchmarking adapter. It is not a full Benchpress replacement and does not provide production benchmark parity.\", \"QuantumBridge benchmark results are deterministic local validation results for small educational workloads, not official performance rankings.\"], \"workflow\": \"benchmark_case\"}, {\"capability_level\": 2, \"case_id\": \"circuit_basic.bell_qasm_counts\", \"case_name\": \"Bell qasm counts\", \"category\": \"circuit_basic\", \"ecosystem\": \"quantumbridge_native_benchmarking\", \"elapsed_seconds\": 0.00029324999999857937, \"expected_summary\": {}, \"metadata\": {\"case\": {\"case_id\": \"circuit_basic.bell_qasm_counts\", \"category\": \"circuit_basic\", \"deterministic\": true, \"expected_summary\": {\"allowed_counts\": [\"00\", \"11\"]}, \"input_summary\": {\"circuit\": \"Bell measured\", \"shots\": 128}, \"metadata\": {\"cloud_access\": false, \"hardware_access\": false, \"official_benchmark_claim\": false, \"production_benchmark_parity_claim\": false, \"token_access\": false}, \"name\": \"Bell qasm counts\", \"production_ready\": false, \"provenance\": {\"adapter_package\": \"benchpress\", \"clean_room\": true, \"cloud_access\": false, \"copied_upstream_source\": false, \"copied_upstream_text\": false, \"hardware_access\": false, \"official_benchmark\": false, \"official_endorsement\": false, \"production_benchmark_parity\": false, \"token_access\": false}, \"runner\": \"_run_bell_counts_case\", \"seed\": 7, \"tags\": [\"circuit\", \"counts\"], \"timeout_seconds\": 10.0, \"warnings\": [\"QuantumBridge Benchpress compatibility support is a clean-room educational benchmarking adapter. It is not a full Benchpress replacement and does not provide production benchmark parity.\", \"QuantumBridge benchmark results are deterministic local validation results for small educational workloads, not official performance rankings.\"], \"workload_type\": \"callable\"}}, \"metrics\": {\"shot_count\": 128}, \"mode\": \"native_minimal\", \"native_implementation\": true, \"output_summary\": {\"backend\": \"qasm\", \"capability_level\": 3, \"counts\": {\"00\": 61, \"11\": 67}, \"data\": null, \"ecosystem\": \"quantumbridge_native_simulator\", \"final_statevector\": [], \"metadata\": {\"backend\": \"qasm\", \"cloud_access\": false, \"hardware_access\": false, \"measurement_count\": 2, \"operation_count\": 2, \"production_simulator\": false, \"qiskit_aer_parity_claim\": false, \"supported_gates\": [\"cx\", \"cz\", \"h\", \"phase\", \"rx\", \"ry\", \"rz\", \"swap\", \"x\", \"y\", \"z\"], \"token_read\": false}, \"mode\": \"native_minimal\", \"native_implementation\": true, \"noise_model\": null, \"num_qubits\": 2, \"probabilities\": {\"00\": 0.4765625, \"11\": 0.5234375}, \"production_ready\": false, \"provenance\": {\"adapter\": \"quantumbridge.compat.qiskit_aer\", \"cloud_access\": false, \"hardware_access\": false, \"ibm_branding_copied\": false, \"official_endorsement\": false, \"source_code_copied\": false, \"stage\": \"9F\", \"token_read\": false, \"upstream_source_copied\": false, \"workflow\": \"qasm_simulator_native\"}, \"quantumbridge_version\": null, \"raw_type\": \"QuantumBridgeQasmCounts\", \"schema_version\": \"0.1\", \"seed\": 7, \"shots\": 128, \"unsupported_reason\": null, \"upstream_package\": null, \"upstream_version\": null, \"warnings\": [\"QuantumBridge Qiskit Aer support is an optional passthrough/schema bridge plus minimal educational native simulator workflows. It is not a full Qiskit Aer replacement and is not production simulator software.\", \"Native simulator support is a minimal deterministic educational simulator for small circuits.\"], \"workflow\": \"qasm_simulator_native\"}, \"passed\": true, \"production_ready\": false, \"provenance\": {\"adapter_package\": \"benchpress\", \"clean_room\": true, \"cloud_access\": false, \"copied_upstream_source\": false, \"copied_upstream_text\": false, \"hardware_access\": false, \"official_benchmark\": false, \"official_endorsement\": false, \"production_benchmark_parity\": false, \"token_access\": false}, \"quantumbridge_version\": null, \"raw_type\": \"dict\", \"report\": {}, \"schema_version\": \"0.1\", \"skipped\": false, \"status\": \"passed\", \"tags\": [\"circuit\", \"counts\"], \"unsupported\": false, \"unsupported_reason\": null, \"upstream_package\": null, \"upstream_version\": null, \"warnings\": [\"QuantumBridge Benchpress compatibility support is a clean-room educational benchmarking adapter. It is not a full Benchpress replacement and does not provide production benchmark parity.\", \"QuantumBridge benchmark results are deterministic local validation results for small educational workloads, not official performance rankings.\"], \"workflow\": \"benchmark_case\"}, {\"capability_level\": 2, \"case_id\": \"circuit_basic.parameterized_rx_ry_statevector\", \"case_name\": \"Parameterized RX RY statevector\", \"category\": \"circuit_basic\", \"ecosystem\": \"quantumbridge_native_benchmarking\", \"elapsed_seconds\": 0.00012441699999499178, \"expected_summary\": {}, \"metadata\": {\"case\": {\"case_id\": \"circuit_basic.parameterized_rx_ry_statevector\", \"category\": \"circuit_basic\", \"deterministic\": true, \"expected_summary\": {\"probability_sum\": 1.0}, \"input_summary\": {\"circuit\": \"RX/RY\", \"parameters\": [0.7853981633974483, 0.5235987755982988]}, \"metadata\": {\"cloud_access\": false, \"hardware_access\": false, \"official_benchmark_claim\": false, \"production_benchmark_parity_claim\": false, \"token_access\": false}, \"name\": \"Parameterized RX RY statevector\", \"production_ready\": false, \"provenance\": {\"adapter_package\": \"benchpress\", \"clean_room\": true, \"cloud_access\": false, \"copied_upstream_source\": false, \"copied_upstream_text\": false, \"hardware_access\": false, \"official_benchmark\": false, \"official_endorsement\": false, \"production_benchmark_parity\": false, \"token_access\": false}, \"runner\": \"_run_parameterized_case\", \"seed\": 7, \"tags\": [\"circuit\", \"parameters\"], \"timeout_seconds\": 10.0, \"warnings\": [\"QuantumBridge Benchpress compatibility support is a clean-room educational benchmarking adapter. It is not a full Benchpress replacement and does not provide production benchmark parity.\", \"QuantumBridge benchmark results are deterministic local validation results for small educational workloads, not official performance rankings.\"], \"workload_type\": \"callable\"}}, \"metrics\": {\"probability_sum\": 1.0}, \"mode\": \"native_minimal\", \"native_implementation\": true, \"output_summary\": {\"backend\": \"statevector\", \"capability_level\": 3, \"counts\": {}, \"data\": null, \"ecosystem\": \"quantumbridge_native_simulator\", \"final_statevector\": [{\"imag\": 0.09904576054128762, \"real\": 0.8923991008325228}, {\"imag\": -0.3696438106143861, \"real\": 0.23911761839433449}], \"metadata\": {\"backend\": \"statevector\", \"cloud_access\": false, \"hardware_access\": false, \"measurement_count\": 0, \"operation_count\": 2, \"production_simulator\": false, \"qiskit_aer_parity_claim\": false, \"supported_gates\": [\"cx\", \"cz\", \"h\", \"phase\", \"rx\", \"ry\", \"rz\", \"swap\", \"x\", \"y\", \"z\"], \"token_read\": false}, \"mode\": \"native_minimal\", \"native_implementation\": true, \"noise_model\": null, \"num_qubits\": 1, \"probabilities\": {\"0\": 0.8061862178478973, \"1\": 0.1938137821521027}, \"production_ready\": false, \"provenance\": {\"adapter\": \"quantumbridge.compat.qiskit_aer\", \"cloud_access\": false, \"hardware_access\": false, \"ibm_branding_copied\": false, \"official_endorsement\": false, \"source_code_copied\": false, \"stage\": \"9F\", \"token_read\": false, \"upstream_source_copied\": false, \"workflow\": \"statevector_simulator_native\"}, \"quantumbridge_version\": null, \"raw_type\": \"QuantumBridgeStatevector\", \"schema_version\": \"0.1\", \"seed\": null, \"shots\": null, \"unsupported_reason\": null, \"upstream_package\": null, \"upstream_version\": null, \"warnings\": [\"QuantumBridge Qiskit Aer support is an optional passthrough/schema bridge plus minimal educational native simulator workflows. It is not a full Qiskit Aer replacement and is not production simulator software.\", \"Native simulator support is a minimal deterministic educational simulator for small circuits.\"], \"workflow\": \"statevector_simulator_native\"}, \"passed\": true, \"production_ready\": false, \"provenance\": {\"adapter_package\": \"benchpress\", \"clean_room\": true, \"cloud_access\": false, \"copied_upstream_source\": false, \"copied_upstream_text\": false, \"hardware_access\": false, \"official_benchmark\": false, \"official_endorsement\": false, \"production_benchmark_parity\": false, \"token_access\": false}, \"quantumbridge_version\": null, \"raw_type\": \"dict\", \"report\": {}, \"schema_version\": \"0.1\", \"skipped\": false, \"status\": \"passed\", \"tags\": [\"circuit\", \"parameters\"], \"unsupported\": false, \"unsupported_reason\": null, \"upstream_package\": null, \"upstream_version\": null, \"warnings\": [\"QuantumBridge Benchpress compatibility support is a clean-room educational benchmarking adapter. It is not a full Benchpress replacement and does not provide production benchmark parity.\", \"QuantumBridge benchmark results are deterministic local validation results for small educational workloads, not official performance rankings.\"], \"workflow\": \"benchmark_case\"}]}, \"passed\": true, \"production_ready\": false, \"provenance\": {\"adapter_package\": \"benchpress\", \"clean_room\": true, \"cloud_access\": false, \"copied_upstream_source\": false, \"copied_upstream_text\": false, \"hardware_access\": false, \"official_benchmark\": false, \"official_endorsement\": false, \"production_benchmark_parity\": false, \"token_access\": false}, \"quantumbridge_version\": null, \"raw_type\": null, \"report\": {\"summary\": {\"failed\": 0, \"passed\": 3, \"skipped\": 0, \"total\": 3, \"unsupported\": 0}}, \"schema_version\": \"0.1\", \"skipped\": false, \"status\": \"passed\", \"tags\": [\"benchpress\", \"suite\"], \"unsupported\": false, \"unsupported_reason\": null, \"upstream_package\": null, \"upstream_version\": null, \"warnings\": [\"QuantumBridge Benchpress compatibility support is a clean-room educational benchmarking adapter. It is not a full Benchpress replacement and does not provide production benchmark parity.\", \"QuantumBridge benchmark results are deterministic local validation results for small educational workloads, not official performance rankings.\"], \"workflow\": \"studio_circuit_basic\"}",
    "report_markdown": "# QuantumBridge Studio Benchmark Report\n\n- workflow: studio_circuit_basic\n- status: passed\n- passed: True\n- elapsed_seconds: 0.0006572080000069036\n\n## Boundaries\n\n- not official Benchpress output\n- not production performance ranking\n- no cloud/token/hardware access\n",
    "result": {
      "capability_level": 2,
      "case_id": "studio_circuit_basic",
      "case_name": "studio_circuit_basic",
      "category": "suite",
      "ecosystem": "quantumbridge_native_benchmarking",
      "elapsed_seconds": 0.0006572080000069036,
      "expected_summary": {
        "case_count": 3
      },
      "metadata": {},
      "metrics": {
        "failed": 0,
        "passed": 3,
        "skipped": 0,
        "total": 3,
        "unsupported": 0
      },
      "mode": "native_minimal",
      "native_implementation": true,
      "output_summary": {
        "cases": [
          {
            "capability_level": 2,
            "case_id": "circuit_basic.h_circuit_statevector",
            "case_name": "H circuit statevector",
            "category": "circuit_basic",
            "ecosystem": "quantumbridge_native_benchmarking",
            "elapsed_seconds": 0.00017137500000785622,
            "expected_summary": {
              "0": 0.5,
              "1": 0.5
            },
            "metadata": {
              "case": {
                "case_id": "circuit_basic.h_circuit_statevector",
                "category": "circuit_basic",
                "deterministic": true,
                "expected_summary": {
                  "probabilities": {
                    "0": 0.5,
                    "1": 0.5
                  }
                },
                "input_summary": {
                  "circuit": "single-qubit H",
                  "runner": "Stage 9F statevector"
                },
                "metadata": {
                  "cloud_access": false,
                  "hardware_access": false,
                  "official_benchmark_claim": false,
                  "production_benchmark_parity_claim": false,
                  "token_access": false
                },
                "name": "H circuit statevector",
                "production_ready": false,
                "provenance": {
                  "adapter_package": "benchpress",
                  "clean_room": true,
                  "cloud_access": false,
                  "copied_upstream_source": false,
                  "copied_upstream_text": false,
                  "hardware_access": false,
                  "official_benchmark": false,
                  "official_endorsement": false,
                  "production_benchmark_parity": false,
                  "token_access": false
                },
                "runner": "_run_h_statevector_case",
                "seed": 7,
                "tags": [
                  "circuit",
                  "statevector"
                ],
                "timeout_seconds": 10.0,
                "warnings": [
                  "QuantumBridge Benchpress compatibility support is a clean-room educational benchmarking adapter. It is not a full Benchpress replacement and does not provide production benchmark parity.",
                  "QuantumBridge benchmark results are deterministic local validation results for small educational workloads, not official performance rankings."
                ],
                "workload_type": "callable"
              }
            },
            "metrics": {
              "max_probability_delta": 1.1102230246251565e-16
            },
            "mode": "native_minimal",
            "native_implementation": true,
            "output_summary": {
              "backend": "statevector",
              "capability_level": 3,
              "counts": {},
              "data": null,
              "ecosystem": "quantumbridge_native_simulator",
              "final_statevector": [
                {
                  "imag": 0.0,
                  "real": 0.7071067811865475
                },
                {
                  "imag": 0.0,
                  "real": 0.7071067811865475
                }
              ],
              "metadata": {
                "backend": "statevector",
                "cloud_access": false,
                "hardware_access": false,
                "measurement_count": 0,
                "operation_count": 1,
                "production_simulator": false,
                "qiskit_aer_parity_claim": false,
                "supported_gates": [
                  "cx",
                  "cz",
                  "h",
                  "phase",
                  "rx",
                  "ry",
                  "rz",
                  "swap",
                  "x",
                  "y",
                  "z"
                ],
                "token_read": false
              },
              "mode": "native_minimal",
              "native_implementation": true,
              "noise_model": null,
              "num_qubits": 1,
              "probabilities": {
                "0": 0.4999999999999999,
                "1": 0.4999999999999999
              },
              "production_ready": false,
              "provenance": {
                "adapter": "quantumbridge.compat.qiskit_aer",
                "cloud_access": false,
                "hardware_access": false,
                "ibm_branding_copied": false,
                "official_endorsement": false,
                "source_code_copied": false,
                "stage": "9F",
                "token_read": false,
                "upstream_source_copied": false,
                "workflow": "statevector_simulator_native"
              },
              "quantumbridge_version": null,
              "raw_type": "QuantumBridgeStatevector",
              "schema_version": "0.1",
              "seed": null,
              "shots": null,
              "unsupported_reason": null,
              "upstream_package": null,
              "upstream_version": null,
              "warnings": [
                "QuantumBridge Qiskit Aer support is an optional passthrough/schema bridge plus minimal educational native simulator workflows. It is not a full Qiskit Aer replacement and is not production simulator software.",
                "Native simulator support is a minimal deterministic educational simulator for small circuits."
              ],
              "workflow": "statevector_simulator_native"
            },
            "passed": true,
            "production_ready": false,
            "provenance": {
              "adapter_package": "benchpress",
              "clean_room": true,
              "cloud_access": false,
              "copied_upstream_source": false,
              "copied_upstream_text": false,
              "hardware_access": false,
              "official_benchmark": false,
              "official_endorsement": false,
              "production_benchmark_parity": false,
              "token_access": false
            },
            "quantumbridge_version": null,
            "raw_type": "dict",
            "report": {},
            "schema_version": "0.1",
            "skipped": false,
            "status": "passed",
            "tags": [
              "circuit",
              "statevector"
            ],
            "unsupported": false,
            "unsupported_reason": null,
            "upstream_package": null,
            "upstream_version": null,
            "warnings": [
              "QuantumBridge Benchpress compatibility support is a clean-room educational benchmarking adapter. It is not a full Benchpress replacement and does not provide production benchmark parity.",
              "QuantumBridge benchmark results are deterministic local validation results for small educational workloads, not official performance rankings."
            ],
            "workflow": "benchmark_case"
          },
          {
            "capability_level": 2,
            "case_id": "circuit_basic.bell_qasm_counts",
            "case_name": "Bell qasm counts",
            "category": "circuit_basic",
            "ecosystem": "quantumbridge_native_benchmarking",
            "elapsed_seconds": 0.00029324999999857937,
            "expected_summary": {},
            "metadata": {
              "case": {
                "case_id": "circuit_basic.bell_qasm_counts",
                "category": "circuit_basic",
                "deterministic": true,
                "expected_summary": {
                  "allowed_counts": [
                    "00",
                    "11"
                  ]
                },
                "input_summary": {
                  "circuit": "Bell measured",
                  "shots": 128
                },
                "metadata": {
                  "cloud_access": false,
                  "hardware_access": false,
                  "official_benchmark_claim": false,
                  "production_benchmark_parity_claim": false,
                  "token_access": false
                },
                "name": "Bell qasm counts",
                "production_ready": false,
                "provenance": {
                  "adapter_package": "benchpress",
                  "clean_room": true,
                  "cloud_access": false,
                  "copied_upstream_source": false,
                  "copied_upstream_text": false,
                  "hardware_access": false,
                  "official_benchmark": false,
                  "official_endorsement": false,
                  "production_benchmark_parity": false,
                  "token_access": false
                },
                "runner": "_run_bell_counts_case",
                "seed": 7,
                "tags": [
                  "circuit",
                  "counts"
                ],
                "timeout_seconds": 10.0,
                "warnings": [
                  "QuantumBridge Benchpress compatibility support is a clean-room educational benchmarking adapter. It is not a full Benchpress replacement and does not provide production benchmark parity.",
                  "QuantumBridge benchmark results are deterministic local validation results for small educational workloads, not official performance rankings."
                ],
                "workload_type": "callable"
              }
            },
            "metrics": {
              "shot_count": 128
            },
            "mode": "native_minimal",
            "native_implementation": true,
            "output_summary": {
              "backend": "qasm",
              "capability_level": 3,
              "counts": {
                "00": 61,
                "11": 67
              },
              "data": null,
              "ecosystem": "quantumbridge_native_simulator",
              "final_statevector": [],
              "metadata": {
                "backend": "qasm",
                "cloud_access": false,
                "hardware_access": false,
                "measurement_count": 2,
                "operation_count": 2,
                "production_simulator": false,
                "qiskit_aer_parity_claim": false,
                "supported_gates": [
                  "cx",
                  "cz",
                  "h",
                  "phase",
                  "rx",
                  "ry",
                  "rz",
                  "swap",
                  "x",
                  "y",
                  "z"
                ],
                "token_read": false
              },
              "mode": "native_minimal",
              "native_implementation": true,
              "noise_model": null,
              "num_qubits": 2,
              "probabilities": {
                "00": 0.4765625,
                "11": 0.5234375
              },
              "production_ready": false,
              "provenance": {
                "adapter": "quantumbridge.compat.qiskit_aer",
                "cloud_access": false,
                "hardware_access": false,
                "ibm_branding_copied": false,
                "official_endorsement": false,
                "source_code_copied": false,
                "stage": "9F",
                "token_read": false,
                "upstream_source_copied": false,
                "workflow": "qasm_simulator_native"
              },
              "quantumbridge_version": null,
              "raw_type": "QuantumBridgeQasmCounts",
              "schema_version": "0.1",
              "seed": 7,
              "shots": 128,
              "unsupported_reason": null,
              "upstream_package": null,
              "upstream_version": null,
              "warnings": [
                "QuantumBridge Qiskit Aer support is an optional passthrough/schema bridge plus minimal educational native simulator workflows. It is not a full Qiskit Aer replacement and is not production simulator software.",
                "Native simulator support is a minimal deterministic educational simulator for small circuits."
              ],
              "workflow": "qasm_simulator_native"
            },
            "passed": true,
            "production_ready": false,
            "provenance": {
              "adapter_package": "benchpress",
              "clean_room": true,
              "cloud_access": false,
              "copied_upstream_source": false,
              "copied_upstream_text": false,
              "hardware_access": false,
              "official_benchmark": false,
              "official_endorsement": false,
              "production_benchmark_parity": false,
              "token_access": false
            },
            "quantumbridge_version": null,
            "raw_type": "dict",
            "report": {},
            "schema_version": "0.1",
            "skipped": false,
            "status": "passed",
            "tags": [
              "circuit",
              "counts"
            ],
            "unsupported": false,
            "unsupported_reason": null,
            "upstream_package": null,
            "upstream_version": null,
            "warnings": [
              "QuantumBridge Benchpress compatibility support is a clean-room educational benchmarking adapter. It is not a full Benchpress replacement and does not provide production benchmark parity.",
              "QuantumBridge benchmark results are deterministic local validation results for small educational workloads, not official performance rankings."
            ],
            "workflow": "benchmark_case"
          },
          {
            "capability_level": 2,
            "case_id": "circuit_basic.parameterized_rx_ry_statevector",
            "case_name": "Parameterized RX RY statevector",
            "category": "circuit_basic",
            "ecosystem": "quantumbridge_native_benchmarking",
            "elapsed_seconds": 0.00012441699999499178,
            "expected_summary": {},
            "metadata": {
              "case": {
                "case_id": "circuit_basic.parameterized_rx_ry_statevector",
                "category": "circuit_basic",
                "deterministic": true,
                "expected_summary": {
                  "probability_sum": 1.0
                },
                "input_summary": {
                  "circuit": "RX/RY",
                  "parameters": [
                    0.7853981633974483,
                    0.5235987755982988
                  ]
                },
                "metadata": {
                  "cloud_access": false,
                  "hardware_access": false,
                  "official_benchmark_claim": false,
                  "production_benchmark_parity_claim": false,
                  "token_access": false
                },
                "name": "Parameterized RX RY statevector",
                "production_ready": false,
                "provenance": {
                  "adapter_package": "benchpress",
                  "clean_room": true,
                  "cloud_access": false,
                  "copied_upstream_source": false,
                  "copied_upstream_text": false,
                  "hardware_access": false,
                  "official_benchmark": false,
                  "official_endorsement": false,
                  "production_benchmark_parity": false,
                  "token_access": false
                },
                "runner": "_run_parameterized_case",
                "seed": 7,
                "tags": [
                  "circuit",
                  "parameters"
                ],
                "timeout_seconds": 10.0,
                "warnings": [
                  "QuantumBridge Benchpress compatibility support is a clean-room educational benchmarking adapter. It is not a full Benchpress replacement and does not provide production benchmark parity.",
                  "QuantumBridge benchmark results are deterministic local validation results for small educational workloads, not official performance rankings."
                ],
                "workload_type": "callable"
              }
            },
            "metrics": {
              "probability_sum": 1.0
            },
            "mode": "native_minimal",
            "native_implementation": true,
            "output_summary": {
              "backend": "statevector",
              "capability_level": 3,
              "counts": {},
              "data": null,
              "ecosystem": "quantumbridge_native_simulator",
              "final_statevector": [
                {
                  "imag": 0.09904576054128762,
                  "real": 0.8923991008325228
                },
                {
                  "imag": -0.3696438106143861,
                  "real": 0.23911761839433449
                }
              ],
              "metadata": {
                "backend": "statevector",
                "cloud_access": false,
                "hardware_access": false,
                "measurement_count": 0,
                "operation_count": 2,
                "production_simulator": false,
                "qiskit_aer_parity_claim": false,
                "supported_gates": [
                  "cx",
                  "cz",
                  "h",
                  "phase",
                  "rx",
                  "ry",
                  "rz",
                  "swap",
                  "x",
                  "y",
                  "z"
                ],
                "token_read": false
              },
              "mode": "native_minimal",
              "native_implementation": true,
              "noise_model": null,
              "num_qubits": 1,
              "probabilities": {
                "0": 0.8061862178478973,
                "1": 0.1938137821521027
              },
              "production_ready": false,
              "provenance": {
                "adapter": "quantumbridge.compat.qiskit_aer",
                "cloud_access": false,
                "hardware_access": false,
                "ibm_branding_copied": false,
                "official_endorsement": false,
                "source_code_copied": false,
                "stage": "9F",
                "token_read": false,
                "upstream_source_copied": false,
                "workflow": "statevector_simulator_native"
              },
              "quantumbridge_version": null,
              "raw_type": "QuantumBridgeStatevector",
              "schema_version": "0.1",
              "seed": null,
              "shots": null,
              "unsupported_reason": null,
              "upstream_package": null,
              "upstream_version": null,
              "warnings": [
                "QuantumBridge Qiskit Aer support is an optional passthrough/schema bridge plus minimal educational native simulator workflows. It is not a full Qiskit Aer replacement and is not production simulator software.",
                "Native simulator support is a minimal deterministic educational simulator for small circuits."
              ],
              "workflow": "statevector_simulator_native"
            },
            "passed": true,
            "production_ready": false,
            "provenance": {
              "adapter_package": "benchpress",
              "clean_room": true,
              "cloud_access": false,
              "copied_upstream_source": false,
              "copied_upstream_text": false,
              "hardware_access": false,
              "official_benchmark": false,
              "official_endorsement": false,
              "production_benchmark_parity": false,
              "token_access": false
            },
            "quantumbridge_version": null,
            "raw_type": "dict",
            "report": {},
            "schema_version": "0.1",
            "skipped": false,
            "status": "passed",
            "tags": [
              "circuit",
              "parameters"
            ],
            "unsupported": false,
            "unsupported_reason": null,
            "upstream_package": null,
            "upstream_version": null,
            "warnings": [
              "QuantumBridge Benchpress compatibility support is a clean-room educational benchmarking adapter. It is not a full Benchpress replacement and does not provide production benchmark parity.",
              "QuantumBridge benchmark results are deterministic local validation results for small educational workloads, not official performance rankings."
            ],
            "workflow": "benchmark_case"
          }
        ]
      },
      "passed": true,
      "production_ready": false,
      "provenance": {
        "adapter_package": "benchpress",
        "clean_room": true,
        "cloud_access": false,
        "copied_upstream_source": false,
        "copied_upstream_text": false,
        "hardware_access": false,
        "official_benchmark": false,
        "official_endorsement": false,
        "production_benchmark_parity": false,
        "token_access": false
      },
      "quantumbridge_version": null,
      "raw_type": null,
      "report": {
        "summary": {
          "failed": 0,
          "passed": 3,
          "skipped": 0,
          "total": 3,
          "unsupported": 0
        }
      },
      "schema_version": "0.1",
      "skipped": false,
      "status": "passed",
      "tags": [
        "benchpress",
        "suite"
      ],
      "unsupported": false,
      "unsupported_reason": null,
      "upstream_package": null,
      "upstream_version": null,
      "warnings": [
        "QuantumBridge Benchpress compatibility support is a clean-room educational benchmarking adapter. It is not a full Benchpress replacement and does not provide production benchmark parity.",
        "QuantumBridge benchmark results are deterministic local validation results for small educational workloads, not official performance rankings."
      ],
      "workflow": "studio_circuit_basic"
    },
    "schema_version": "quantumbridge-studio-api-v0.1",
    "suite_id": "circuit_basic",
    "unsupported_reason": null,
    "warnings": [
      "QuantumBridge Benchpress compatibility support is a clean-room educational benchmarking adapter. It is not a full Benchpress replacement and does not provide production benchmark parity.",
      "QuantumBridge benchmark results are deterministic local validation results for small educational workloads, not official performance rankings."
    ]
  },
  "notices": [
    "QuantumBridge Studio is an independent local prototype.",
    "No official endorsement is claimed.",
    "Local-only: no cloud execution, credential reading, or hardware access.",
    "Third-party package names are used only for compatibility identification.",
    "This prototype is not production-ready."
  ]
};
