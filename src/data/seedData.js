// This file is generated from QuantumBridge-owned Stage 10C/10E backend API outputs.

// Local prototype seed data only: no secrets, credentials, cloud calls, or hardware access.

export const sampleCatalog = {
  "backend_schema_version": "quantumbridge-studio-api-v0.1",
  "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
  "generated_at": "2026-06-10T01:36:50+00:00",
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
  "provenance": {
    "cloud_access": false,
    "copied_upstream_source": false,
    "copied_upstream_ui": false,
    "hardware_access": false,
    "official_endorsement": false,
    "production_ready": false,
    "source": "quantumbridge.studio.backend",
    "token_access": false
  },
  "quantumbridge_version": "0.1.0rc1",
  "schema_version": "quantumbridge-studio-frontend-seed-v0.1",
  "section": "catalog",
  "source": "quantumbridge.studio.backend",
  "summary": {
    "cloud_access": false,
    "executable_workflow_count": 59,
    "hardware_access": false,
    "official_endorsement": false,
    "project_count": 12,
    "studio_ready": {
      "partial": 12
    },
    "token_access": false
  },
  "warnings": [
    "Local prototype seed data only.",
    "No production UI claim.",
    "No cloud execution, credential reading, or hardware access.",
    "Compatibility names are inventory identifiers, not endorsement claims."
  ]
};

