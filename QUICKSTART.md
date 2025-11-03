# Quick Start Guide

Get started with the RISU Ansible module.

## Step 1: Install the Module

```bash
# Clone the repository
git clone https://github.com/your-repo/ansible-risu.git
cd ansible-risu

# Copy to your project
mkdir -p ~/my-ansible-project/library
cp library/risu.py ~/my-ansible-project/library/
```

## Step 2: Test the Module

```bash
cd ~/my-ansible-project

# Quick test on localhost
ansible localhost -m risu -a "state=validate"
```

Expected output:
```
localhost | SUCCESS => {
    "risu_version": "RISU version 3.1.4",
    "msg": "RISU is installed and working",
    "rc": 0,
    "elapsed": 0.5
}
```

## Step 3: Run Your First Diagnostic

Create a simple playbook `scan.yml`:

```yaml
---
- name: Run RISU diagnostics
  hosts: localhost
  tasks:
    - name: Run system scan
      risu:
        state: run
        filter: system
        output: /tmp/scan.json
      register: result
    
    - debug:
        msg: "Found {{ result.summary.failed }} issues"
```

Run it:

```bash
ansible-playbook scan.yml
```

## Step 4: Check Results

```bash
# View summary
cat /tmp/scan.json | python3 -m json.tool | head -20

# Or use jq if available
cat /tmp/scan.json | jq '.results | length'
```

## Step 5: Use in Your Playbooks

Now use it in any playbook:

```yaml
---
- name: Security scan
  hosts: production
  tasks:
    - name: Run security diagnostics
      risu:
        state: run
        filter: security
        output: /var/log/risu/security-{{ inventory_hostname }}.json
        timeout: 300
      register: scan
    
    - name: Fail if critical issues
      fail:
        msg: "{{ scan.summary.failed }} security issues found!"
      when: scan.summary.failed > 0
```

## Common Use Cases

### List Available Plugins

```yaml
- risu:
    state: list
  register: plugins

- debug:
    msg: "{{ plugins.plugin_count }} plugins available"
```

### Run with Custom RISU Path

```yaml
- risu:
    state: run
    risu_path: /opt/risu/risu.py
    output: /tmp/results.json
```

### Generate HTML Report

```yaml
- risu:
    state: run
    output: /var/www/html/report.html
    output_format: html
```

## Troubleshooting

### RISU Not Found

```bash
# Install RISU first
pip3 install risu
# or
sudo zypper install risu
```

### Module Not Found

```bash
# Verify module path
ls -la library/risu.py

# Or set in ansible.cfg
echo "[defaults]" > ansible.cfg
echo "library = ./library" >> ansible.cfg
```

### Permission Errors

```yaml
# Use become for system-level scans
- risu:
    state: run
  become: yes
```
