# System Documentation

![High Level Architecture](/docs/images/Savannah%20Orders%20High%20Level.png)

## Overview

This document outlines the system architecture, components, and interactions in a structured manner. The system is designed to be scalable, secure, and automated, integrating modern DevOps and cloud-native practices.

## System Components

### 1. User Interaction

- Users interact with the system via a **REST API**.
- Authentication is handled using **OpenID Connect**.

### 2. API Layer

- The **API** is the central component facilitating communication between the user and backend services.
- It manages authentication and directs requests to relevant services.

### 3. CI/CD Pipeline

- **GitHub** is used as the version control system.
- The **CI/CD Pipeline** automates:
  - **Automated Testing** to ensure code quality and reliability using **pytest**.
  - **Test Coverage** validation, with reports uploaded to **Codecov**.
  - **Code Formatting** enforced using **Black**.
  - **Linting and Code Style Checks** using **Flake8**.
  - **Type Checking** with **Mypy**.
  - **Security Analysis** performed using **Bandit**.
  - **Dependency Management** handled via **Poetry**.
  - **Deployment to Kubernetes** for containerized applications.

### 4. Deployment and Infrastructure

- **Kubernetes** orchestrates containerized applications.
- **Helm Chart** is used to define and manage Kubernetes deployments.
- **Docker Containers** package the application for deployment.
- **Debian Server** hosts the containerized services.
- **Ansible** automates server configuration and management.

### 5. Backend Services

- **FastAPI Service** serves as the backend application.
- It interacts with:
  - **PostgreSQL** as the primary database.
  - **SMS Gateway (Africa’s Talking)** for messaging services.
  