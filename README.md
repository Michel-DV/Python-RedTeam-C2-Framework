# Python-RedTeam-C2-Framework
A lightweight Command &amp; Control (C2) architecture implementation in Python. Designed to demonstrate client-server socket communication and remote shell execution for Red Teaming educational purposes.


![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat&logo=python)
![Category](https://img.shields.io/badge/Category-Red%20Teaming-red)
![Status](https://img.shields.io/badge/Status-Educational-yellow)

## 📋 Overview
This repository contains a Proof of Concept (PoC) implementation of a **Command & Control (C2)** architecture. The project demonstrates the fundamental mechanics of malware communication, including socket programming, client-server handshake, and remote command execution.

**Key concepts demonstrated:**
- **Socket Programming:** Low-level networking implementation using Python standard libraries.
- **Reverse Shell Logic:** Simulating an agent (implant) calling back to the C2 server.
- **Process Management:** Using `subprocess` to interact with the OS shell seamlessly.

## 🏗️ Architecture

```mermaid
graph LR
    A[Attacker / C2 Server] -- Listens on Port 5555 --> B((Internet / Network))
    C[Target / Agent] -- Reverse TCP Connection --> B
    A -- Sends Commands (e.g., 'whoami') --> C
    C -- Executes & Returns Output --> A