export const sampleWorkflows = {
  "backend_schema_version": "quantumbridge-studio-api-v0.1",
  "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
  "details": [
    {
      "category": "finance",
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
  "generated_at": "2026-06-10T01:36:50+00:00",
  "provenance": {
    "cloud_access": false,
    "copied_upstream_source": false,
    "copied_upstream_ui": false,
    "hardware_access": false,
    "official_endorsement": false,
    "production_ready": false,
    "source": "quantumbridge.studio.backend",
    "token_access": false
  },
  "quantumbridge_version": "0.1.0rc1",
  "schema_version": "quantumbridge-studio-frontend-seed-v0.1",
  "section": "workflows",
  "source": "quantumbridge.studio.backend",
  "warnings": [
    "Local prototype seed data only.",
    "No production UI claim.",
    "No cloud execution, credential reading, or hardware access.",
    "Compatibility names are inventory identifiers, not endorsement claims."
  ],
  "workflow_count": 36,
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

export const sampleWorkflowDetails = {
  "backend_schema_version": "quantumbridge-studio-api-v0.1",
  "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
  "details": [
    {
      "category": "finance",
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
      "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
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
      "unsupported_limitations": [
        "local prototype surface",
        "not production UI",
        "no cloud/token/hardware route"
      ],
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
  "generated_at": "2026-06-10T01:36:50+00:00",
  "provenance": {
    "cloud_access": false,
    "copied_upstream_source": false,
    "copied_upstream_ui": false,
    "hardware_access": false,
    "official_endorsement": false,
    "production_ready": false,
    "source": "quantumbridge.studio.backend",
    "token_access": false
  },
  "quantumbridge_version": "0.1.0rc1",
  "schema_version": "quantumbridge-studio-frontend-seed-v0.1",
  "section": "workflow_details",
  "source": "quantumbridge.studio.backend",
  "warnings": [
    "Local prototype seed data only.",
    "No production UI claim.",
    "No cloud execution, credential reading, or hardware access.",
    "Compatibility names are inventory identifiers, not endorsement claims."
  ],
  "workflow_detail_count": 36
};

export const sampleResults = {
  "backend_schema_version": "quantumbridge-studio-api-v0.1",
  "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
  "generated_at": "2026-06-10T01:36:50+00:00",
  "provenance": {
    "cloud_access": false,
    "copied_upstream_source": false,
    "copied_upstream_ui": false,
    "hardware_access": false,
    "official_endorsement": false,
    "production_ready": false,
    "source": "quantumbridge.studio.backend",
    "token_access": false
  },
  "quantumbridge_version": "0.1.0rc1",
  "result_count": 18,
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
          "workflow": "statevector_simulator_native"
        },
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "aer.statevector_native"
      },
      "result": {
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
            "real": 0.0
          },
          {
            "imag": 0.0,
            "real": 0.0
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
          "00": 0.4999999999999999,
          "11": 0.4999999999999999
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
      "schema_version": "quantumbridge-studio-api-v0.1",
      "status": "succeeded",
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-aer; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow aer.statevector_native is local-only: no cloud, token, credential, or hardware access.",
        "QuantumBridge Qiskit Aer support is an optional passthrough/schema bridge plus minimal educational native simulator workflows. It is not a full Qiskit Aer replacement and is not production simulator software.",
        "Native simulator support is a minimal deterministic educational simulator for small circuits."
      ],
      "workflow_id": "aer.statevector_native"
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
      "execution_id": "studio-exec-000003",
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
          "workflow": "noisy_qasm_simulator_native"
        },
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "aer.noisy_counts_native"
      },
      "result": {
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
          "noise_applied": true,
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
        "noise_model": {
          "educational_only": true,
          "p": 0.0,
          "production_ready": false,
          "qiskit_aer_noise_model_parity": false,
          "type": "measurement_bitflip"
        },
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
          "workflow": "noisy_qasm_simulator_native"
        },
        "quantumbridge_version": null,
        "raw_type": "QuantumBridgeNoisyQasmCounts",
        "schema_version": "0.1",
        "seed": 7,
        "shots": 128,
        "unsupported_reason": null,
        "upstream_package": null,
        "upstream_version": null,
        "warnings": [
          "QuantumBridge Qiskit Aer support is an optional passthrough/schema bridge plus minimal educational native simulator workflows. It is not a full Qiskit Aer replacement and is not production simulator software.",
          "Native simulator support is a minimal deterministic educational simulator for small circuits.",
          "Native noise support is educational metadata / simple sampling noise only and does not provide Qiskit Aer noise-model parity."
        ],
        "workflow": "noisy_qasm_simulator_native"
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
        "Studio workflow aer.noisy_counts_native is local-only: no cloud, token, credential, or hardware access.",
        "QuantumBridge Qiskit Aer support is an optional passthrough/schema bridge plus minimal educational native simulator workflows. It is not a full Qiskit Aer replacement and is not production simulator software.",
        "Native simulator support is a minimal deterministic educational simulator for small circuits.",
        "Native noise support is educational metadata / simple sampling noise only and does not provide Qiskit Aer noise-model parity."
      ],
      "workflow_id": "aer.noisy_counts_native"
    },
    {
      "error": null,
      "execution_id": "studio-exec-000004",
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
    },
    {
      "error": null,
      "execution_id": "studio-exec-000005",
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
        "result_provenance": {
          "adapter_package": "qiskit-optimization",
          "cloud_access": false,
          "copied_upstream_source": false,
          "hardware_access": false,
          "native_subset": "binary quadratic program exact enumeration",
          "official_endorsement": false,
          "token_access": false
        },
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "optimization.quadratic_program_native"
      },
      "result": {
        "assignment": {
          "x0": 1,
          "x1": 0
        },
        "constraints": [
          {
            "coefficients": {
              "x0": 1.0,
              "x1": 1.0
            },
            "name": "budget",
            "rhs": 1.0,
            "sense": "<="
          }
        ],
        "feasible": true,
        "feasible_assignments": [
          {
            "x0": 0,
            "x1": 0
          },
          {
            "x0": 0,
            "x1": 1
          },
          {
            "x0": 1,
            "x1": 0
          }
        ],
        "ising_metadata": {
          "format": "ising-metadata-v0.1",
          "h": {
            "x0": 0.4375,
            "x1": 0.3125
          },
          "j": [
            {
              "coefficient": 0.0625,
              "left": "x0",
              "right": "x1"
            }
          ],
          "offset": -0.8125,
          "production_ready": false,
          "source_qubo_format": "qubo-metadata-v0.1",
          "variables": [
            "x0",
            "x1"
          ],
          "warnings": []
        },
        "metadata": {
          "num_constraints": 1,
          "num_variables": 2,
          "production_ready": false,
          "solver": "deterministic full enumeration"
        },
        "method": "bruteforce-exact",
        "objective_sense": "minimize",
        "objective_value": -1.0,
        "path": "quantumbridge-native",
        "problem_name": "studio_binary_program",
        "provenance": {
          "adapter_package": "qiskit-optimization",
          "cloud_access": false,
          "copied_upstream_source": false,
          "hardware_access": false,
          "native_subset": "binary quadratic program exact enumeration",
          "official_endorsement": false,
          "token_access": false
        },
        "qubo_metadata": {
          "constraints": [
            {
              "coefficients": {
                "x0": 1.0,
                "x1": 1.0
              },
              "name": "budget",
              "rhs": 1.0,
              "sense": "<="
            }
          ],
          "format": "qubo-metadata-v0.1",
          "linear": {
            "x0": -1.0,
            "x1": -0.75
          },
          "minimization_offset": 0.0,
          "objective_sense": "minimize",
          "penalty": null,
          "penalty_applied": false,
          "production_ready": false,
          "quadratic": [
            {
              "coefficient": 0.25,
              "left": "x0",
              "right": "x1"
            }
          ],
          "variables": [
            "x0",
            "x1"
          ],
          "warnings": []
        },
        "samples": [
          {
            "assignment": {
              "x0": 0,
              "x1": 0
            },
            "bitstring": "00",
            "feasible": true,
            "objective_value": 0.0
          },
          {
            "assignment": {
              "x0": 0,
              "x1": 1
            },
            "bitstring": "01",
            "feasible": true,
            "objective_value": -0.75
          },
          {
            "assignment": {
              "x0": 1,
              "x1": 0
            },
            "bitstring": "10",
            "feasible": true,
            "objective_value": -1.0
          },
          {
            "assignment": {
              "x0": 1,
              "x1": 1
            },
            "bitstring": "11",
            "feasible": false,
            "objective_value": -1.5
          }
        ],
        "schema_version": "0.1",
        "unsupported_reason": null,
        "upstream_package": null,
        "upstream_version": null,
        "warnings": [
          "QuantumBridge Qiskit Optimization support is an optional passthrough/schema bridge plus minimal educational native examples. It is not a full Qiskit Optimization replacement and is not production optimization software.",
          "Native QuadraticProgram support is a minimal deterministic educational binary optimization solver for small problems."
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
        "QuantumBridge Studio uses clean-room local metadata for qiskit-optimization; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow optimization.quadratic_program_native is local-only: no cloud, token, credential, or hardware access.",
        "QuantumBridge Qiskit Optimization support is an optional passthrough/schema bridge plus minimal educational native examples. It is not a full Qiskit Optimization replacement and is not production optimization software.",
        "Native QuadraticProgram support is a minimal deterministic educational binary optimization solver for small problems."
      ],
      "workflow_id": "optimization.quadratic_program_native"
    },
    {
      "error": null,
      "execution_id": "studio-exec-000006",
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
        "result_provenance": {
          "adapter_package": "qiskit-algorithms",
          "cloud_access": false,
          "copied_upstream_source": false,
          "feature": "qaoa_maxcut_exact_verification",
          "hardware_access": false,
          "mode": "native_minimal",
          "official_endorsement": false,
          "token_access": false
        },
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "algorithms.qaoa_native"
      },
      "result": {
        "algorithm": "QAOA",
        "bitstring": "001",
        "capability_level": 3,
        "ecosystem": "quantumbridge_native_algorithms",
        "eigenvalue": null,
        "input_summary": {
          "edges": [
            [
              0,
              1
            ],
            [
              1,
              2
            ],
            [
              2,
              0
            ]
          ],
          "num_nodes": 3,
          "p": 1
        },
        "metadata": {
          "cost_hamiltonian": {
            "edges": [
              [
                0,
                1
              ],
              [
                1,
                2
              ],
              [
                2,
                0
              ]
            ],
            "num_nodes": 3,
            "problem_type": "maxcut",
            "terms": [
              {
                "coefficient": 0.5,
                "edge": [
                  0,
                  1
                ],
                "pauli": "III"
              },
              {
                "coefficient": 0.5,
                "edge": [
                  1,
                  2
                ],
                "pauli": "III"
              },
              {
                "coefficient": 0.5,
                "edge": [
                  2,
                  0
                ],
                "pauli": "III"
              },
              {
                "coefficient": -0.5,
                "edge": [
                  0,
                  1
                ],
                "pauli": "ZZI"
              },
              {
                "coefficient": -0.5,
                "edge": [
                  1,
                  2
                ],
                "pauli": "IZZ"
              },
              {
                "coefficient": -0.5,
                "edge": [
                  2,
                  0
                ],
                "pauli": "ZIZ"
              }
            ]
          },
          "qaoa_depth": 1,
          "verification_solver": "bruteforce_exact"
        },
        "mode": "native_minimal",
        "native_implementation": true,
        "objective_value": 2.0,
        "optimal_parameters": [],
        "output_summary": {
          "best_bitstring": "001",
          "cut_value": 2,
          "num_optimal_bitstrings": 6
        },
        "probabilities": {
          "001": 0.16666666666666666,
          "010": 0.16666666666666666,
          "011": 0.16666666666666666,
          "100": 0.16666666666666666,
          "101": 0.16666666666666666,
          "110": 0.16666666666666666
        },
        "problem_type": "maxcut",
        "production_ready": false,
        "provenance": {
          "adapter_package": "qiskit-algorithms",
          "cloud_access": false,
          "copied_upstream_source": false,
          "feature": "qaoa_maxcut_exact_verification",
          "hardware_access": false,
          "mode": "native_minimal",
          "official_endorsement": false,
          "token_access": false
        },
        "quantumbridge_version": null,
        "raw_type": "NativeQAOAMaxCutExactVerification",
        "schema_version": "0.1",
        "unsupported_reason": null,
        "upstream_package": null,
        "upstream_version": null,
        "warnings": [
          "QuantumBridge Qiskit Algorithms support is an optional passthrough/schema bridge plus minimal educational native examples. It is not a full Qiskit Algorithms replacement and is not production algorithm software.",
          "Native QAOA is a minimal educational MaxCut-compatible workflow and may use exact enumeration for verification."
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
        "QuantumBridge Studio uses clean-room local metadata for qiskit-algorithms; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow algorithms.qaoa_native is local-only: no cloud, token, credential, or hardware access.",
        "QuantumBridge Qiskit Algorithms support is an optional passthrough/schema bridge plus minimal educational native examples. It is not a full Qiskit Algorithms replacement and is not production algorithm software.",
        "Native QAOA is a minimal educational MaxCut-compatible workflow and may use exact enumeration for verification."
      ],
      "workflow_id": "algorithms.qaoa_native"
    },
    {
      "error": null,
      "execution_id": "studio-exec-000007",
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
        "result_provenance": {
          "adapter_package": "qiskit-algorithms",
          "cloud_access": false,
          "copied_upstream_source": false,
          "feature": "grover_statevector",
          "hardware_access": false,
          "mode": "native_minimal",
          "official_endorsement": false,
          "token_access": false
        },
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "algorithms.grover_native"
      },
      "result": {
        "algorithm": "Grover",
        "bitstring": "11",
        "capability_level": 3,
        "ecosystem": "quantumbridge_native_algorithms",
        "eigenvalue": null,
        "input_summary": {
          "iterations": 1,
          "marked_bitstrings": [
            "11"
          ],
          "num_qubits": 2
        },
        "metadata": {
          "oracle": {
            "iterations": 1,
            "marked_bitstrings": [
              "11"
            ],
            "marked_indices": [
              3
            ],
            "num_qubits": 2,
            "oracle_type": "marked_bitstring_phase_oracle"
          }
        },
        "mode": "native_minimal",
        "native_implementation": true,
        "objective_value": 1.0,
        "optimal_parameters": [],
        "output_summary": {
          "top_measurement": "11",
          "top_probability": 1.0
        },
        "probabilities": {
          "00": 0.0,
          "01": 0.0,
          "10": 0.0,
          "11": 1.0
        },
        "problem_type": "marked_bitstring_search",
        "production_ready": false,
        "provenance": {
          "adapter_package": "qiskit-algorithms",
          "cloud_access": false,
          "copied_upstream_source": false,
          "feature": "grover_statevector",
          "hardware_access": false,
          "mode": "native_minimal",
          "official_endorsement": false,
          "token_access": false
        },
        "quantumbridge_version": null,
        "raw_type": "NativeGroverStatevector",
        "schema_version": "0.1",
        "unsupported_reason": null,
        "upstream_package": null,
        "upstream_version": null,
        "warnings": [
          "QuantumBridge Qiskit Algorithms support is an optional passthrough/schema bridge plus minimal educational native examples. It is not a full Qiskit Algorithms replacement and is not production algorithm software.",
          "Native Grover is a minimal educational statevector workflow for small marked-bitstring search problems."
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
        "QuantumBridge Studio uses clean-room local metadata for qiskit-algorithms; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow algorithms.grover_native is local-only: no cloud, token, credential, or hardware access.",
        "QuantumBridge Qiskit Algorithms support is an optional passthrough/schema bridge plus minimal educational native examples. It is not a full Qiskit Algorithms replacement and is not production algorithm software.",
        "Native Grover is a minimal educational statevector workflow for small marked-bitstring search problems."
      ],
      "workflow_id": "algorithms.grover_native"
    },
    {
      "error": null,
      "execution_id": "studio-exec-000008",
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
        "result_provenance": {
          "adapter": "quantumbridge.compat.qiskit_nature.chemistry_native",
          "ibm_branding_copied": false,
          "official_endorsement": false,
          "source_code_copied": false,
          "stage": "9D",
          "upstream_source_copied": false
        },
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "nature.h2_native"
      },
      "result": {
        "basis": "sto-3g",
        "bond_length": 0.735,
        "capability_level": 3,
        "driver": "quantumbridge-native-minimal",
        "ecosystem": "quantumbridge_native_chemistry",
        "eigenvalues": [
          -1.8572750302023797,
          -1.2445845498133257,
          -0.8827221502448626,
          -0.2249112528308669
        ],
        "electronic_energy": -1.8572750302023797,
        "ground_state_energy": -1.1421706911212985,
        "mapper": "pauli-hamiltonian",
        "metadata": {
          "cloud_access": false,
          "hardware_access": false,
          "materials_band_gap": false,
          "reference_note": "Small two-qubit educational Hamiltonian used for deterministic adapter tests.",
          "token_read": false
        },
        "mode": "native_minimal",
        "molecule": "H2",
        "native_implementation": true,
        "nuclear_repulsion_energy": 0.7151043390810812,
        "particle_count": 2,
        "pauli_terms": [
          {
            "coefficient": -1.052373245772859,
            "paulis": []
          },
          {
            "coefficient": 0.39793742484318045,
            "paulis": [
              {
                "op": "Z",
                "wire": 0
              }
            ]
          },
          {
            "coefficient": -0.39793742484318045,
            "paulis": [
              {
                "op": "Z",
                "wire": 1
              }
            ]
          },
          {
            "coefficient": -0.01128010425623538,
            "paulis": [
              {
                "op": "Z",
                "wire": 0
              },
              {
                "op": "Z",
                "wire": 1
              }
            ]
          },
          {
            "coefficient": 0.18093119978423156,
            "paulis": [
              {
                "op": "X",
                "wire": 0
              },
              {
                "op": "X",
                "wire": 1
              }
            ]
          }
        ],
        "production_ready": false,
        "provenance": {
          "adapter": "quantumbridge.compat.qiskit_nature.chemistry_native",
          "ibm_branding_copied": false,
          "official_endorsement": false,
          "source_code_copied": false,
          "stage": "9D",
          "upstream_source_copied": false
        },
        "quantumbridge_version": null,
        "qubit_count": 2,
        "raw_type": "MinimalMolecularProblem",
        "schema_version": "0.1",
        "unsupported_reason": null,
        "upstream_package": null,
        "upstream_version": null,
        "warnings": [
          "QuantumBridge Qiskit Nature support is an optional passthrough/schema bridge plus minimal educational native chemistry workflows. It is not a full Qiskit Nature replacement and is not production quantum chemistry software.",
          "Native H2/LiH workflows are deterministic educational examples for small Hamiltonians, not production electronic-structure calculations.",
          "Materials band-gap workflows are not implemented in this stage."
        ],
        "workflow": "h2_native_exact"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "status": "succeeded",
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-nature; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow nature.h2_native is local-only: no cloud, token, credential, or hardware access.",
        "QuantumBridge Qiskit Nature support is an optional passthrough/schema bridge plus minimal educational native chemistry workflows. It is not a full Qiskit Nature replacement and is not production quantum chemistry software.",
        "Native H2/LiH workflows are deterministic educational examples for small Hamiltonians, not production electronic-structure calculations.",
        "Materials band-gap workflows are not implemented in this stage."
      ],
      "workflow_id": "nature.h2_native"
    },
    {
      "error": null,
      "execution_id": "studio-exec-000009",
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
        "result_provenance": {
          "adapter": "quantumbridge.compat.qiskit_machine_learning",
          "cloud_access": false,
          "hardware_access": false,
          "ibm_branding_copied": false,
          "official_endorsement": false,
          "source_code_copied": false,
          "stage": "9E",
          "token_read": false,
          "upstream_source_copied": false,
          "workflow": "quantum_kernel_native"
        },
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "ml.quantum_kernel_native"
      },
      "result": {
        "accuracy": null,
        "capability_level": 3,
        "dataset_summary": {
          "deterministic": true,
          "features": 2,
          "high_risk_decision_use": false,
          "labels": {
            "0": 2,
            "1": 2
          },
          "network_access": false,
          "real_user_data": false,
          "samples": 4
        },
        "ecosystem": "quantumbridge_native_qml",
        "expectation": null,
        "feature_map": {
          "metadata": {
            "feature_map": "angle_rx_ry_rz_linear_entangler",
            "normalized_angles": [
              -1.5707963267948966,
              -1.5707963267948966
            ],
            "provenance": {
              "adapter": "quantumbridge.compat.qiskit_machine_learning",
              "cloud_access": false,
              "hardware_access": false,
              "ibm_branding_copied": false,
              "official_endorsement": false,
              "source_code_copied": false,
              "stage": "9E",
              "token_read": false,
              "upstream_source_copied": false,
              "workflow": "angle_feature_map"
            },
            "warnings": [
              "QuantumBridge Qiskit Machine Learning support is an optional passthrough/schema bridge plus minimal educational native QML workflows. It is not a full Qiskit Machine Learning replacement and is not production machine learning software.",
              "QuantumBridge QML examples are not intended for medical, financial, employment, identity, safety, or other high-risk automated decisions.",
              "Native quantum kernel support is a deterministic educational workflow for small toy datasets."
            ]
          },
          "name": "qb_angle_feature_map",
          "num_qubits": 2,
          "operations": [
            {
              "controls": [],
              "name": "ry",
              "params": [
                -1.5707963267948966
              ],
              "targets": [
                0
              ]
            },
            {
              "controls": [],
              "name": "rz",
              "params": [
                -0.7853981633974483
              ],
              "targets": [
                0
              ]
            },
            {
              "controls": [],
              "name": "ry",
              "params": [
                -1.5707963267948966
              ],
              "targets": [
                1
              ]
            },
            {
              "controls": [],
              "name": "rz",
              "params": [
                -0.7853981633974483
              ],
              "targets": [
                1
              ]
            },
            {
              "controls": [
                0
              ],
              "name": "cx",
              "params": [],
              "targets": [
                1
              ]
            },
            {
              "controls": [],
              "name": "rx",
              "params": [
                0.7853981633974483
              ],
              "targets": [
                1
              ]
            }
          ]
        },
        "kernel_matrix": [
          [
            0.9999999999999998,
            0.24999999999999994,
            0.3749999999999998,
            0.25
          ],
          [
            0.24999999999999994,
            0.9999999999999998,
            0.24999999999999994,
            0.3749999999999998
          ],
          [
            0.3749999999999998,
            0.24999999999999994,
            0.9999999999999998,
            0.24999999999999994
          ],
          [
            0.25,
            0.3749999999999998,
            0.24999999999999994,
            0.9999999999999998
          ]
        ],
        "metadata": {
          "cloud_access": false,
          "hardware_access": false,
          "high_risk_decision_use": false,
          "token_read": false
        },
        "mode": "native_minimal",
        "model_summary": {
          "diagonal_near_one": true,
          "kernel": "state_fidelity",
          "symmetric": true
        },
        "native_implementation": true,
        "predictions": [],
        "production_ready": false,
        "provenance": {
          "adapter": "quantumbridge.compat.qiskit_machine_learning",
          "cloud_access": false,
          "hardware_access": false,
          "ibm_branding_copied": false,
          "official_endorsement": false,
          "source_code_copied": false,
          "stage": "9E",
          "token_read": false,
          "upstream_source_copied": false,
          "workflow": "quantum_kernel_native"
        },
        "quantumbridge_version": null,
        "raw_type": "NativeQuantumKernelMatrix",
        "schema_version": "0.1",
        "unsupported_reason": null,
        "upstream_package": null,
        "upstream_version": null,
        "warnings": [
          "QuantumBridge Qiskit Machine Learning support is an optional passthrough/schema bridge plus minimal educational native QML workflows. It is not a full Qiskit Machine Learning replacement and is not production machine learning software.",
          "QuantumBridge QML examples are not intended for medical, financial, employment, identity, safety, or other high-risk automated decisions.",
          "Native quantum kernel support is a deterministic educational workflow for small toy datasets."
        ],
        "weights": [],
        "workflow": "quantum_kernel_native"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "status": "succeeded",
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qiskit-machine-learning; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow ml.quantum_kernel_native is local-only: no cloud, token, credential, or hardware access.",
        "QuantumBridge Qiskit Machine Learning support is an optional passthrough/schema bridge plus minimal educational native QML workflows. It is not a full Qiskit Machine Learning replacement and is not production machine learning software.",
        "QuantumBridge QML examples are not intended for medical, financial, employment, identity, safety, or other high-risk automated decisions.",
        "Native quantum kernel support is a deterministic educational workflow for small toy datasets."
      ],
      "workflow_id": "ml.quantum_kernel_native"
    },
    {
      "error": null,
      "execution_id": "studio-exec-000010",
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
        "result_provenance": {
          "adapter": "quantumbridge.compat.mitiq",
          "cloud_access": false,
          "hardware_access": false,
          "ibm_branding_copied": false,
          "mitiq_source_copied": false,
          "official_endorsement": false,
          "source_code_copied": false,
          "stage": "9G",
          "token_read": false,
          "upstream_source_copied": false,
          "workflow": "zne_native"
        },
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "mitiq.zne_native"
      },
      "result": {
        "calibration_matrix": [],
        "capability_level": 3,
        "circuit_summary": {
          "measurement_count": 2,
          "num_bits": 2,
          "num_qubits": 2,
          "operation_count": 2
        },
        "data": {
          "counts_by_scale": [
            {
              "00": 118,
              "01": 10,
              "10": 5,
              "11": 123
            },
            {
              "00": 109,
              "01": 12,
              "10": 16,
              "11": 119
            },
            {
              "00": 106,
              "01": 13,
              "10": 20,
              "11": 117
            }
          ]
        },
        "ecosystem": "quantumbridge_native_error_mitigation",
        "ideal_expectation_value": 0.0,
        "metadata": {
          "cloud_access": false,
          "hardware_access": false,
          "mitiq_parity_claim": false,
          "production_error_mitigation": false,
          "token_read": false,
          "workflow": "zne_native"
        },
        "mitigated_expectation_value": 0.02864583333333331,
        "mitigated_probabilities": {},
        "mode": "native_minimal",
        "native_implementation": true,
        "noise_model": {
          "educational_only": true,
          "p": 0.03,
          "production_ready": false,
          "qiskit_aer_noise_model_parity": false,
          "type": "measurement_bitflip"
        },
        "noise_scales": [
          1.0,
          2.0,
          3.0
        ],
        "noisy_counts": {
          "00": 106,
          "01": 13,
          "10": 20,
          "11": 117
        },
        "noisy_expectation_values": [
          0.0,
          -0.0546875,
          -0.0703125
        ],
        "observable": "Z0",
        "production_ready": false,
        "provenance": {
          "adapter": "quantumbridge.compat.mitiq",
          "cloud_access": false,
          "hardware_access": false,
          "ibm_branding_copied": false,
          "mitiq_source_copied": false,
          "official_endorsement": false,
          "source_code_copied": false,
          "stage": "9G",
          "token_read": false,
          "upstream_source_copied": false,
          "workflow": "zne_native"
        },
        "quantumbridge_version": null,
        "raw_counts": {},
        "raw_type": "QuantumBridgeNativeZNE",
        "schema_version": "0.1",
        "seed": 13,
        "shots": 256,
        "unsupported_reason": null,
        "upstream_package": null,
        "upstream_version": null,
        "warnings": [
          "QuantumBridge Mitiq support is an optional passthrough/schema bridge plus minimal educational native error-mitigation workflows. It is not a full Mitiq replacement and is not production error-mitigation software.",
          "Native ZNE support is a deterministic educational workflow for small simulated circuits and simple extrapolation."
        ],
        "workflow": "zne_native"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "status": "succeeded",
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for mitiq; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow mitiq.zne_native is local-only: no cloud, token, credential, or hardware access.",
        "QuantumBridge Mitiq support is an optional passthrough/schema bridge plus minimal educational native error-mitigation workflows. It is not a full Mitiq replacement and is not production error-mitigation software.",
        "Native ZNE support is a deterministic educational workflow for small simulated circuits and simple extrapolation."
      ],
      "workflow_id": "mitiq.zne_native"
    },
    {
      "error": null,
      "execution_id": "studio-exec-000011",
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
        "result_provenance": {
          "adapter": "quantumbridge.compat.pennylane_qiskit",
          "cloud_access": false,
          "hardware_access": false,
          "ibm_branding_copied": false,
          "official_endorsement": false,
          "pennylane_qiskit_source_copied": false,
          "pennylane_source_copied": false,
          "qiskit_source_copied": false,
          "source_code_copied": false,
          "stage": "9H",
          "token_read": false,
          "upstream_source_copied": false,
          "workflow": "qiskit_to_pennylane_bridge_native"
        },
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "pennylane_qiskit.qiskit_to_pennylane"
      },
      "result": {
        "capability_level": 3,
        "circuit_summary": {
          "measurements": [
            {
              "bit": 0,
              "wire": 0
            },
            {
              "bit": 1,
              "wire": 1
            }
          ],
          "num_bits": 2,
          "num_qubits": 2,
          "operations": [
            "h",
            "cx"
          ],
          "type": "QuantumBridgeCircuit"
        },
        "converted_ir": {
          "instructions": [
            {
              "controls": [],
              "metadata": {},
              "op": "h",
              "params": [],
              "targets": [
                0
              ]
            },
            {
              "controls": [
                0
              ],
              "metadata": {},
              "op": "cx",
              "params": [],
              "targets": [
                1
              ]
            }
          ],
          "ir_version": "qb-ir-v0.1",
          "measurements": [
            {
              "bits": [
                0
              ],
              "kind": "computational",
              "wires": [
                0
              ]
            },
            {
              "bits": [
                1
              ],
              "kind": "computational",
              "wires": [
                1
              ]
            }
          ],
          "metadata": {
            "bridge": "pennylane_qiskit",
            "source_ecosystem": "qiskit",
            "stage": "9H",
            "target_ecosystem": "pennylane"
          },
          "name": null,
          "registers": {
            "classical": {
              "size": 2
            },
            "quantum": {
              "size": 2
            }
          }
        },
        "converted_target": {
          "cloud_access": false,
          "ecosystem": "pennylane",
          "full_plugin_parity_claim": false,
          "hardware_access": false,
          "measurements": [
            {
              "measurement": "probs",
              "wires": [
                0,
                1
              ]
            }
          ],
          "num_qubits": 2,
          "operations": [
            {
              "metadata_only": false,
              "operation": "Hadamard",
              "parameters": [],
              "wires": [
                0
              ]
            },
            {
              "metadata_only": false,
              "operation": "CNOT",
              "parameters": [],
              "wires": [
                0,
                1
              ]
            }
          ],
          "production_ready": false,
          "provenance": {
            "adapter": "quantumbridge.compat.pennylane_qiskit",
            "cloud_access": false,
            "hardware_access": false,
            "ibm_branding_copied": false,
            "official_endorsement": false,
            "pennylane_qiskit_source_copied": false,
            "pennylane_source_copied": false,
            "qiskit_source_copied": false,
            "source_code_copied": false,
            "stage": "9H",
            "token_read": false,
            "upstream_source_copied": false,
            "workflow": "qiskit_to_pennylane_spec"
          },
          "schema_version": "0.1",
          "source": "quantumbridge_ir",
          "token_read": false,
          "warnings": [
            "QuantumBridge PennyLane-Qiskit bridge support is a clean-room educational adapter. It is not a full PennyLane-Qiskit plugin replacement and does not provide complete Qiskit or PennyLane parity.",
            "Qiskit-to-PennyLane conversion currently supports a small basic-gate subset and may not preserve all advanced circuit semantics."
          ],
          "workflow": "qiskit_to_pennylane_spec"
        },
        "counts": {
          "00": 61,
          "11": 67
        },
        "data": null,
        "ecosystem": "pennylane_qiskit_bridge",
        "equivalence_status": null,
        "metadata": {
          "cloud_access": false,
          "full_pennylane_parity_claim": false,
          "full_plugin_parity_claim": false,
          "full_qiskit_parity_claim": false,
          "hardware_access": false,
          "production_ready": false,
          "supported_gate_subset": [
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
          "token_read": false,
          "workflow": "qiskit_to_pennylane_bridge_native"
        },
        "mode": "native_bridge",
        "native_implementation": true,
        "num_qubits": 2,
        "operation_count": 2,
        "production_ready": false,
        "provenance": {
          "adapter": "quantumbridge.compat.pennylane_qiskit",
          "cloud_access": false,
          "hardware_access": false,
          "ibm_branding_copied": false,
          "official_endorsement": false,
          "pennylane_qiskit_source_copied": false,
          "pennylane_source_copied": false,
          "qiskit_source_copied": false,
          "source_code_copied": false,
          "stage": "9H",
          "token_read": false,
          "upstream_source_copied": false,
          "workflow": "qiskit_to_pennylane_bridge_native"
        },
        "quantumbridge_version": null,
        "raw_type": "PennyLaneSpec",
        "schema_version": "0.1",
        "seed": 7,
        "shots": 128,
        "source_ecosystem": "qiskit",
        "statevector_probabilities": {
          "00": 0.4999999999999999,
          "11": 0.4999999999999999
        },
        "target_ecosystem": "pennylane",
        "tolerance": null,
        "unsupported_reason": null,
        "upstream_package": null,
        "upstream_version": null,
        "warnings": [
          "QuantumBridge PennyLane-Qiskit bridge support is a clean-room educational adapter. It is not a full PennyLane-Qiskit plugin replacement and does not provide complete Qiskit or PennyLane parity.",
          "Qiskit-to-PennyLane conversion currently supports a small basic-gate subset and may not preserve all advanced circuit semantics."
        ],
        "workflow": "qiskit_to_pennylane_bridge_native"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "status": "succeeded",
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for pennylane-qiskit; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow pennylane_qiskit.qiskit_to_pennylane is local-only: no cloud, token, credential, or hardware access.",
        "QuantumBridge PennyLane-Qiskit bridge support is a clean-room educational adapter. It is not a full PennyLane-Qiskit plugin replacement and does not provide complete Qiskit or PennyLane parity.",
        "Qiskit-to-PennyLane conversion currently supports a small basic-gate subset and may not preserve all advanced circuit semantics."
      ],
      "workflow_id": "pennylane_qiskit.qiskit_to_pennylane"
    },
    {
      "error": null,
      "execution_id": "studio-exec-000012",
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
        "result_provenance": {
          "adapter": "quantumbridge.compat.pennylane_qiskit",
          "cloud_access": false,
          "hardware_access": false,
          "ibm_branding_copied": false,
          "official_endorsement": false,
          "pennylane_qiskit_source_copied": false,
          "pennylane_source_copied": false,
          "qiskit_source_copied": false,
          "source_code_copied": false,
          "stage": "9H",
          "token_read": false,
          "upstream_source_copied": false,
          "workflow": "pennylane_to_qiskit_bridge_native"
        },
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "pennylane_qiskit.pennylane_to_qiskit"
      },
      "result": {
        "capability_level": 3,
        "circuit_summary": {
          "measurements": [],
          "num_bits": 0,
          "num_qubits": 2,
          "operations": [
            "h",
            "cx",
            "ry"
          ],
          "type": "QuantumBridgeCircuit"
        },
        "converted_ir": {
          "instructions": [
            {
              "controls": [],
              "metadata": {},
              "op": "h",
              "params": [],
              "targets": [
                0
              ]
            },
            {
              "controls": [
                0
              ],
              "metadata": {},
              "op": "cx",
              "params": [],
              "targets": [
                1
              ]
            },
            {
              "controls": [],
              "metadata": {},
              "op": "ry",
              "params": [
                0.125
              ],
              "targets": [
                1
              ]
            }
          ],
          "ir_version": "qb-ir-v0.1",
          "measurements": [],
          "metadata": {
            "bridge": "pennylane_qiskit",
            "source_ecosystem": "pennylane",
            "stage": "9H",
            "target_ecosystem": "qiskit"
          },
          "name": null,
          "registers": {
            "classical": {
              "size": 0
            },
            "quantum": {
              "size": 2
            }
          }
        },
        "converted_target": {
          "num_clbits": 0,
          "num_qubits": 2,
          "operations": [
            "h",
            "cx",
            "ry"
          ],
          "type": "QuantumCircuit"
        },
        "counts": {
          "00": 61,
          "11": 67
        },
        "data": null,
        "ecosystem": "pennylane_qiskit_bridge",
        "equivalence_status": null,
        "metadata": {
          "cloud_access": false,
          "full_pennylane_parity_claim": false,
          "full_plugin_parity_claim": false,
          "full_qiskit_parity_claim": false,
          "hardware_access": false,
          "production_ready": false,
          "supported_gate_subset": [
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
          "token_read": false,
          "workflow": "pennylane_to_qiskit_bridge_native"
        },
        "mode": "native_bridge",
        "native_implementation": true,
        "num_qubits": 2,
        "operation_count": 3,
        "production_ready": false,
        "provenance": {
          "adapter": "quantumbridge.compat.pennylane_qiskit",
          "cloud_access": false,
          "hardware_access": false,
          "ibm_branding_copied": false,
          "official_endorsement": false,
          "pennylane_qiskit_source_copied": false,
          "pennylane_source_copied": false,
          "qiskit_source_copied": false,
          "source_code_copied": false,
          "stage": "9H",
          "token_read": false,
          "upstream_source_copied": false,
          "workflow": "pennylane_to_qiskit_bridge_native"
        },
        "quantumbridge_version": null,
        "raw_type": "QiskitQuantumCircuit",
        "schema_version": "0.1",
        "seed": 7,
        "shots": 128,
        "source_ecosystem": "pennylane",
        "statevector_probabilities": {
          "00": 0.4980494168073322,
          "01": 0.0019505831926677367,
          "10": 0.0019505831926677367,
          "11": 0.4980494168073322
        },
        "target_ecosystem": "qiskit",
        "tolerance": null,
        "unsupported_reason": null,
        "upstream_package": null,
        "upstream_version": null,
        "warnings": [
          "QuantumBridge PennyLane-Qiskit bridge support is a clean-room educational adapter. It is not a full PennyLane-Qiskit plugin replacement and does not provide complete Qiskit or PennyLane parity.",
          "PennyLane-to-Qiskit conversion currently supports a small operation and measurement subset and may not preserve all device, transform, or gradient semantics."
        ],
        "workflow": "pennylane_to_qiskit_bridge_native"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "status": "succeeded",
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for pennylane-qiskit; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow pennylane_qiskit.pennylane_to_qiskit is local-only: no cloud, token, credential, or hardware access.",
        "QuantumBridge PennyLane-Qiskit bridge support is a clean-room educational adapter. It is not a full PennyLane-Qiskit plugin replacement and does not provide complete Qiskit or PennyLane parity.",
        "PennyLane-to-Qiskit conversion currently supports a small operation and measurement subset and may not preserve all device, transform, or gradient semantics."
      ],
      "workflow_id": "pennylane_qiskit.pennylane_to_qiskit"
    },
    {
      "error": null,
      "execution_id": "studio-exec-000013",
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
        "result_provenance": {},
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "mqt.core_like_circuit"
      },
      "result": {
        "native": {
          "capability_level": 3,
          "circuit_summary": {
            "measurement_count": 2,
            "num_bits": 2,
            "num_qubits": 2,
            "operation_count": 2,
            "supported_gates": [
              "cnot",
              "cx",
              "cz",
              "h",
              "measure",
              "p",
              "phase",
              "rx",
              "ry",
              "rz",
              "swap",
              "x",
              "y",
              "z"
            ]
          },
          "comparison": {},
          "counts": {},
          "decision_diagram_metadata": {},
          "depth_estimate": null,
          "ecosystem": "quantumbridge_native_mqt_compat",
          "final_layout": {},
          "initial_layout": {},
          "mapped_ir": null,
          "measurements": [
            {
              "bit": 0,
              "kind": "computational",
              "wire": 0
            },
            {
              "bit": 1,
              "kind": "computational",
              "wire": 1
            }
          ],
          "metadata": {
            "cloud_access": false,
            "hardware_access": false,
            "mqt_core_parity_claim": false,
            "token_read": false
          },
          "mode": "native_minimal",
          "native_implementation": true,
          "num_qubits": 2,
          "operations": [
            {
              "controls": [],
              "metadata": {},
              "name": "h",
              "params": [],
              "targets": [
                0
              ]
            },
            {
              "controls": [
                0
              ],
              "metadata": {},
              "name": "cx",
              "params": [],
              "targets": [
                1
              ]
            }
          ],
          "probabilities": {},
          "production_ready": false,
          "project": "mqt-core",
          "provenance": {
            "cloud_access": false,
            "copied_upstream_source": false,
            "full_replacement_claim": false,
            "hardware_access": false,
            "official_endorsement_claim": false,
            "production_parity_claim": false,
            "project": "mqt-core",
            "source": "quantumbridge_clean_room_native",
            "token_read": false,
            "workflow": "mqt_core_like_circuit_from_quantumbridge_ir"
          },
          "quantumbridge_version": null,
          "raw_type": "MQTCoreLikeDict",
          "schema_version": "0.1",
          "statevector": [],
          "swap_count": null,
          "topology": null,
          "unsupported_reason": null,
          "upstream_package": null,
          "upstream_version": null,
          "warnings": [
            "QuantumBridge MQT compatibility support is a clean-room educational adapter. It is not a full MQT Core, DDSIM, or QMAP replacement and does not provide production compiler, mapper, or simulator parity."
          ],
          "workflow": "mqt_core_like_circuit_from_quantumbridge_ir"
        },
        "qasm": "OPENQASM 2.0;\ninclude \"qelib1.inc\";\nqreg q[2];\ncreg c[2];\nh q[0];\ncx q[0],q[1];\nmeasure q[0] -> c[0];\nmeasure q[1] -> c[1];\n",
        "roundtrip_ir": {
          "instructions": [
            {
              "controls": [],
              "metadata": {},
              "op": "h",
              "params": [],
              "targets": [
                0
              ]
            },
            {
              "controls": [
                0
              ],
              "metadata": {},
              "op": "cx",
              "params": [],
              "targets": [
                1
              ]
            }
          ],
          "ir_version": "qb-ir-v0.1",
          "measurements": [
            {
              "bits": [
                0
              ],
              "kind": "computational",
              "wires": [
                0
              ]
            },
            {
              "bits": [
                1
              ],
              "kind": "computational",
              "wires": [
                1
              ]
            }
          ],
          "metadata": {
            "mqt_core_parity_claim": false,
            "qasm_subset": true
          },
          "name": null,
          "registers": {
            "classical": {
              "size": 2
            },
            "quantum": {
              "size": 2
            }
          }
        },
        "upstream": {
          "capability_level": 1,
          "circuit_summary": {},
          "comparison": {},
          "counts": {},
          "decision_diagram_metadata": {},
          "depth_estimate": null,
          "ecosystem": "mqt",
          "final_layout": {},
          "initial_layout": {},
          "mapped_ir": null,
          "measurements": [],
          "metadata": {
            "cloud_access": false,
            "hardware_access": false,
            "token_read": false,
            "upstream_passthrough": true
          },
          "mode": "upstream_passthrough",
          "native_implementation": false,
          "num_qubits": null,
          "operations": [],
          "probabilities": {},
          "production_ready": false,
          "project": "mqt",
          "provenance": {
            "cloud_access": false,
            "copied_upstream_source": false,
            "full_replacement_claim": false,
            "hardware_access": false,
            "official_endorsement_claim": false,
            "production_parity_claim": false,
            "project": "mqt",
            "source": "optional_upstream_passthrough_boundary",
            "token_read": false,
            "upstream_package": "mqt-core",
            "workflow": "upstream_mqt_core_passthrough"
          },
          "quantumbridge_version": null,
          "raw_type": "UnsupportedUpstreamMQT",
          "schema_version": "0.1",
          "statevector": [],
          "swap_count": null,
          "topology": null,
          "unsupported_reason": "optional upstream dependency unavailable: mqt-core",
          "upstream_package": "mqt-core",
          "upstream_version": null,
          "warnings": [
            "QuantumBridge MQT compatibility support is a clean-room educational adapter. It is not a full MQT Core, DDSIM, or QMAP replacement and does not provide production compiler, mapper, or simulator parity.",
            "Upstream passthrough requires optional MQT ecosystem packages."
          ],
          "workflow": "upstream_mqt_core_passthrough"
        }
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "status": "succeeded",
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
      "error": null,
      "execution_id": "studio-exec-000014",
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
        "result_provenance": {},
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "mqt.ddsim_like_simulation"
      },
      "result": {
        "comparison": {
          "capability_level": 3,
          "circuit_summary": {
            "measurement_count": 2,
            "num_bits": 2,
            "num_qubits": 2,
            "operation_count": 2
          },
          "comparison": {
            "comparable": true,
            "l1_probability_distance": 0.0,
            "stage9f_counts": {
              "00": 75,
              "11": 53
            },
            "stage9f_probabilities": {
              "00": 0.5859375,
              "11": 0.4140625
            }
          },
          "counts": {
            "00": 75,
            "11": 53
          },
          "decision_diagram_metadata": {
            "compression_hint": "repeated_amplitudes",
            "decision_diagram_parity_claim": false,
            "nonzero_amplitudes": 2,
            "norm": 0.9999999999999998,
            "normalized": true,
            "num_qubits": 2,
            "statevector_length": 4,
            "support_bitstrings": [
              "00",
              "11"
            ],
            "tolerance": 1e-12,
            "unique_amplitude_count": 1
          },
          "depth_estimate": null,
          "ecosystem": "mqt_comparison",
          "final_layout": {},
          "initial_layout": {},
          "mapped_ir": null,
          "measurements": [
            {
              "bit": 0,
              "kind": "computational",
              "wire": 0
            },
            {
              "bit": 1,
              "kind": "computational",
              "wire": 1
            }
          ],
          "metadata": {
            "cloud_access": false,
            "decision_diagram_parity_claim": false,
            "hardware_access": false,
            "production_simulator": false,
            "token_read": false
          },
          "mode": "comparison",
          "native_implementation": true,
          "num_qubits": 2,
          "operations": [
            {
              "controls": [],
              "metadata": {},
              "name": "h",
              "params": [],
              "targets": [
                0
              ]
            },
            {
              "controls": [
                0
              ],
              "metadata": {},
              "name": "cx",
              "params": [],
              "targets": [
                1
              ]
            }
          ],
          "probabilities": {
            "00": 0.5859375,
            "11": 0.4140625
          },
          "production_ready": false,
          "project": "mqt-ddsim",
          "provenance": {
            "cloud_access": false,
            "copied_upstream_source": false,
            "full_replacement_claim": false,
            "hardware_access": false,
            "official_endorsement_claim": false,
            "production_parity_claim": false,
            "project": "mqt-ddsim",
            "source": "quantumbridge_clean_room_native",
            "token_read": false,
            "workflow": "ddsim_like_stage9f_comparison"
          },
          "quantumbridge_version": null,
          "raw_type": "QuantumBridgeDDSIMLikeComparison",
          "schema_version": "0.1",
          "statevector": [],
          "swap_count": null,
          "topology": null,
          "unsupported_reason": null,
          "upstream_package": null,
          "upstream_version": null,
          "warnings": [
            "QuantumBridge MQT compatibility support is a clean-room educational adapter. It is not a full MQT Core, DDSIM, or QMAP replacement and does not provide production compiler, mapper, or simulator parity.",
            "Native DDSIM-like support uses QuantumBridge educational simulation plus decision-diagram-inspired metadata. It is not a full decision-diagram simulator."
          ],
          "workflow": "ddsim_like_stage9f_comparison"
        },
        "counts": {
          "capability_level": 3,
          "circuit_summary": {
            "measurement_count": 2,
            "num_bits": 2,
            "num_qubits": 2,
            "operation_count": 2
          },
          "comparison": {},
          "counts": {
            "00": 75,
            "11": 53
          },
          "decision_diagram_metadata": {
            "compression_hint": "repeated_amplitudes",
            "decision_diagram_parity_claim": false,
            "nonzero_amplitudes": 2,
            "norm": 0.9999999999999998,
            "normalized": true,
            "num_qubits": 2,
            "statevector_length": 4,
            "support_bitstrings": [
              "00",
              "11"
            ],
            "tolerance": 1e-12,
            "unique_amplitude_count": 1
          },
          "depth_estimate": null,
          "ecosystem": "quantumbridge_native_mqt_compat",
          "final_layout": {},
          "initial_layout": {},
          "mapped_ir": null,
          "measurements": [
            {
              "bit": 0,
              "kind": "computational",
              "wire": 0
            },
            {
              "bit": 1,
              "kind": "computational",
              "wire": 1
            }
          ],
          "metadata": {
            "backend": "quantumbridge_native_qasm",
            "cloud_access": false,
            "decision_diagram_parity_claim": false,
            "hardware_access": false,
            "production_simulator": false,
            "seed": 11,
            "shots": 128,
            "token_read": false
          },
          "mode": "native_minimal",
          "native_implementation": true,
          "num_qubits": 2,
          "operations": [
            {
              "controls": [],
              "metadata": {},
              "name": "h",
              "params": [],
              "targets": [
                0
              ]
            },
            {
              "controls": [
                0
              ],
              "metadata": {},
              "name": "cx",
              "params": [],
              "targets": [
                1
              ]
            }
          ],
          "probabilities": {
            "00": 0.5859375,
            "11": 0.4140625
          },
          "production_ready": false,
          "project": "mqt-ddsim",
          "provenance": {
            "cloud_access": false,
            "copied_upstream_source": false,
            "full_replacement_claim": false,
            "hardware_access": false,
            "official_endorsement_claim": false,
            "production_parity_claim": false,
            "project": "mqt-ddsim",
            "source": "quantumbridge_clean_room_native",
            "token_read": false,
            "workflow": "ddsim_like_counts_native"
          },
          "quantumbridge_version": null,
          "raw_type": "QuantumBridgeDDSIMLikeCounts",
          "schema_version": "0.1",
          "statevector": [
            {
              "imag": 0.0,
              "real": 0.7071067811865475
            },
            {
              "imag": 0.0,
              "real": 0.0
            },
            {
              "imag": 0.0,
              "real": 0.0
            },
            {
              "imag": 0.0,
              "real": 0.7071067811865475
            }
          ],
          "swap_count": null,
          "topology": null,
          "unsupported_reason": null,
          "upstream_package": null,
          "upstream_version": null,
          "warnings": [
            "QuantumBridge MQT compatibility support is a clean-room educational adapter. It is not a full MQT Core, DDSIM, or QMAP replacement and does not provide production compiler, mapper, or simulator parity.",
            "Native DDSIM-like support uses QuantumBridge educational simulation plus decision-diagram-inspired metadata. It is not a full decision-diagram simulator."
          ],
          "workflow": "ddsim_like_counts_native"
        },
        "statevector": {
          "capability_level": 3,
          "circuit_summary": {
            "measurement_count": 2,
            "num_bits": 2,
            "num_qubits": 2,
            "operation_count": 2
          },
          "comparison": {},
          "counts": {},
          "decision_diagram_metadata": {
            "compression_hint": "repeated_amplitudes",
            "decision_diagram_parity_claim": false,
            "nonzero_amplitudes": 2,
            "norm": 0.9999999999999998,
            "normalized": true,
            "num_qubits": 2,
            "statevector_length": 4,
            "support_bitstrings": [
              "00",
              "11"
            ],
            "tolerance": 1e-12,
            "unique_amplitude_count": 1
          },
          "depth_estimate": null,
          "ecosystem": "quantumbridge_native_mqt_compat",
          "final_layout": {},
          "initial_layout": {},
          "mapped_ir": null,
          "measurements": [
            {
              "bit": 0,
              "kind": "computational",
              "wire": 0
            },
            {
              "bit": 1,
              "kind": "computational",
              "wire": 1
            }
          ],
          "metadata": {
            "backend": "quantumbridge_native_statevector",
            "cloud_access": false,
            "decision_diagram_parity_claim": false,
            "hardware_access": false,
            "production_simulator": false,
            "token_read": false
          },
          "mode": "native_minimal",
          "native_implementation": true,
          "num_qubits": 2,
          "operations": [
            {
              "controls": [],
              "metadata": {},
              "name": "h",
              "params": [],
              "targets": [
                0
              ]
            },
            {
              "controls": [
                0
              ],
              "metadata": {},
              "name": "cx",
              "params": [],
              "targets": [
                1
              ]
            }
          ],
          "probabilities": {
            "00": 0.4999999999999999,
            "11": 0.4999999999999999
          },
          "production_ready": false,
          "project": "mqt-ddsim",
          "provenance": {
            "cloud_access": false,
            "copied_upstream_source": false,
            "full_replacement_claim": false,
            "hardware_access": false,
            "official_endorsement_claim": false,
            "production_parity_claim": false,
            "project": "mqt-ddsim",
            "source": "quantumbridge_clean_room_native",
            "token_read": false,
            "workflow": "ddsim_like_statevector_native"
          },
          "quantumbridge_version": null,
          "raw_type": "QuantumBridgeDDSIMLikeStatevector",
          "schema_version": "0.1",
          "statevector": [
            {
              "imag": 0.0,
              "real": 0.7071067811865475
            },
            {
              "imag": 0.0,
              "real": 0.0
            },
            {
              "imag": 0.0,
              "real": 0.0
            },
            {
              "imag": 0.0,
              "real": 0.7071067811865475
            }
          ],
          "swap_count": null,
          "topology": null,
          "unsupported_reason": null,
          "upstream_package": null,
          "upstream_version": null,
          "warnings": [
            "QuantumBridge MQT compatibility support is a clean-room educational adapter. It is not a full MQT Core, DDSIM, or QMAP replacement and does not provide production compiler, mapper, or simulator parity.",
            "Native DDSIM-like support uses QuantumBridge educational simulation plus decision-diagram-inspired metadata. It is not a full decision-diagram simulator."
          ],
          "workflow": "ddsim_like_statevector_native"
        },
        "upstream": {
          "capability_level": 1,
          "circuit_summary": {},
          "comparison": {},
          "counts": {},
          "decision_diagram_metadata": {},
          "depth_estimate": null,
          "ecosystem": "mqt",
          "final_layout": {},
          "initial_layout": {},
          "mapped_ir": null,
          "measurements": [],
          "metadata": {
            "cloud_access": false,
            "hardware_access": false,
            "token_read": false,
            "upstream_passthrough": true
          },
          "mode": "upstream_passthrough",
          "native_implementation": false,
          "num_qubits": null,
          "operations": [],
          "probabilities": {},
          "production_ready": false,
          "project": "mqt",
          "provenance": {
            "cloud_access": false,
            "copied_upstream_source": false,
            "full_replacement_claim": false,
            "hardware_access": false,
            "official_endorsement_claim": false,
            "production_parity_claim": false,
            "project": "mqt",
            "source": "optional_upstream_passthrough_boundary",
            "token_read": false,
            "upstream_package": "mqt-ddsim",
            "workflow": "upstream_mqt_ddsim_passthrough"
          },
          "quantumbridge_version": null,
          "raw_type": "UnsupportedUpstreamMQT",
          "schema_version": "0.1",
          "statevector": [],
          "swap_count": null,
          "topology": null,
          "unsupported_reason": "optional upstream dependency unavailable: mqt-ddsim",
          "upstream_package": "mqt-ddsim",
          "upstream_version": null,
          "warnings": [
            "QuantumBridge MQT compatibility support is a clean-room educational adapter. It is not a full MQT Core, DDSIM, or QMAP replacement and does not provide production compiler, mapper, or simulator parity.",
            "Upstream passthrough requires optional MQT ecosystem packages."
          ],
          "workflow": "upstream_mqt_ddsim_passthrough"
        }
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "status": "succeeded",
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
      "error": null,
      "execution_id": "studio-exec-000015",
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
        "result_provenance": {},
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "torchquantum.layer_native"
      },
      "result": {
        "native": {
          "accuracy": null,
          "batch_size": 1,
          "capability_level": 3,
          "circuit_ir": {
            "metadata": {
              "cloud_access": false,
              "hardware_access": false,
              "token_read": false,
              "torchquantum_like_layer": {
                "depth": 1,
                "feature_dim": 2,
                "num_qubits": 2,
                "num_weights": 4,
                "type": "angle_encoder_plus_ry_rz_entangler"
              }
            },
            "num_qubits": 2,
            "operation_count": 9,
            "operations": [
              {
                "controls": [],
                "name": "ry",
                "targets": [
                  0
                ]
              },
              {
                "controls": [],
                "name": "rz",
                "targets": [
                  0
                ]
              },
              {
                "controls": [],
                "name": "ry",
                "targets": [
                  1
                ]
              },
              {
                "controls": [],
                "name": "rz",
                "targets": [
                  1
                ]
              },
              {
                "controls": [],
                "name": "ry",
                "targets": [
                  0
                ]
              },
              {
                "controls": [],
                "name": "rz",
                "targets": [
                  0
                ]
              },
              {
                "controls": [],
                "name": "ry",
                "targets": [
                  1
                ]
              },
              {
                "controls": [],
                "name": "rz",
                "targets": [
                  1
                ]
              },
              {
                "controls": [
                  0
                ],
                "name": "cx",
                "targets": [
                  1
                ]
              }
            ]
          },
          "dataset_summary": {
            "high_risk_decision_use": false,
            "real_user_data": false,
            "single_sample": true
          },
          "ecosystem": "quantumbridge_native_torchquantum_compat",
          "feature_dim": 2,
          "forward_outputs": [
            0.17335925878090586
          ],
          "loss": null,
          "metadata": {
            "cloud_access": false,
            "expectation_z_wire0": 0.6532814824381882,
            "full_torchquantum_replacement_claim": false,
            "hardware_access": false,
            "high_risk_decision_use": false,
            "production_qml_claim": false,
            "token_read": false
          },
          "mode": "native_minimal",
          "native_implementation": true,
          "num_qubits": 2,
          "predictions": [
            0
          ],
          "probabilities": [
            {
              "00": 0.8210669490340056,
              "01": 0.14087281722163775,
              "10": 0.005573792185088497,
              "11": 0.03248644155926812
            }
          ],
          "production_ready": false,
          "provenance": {
            "adapter": "quantumbridge.compat.torchquantum",
            "cloud_access": false,
            "copied_upstream_source": false,
            "full_replacement_claim": false,
            "hardware_access": false,
            "high_risk_decision_claim": false,
            "official_endorsement_claim": false,
            "production_parity_claim": false,
            "source": "quantumbridge_clean_room_native",
            "stage": "9K",
            "token_read": false,
            "workflow": "torchquantum_like_layer_forward_native"
          },
          "quantumbridge_version": null,
          "raw_type": "QuantumBridgeTorchQuantumLikeLayer",
          "schema_version": "0.1",
          "tensor_backend": "numpy",
          "training_trace": [],
          "unsupported_reason": null,
          "upstream_package": null,
          "upstream_version": null,
          "warnings": [
            "QuantumBridge TorchQuantum compatibility support is a clean-room educational adapter. It is not a full TorchQuantum or PyTorch replacement and does not provide production QML training parity.",
            "QuantumBridge QML examples are not intended for medical, financial, employment, identity, safety, or other high-risk automated decisions.",
            "Native TorchQuantum-like layers are minimal educational workflows for small toy datasets and small circuits."
          ],
          "weights": [
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "workflow": "torchquantum_like_layer_forward_native"
        },
        "upstream": {
          "accuracy": null,
          "batch_size": null,
          "capability_level": 0,
          "circuit_ir": {},
          "dataset_summary": {},
          "ecosystem": "torchquantum",
          "feature_dim": null,
          "forward_outputs": [],
          "loss": null,
          "metadata": {
            "args_count": 0,
            "cloud_access": false,
            "dependency": {
              "available": false,
              "cloud_access": false,
              "hardware_access": false,
              "package": "torchquantum",
              "required_by_default": false,
              "token_read": false,
              "version": null
            },
            "hardware_access": false,
            "kwargs": [],
            "token_read": false
          },
          "mode": "upstream_passthrough",
          "native_implementation": false,
          "num_qubits": null,
          "predictions": [],
          "probabilities": [],
          "production_ready": false,
          "provenance": {
            "adapter": "quantumbridge.compat.torchquantum",
            "cloud_access": false,
            "copied_upstream_source": false,
            "full_replacement_claim": false,
            "hardware_access": false,
            "high_risk_decision_claim": false,
            "mode": "upstream_passthrough",
            "official_endorsement_claim": false,
            "production_parity_claim": false,
            "source": "optional_upstream_passthrough_boundary",
            "stage": "9K",
            "token_read": false,
            "upstream_package": "torchquantum",
            "workflow": "upstream_torchquantum_passthrough"
          },
          "quantumbridge_version": null,
          "raw_type": null,
          "schema_version": "0.1",
          "tensor_backend": null,
          "training_trace": [],
          "unsupported_reason": "optional torchquantum package is not installed",
          "upstream_package": "torchquantum",
          "upstream_version": null,
          "warnings": [
            "QuantumBridge TorchQuantum compatibility support is a clean-room educational adapter. It is not a full TorchQuantum or PyTorch replacement and does not provide production QML training parity.",
            "QuantumBridge QML examples are not intended for medical, financial, employment, identity, safety, or other high-risk automated decisions.",
            "Upstream passthrough requires optional TorchQuantum ecosystem packages."
          ],
          "weights": [],
          "workflow": "upstream_torchquantum_passthrough"
        }
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "status": "succeeded",
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
      "error": null,
      "execution_id": "studio-exec-000016",
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
        "result_provenance": {
          "cloud_access": false,
          "copied_upstream_source": false,
          "full_replacement_claim": false,
          "hardware_access": false,
          "official_endorsement_claim": false,
          "production_backend_claim": false,
          "production_parity_claim": false,
          "project": "qos-uqci",
          "source": "quantumbridge_clean_room_native",
          "token_read": false,
          "workflow": "qos_uqci_mock_runtime"
        },
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "qos_uqci.mock_runtime"
      },
      "result": {
        "calset": {
          "calibration_type": "offline_mock",
          "cloud_access": false,
          "generated_from_hardware": false,
          "hardware_access": false,
          "qubits": [
            {
              "id": 0,
              "readout_error": 0.0,
              "t1_us": null,
              "t2_us": null
            },
            {
              "id": 1,
              "readout_error": 0.0,
              "t1_us": null,
              "t2_us": null
            }
          ],
          "schema_version": "0.1",
          "token_read": false
        },
        "capability_level": 3,
        "counts": {
          "00": 61,
          "11": 67
        },
        "device_spec": {
          "backend_type": "offline_mock",
          "basis_gates": [
            "x",
            "y",
            "z",
            "h",
            "rx",
            "ry",
            "rz",
            "phase",
            "cx",
            "cz",
            "swap"
          ],
          "cloud_access": false,
          "coupling_map": [
            [
              0,
              1
            ]
          ],
          "hardware_access": false,
          "name": "quantumbridge_mock_qos_backend",
          "num_qubits": 2,
          "production_backend": false,
          "schema_version": "0.1",
          "token_read": false
        },
        "ecosystem": "quantumbridge_native_qos_uqci_compat",
        "job_spec": {
          "backend_name": "quantumbridge_mock_qos_backend",
          "calset": {
            "calibration_type": "offline_mock",
            "cloud_access": false,
            "generated_from_hardware": false,
            "hardware_access": false,
            "qubits": [
              {
                "id": 0,
                "readout_error": 0.0,
                "t1_us": null,
                "t2_us": null
              },
              {
                "id": 1,
                "readout_error": 0.0,
                "t1_us": null,
                "t2_us": null
              }
            ],
            "schema_version": "0.1",
            "token_read": false
          },
          "cloud_access": false,
          "device_spec": {
            "backend_type": "offline_mock",
            "basis_gates": [
              "x",
              "y",
              "z",
              "h",
              "rx",
              "ry",
              "rz",
              "phase",
              "cx",
              "cz",
              "swap"
            ],
            "cloud_access": false,
            "coupling_map": [
              [
                0,
                1
              ]
            ],
            "hardware_access": false,
            "name": "quantumbridge_mock_qos_backend",
            "num_qubits": 2,
            "production_backend": false,
            "schema_version": "0.1",
            "token_read": false
          },
          "execution_mode": "offline_mock",
          "hardware_access": false,
          "job_id": "qb-qos-uqci-qos_uqci_bell",
          "manifest": {
            "artifact_count": 3,
            "artifacts": [
              "uqci_ir",
              "openqasm_compatibility_artifact",
              "mock_result"
            ],
            "cloud_access": false,
            "hardware_access": false,
            "job_id": "qb-qos-uqci-qos_uqci_bell",
            "manifest_type": "qos_uqci_offline_mock",
            "production_runtime": false,
            "schema_version": "0.1",
            "token_read": false
          },
          "official_endorsement_claim": false,
          "openqasm_compatibility_artifact": {
            "canonical_ir": "qos_uqci_clean_room_ir",
            "cloud_access": false,
            "format": "openqasm2_compatibility_artifact",
            "generated": true,
            "hardware_access": false,
            "qasm": "OPENQASM 2.0;\ninclude \"qelib1.inc\";\nqreg q[2];\ncreg c[2];\nh q[0];\ncx q[0],q[1];\nmeasure q[0] -> c[0];\nmeasure q[1] -> c[1];\n",
            "schema_version": "0.1",
            "token_read": false
          },
          "production_runtime": false,
          "provenance": {
            "cloud_access": false,
            "copied_upstream_source": false,
            "full_replacement_claim": false,
            "hardware_access": false,
            "official_endorsement_claim": false,
            "production_backend_claim": false,
            "production_parity_claim": false,
            "project": "qos-uqci",
            "source": "quantumbridge_clean_room_native",
            "token_read": false,
            "workflow": "build_qos_uqci_job_spec"
          },
          "schema_version": "0.1",
          "seed": 21,
          "shots": 128,
          "target": "qos_uqci",
          "token_read": false,
          "uqci_ir": {
            "ir_type": "qos_uqci_clean_room_ir",
            "measurements": [
              {
                "bit": 0,
                "kind": "computational",
                "wire": 0
              },
              {
                "bit": 1,
                "kind": "computational",
                "wire": 1
              }
            ],
            "metadata": {
              "cloud_access": false,
              "hardware_access": false,
              "production_runtime_claim": false,
              "token_read": false
            },
            "name": "qos_uqci_bell",
            "num_clbits": 2,
            "num_qubits": 2,
            "operations": [
              {
                "controls": [],
                "gate": "h",
                "id": "op_0",
                "parameters": [],
                "targets": [
                  0
                ]
              },
              {
                "controls": [
                  0
                ],
                "gate": "cx",
                "id": "op_1",
                "parameters": [],
                "targets": [
                  1
                ]
              }
            ],
            "provenance": {
              "cloud_access": false,
              "copied_upstream_source": false,
              "full_replacement_claim": false,
              "hardware_access": false,
              "official_endorsement_claim": false,
              "production_backend_claim": false,
              "production_parity_claim": false,
              "project": "qos-uqci",
              "source": "quantumbridge_clean_room_native",
              "token_read": false,
              "workflow": "quantumbridge_ir_to_uqci_ir"
            },
            "schema_version": "0.1",
            "source": "quantumbridge_ir",
            "warnings": [
              "QuantumBridge QOS-UQCI compatibility support is a clean-room offline adapter. It is not a production QOS runtime and does not access real cloud services or hardware.",
              "Mock backend execution uses QuantumBridge local simulation and is not real quantum hardware execution.",
              "No token or credential is read by this workflow."
            ]
          },
          "warnings": [
            "QuantumBridge QOS-UQCI compatibility support is a clean-room offline adapter. It is not a production QOS runtime and does not access real cloud services or hardware.",
            "Mock backend execution uses QuantumBridge local simulation and is not real quantum hardware execution.",
            "No token or credential is read by this workflow."
          ]
        },
        "manifest": {
          "artifact_count": 3,
          "artifacts": [
            "uqci_ir",
            "openqasm_compatibility_artifact",
            "mock_result"
          ],
          "cloud_access": false,
          "hardware_access": false,
          "job_id": "qb-qos-uqci-qos_uqci_bell",
          "manifest_type": "qos_uqci_offline_mock",
          "production_runtime": false,
          "schema_version": "0.1",
          "token_read": false
        },
        "metadata": {
          "backend_name": "quantumbridge_mock_qos_backend",
          "cloud_access": false,
          "hardware_access": false,
          "official_endorsement_claim": false,
          "production_backend": false,
          "token_read": false
        },
        "mode": "native_mock",
        "native_implementation": true,
        "openqasm_artifact": {
          "canonical_ir": "qos_uqci_clean_room_ir",
          "cloud_access": false,
          "format": "openqasm2_compatibility_artifact",
          "generated": true,
          "hardware_access": false,
          "qasm": "OPENQASM 2.0;\ninclude \"qelib1.inc\";\nqreg q[2];\ncreg c[2];\nh q[0];\ncx q[0],q[1];\nmeasure q[0] -> c[0];\nmeasure q[1] -> c[1];\n",
          "schema_version": "0.1",
          "token_read": false
        },
        "payload": {
          "ir_type": "qos_uqci_clean_room_ir",
          "measurements": [
            {
              "bit": 0,
              "kind": "computational",
              "wire": 0
            },
            {
              "bit": 1,
              "kind": "computational",
              "wire": 1
            }
          ],
          "metadata": {
            "cloud_access": false,
            "hardware_access": false,
            "production_runtime_claim": false,
            "token_read": false
          },
          "name": "qos_uqci_bell",
          "num_clbits": 2,
          "num_qubits": 2,
          "operations": [
            {
              "controls": [],
              "gate": "h",
              "id": "op_0",
              "parameters": [],
              "targets": [
                0
              ]
            },
            {
              "controls": [
                0
              ],
              "gate": "cx",
              "id": "op_1",
              "parameters": [],
              "targets": [
                1
              ]
            }
          ],
          "provenance": {
            "cloud_access": false,
            "copied_upstream_source": false,
            "full_replacement_claim": false,
            "hardware_access": false,
            "official_endorsement_claim": false,
            "production_backend_claim": false,
            "production_parity_claim": false,
            "project": "qos-uqci",
            "source": "quantumbridge_clean_room_native",
            "token_read": false,
            "workflow": "quantumbridge_ir_to_uqci_ir"
          },
          "schema_version": "0.1",
          "source": "quantumbridge_ir",
          "warnings": [
            "QuantumBridge QOS-UQCI compatibility support is a clean-room offline adapter. It is not a production QOS runtime and does not access real cloud services or hardware.",
            "Mock backend execution uses QuantumBridge local simulation and is not real quantum hardware execution.",
            "No token or credential is read by this workflow."
          ]
        },
        "probabilities": {
          "00": 0.4765625,
          "11": 0.5234375
        },
        "production_ready": false,
        "project": "qos-uqci",
        "provenance": {
          "cloud_access": false,
          "copied_upstream_source": false,
          "full_replacement_claim": false,
          "hardware_access": false,
          "official_endorsement_claim": false,
          "production_backend_claim": false,
          "production_parity_claim": false,
          "project": "qos-uqci",
          "source": "quantumbridge_clean_room_native",
          "token_read": false,
          "workflow": "qos_uqci_mock_runtime"
        },
        "quantumbridge_version": null,
        "raw_type": "QuantumBridgeQOSUQCIMockRuntime",
        "schema_version": "0.1",
        "seed": 21,
        "shots": 128,
        "unsupported_reason": null,
        "upstream_package": null,
        "upstream_version": null,
        "warnings": [
          "QuantumBridge QOS-UQCI compatibility support is a clean-room offline adapter. It is not a production QOS runtime and does not access real cloud services or hardware.",
          "Mock backend execution uses QuantumBridge local simulation and is not real quantum hardware execution.",
          "No token or credential is read by this workflow."
        ],
        "workflow": "qos_uqci_mock_runtime"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "status": "succeeded",
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for qos-uqci; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow qos_uqci.mock_runtime is local-only: no cloud, token, credential, or hardware access.",
        "QuantumBridge QOS-UQCI compatibility support is a clean-room offline adapter. It is not a production QOS runtime and does not access real cloud services or hardware.",
        "Mock backend execution uses QuantumBridge local simulation and is not real quantum hardware execution.",
        "No token or credential is read by this workflow."
      ],
      "workflow_id": "qos_uqci.mock_runtime"
    },
    {
      "error": null,
      "execution_id": "studio-exec-000017",
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
        "result_provenance": {
          "cloud_access": false,
          "copied_upstream_source": false,
          "full_replacement_claim": false,
          "hardware_access": false,
          "official_endorsement_claim": false,
          "production_backend_claim": false,
          "production_parity_claim": false,
          "project": "quafu",
          "source": "quantumbridge_clean_room_native",
          "token_read": false,
          "workflow": "quafu_mock_backend"
        },
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "quafu.mock_backend"
      },
      "result": {
        "calset": {},
        "capability_level": 3,
        "counts": {
          "00": 60,
          "11": 68
        },
        "device_spec": {},
        "ecosystem": "quantumbridge_native_quafu_compat",
        "job_spec": {
          "backend_name": "quantumbridge_mock_quafu_backend",
          "cloud_access": false,
          "execution_mode": "offline_mock",
          "hardware_access": false,
          "job_id": "qb-quafu-quafu_bell",
          "official_endorsement_claim": false,
          "payload": {
            "gates": [
              {
                "controls": [],
                "index": 0,
                "name": "h",
                "params": [],
                "targets": [
                  0
                ]
              },
              {
                "controls": [
                  0
                ],
                "index": 1,
                "name": "cx",
                "params": [],
                "targets": [
                  1
                ]
              }
            ],
            "measurements": [
              {
                "bit": 0,
                "kind": "computational",
                "wire": 0
              },
              {
                "bit": 1,
                "kind": "computational",
                "wire": 1
              }
            ],
            "metadata": {
              "cloud_access": false,
              "hardware_access": false,
              "official_endorsement_claim": false,
              "production_backend_claim": false,
              "token_read": false
            },
            "name": "quafu_bell",
            "num_clbits": 2,
            "num_qubits": 2,
            "payload_type": "quafu_clean_room_payload",
            "provenance": {
              "cloud_access": false,
              "copied_upstream_source": false,
              "full_replacement_claim": false,
              "hardware_access": false,
              "official_endorsement_claim": false,
              "production_backend_claim": false,
              "production_parity_claim": false,
              "project": "quafu",
              "source": "quantumbridge_clean_room_native",
              "token_read": false,
              "workflow": "quantumbridge_ir_to_quafu_payload"
            },
            "schema_version": "0.1",
            "source": "quantumbridge_ir",
            "warnings": [
              "QuantumBridge Quafu compatibility support is a clean-room offline adapter. It is not a full pyquafu replacement, official Quafu integration, or production backend.",
              "Mock backend execution uses QuantumBridge local simulation and is not real quantum hardware execution.",
              "No token or credential is read by this workflow."
            ]
          },
          "production_backend": false,
          "provenance": {
            "cloud_access": false,
            "copied_upstream_source": false,
            "full_replacement_claim": false,
            "hardware_access": false,
            "official_endorsement_claim": false,
            "production_backend_claim": false,
            "production_parity_claim": false,
            "project": "quafu",
            "source": "quantumbridge_clean_room_native",
            "token_read": false,
            "workflow": "build_quafu_job_spec"
          },
          "schema_version": "0.1",
          "seed": 23,
          "shots": 128,
          "target": "quafu",
          "token_read": false,
          "warnings": [
            "QuantumBridge Quafu compatibility support is a clean-room offline adapter. It is not a full pyquafu replacement, official Quafu integration, or production backend.",
            "Mock backend execution uses QuantumBridge local simulation and is not real quantum hardware execution.",
            "No token or credential is read by this workflow."
          ]
        },
        "manifest": {},
        "metadata": {
          "backend_name": "quantumbridge_mock_quafu_backend",
          "cloud_access": false,
          "hardware_access": false,
          "official_endorsement_claim": false,
          "production_backend": false,
          "token_read": false
        },
        "mode": "native_mock",
        "native_implementation": true,
        "openqasm_artifact": {},
        "payload": {
          "gates": [
            {
              "controls": [],
              "index": 0,
              "name": "h",
              "params": [],
              "targets": [
                0
              ]
            },
            {
              "controls": [
                0
              ],
              "index": 1,
              "name": "cx",
              "params": [],
              "targets": [
                1
              ]
            }
          ],
          "measurements": [
            {
              "bit": 0,
              "kind": "computational",
              "wire": 0
            },
            {
              "bit": 1,
              "kind": "computational",
              "wire": 1
            }
          ],
          "metadata": {
            "cloud_access": false,
            "hardware_access": false,
            "official_endorsement_claim": false,
            "production_backend_claim": false,
            "token_read": false
          },
          "name": "quafu_bell",
          "num_clbits": 2,
          "num_qubits": 2,
          "payload_type": "quafu_clean_room_payload",
          "provenance": {
            "cloud_access": false,
            "copied_upstream_source": false,
            "full_replacement_claim": false,
            "hardware_access": false,
            "official_endorsement_claim": false,
            "production_backend_claim": false,
            "production_parity_claim": false,
            "project": "quafu",
            "source": "quantumbridge_clean_room_native",
            "token_read": false,
            "workflow": "quantumbridge_ir_to_quafu_payload"
          },
          "schema_version": "0.1",
          "source": "quantumbridge_ir",
          "warnings": [
            "QuantumBridge Quafu compatibility support is a clean-room offline adapter. It is not a full pyquafu replacement, official Quafu integration, or production backend.",
            "Mock backend execution uses QuantumBridge local simulation and is not real quantum hardware execution.",
            "No token or credential is read by this workflow."
          ]
        },
        "probabilities": {
          "00": 0.46875,
          "11": 0.53125
        },
        "production_ready": false,
        "project": "quafu",
        "provenance": {
          "cloud_access": false,
          "copied_upstream_source": false,
          "full_replacement_claim": false,
          "hardware_access": false,
          "official_endorsement_claim": false,
          "production_backend_claim": false,
          "production_parity_claim": false,
          "project": "quafu",
          "source": "quantumbridge_clean_room_native",
          "token_read": false,
          "workflow": "quafu_mock_backend"
        },
        "quantumbridge_version": null,
        "raw_type": "QuantumBridgeQuafuMockBackend",
        "schema_version": "0.1",
        "seed": 23,
        "shots": 128,
        "unsupported_reason": null,
        "upstream_package": null,
        "upstream_version": null,
        "warnings": [
          "QuantumBridge Quafu compatibility support is a clean-room offline adapter. It is not a full pyquafu replacement, official Quafu integration, or production backend.",
          "Mock backend execution uses QuantumBridge local simulation and is not real quantum hardware execution.",
          "No token or credential is read by this workflow."
        ],
        "workflow": "quafu_mock_backend"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "status": "succeeded",
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for quafu; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow quafu.mock_backend is local-only: no cloud, token, credential, or hardware access.",
        "QuantumBridge Quafu compatibility support is a clean-room offline adapter. It is not a full pyquafu replacement, official Quafu integration, or production backend.",
        "Mock backend execution uses QuantumBridge local simulation and is not real quantum hardware execution.",
        "No token or credential is read by this workflow."
      ],
      "workflow_id": "quafu.mock_backend"
    },
    {
      "error": null,
      "execution_id": "studio-exec-000018",
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
        "result_provenance": {
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
        "source": "quantumbridge",
        "token_access": false,
        "workflow_id": "benchpress.basic_suite"
      },
      "result": {
        "capability_level": 2,
        "case_id": "studio_benchpress_basic",
        "case_name": "studio_benchpress_basic",
        "category": "suite",
        "ecosystem": "quantumbridge_native_benchmarking",
        "elapsed_seconds": 0.0004559169999538426,
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
              "elapsed_seconds": 0.0001445000000330765,
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
              "elapsed_seconds": 0.0002067499999611755,
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
              "elapsed_seconds": 6.508299998131406e-05,
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
        "workflow": "studio_benchpress_basic"
      },
      "schema_version": "quantumbridge-studio-api-v0.1",
      "status": "succeeded",
      "unsupported_reason": null,
      "warnings": [
        "QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.",
        "Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.",
        "This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.",
        "This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.",
        "QuantumBridge Studio uses clean-room local metadata for benchpress; no third-party source, UI, prose, or branding is copied.",
        "Studio workflow benchpress.basic_suite is local-only: no cloud, token, credential, or hardware access.",
        "QuantumBridge Benchpress compatibility support is a clean-room educational benchmarking adapter. It is not a full Benchpress replacement and does not provide production benchmark parity.",
        "QuantumBridge benchmark results are deterministic local validation results for small educational workloads, not official performance rankings."
      ],
      "workflow_id": "benchpress.basic_suite"
    }
  ],
  "sampled_workflows": [
    "aer.statevector_native",
    "aer.qasm_counts_native",
    "aer.noisy_counts_native",
    "finance.portfolio_optimization_native",
    "optimization.quadratic_program_native",
    "algorithms.qaoa_native",
    "algorithms.grover_native",
    "nature.h2_native",
    "ml.quantum_kernel_native",
    "mitiq.zne_native",
    "pennylane_qiskit.qiskit_to_pennylane",
    "pennylane_qiskit.pennylane_to_qiskit",
    "mqt.core_like_circuit",
    "mqt.ddsim_like_simulation",
    "torchquantum.layer_native",
    "qos_uqci.mock_runtime",
    "quafu.mock_backend",
    "benchpress.basic_suite"
  ],
  "schema_version": "quantumbridge-studio-frontend-seed-v0.1",
  "section": "results",
  "source": "quantumbridge.studio.backend",
  "warnings": [
    "Local prototype seed data only.",
    "No production UI claim.",
    "No cloud execution, credential reading, or hardware access.",
    "Compatibility names are inventory identifiers, not endorsement claims."
  ]
};

