# gm-rvm-system
Prototype implementation of a Reverse Vending Machine (RVM) integrating computer vision, backend services, and a web-based frontend to identify plastic bottles, validate deposits, and issue rewards.

# Reverse Vending Machine (RVM) System

## Overview

This repository contains the complete system for a **Reverse Vending Machine (RVM) prototype** that rewards users (e.g., via printed coupons) for depositing used plastic bottles.

The project integrates:
- A user-facing interface
- Backend business logic
- Computer vision–based bottle detection
- Hardware integration (camera, thermal printer)
- Containerized, edge-device-friendly deployment

The system is designed to be **modular, scalable, and production-oriented**, while remaining practical for prototyping and research use.

---

## Repository Structure
rvm-system/
│
├── frontend/ # User interface (kiosk, admin, or mobile UI)
│
├── backend/ # APIs, business rules, coupon logic, logging
│
├── ai/ # Computer vision (training and inference)
│
├── hardware/ # Camera, printer, GPIO, and device integrations
│
├── shared/ # Shared contracts, schemas, and constants
│
├── docs/ # Architecture docs, setup guides, diagrams
│
├── scripts/ # Automation, setup, and helper scripts
│
├── infra/ # Docker, CI/CD, and infrastructure configuration
│
├── README.md
└── .gitignore


---

## Folder Responsibilities

### frontend/
Contains all user-facing interfaces, such as:
- RVM kiosk UI
- Admin dashboard
- Mobile or web client (if applicable)

This layer never communicates directly with hardware or AI — all interactions go through the backend.

---

### backend/
Acts as the system’s orchestrator:
- Exposes APIs to the frontend
- Communicates with the AI inference service
- Applies business rules (e.g., valid bottle → reward)
- Triggers hardware actions (e.g., printing coupons)
- Stores logs and operational data

---

### ai/
Contains all computer vision and machine learning components, separated into:
- Training (datasets, experiments)
- Inference (lightweight, production-ready service)

Training and inference are intentionally decoupled to avoid deploying heavy ML tooling to the RVM device.

---

### hardware/
Handles direct device interaction, including:
- Camera capture
- Thermal printer control
- GPIO or serial communication

This layer is isolated to simplify hardware replacement or upgrades.

---

### shared/
Defines shared contracts between services:
- API schemas
- Data formats
- Constants and enumerations

This prevents silent breaking changes across system components.

---

### docs/
Project documentation, including:
- System architecture
- API contracts
- Setup and deployment guides
- Research notes and assumptions

This folder is essential for maintainability and academic review.

---

### infra/
Infrastructure and DevOps configuration:
- Dockerfiles
- Environment configuration
- CI/CD support files

Keeps operational concerns separate from application logic.

---

### scripts/
Utility scripts for:
- Local setup
- Data preparation
- Deployment automation
- Maintenance tasks

---

## Development Philosophy

- Modular by design — components can evolve independently
- Edge-device friendly — minimal runtime overhead
- Containerized — consistent behavior across environments
- Scalable — can transition to multi-repo or cloud-based deployment later
- Research-safe — reproducible and auditable system behavior

---

## Getting Started (High-Level)

1. Clone the repository
2. Configure environment variables (.env)
3. Build and run services using Docker Compose:
docker compose up


4. Access the frontend and interact with the RVM workflow

Detailed instructions are available in the docs/ directory.

---

## Versioning & Deployment

- The main branch is always deployable
- Releases are tagged for rollback safety
- Models and system behavior are versioned together for reproducibility

---

## Intended Use

This project may be used for:
- Academic research and prototyping
- Environmental awareness initiatives
- Smart infrastructure demonstrations
- Computer vision–based embedded systems

---

## License

License information will be added once the project reaches a stable milestone.

---

## Contact / Maintainers

Project maintained by the RVM development team.  
Refer to the docs/ folder for contributor guidelines and ownership.

