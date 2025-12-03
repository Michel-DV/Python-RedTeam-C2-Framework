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


🚀 Usage
1. Start the C2 Server (Attacker)
Run the server listener first. It will wait for incoming connections.

Bash: python3 server.py

2. Execute the Agent (Target)
Run the agent on the target machine (or a separate terminal for testing).

Bash: python3 agent.py

3. Interaction
Once the connection is established, you will receive a shell prompt on the server:

[x] Listening on 0.0.0.0:5555...
[x] Connection received from: 127.0.0.1:45892
C2_Shell> whoami
desktop-user\xxx
C2_Shell> ipconfig
...

⚠️ Disclaimer & Legal Warning
This project is created for EDUCATIONAL PURPOSES ONLY.

The source code provided here is intended to help security professionals and students understand how C2 frameworks operate to better detect and defend against them.

Do not use this software on systems you do not own or do not have explicit permission to test.

The author bears no responsibility for any misuse of this code.

Project developed by as part of the Advanced Cybersecurity Portfolio.

## 🏗️ Architecture

```mermaid
graph LR
    A[Attacker / C2 Server] -- Listens on Port 5555 --> B((Internet / Network))
    C[Target / Agent] -- Reverse TCP Connection --> B
    A -- Sends Commands (e.g., 'whoami') --> C
    C -- Executes & Returns Output --> A

