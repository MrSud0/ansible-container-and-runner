import docker
import sys
import os
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    filename='ansible_playbook_runner.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def run_ansible_playbook(working_directory, primary_script, playbooks, inventory_path, results_dir, extra_vars=None):
    """
    Run an Ansible playbook using a Docker container.
    
    :param working_directory: Base directory for all file paths.
    :param primary_script: Path to the primary script.
    :param playbooks: List of paths to the Ansible playbooks.
    :param inventory_path: Path to the inventory file.
    :param results_dir: Directory to save the results file.
    :param extra_vars: Additional variables to pass to the playbook (optional).
    """
    logging.info(f"Running Ansible playbook: {primary_script} with inventory: {inventory_path} and extra_vars: {extra_vars}")
    client = docker.from_env()

    volumes = {
        os.path.join(working_directory, primary_script): {'bind': '/home/discovery/ansible-runner.py', 'mode': 'ro'},
        os.path.join(working_directory, inventory_path): {'bind': '/home/discovery/inventory.ini', 'mode': 'ro'},
        os.path.abspath(results_dir): {'bind': '/tmp', 'mode': 'rw'}
    }
    
    for playbook in playbooks:
        volumes[os.path.join(working_directory, playbook)] = {'bind': f'/home/discovery/{Path(playbook).name}', 'mode': 'ro'}

    command = ["python3", "/home/discovery/ansible-runner.py"]

    if extra_vars:
        command.extend(["--extra-vars", extra_vars])

    try:
        logging.info(f"Starting Docker container with command: {command} and volumes: {volumes}")
        container = client.containers.run(
            "ansible-v2", 
            command=command, 
            volumes=volumes, 
            remove=True,
            stdout=True,
            stderr=True
        )
        logging.info("Ansible playbook executed successfully")
        print(container.decode("utf-8"))

        # The results will be automatically saved to the specified directory on the host
    except docker.errors.ContainerError as e:
        logging.error(f"Error running Ansible playbook: {e.stderr.decode('utf-8')}")
        print("Error running Ansible playbook:", file=sys.stderr)
        print(e.stderr.decode("utf-8"), file=sys.stderr)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(f"Unexpected error: {e}", file=sys.stderr)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Prepare hosts for Ansible connections and run an Ansible playbook using a Docker container.")
    subparsers = parser.add_subparsers(dest="mode", help="Operation mode: setup or run")

    run_parser = subparsers.add_parser("run", help="Run mode to execute an Ansible playbook")
    run_parser.add_argument("--working-directory", default=".", help="Working directory for all files (default: current directory)")
    run_parser.add_argument("--primary-script", default="ansible-runner.py", help="Path to the primary script to run (default: ansible-runner.py)")
    run_parser.add_argument("--playbooks", nargs='+', default=["disLin.yml", "disWin.yml"], help="Paths to the Ansible playbooks to load (default: disLin.yml disWin.yml)")
    run_parser.add_argument("--inventory", default="inventory.ini", help="Path to the inventory file to use (default: inventory.ini)")
    run_parser.add_argument("--results-dir", default="/home/env-admin/asset_discovery_tool/results", help="Directory to save the results file (default: /home/env-admin/asset_discovery_tool/results)")
    run_parser.add_argument("--extra-vars", help="Additional variables to pass to the playbook")
    
    args = parser.parse_args()

    if args.mode == "run":
        logging.info(f"Script started with arguments: {args}")
        run_ansible_playbook(args.working_directory, args.primary_script, args.playbooks, args.inventory, args.results_dir, args.extra_vars)
        logging.info("Script finished")
