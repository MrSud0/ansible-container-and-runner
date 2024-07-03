import argparse
import configparser

def generate_inventory(unix_hosts_file, win_hosts_file, ssh_hosts_file, ansible_user, ansible_password, ansible_port, ssh_private_key, ssh_public_key, inventory_path='inventory.ini'):
    config = configparser.ConfigParser(allow_no_value=True)
    
    # Read the UNIX hosts from the file
    with open(unix_hosts_file, 'r') as file:
        unix_hosts = [line.strip() for line in file.readlines()]

    # Read the Windows hosts from the file
    with open(win_hosts_file, 'r') as file:
        win_hosts = [line.strip() for line in file.readlines()]

    # Read the SSH hosts from the file
    with open(ssh_hosts_file, 'r') as file:
        ssh_hosts = [line.strip() for line in file.readlines()]

    # All hosts
    config.add_section('all')

    # UNIX hosts
    config.add_section('UNIX')
    for host in unix_hosts:
        config.set('UNIX', host)

    # WINDOWS hosts
    config.add_section('WINDOWS')
    for host in win_hosts:
        config.set('WINDOWS', host)

    # SSH hosts
    config.add_section('SSH')
    for host in ssh_hosts:
        config.set('SSH', host)
    
    # all:vars
    config.add_section('all:vars')
    
    # UNIX:vars
    config.add_section('UNIX:vars')
    config.set('UNIX:vars', 'ansible_user', ansible_user)
    config.set('UNIX:vars', 'ansible_password', ansible_password)
    config.set('UNIX:vars', 'ansible_connection', 'ssh')
    config.set('UNIX:vars', 'ansible_port', str(ansible_port))
    config.set('UNIX:vars', 'ansible_ssh_private_key_file', ssh_private_key)
    config.set('UNIX:vars', 'ansible_ssh_public_key_file', ssh_public_key)
    config.set('UNIX:vars', 'ansible_ssh_common_args', "'-o StrictHostKeyChecking=no'")
    
    # WINDOWS:vars
    config.add_section('WINDOWS:vars')
    config.set('WINDOWS:vars', 'ansible_user', ansible_user)
    config.set('WINDOWS:vars', 'ansible_password', ansible_password)
    config.set('WINDOWS:vars', 'ansible_connection', 'winrm')
    config.set('WINDOWS:vars', 'ansible_winrm_server_cert_validation', 'ignore')
    config.set('WINDOWS:vars', 'ansible_winrm_transport', 'ntlm')
    
    # SSH:vars
    config.add_section('SSH:vars')
    config.set('SSH:vars', 'ansible_user', ansible_user)
    config.set('SSH:vars', 'ansible_password', ansible_password)
    config.set('SSH:vars', 'ansible_connection', 'ssh')
    config.set('SSH:vars', 'ansible_port', str(ansible_port))
    config.set('SSH:vars', 'ansible_ssh_private_key_file', ssh_private_key)
    config.set('SSH:vars', 'ansible_ssh_public_key_file', ssh_public_key)
    config.set('SSH:vars', 'ansible_ssh_common_args', "'-o StrictHostKeyChecking=no'")
    
    with open(inventory_path, 'w') as configfile:
        config.write(configfile)
    print(f"Created inventory file: {inventory_path}")

def main():
    parser = argparse.ArgumentParser(description='Generate an Ansible inventory file.')
    parser.add_argument('--unix_hosts_file', type=str, default='unix_hosts.txt', help='Path to the UNIX hosts file (default: unix_hosts.txt)')
    parser.add_argument('--win_hosts_file', type=str, default='win_hosts.txt', help='Path to the Windows hosts file (default: win_hosts.txt)')
    parser.add_argument('--ssh_hosts_file', type=str, default='ssh_hosts.txt', help='Path to the SSH hosts file (default: ssh_hosts.txt)')
    parser.add_argument('--ansible_user', type=str, default='ansible', help='Ansible user name (default: ansible)')
    parser.add_argument('--ansible_password', type=str, default='ComplexPassw0rd!', help='Ansible password (default: ComplexPassw0rd!)')
    parser.add_argument('--ansible_port', type=int, default=22, help='Ansible SSH port (default: 22)')
    parser.add_argument('--ssh_private_key', type=str, default='ansible_key', help='Path to the SSH private key file (default: ansible_key)')
    parser.add_argument('--ssh_public_key', type=str, default='ansible_key.pub', help='Path to the SSH public key file (default: ansible_key.pub)')
    parser.add_argument('--inventory_path', type=str, default='inventory.ini', help='Path to the inventory file (default: inventory.ini)')

    args = parser.parse_args()

    generate_inventory(args.unix_hosts_file, args.win_hosts_file, args.ssh_hosts_file, args.ansible_user, args.ansible_password, args.ansible_port, args.ssh_private_key, args.ssh_public_key, args.inventory_path)

if __name__ == "__main__":
    main()
