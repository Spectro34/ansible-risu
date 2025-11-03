# Installation Guide

## Prerequisites

- Ansible 2.9 or higher
- Python 3.6+ on managed nodes
- RISU framework installed on target hosts

## Installing RISU

Before using this module, ensure RISU is installed on your target systems.

### Manual Installation

```bash
git clone https://github.com/risuorg/risu.git /opt/risu
cd /opt/risu
sudo ln -s /opt/risu/risu.py /usr/local/bin/risu
```

## Installing the Ansible Module

### Quick Start

```bash
# Clone the repository
git clone
cd ansible-risu

# Copy module to your project
mkdir -p ~/my-project/library
cp library/risu.py ~/my-project/library/

# Test it
cd ~/my-project
ansible localhost -m risu -a "state=validate"
```

### System-Wide Installation

```bash
# For all users
sudo mkdir -p /usr/share/ansible/plugins/modules/
sudo cp library/risu.py /usr/share/ansible/plugins/modules/

# Verify
ansible-doc risu
```

### Per-User Installation

```bash
# Create user module directory
mkdir -p ~/.ansible/plugins/modules/

# Copy module
cp library/risu.py ~/.ansible/plugins/modules/

# Verify
ansible localhost -m risu -a "state=validate"
```

### In an Ansible Role

```bash
# Add to your role structure
roles/
  your-role/
    library/
      risu.py  # Place module here
    tasks/
      main.yml
```

### Using Module Library Path

Add to your `ansible.cfg`:

```ini
[defaults]
library = ./library
```

Then copy the module:

```bash
mkdir -p library
cp path/to/ansible-risu/library/risu.py library/
```

## Verification

### Test Module Installation

```bash
# Check if module is available
ansible-doc -t module risu

# Quick test
ansible localhost -m risu -a "state=validate"
```

### Run Example Playbook

```bash
cd ansible-risu/examples
cp inventory.example inventory
# Edit inventory to add your hosts
ansible-playbook basic-usage.yml
```

## Configuration

### ansible.cfg Example

```ini
[defaults]
library = ./library
inventory = ./inventory
host_key_checking = False
```

### Inventory Setup

```ini
[risu_hosts]
server1.example.com
server2.example.com

[risu_hosts:vars]
ansible_user=root
ansible_python_interpreter=/usr/bin/python3
```

## Troubleshooting

### Module Not Found

If you get "module not found" error:

```bash
# Check module path
ansible-config dump | grep DEFAULT_MODULE_PATH

# Verify module is in one of those paths
ls -la ~/.ansible/plugins/modules/risu.py
```

### RISU Not Found on Target

If diagnostics fail with "RISU not found":

1. Verify RISU is installed:
   ```bash
   ansible your-host -m shell -a "which risu"
   ```

2. If not found, install RISU first (see above)

3. Or specify custom path:
   ```yaml
   - risu:
       state: validate
       risu_path: /opt/risu/risu.py
   ```

### Permission Issues

If you get permission errors:

```bash
# Ensure module is executable
chmod +x library/risu.py

# Check target system permissions
ansible your-host -m shell -a "ls -la /usr/bin/risu"
```