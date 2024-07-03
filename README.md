# Ansible Container and Runner

![License](https://img.shields.io/github/license/MrSud0/ansible-container-and-runner)
![Stars](https://img.shields.io/github/stars/MrSud0/ansible-container-and-runner)
![Forks](https://img.shields.io/github/forks/MrSud0/ansible-container-and-runner)

Ansible Container and Runner is a project designed to simplify running Ansible playbooks inside a Docker container. This repository contains the necessary scripts and configurations to build a Docker image and run Ansible playbooks within it.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Files](#files)
- [Contributing](#contributing)
- [License](#license)

## Features
- Dockerfile to create a containerized environment for Ansible
- Python scripts to generate inventory and run Ansible playbooks
- Entrypoint script to set up and execute the playbooks

## Prerequisites
- Docker installed on your system
- Python 3.x

## Installation
1. Clone this repository:
    ```sh
    git clone https://github.com/MrSud0/ansible-container-and-runner.git
    cd ansible-container-and-runner
    ```
2. Build the Docker image:
    ```sh
    docker build -t ansible-runner .
    ```

## Usage
1. Generate the inventory:
    ```sh
    python generate-inventory.py
    ```
2. Run the setup playbook:
    ```sh
    python run-setup-ansible.py
    ```
3. Execute the playbooks:
    ```sh
    python run-ansible-playbooks.py
    ```

## Files
- `Dockerfile`: Defines the Docker image setup.
- `entrypoint.sh`: Entrypoint script for initializing the container.
- `generate-inventory.py`: Script to generate Ansible inventory.
- `run-ansible-playbooks.py`: Script to run Ansible playbooks.
- `run-setup-ansible.py`: Script to set up Ansible.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
