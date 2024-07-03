import paramiko
import subprocess
from pathlib import Path
import configparser
import docker
import sys
import os
import logging

def generate_ssh_key_pair(key_name="ansible_key", output_dir=Path.cwd()):
    private_key_path = output_dir / key_name
    public_key_path = private_key_path.with_suffix(".pub")

    # Generate SSH key pair if not exists
    if not private_key_path.exists() or not public_key_path.exists():
        subprocess.run(["ssh-keygen", "-t", "rsa", "-b", "2048", "-f", str(private_key_path), "-q", "-N", ""])
        print(f"Generated SSH key pair: {private_key_path} and {public_key_path}")
    else:
        print(f"SSH key pair already exists: {private_key_path} and {public_key_path}")

    return private_key_path, public_key_path

def upload_ssh_key(host, username, password, public_key_path, port=22):
    logging.info(f"Uploading SSH key to {host}, with username {username}, password {password}, on port {port}")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host, port=port, username=username, password=password)
        sftp = ssh.open_sftp()
        try:
            sftp.mkdir('.ssh')
        except IOError:
            pass
        sftp.close()
        public_key = public_key_path.read_text()
        ssh.exec_command(f'echo "{public_key}" >> ~/.ssh/authorized_keys')
        ssh.exec_command('chmod 600 ~/.ssh/authorized_keys')
        ssh.exec_command('chmod 700 ~/.ssh')
        print(f"Uploaded SSH key to {host}")
    except Exception as e:
        print(f"Failed to upload SSH key to {host}: {e}")
    finally:
        ssh.close()

def create_inventory_file(hosts_file, private_key_path, public_key_path, inventory_path="inventory.ini"):
    with open(hosts_file, 'r') as file:
        hosts = [line.strip() for line in file.readlines()]

    config = configparser.ConfigParser(allow_no_value=True)
    config.add_section('all')
    for host in hosts:
        config.set('all', host)
    
    config.add_section('all:vars')
    config.set('all:vars', 'ansible_ssh_user', 'ansible')
    config.set('all:vars', 'ansible_ssh_private_key_file', str(private_key_path))
    config.set('all:vars', 'ansible_ssh_public_key_file', str(public_key_path))
    config.set('all:vars', 'ansible_port', '2222')
    config.set('all:vars', 'ansible_user', 'ansible')
    config.set('all:vars', 'ansible_password', 'ansible')
    config.set('all:vars', 'ansible_ssh_common_args', '-o StrictHostKeyChecking=no')

    with open(inventory_path, 'w') as configfile:
        config.write(configfile)
    print(f"Created inventory file: {inventory_path}")

def run_ansible_playbook(playbook_path, inventory_path, extra_vars=None):
    """
    Run an Ansible playbook using a Docker container.
    
    :param playbook_path: Path to the Ansible playbook.
    :param inventory_path: Path to the inventory file.
    :param extra_vars: Additional variables to pass to the playbook (optional).
    """
    client = docker.from_env()

    volumes = {
        os.path.abspath(playbook_path): {'bind': '/home/ansible/playbook.yml', 'mode': 'ro'},
        os.path.abspath(inventory_path): {'bind': '/home/ansible/inventory.ini', 'mode': 'ro'}
    }

    command = ["ansible-playbook", "/home/ansible/playbook.yml", "-i", "/home/ansible/inventory.ini"]

    if extra_vars:
        command.extend(["--extra-vars", extra_vars])

    try:
        container = client.containers.run(
            "ansible-container", 
            command=command, 
            volumes=volumes, 
            remove=True,
            stdout=True,
            stderr=True
        )
        print(container.decode("utf-8"))
    except docker.errors.ContainerError as e:
        print("Error running Ansible playbook:", file=sys.stderr)
        print(e.stderr.decode("utf-8"), file=sys.stderr)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Prepare hosts for Ansible connections and run an Ansible playbook using a Docker container.")
    subparsers = parser.add_subparsers(dest="mode", help="Operation mode: setup or run")

    setup_parser = subparsers.add_parser("setup", help="Setup mode to prepare hosts and generate files")
    setup_parser.add_argument("--generate-key", action="store_true", help="Generate a new SSH key pair")
    setup_parser.add_argument("--import-key", help="Path to an existing private SSH key")
    setup_parser.add_argument("--upload-key", action="store_true", help="Upload the SSH key to the hosts")
    setup_parser.add_argument("--generate-inventory", action="store_true", help="Generate inventory.ini file from hosts.txt")
    setup_parser.add_argument("--hosts-file", help="Path to the .txt file containing the list of hosts")
    setup_parser.add_argument("--port", type=int, default=22, help="SSH port to use for uploading keys")

    run_parser = subparsers.add_parser("run", help="Run mode to execute an Ansible playbook")
    run_parser.add_argument("--playbook", required=True, help="Path to the Ansible playbook to run")
    run_parser.add_argument("--inventory", required=True, help="Path to the inventory file to use")
    run_parser.add_argument("--extra-vars", help="Additional variables to pass to the playbook")
    
    args = parser.parse_args()

    if args.mode == "setup":
        private_key_path, public_key_path = None, None

        # Generate or import SSH key pair
        if args.generate_key:
            private_key_path, public_key_path = generate_ssh_key_pair()
        elif args.import_key:
            private_key_path = Path(args.import_key)
            public_key_path = private_key_path.with_suffix(".pub")
            if not private_key_path.exists() or not public_key_path.exists():
                print("Specified SSH key pair does not exist.")
                sys.exit(1)
        else:
            print("You must specify either --generate-key or --import-key.")
            sys.exit(1)

        # Upload SSH key to each host
        if args.upload_key:
            if not args.hosts_file:
                print("You must specify --hosts-file to upload keys.")
                sys.exit(1)
            with open(args.hosts_file, 'r') as file:
                hosts = [line.strip() for line in file.readlines()]
            for host in hosts:
                upload_ssh_key(host, "ansible", "ansible", public_key_path, port=args.port)

        # Generate inventory file
        if args.generate_inventory:
            if not args.hosts_file:
                print("You must specify --hosts-file to generate inventory.")
                sys.exit(1)
            create_inventory_file(args.hosts_file, private_key_path, public_key_path)

    elif args.mode == "run":
        run_ansible_playbook(args.playbook, args.inventory, args.extra_vars)
