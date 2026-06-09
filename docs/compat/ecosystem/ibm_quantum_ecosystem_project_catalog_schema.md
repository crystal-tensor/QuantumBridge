# QuantumBridge Ecosystem Project Catalog Schema

Status: Stage 9C-Revision planning and schema baseline

This document defines the QuantumBridge-owned clean-room ecosystem catalog
schema. It is not a scraped copy of IBM Quantum Ecosystem and does not copy
IBM project card text, UI, icons, images, or branding.

## Fields

| Field | Meaning |
| --- | --- |
| `project_id` | Stable QuantumBridge catalog key. |
| `display_name` | QuantumBridge-facing display label. |
| `upstream_name` | Public upstream project name used for compatibility identification. |
| `upstream_homepage` | Optional upstream homepage URL. |
| `upstream_repository` | Optional upstream source repository URL. |
| `upstream_license` | Upstream license when known. |
| `upstream_owner` | Upstream owner or maintainer when known. |
| `category` | QuantumBridge category such as algorithms, chemistry, simulator, QML. |
| `tags` | QuantumBridge search and filter tags. |
| `install_extra` | QuantumBridge optional extra, if any. |
| `package_name` | Optional Python package name. |
| `dependency_available` | Local dependency detection status. |
| `adapter_module` | QuantumBridge adapter module. |
| `capability_level` | 0 inventory, 1 passthrough, 2 schema adapter, 3 native subset, 4 production equivalent. |
| `executable_workflows` | Reviewed executable workflow ids. |
| `examples` | QuantumBridge example files. |
| `tests` | QuantumBridge tests. |
| `docs` | QuantumBridge docs. |
| `warnings` | Required warnings. |
| `provenance` | Source and adapter metadata. |
| `official_endorsement` | Always false unless upstream grants written approval and legal review accepts it. |
| `clean_room_status` | planned, inventory, passthrough, executable, or advisory. |
| `ui_ready` | Whether Studio can safely surface the entry. |
| `priority` | QuantumBridge implementation priority. |
| `notes` | QuantumBridge-owned notes. |

## Rules

- Do not scrape IBM pages.
- Do not copy IBM project card descriptions.
- Do not copy third-party README text into catalog rows.
- Do not copy logos, icons, screenshots, or brand assets.
- Use project names only for compatibility identification.
- Every row must keep `official_endorsement` false unless a separate legal
  review says otherwise.