export const sampleBenchmarkReport = {
  "backend_schema_version": "quantumbridge-studio-api-v0.1",
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
    "report_json": "{\"capability_level\": 2, \"case_id\": \"studio_circuit_basic\", \"case_name\": \"studio_circuit_basic\", \"category\": \"suite\", \"ecosystem\": \"quantumbridge_native_benchmarking\", \"elapsed_seconds\": 0.0002962080000088463, \"expected_summary\": {\"case_count\": 3}, \"metadata\": {}, \"metrics\": {\"failed\": 0, \"passed\": 3, \"skipped\": 0, \"total\": 3, \"unsupported\": 0}, \"mode\": \"native_minimal\", \"native_implementation\": true, \"output_summary\": {\"cases\": [{\"capability_level\": 2, \"case_id\": \"circuit_basic.h_circuit_statevector\", \"case_name\": \"H circuit statevector\", \"category\": \"circuit_basic\", \"ecosystem\": \"quantumbridge_native_benchmarking\", \"elapsed_seconds\": 6.058299982214521e-05, \"expected_summary\": {\"0\": 0.5, \"1\": 0.5}, \"metadata\": {\"case\": {\"case_id\": \"circuit_basic.h_circuit_statevector\", \"category\": \"circuit_basic\", \"deterministic\": true, \"expected_summary\": {\"probabilities\": {\"0\": 0.5, \"1\": 0.5}}, \"input_summary\": {\"circuit\": \"single-qubit H\", \"runner\": \"Stage 9F statevector\"}, \"metadata\": {\"cloud_access\": false, \"hardware_access\": false, \"official_benchmark_claim\": false, \"production_benchmark_parity_claim\": false, \"token_access\": false}, \"name\": \"H circuit statevector\", \"production_ready\": false, \"provenance\": {\"adapter_package\": \"benchpress\", \"clean_room\": true, \"cloud_access\": false, \"copied_upstream_source\": false, \"copied_upstream_text\": false, \"hardware_access\": false, \"official_benchmark\": false, \"official_endorsement\": false, \"production_benchmark_parity\": false, \"token_access\": false}, \"runner\": \"_run_h_statevector_case\", \"seed\": 7, \"tags\": [\"circuit\", \"statevector\"], \"timeout_seconds\": 10.0, \"warnings\": [\"QuantumBridge Benchpress compatibility support is a clean-room educational benchmarking adapter. It is not a full Benchpress replacement and does not provide production benchmark parity.\", \"QuantumBridge benchmark results are deterministic local validation results for small educational workloads, not official performance rankings.\"], \"workload_type\": \"callable\"}}, \"metrics\": {\"max_probability_delta\": 1.1102230246251565e-16}, \"mode\": \"native_minimal\", \"native_implementation\": true, \"output_summary\": {\"backend\": \"statevector\", \"capability_level\": 3, \"counts\": {}, \"data\": null, \"ecosystem\": \"quantumbridge_native_simulator\", \"final_statevector\": [{\"imag\": 0.0, \"real\": 0.7071067811865475}, {\"imag\": 0.0, \"real\": 0.7071067811865475}], \"metadata\": {\"backend\": \"statevector\", \"cloud_access\": false, \"hardware_access\": false, \"measurement_count\": 0, \"operation_count\": 1, \"production_simulator\": false, \"qiskit_aer_parity_claim\": false, \"supported_gates\": [\"cx\", \"cz\", \"h\", \"phase\", \"rx\", \"ry\", \"rz\", \"swap\", \"x\", \"y\", \"z\"], \"token_read\": false}, \"mode\": \"native_minimal\", \"native_implementation\": true, \"noise_model\": null, \"num_qubits\": 1, \"probabilities\": {\"0\": 0.4999999999999999, \"1\": 0.4999999999999999}, \"production_ready\": false, \"provenance\": {\"adapter\": \"quantumbridge.compat.qiskit_aer\", \"cloud_access\": false, \"hardware_access\": false, \"ibm_branding_copied\": false, \"official_endorsement\": false, \"source_code_copied\": false, \"stage\": \"9F\", \"token_read\": false, \"upstream_source_copied\": false, \"workflow\": \"statevector_simulator_native\"}, \"quantumbridge_version\": null, \"raw_type\": \"QuantumBridgeStatevector\", \"schema_version\": \"0.1\", \"seed\": null, \"shots\": null, \"unsupported_reason\": null, \"upstream_package\": null, \"upstream_version\": null, \"warnings\": [\"QuantumBridge Qiskit Aer support is an optional passthrough/schema bridge plus minimal educational native simulator workflows. It is not a full Qiskit Aer replacement and is not production simulator software.\", \"Native simulator support is a minimal deterministic educational simulator for small circuits.\"], \"workflow\": \"statevector_simulator_native\"}, \"passed\": true, \"production_ready\": false, \"provenance\": {\"adapter_package\": \"benchpress\", \"clean_room\": true, \"cloud_access\": false, \"copied_upstream_source\": false, \"copied_upstream_text\": false, \"hardware_access\": false, \"official_benchmark\": false, \"official_endorsement\": false, \"production_benchmark_parity\": false, \"token_access\": false}, \"quantumbridge_version\": null, \"raw_type\": \"dict\", \"report\": {}, \"schema_version\": \"0.1\", \"skipped\": false, \"status\": \"passed\", \"tags\": [\"circuit\", \"statevector\"], \"unsupported\": false, \"unsupported_reason\": null, \"upstream_package\": null, \"upstream_version\": null, \"warnings\": [\"QuantumBridge Benchpress compatibility support is a clean-room educational benchmarking adapter. It is not a full Benchpress replacement and does not provide production benchmark parity.\", \"QuantumBridge benchmark results are deterministic local validation results for small educational workloads, not official performance rankings.\"], \"workflow\": \"benchmark_case\"}, {\"capability_level\": 2, \"case_id\": \"circuit_basic.bell_qasm_counts\", \"case_name\": \"Bell qasm counts\", \"category\": \"circuit_basic\", \"ecosystem\": \"quantumbridge_native_benchmarking\", \"elapsed_seconds\": 0.00011700000004566391, \"expected_summary\": {}, \"metadata\": {\"case\": {\"case_id\": \"circuit_basic.bell_qasm_counts\", \"category\": \"circuit_basic\", \"deterministic\": true, \"expected_summary\": {\"allowed_counts\": [\"00\", \"11\"]}, \"input_summary\": {\"circuit\": \"Bell measured\", \"shots\": 128}, \"metadata\": {\"cloud_access\": false, \"hardware_access\": false, \"official_benchmark_claim\": false, \"production_benchmark_parity_claim\": false, \"token_access\": false}, \"name\": \"Bell qasm counts\", \"production_ready\": false, \"provenance\": {\"adapter_package\": \"benchpress\", \"clean_room\": true, \"cloud_access\": false, \"copied_upstream_source\": false, \"copied_upstream_text\": false, \"hardware_access\": false, \"official_benchmark\": false, \"official_endorsement\": false, \"production_benchmark_parity\": false, \"token_access\": false}, \"runner\": \"_run_bell_counts_case\", \"seed\": 7, \"tags\": [\"circuit\", \"counts\"], \"timeout_seconds\": 10.0, \"warnings\": [\"QuantumBridge Benchpress compatibility support is a clean-room educational benchmarking adapter. It is not a full Benchpress replacement and does not provide production benchmark parity.\", \"QuantumBridge benchmark results are deterministic local validation results for small educational workloads, not official performance rankings.\"], \"workload_type\": \"callable\"}}, \"metrics\": {\"shot_count\": 128}, \"mode\": \"native_minimal\", \"native_implementation\": true, \"output_summary\": {\"backend\": \"qasm\", \"capability_level\": 3, \"counts\": {\"00\": 61, \"11\": 67}, \"data\": null, \"ecosystem\": \"quantumbridge_native_simulator\", \"final_statevector\": [], \"metadata\": {\"backend\": \"qasm\", \"cloud_access\": false, \"hardware_access\": false, \"measurement_count\": 2, \"operation_count\": 2, \"production_simulator\": false, \"qiskit_aer_parity_claim\": false, \"supported_gates\": [\"cx\", \"cz\", \"h\", \"phase\", \"rx\", \"ry\", \"rz\", \"swap\", \"x\", \"y\", \"z\"], \"token_read\": false}, \"mode\": \"native_minimal\", \"native_implementation\": true, \"noise_model\": null, \"num_qubits\": 2, \"probabilities\": {\"00\": 0.4765625, \"11\": 0.5234375}, \"production_ready\": false, \"provenance\": {\"adapter\": \"quantumbridge.compat.qiskit_aer\", \"cloud_access\": false, \"hardware_access\": false, \"ibm_branding_copied\": false, \"official_endorsement\": false, \"source_code_copied\": false, \"stage\": \"9F\", \"token_read\": false, \"upstream_source_copied\": false, \"workflow\": \"qasm_simulator_native\"}, \"quantumbridge_version\": null, \"raw_type\": \"QuantumBridgeQasmCounts\", \"schema_version\": \"0.1\", \"seed\": 7, \"shots\": 128, \"unsupported_reason\": null, \"upstream_package\": null, \"upstream_version\": null, \"warnings\": [\"QuantumBridge Qiskit Aer support is an optional passthrough/schema bridge plus minimal educational native simulator workflows. It is not a full Qiskit Aer replacement and is not production simulator software.\", \"Native simulator support is a minimal deterministic educational simulator for small circuits.\"], \"workflow\": \"qasm_simulator_native\"}, \"passed\": true, \"production_ready\": false, \"provenance\": {\"adapter_package\": \"benchpress\", \"clean_room\": true, \"cloud_access\": false, \"copied_upstream_source\": false, \"copied_upstream_text\": false, \"hardware_access\": false, \"official_benchmark\": false, \"official_endorsement\": false, \"production_benchmark_parity\": false, \"token_access\": false}, \"quantumbridge_version\": null, \"raw_type\": \"dict\", \"report\": {}, \"schema_version\": \"0.1\", \"skipped\": false, \"status\": \"passed\", \"tags\": [\"circuit\", \"counts\"], \"unsupported\": false, \"unsupported_reason\": null, \"upstream_package\": null, \"upstream_version\": null, \"warnings\": [\"QuantumBridge Benchpress compatibility support is a clean-room educational benchmarking adapter. It is not a full Benchpress replacement and does not provide production benchmark parity.\", \"QuantumBridge benchmark results are deterministic local validation results for small educational workloads, not official performance rankings.\"], \"workflow\": \"benchmark_case\"}, {\"capability_level\": 2, \"case_id\": \"circuit_basic.parameterized_rx_ry_statevector\", \"case_name\": \"Parameterized RX RY statevector\", \"category\": \"circuit_basic\", \"ecosystem\": \"quantumbridge_native_benchmarking\", \"elapsed_seconds\": 9.616700003789447e-05, \"expected_summary\": {}, \"metadata\": {\"case\": {\"case_id\": \"circuit_basic.parameterized_rx_ry_statevector\", \"category\": \"circuit_basic\", \"deterministic\": true, \"expected_summary\": {\"probability_sum\": 1.0}, \"input_summary\": {\"circuit\": \"RX/RY\", \"parameters\": [0.7853981633974483, 0.5235987755982988]}, \"metadata\": {\"cloud_access\": false, \"hardware_access\": false, \"official_benchmark_claim\": false, \"production_benchmark_parity_claim\": false, \"token_access\": false}, \"name\": \"Parameterized RX RY statevector\", \"production_ready\": false, \"provenance\": {\"adapter_package\": \"benchpress\", \"clean_room\": true, \"cloud_access\": false, \"copied_upstream_source\": false, \"copied_upstream_text\": false, \"hardware_access\": false, \"official_benchmark\": false, \"official_endorsement\": false, \"production_benchmark_parity\": false, \"token_access\": false}, \"runner\": \"_run_parameterized_case\", \"seed\": 7, \"tags\": [\"circuit\", \"parameters\"], \"timeout_seconds\": 10.0, \"warnings\": [\"QuantumBridge Benchpress compatibility support is a clean-room educational benchmarking adapter. It is not a full Benchpress replacement and does not provide production benchmark parity.\", \"QuantumBridge benchmark results are deterministic local validation results for small educational workloads, not official performance rankings.\"], \"workload_type\": \"callable\"}}, \"metrics\": {\"probability_sum\": 1.0}, \"mode\": \"native_minimal\", \"native_implementation\": true, \"output_summary\": {\"backend\": \"statevector\", \"capability_level\": 3, \"counts\": {}, \"data\": null, \"ecosystem\": \"quantumbridge_native_simulator\", \"final_statevector\": [{\"imag\": 0.09904576054128762, \"real\": 0.8923991008325228}, {\"imag\": -0.3696438106143861, \"real\": 0.23911761839433449}], \"metadata\": {\"backend\": \"statevector\", \"cloud_access\": false, \"hardware_access\": false, \"measurement_count\": 0, \"operation_count\": 2, \"production_simulator\": false, \"qiskit_aer_parity_claim\": false, \"supported_gates\": [\"cx\", \"cz\", \"h\", \"phase\", \"rx\", \"ry\", \"rz\", \"swap\", \"x\", \"y\", \"z\"], \"token_read\": false}, \"mode\": \"native_minimal\", \"native_implementation\": true, \"noise_model\": null, \"num_qubits\": 1, \"probabilities\": {\"0\": 0.8061862178478973, \"1\": 0.1938137821521027}, \"production_ready\": false, \"provenance\": {\"adapter\": \"quantumbridge.compat.qiskit_aer\", \"cloud_access\": false, \"hardware_access\": false, \"ibm_branding_copied\": false, \"official_endorsement\": false, \"source_code_copied\": false, \"stage\": \"9F\", \"token_read\": false, \"upstream_source_copied\": false, \"workflow\": \"statevector_simulator_native\"}, \"quantumbridge_version\": null, \"raw_type\": \"QuantumBridgeStatevector\", \"schema_version\": \"0.1\", \"seed\": null, \"shots\": null, \"unsupported_reason\": null, \"upstream_package\": null, \"upstream_version\": null, \"warnings\": [\"QuantumBridge Qiskit Aer support is an optional passthrough/schema bridge plus minimal educational native simulator workflows. It is not a full Qiskit Aer replacement and is not production simulator software.\", \"Native simulator support is a minimal deterministic educational simulator for small circuits.\"], \"workflow\": \"statevector_simulator_native\"}, \"passed\": true, \"production_ready\": false, \"provenance\": {\"adapter_package\": \"benchpress\", \"clean_room\": true, \"cloud_access\": false, \"copied_upstream_source\": false, \"copied_upstream_text\": false, \"hardware_access\": false, \"official_benchmark\": false, \"official_endorsement\": false, \"production_benchmark_parity\": false, \"token_access\": false}, \"quantumbridge_version\": null, \"raw_type\": \"dict\", \"report\": {}, \"schema_version\": \"0.1\", \"skipped\": false, \"status\": \"passed\", \"tags\": [\"circuit\", \"parameters\"], \"unsupported\": false, \"unsupported_reason\": null, \"upstream_package\": null, \"upstream_version\": null, \"warnings\": [\"QuantumBridge Benchpress compatibility support is a clean-room educational benchmarking adapter. It is not a full Benchpress replacement and does not provide production benchmark parity.\", \"QuantumBridge benchmark results are deterministic local validation results for small educational workloads, not official performance rankings.\"], \"workflow\": \"benchmark_case\"}]}, \"passed\": true, \"production_ready\": false, \"provenance\": {\"adapter_package\": \"benchpress\", \"clean_room\": true, \"cloud_access\": false, \"copied_upstream_source\": false, \"copied_upstream_text\": false, \"hardware_access\": false, \"official_benchmark\": false, \"official_endorsement\": false, \"production_benchmark_parity\": false, \"token_access\": false}, \"quantumbridge_version\": null, \"raw_type\": null, \"report\": {\"summary\": {\"failed\": 0, \"passed\": 3, \"skipped\": 0, \"total\": 3, \"unsupported\": 0}}, \"schema_version\": \"0.1\", \"skipped\": false, \"status\": \"passed\", \"tags\": [\"benchpress\", \"suite\"], \"unsupported\": false, \"unsupported_reason\": null, \"upstream_package\": null, \"upstream_version\": null, \"warnings\": [\"QuantumBridge Benchpress compatibility support is a clean-room educational benchmarking adapter. It is not a full Benchpress replacement and does not provide production benchmark parity.\", \"QuantumBridge benchmark results are deterministic local validation results for small educational workloads, not official performance rankings.\"], \"workflow\": \"studio_circuit_basic\"}",
    "report_markdown": "# QuantumBridge Studio Benchmark Report\n\n- workflow: studio_circuit_basic\n- status: passed\n- passed: True\n- elapsed_seconds: 0.0002962080000088463\n\n## Boundaries\n\n- not official Benchpress output\n- not production performance ranking\n- no cloud/token/hardware access\n",
    "result": {
      "capability_level": 2,
      "case_id": "studio_circuit_basic",
      "case_name": "studio_circuit_basic",
      "category": "suite",
      "ecosystem": "quantumbridge_native_benchmarking",
      "elapsed_seconds": 0.0002962080000088463,
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
            "elapsed_seconds": 6.058299982214521e-05,
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
            "elapsed_seconds": 0.00011700000004566391,
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
            "elapsed_seconds": 9.616700003789447e-05,
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
  "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
  "generated_at": "2026-06-10T01:36:50+00:00",
  "provenance": {
    "cloud_access": false,
    "copied_upstream_source": false,
    "copied_upstream_ui": false,
    "hardware_access": false,
    "official_endorsement": false,
    "production_ready": false,
    "source": "quantumbridge.studio.backend",
    "token_access": false
  },
  "quantumbridge_version": "0.1.0rc1",
  "schema_version": "quantumbridge-studio-frontend-seed-v0.1",
  "section": "benchmark",
  "source": "quantumbridge.studio.backend",
  "suite_id": "circuit_basic",
  "warnings": [
    "Local prototype seed data only.",
    "No production UI claim.",
    "No cloud execution, credential reading, or hardware access.",
    "Compatibility names are inventory identifiers, not endorsement claims."
  ]
};

export const sampleExports = {
  "backend_schema_version": "quantumbridge-studio-api-v0.1",
  "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
  "exports": {
    "json": {
      "content": "{\n  \"error\": null,\n  \"execution_id\": \"studio-exec-000001\",\n  \"provenance\": {\n    \"cloud_access\": false,\n    \"copied_upstream_source\": false,\n    \"hardware_access\": false,\n    \"metadata\": {\n      \"api_layer\": \"quantumbridge.studio\",\n      \"frontend_ui_implementation\": false,\n      \"local_router\": true\n    },\n    \"official_endorsement\": false,\n    \"production_ready\": false,\n    \"project_id\": \"qiskit-aer\",\n    \"result_provenance\": {\n      \"adapter\": \"quantumbridge.compat.qiskit_aer\",\n      \"cloud_access\": false,\n      \"hardware_access\": false,\n      \"ibm_branding_copied\": false,\n      \"official_endorsement\": false,\n      \"source_code_copied\": false,\n      \"stage\": \"9F\",\n      \"token_read\": false,\n      \"upstream_source_copied\": false,\n      \"workflow\": \"statevector_simulator_native\"\n    },\n    \"source\": \"quantumbridge\",\n    \"token_access\": false,\n    \"workflow_id\": \"aer.statevector_native\"\n  },\n  \"result\": {\n    \"backend\": \"statevector\",\n    \"capability_level\": 3,\n    \"counts\": {},\n    \"data\": null,\n    \"ecosystem\": \"quantumbridge_native_simulator\",\n    \"final_statevector\": [\n      {\n        \"imag\": 0.0,\n        \"real\": 0.7071067811865475\n      },\n      {\n        \"imag\": 0.0,\n        \"real\": 0.0\n      },\n      {\n        \"imag\": 0.0,\n        \"real\": 0.0\n      },\n      {\n        \"imag\": 0.0,\n        \"real\": 0.7071067811865475\n      }\n    ],\n    \"metadata\": {\n      \"backend\": \"statevector\",\n      \"cloud_access\": false,\n      \"hardware_access\": false,\n      \"measurement_count\": 0,\n      \"operation_count\": 2,\n      \"production_simulator\": false,\n      \"qiskit_aer_parity_claim\": false,\n      \"supported_gates\": [\n        \"cx\",\n        \"cz\",\n        \"h\",\n        \"phase\",\n        \"rx\",\n        \"ry\",\n        \"rz\",\n        \"swap\",\n        \"x\",\n        \"y\",\n        \"z\"\n      ],\n      \"token_read\": false\n    },\n    \"mode\": \"native_minimal\",\n    \"native_implementation\": true,\n    \"noise_model\": null,\n    \"num_qubits\": 2,\n    \"probabilities\": {\n      \"00\": 0.4999999999999999,\n      \"11\": 0.4999999999999999\n    },\n    \"production_ready\": false,\n    \"provenance\": {\n      \"adapter\": \"quantumbridge.compat.qiskit_aer\",\n      \"cloud_access\": false,\n      \"hardware_access\": false,\n      \"ibm_branding_copied\": false,\n      \"official_endorsement\": false,\n      \"source_code_copied\": false,\n      \"stage\": \"9F\",\n      \"token_read\": false,\n      \"upstream_source_copied\": false,\n      \"workflow\": \"statevector_simulator_native\"\n    },\n    \"quantumbridge_version\": null,\n    \"raw_type\": \"QuantumBridgeStatevector\",\n    \"schema_version\": \"0.1\",\n    \"seed\": null,\n    \"shots\": null,\n    \"unsupported_reason\": null,\n    \"upstream_package\": null,\n    \"upstream_version\": null,\n    \"warnings\": [\n      \"QuantumBridge Qiskit Aer support is an optional passthrough/schema bridge plus minimal educational native simulator workflows. It is not a full Qiskit Aer replacement and is not production simulator software.\",\n      \"Native simulator support is a minimal deterministic educational simulator for small circuits.\"\n    ],\n    \"workflow\": \"statevector_simulator_native\"\n  },\n  \"schema_version\": \"quantumbridge-studio-api-v0.1\",\n  \"status\": \"succeeded\",\n  \"unsupported_reason\": null,\n  \"warnings\": [\n    \"QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.\",\n    \"Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.\",\n    \"This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.\",\n    \"This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.\",\n    \"QuantumBridge Studio uses clean-room local metadata for qiskit-aer; no third-party source, UI, prose, or branding is copied.\",\n    \"Studio workflow aer.statevector_native is local-only: no cloud, token, credential, or hardware access.\",\n    \"QuantumBridge Qiskit Aer support is an optional passthrough/schema bridge plus minimal educational native simulator workflows. It is not a full Qiskit Aer replacement and is not production simulator software.\",\n    \"Native simulator support is a minimal deterministic educational simulator for small circuits.\"\n  ],\n  \"workflow_id\": \"aer.statevector_native\"\n}",
      "execution_id": null,
      "export_type": "json",
      "provenance": {},
      "schema_version": "quantumbridge-studio-api-v0.1",
      "unsupported_reason": null,
      "warnings": [],
      "workflow_id": null
    },
    "markdown": {
      "content": "# QuantumBridge Studio Result\\n\\n- execution_id: `studio-exec-000001`\\n- workflow_id: `aer.statevector_native`\\n\\n```json\\n{\n  \"error\": null,\n  \"execution_id\": \"studio-exec-000001\",\n  \"provenance\": {\n    \"cloud_access\": false,\n    \"copied_upstream_source\": false,\n    \"hardware_access\": false,\n    \"metadata\": {\n      \"api_layer\": \"quantumbridge.studio\",\n      \"frontend_ui_implementation\": false,\n      \"local_router\": true\n    },\n    \"official_endorsement\": false,\n    \"production_ready\": false,\n    \"project_id\": \"qiskit-aer\",\n    \"result_provenance\": {\n      \"adapter\": \"quantumbridge.compat.qiskit_aer\",\n      \"cloud_access\": false,\n      \"hardware_access\": false,\n      \"ibm_branding_copied\": false,\n      \"official_endorsement\": false,\n      \"source_code_copied\": false,\n      \"stage\": \"9F\",\n      \"token_read\": false,\n      \"upstream_source_copied\": false,\n      \"workflow\": \"statevector_simulator_native\"\n    },\n    \"source\": \"quantumbridge\",\n    \"token_access\": false,\n    \"workflow_id\": \"aer.statevector_native\"\n  },\n  \"result\": {\n    \"backend\": \"statevector\",\n    \"capability_level\": 3,\n    \"counts\": {},\n    \"data\": null,\n    \"ecosystem\": \"quantumbridge_native_simulator\",\n    \"final_statevector\": [\n      {\n        \"imag\": 0.0,\n        \"real\": 0.7071067811865475\n      },\n      {\n        \"imag\": 0.0,\n        \"real\": 0.0\n      },\n      {\n        \"imag\": 0.0,\n        \"real\": 0.0\n      },\n      {\n        \"imag\": 0.0,\n        \"real\": 0.7071067811865475\n      }\n    ],\n    \"metadata\": {\n      \"backend\": \"statevector\",\n      \"cloud_access\": false,\n      \"hardware_access\": false,\n      \"measurement_count\": 0,\n      \"operation_count\": 2,\n      \"production_simulator\": false,\n      \"qiskit_aer_parity_claim\": false,\n      \"supported_gates\": [\n        \"cx\",\n        \"cz\",\n        \"h\",\n        \"phase\",\n        \"rx\",\n        \"ry\",\n        \"rz\",\n        \"swap\",\n        \"x\",\n        \"y\",\n        \"z\"\n      ],\n      \"token_read\": false\n    },\n    \"mode\": \"native_minimal\",\n    \"native_implementation\": true,\n    \"noise_model\": null,\n    \"num_qubits\": 2,\n    \"probabilities\": {\n      \"00\": 0.4999999999999999,\n      \"11\": 0.4999999999999999\n    },\n    \"production_ready\": false,\n    \"provenance\": {\n      \"adapter\": \"quantumbridge.compat.qiskit_aer\",\n      \"cloud_access\": false,\n      \"hardware_access\": false,\n      \"ibm_branding_copied\": false,\n      \"official_endorsement\": false,\n      \"source_code_copied\": false,\n      \"stage\": \"9F\",\n      \"token_read\": false,\n      \"upstream_source_copied\": false,\n      \"workflow\": \"statevector_simulator_native\"\n    },\n    \"quantumbridge_version\": null,\n    \"raw_type\": \"QuantumBridgeStatevector\",\n    \"schema_version\": \"0.1\",\n    \"seed\": null,\n    \"shots\": null,\n    \"unsupported_reason\": null,\n    \"upstream_package\": null,\n    \"upstream_version\": null,\n    \"warnings\": [\n      \"QuantumBridge Qiskit Aer support is an optional passthrough/schema bridge plus minimal educational native simulator workflows. It is not a full Qiskit Aer replacement and is not production simulator software.\",\n      \"Native simulator support is a minimal deterministic educational simulator for small circuits.\"\n    ],\n    \"workflow\": \"statevector_simulator_native\"\n  },\n  \"schema_version\": \"quantumbridge-studio-api-v0.1\",\n  \"status\": \"succeeded\",\n  \"unsupported_reason\": null,\n  \"warnings\": [\n    \"QuantumBridge Studio backend API is a local executable service layer. It is not a production API server, not a frontend UI, and not an official IBM, Qiskit, PennyLane, Benchpress, Quafu, QOS-UQCI, MQT, Mitiq, or TorchQuantum service.\",\n    \"Studio workflows are local-only by default and do not access cloud services, tokens, credentials, or real hardware.\",\n    \"This Studio API slice uses QuantumBridge-owned clean-room metadata and execution wrappers; no third-party source, UI, tutorial prose, or branding is copied.\",\n    \"This slice does not claim full replacement, production parity, official benchmark status, or official endorsement.\",\n    \"QuantumBridge Studio uses clean-room local metadata for qiskit-aer; no third-party source, UI, prose, or branding is copied.\",\n    \"Studio workflow aer.statevector_native is local-only: no cloud, token, credential, or hardware access.\",\n    \"QuantumBridge Qiskit Aer support is an optional passthrough/schema bridge plus minimal educational native simulator workflows. It is not a full Qiskit Aer replacement and is not production simulator software.\",\n    \"Native simulator support is a minimal deterministic educational simulator for small circuits.\"\n  ],\n  \"workflow_id\": \"aer.statevector_native\"\n}\\n```\\n",
      "execution_id": "studio-exec-000001",
      "export_type": "markdown",
      "provenance": {},
      "schema_version": "quantumbridge-studio-api-v0.1",
      "unsupported_reason": null,
      "warnings": [],
      "workflow_id": "aer.statevector_native"
    },
    "notebook_stub": {
      "content": "{\n  \"metadata\": {\n    \"quantumbridge\": \"studio-notebook-stub-v0.1\"\n  },\n  \"cells\": [\n    {\n      \"cell_type\": \"markdown\",\n      \"source\": [\n        \"# QuantumBridge Studio workflow: aer.statevector_native\\\\n\"\n      ]\n    },\n    {\n      \"cell_type\": \"code\",\n      \"source\": [\n        \"from quantumbridge.studio.execution_service import execute_workflow\\\\n\\\\nresult = execute_workflow('aer.statevector_native', inputs={})\\\\nprint(result.to_json())\\\\n\"\n      ],\n      \"outputs\": []\n    }\n  ],\n  \"nbformat\": 4,\n  \"nbformat_minor\": 5\n}",
      "execution_id": null,
      "export_type": "notebook_stub",
      "provenance": {},
      "schema_version": "quantumbridge-studio-api-v0.1",
      "unsupported_reason": null,
      "warnings": [],
      "workflow_id": "aer.statevector_native"
    },
    "python": {
      "content": "from quantumbridge.studio.execution_service import execute_workflow\\n\\nresult = execute_workflow('aer.statevector_native', inputs={})\\nprint(result.to_json())\\n",
      "execution_id": null,
      "export_type": "python",
      "provenance": {},
      "schema_version": "quantumbridge-studio-api-v0.1",
      "unsupported_reason": null,
      "warnings": [],
      "workflow_id": "aer.statevector_native"
    }
  },
  "formats": [
    "json",
    "markdown",
    "notebook_stub",
    "python"
  ],
  "generated_at": "2026-06-10T01:36:50+00:00",
  "provenance": {
    "cloud_access": false,
    "copied_upstream_source": false,
    "copied_upstream_ui": false,
    "hardware_access": false,
    "official_endorsement": false,
    "production_ready": false,
    "source": "quantumbridge.studio.backend",
    "token_access": false
  },
  "quantumbridge_version": "0.1.0rc1",
  "schema_version": "quantumbridge-studio-frontend-seed-v0.1",
  "section": "exports",
  "source": "quantumbridge.studio.backend",
  "warnings": [
    "Local prototype seed data only.",
    "No production UI claim.",
    "No cloud execution, credential reading, or hardware access.",
    "Compatibility names are inventory identifiers, not endorsement claims."
  ]
};

export const studioSchemaVersion = {
  "backend_schema_version": "quantumbridge-studio-api-v0.1",
  "clean_room_notice": "QuantumBridge Studio seed data is generated from QuantumBridge local backend services. Third-party project names identify compatibility targets only; no official endorsement, copied upstream UI, copied prose, cloud access, token access, hardware access, or production readiness is claimed.",
  "export_formats": [
    "json",
    "markdown",
    "notebook_stub",
    "python"
  ],
  "files": {
    "benchmark": "sampleBenchmarkReport.json",
    "catalog": "sampleCatalog.json",
    "exports": "sampleExports.json",
    "results": "sampleResults.json",
    "schema": "studioSchemaVersion.json",
    "workflow_details": "sampleWorkflowDetails.json",
    "workflows": "sampleWorkflows.json"
  },
  "frontend_schema_version": "quantumbridge-studio-frontend-seed-v0.1",
  "generated_at": "2026-06-10T01:36:50+00:00",
  "provenance": {
    "cloud_access": false,
    "copied_upstream_source": false,
    "copied_upstream_ui": false,
    "hardware_access": false,
    "official_endorsement": false,
    "production_ready": false,
    "source": "quantumbridge.studio.backend",
    "token_access": false
  },
  "quantumbridge_version": "0.1.0rc1",
  "sample_result_count": 18,
  "schema_version": "quantumbridge-studio-frontend-seed-v0.1",
  "section": "schema",
  "source": "quantumbridge.studio.backend",
  "warnings": [
    "Local prototype seed data only.",
    "No production UI claim.",
    "No cloud execution, credential reading, or hardware access.",
    "Compatibility names are inventory identifiers, not endorsement claims."
  ],
  "workflow_count": 36,
  "workflow_detail_count": 36
};
