# Ansible RISU Module

A standalone, reusable Ansible module for interacting with the RISU diagnostic framework.

## Description

This module provides a interface to the [RISU](https://github.com/risuorg/risu) diagnostic framework. It can be used in any Ansible playbook or role without dependencies on specific project structures.

## Requirements

- Ansible 2.9 or higher
- Python 3.6+ on managed nodes
- RISU framework installed on target hosts

## Installation

### Copy to Your Project

```bash
# Copy module to your playbook directory
mkdir -p library/
wget https://raw.githubusercontent.com/ansible-risu/main/library/risu.py -O library/risu.py
```

### Install in Ansible Module Path

```bash
# System-wide installation
sudo mkdir -p /usr/share/ansible/plugins/modules/
sudo wget https://raw.githubusercontent.com/ansible-risu/main/library/risu.py \
     -O /usr/share/ansible/plugins/modules/risu.py

# Per-user installation
mkdir -p ~/.ansible/plugins/modules/
wget https://raw.githubusercontent.com/ansible-risu/main/library/risu.py \
     -O ~/.ansible/plugins/modules/risu.py
```

### Use in a Role

```bash
roles/
  your-role/
    library/
      risu.py  # Place module here
```

## Quick Start

### Validate RISU Installation

```yaml
- name: Check if RISU is installed
  risu:
    state: validate
  register: risu_status
```

### List Available Plugins

```yaml
- name: Get list of diagnostic plugins
  risu:
    state: list
  register: plugins

- debug:
    msg: "Found {{ plugins.plugin_count }} plugins"
```

### Run Diagnostics

```yaml
- name: Run system diagnostics
  risu:
    state: run
    filter: system
    output: /var/log/risu/scan.json
    timeout: 300
  register: results

- debug:
    msg: "Found {{ results.summary.failed }} issues"
```

## Module Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `state` | string | `list` | Action to perform: `list`, `run`, or `validate` |
| `risu_path` | string | `/usr/bin/risu` | Path to RISU executable |
| `filter` | string | - | Plugin filter pattern |
| `output` | string | - | Output file path |
| `output_format` | string | `json` | Output format: `json`, `html`, or `text` |
| `quiet` | boolean | `true` | Reduce verbosity |
| `timeout` | integer | `300` | Execution timeout in seconds |
| `async_mode` | boolean | `false` | Enable async execution |
| `job_id` | string | - | Job ID for async tracking |

## Examples

See the [examples](examples/) directory for complete playbook examples:

- [basic-usage.yml](examples/basic-usage.yml) - Simple diagnostic scan
- [compliance-scan.yml](examples/compliance-scan.yml) - Compliance checking
- [monitoring-integration.yml](examples/monitoring-integration.yml) - Integration with monitoring systems

## Return Values

| Key | Type | Description |
|-----|------|-------------|
| `rc` | int | Return code from RISU |
| `stdout` | string | Command output |
| `stderr` | string | Error output |
| `elapsed` | float | Execution time in seconds |
| `plugins` | list | List of plugins (when state=list) |
| `plugin_count` | int | Number of plugins found |
| `results` | dict | Diagnostic results (when state=run) |
| `summary` | dict | Summary with pass/fail/skip counts |
| `output_file` | string | Path to output file |

### Running Tests

```bash
# Syntax check
ansible-playbook examples/basic-usage.yml --syntax-check

# Dry run
ansible-playbook examples/basic-usage.yml --check

# Run on test hosts
ansible-playbook examples/basic-usage.yml -i inventory
```


## Author

Harshvardhan Sharma

## Acknowledgments

- RISU Framework Team - Original diagnostic framework
