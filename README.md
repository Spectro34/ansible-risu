# Ansible RISU Module

A standalone, reusable Ansible module for interacting with the RISU diagnostic framework.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Ansible](https://img.shields.io/badge/Ansible-2.9%2B-red.svg)](https://www.ansible.com/)

## Description

This module provides a secure, production-ready interface to the [RISU](https://github.com/risuorg/risu) diagnostic framework. It can be used in any Ansible playbook or role without dependencies on specific project structures.

## Features

- ✅ **Standalone** - Works independently in any Ansible project
- ✅ **Security Hardened** - Uses subprocess.run(), no eval()
- ✅ **Distribution Agnostic** - Works with RPM, pip, or manual RISU installations
- ✅ **Timeout Support** - Configurable execution timeouts
- ✅ **Async Mode** - Support for long-running diagnostics
- ✅ **Multiple Output Formats** - JSON, HTML, or text
- ✅ **Check Mode** - Dry-run support

## Requirements

- Ansible 2.9 or higher
- Python 3.6+ on managed nodes
- RISU framework installed on target hosts

## Installation

### Method 1: Copy to Your Project

```bash
# Copy module to your playbook directory
mkdir -p library/
wget https://raw.githubusercontent.com/your-repo/ansible-risu/main/library/risu.py -O library/risu.py
```

### Method 2: Install in Ansible Module Path

```bash
# System-wide installation
sudo mkdir -p /usr/share/ansible/plugins/modules/
sudo wget https://raw.githubusercontent.com/your-repo/ansible-risu/main/library/risu.py \
     -O /usr/share/ansible/plugins/modules/risu.py

# Per-user installation
mkdir -p ~/.ansible/plugins/modules/
wget https://raw.githubusercontent.com/your-repo/ansible-risu/main/library/risu.py \
     -O ~/.ansible/plugins/modules/risu.py
```

### Method 3: Use in a Role

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

## Development

### Running Tests

```bash
# Syntax check
ansible-playbook examples/basic-usage.yml --syntax-check

# Dry run
ansible-playbook examples/basic-usage.yml --check

# Run on test hosts
ansible-playbook examples/basic-usage.yml -i inventory
```

### Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## Compatibility

### RISU Installations

- ✅ RPM packages (SUSE, RHEL, Fedora)
- ✅ pip installations
- ✅ Manual installations from source

### Linux Distributions

- ✅ SUSE Linux Enterprise Server (SLES)
- ✅ openSUSE
- ✅ Red Hat Enterprise Linux (RHEL)
- ✅ CentOS / Rocky / Alma Linux
- ✅ Fedora
- ✅ Ubuntu / Debian

### Ansible Versions

- ✅ Ansible 2.9+
- ✅ Ansible Core 2.11+
- ✅ Ansible 5.x - 8.x

## Security

This module implements security best practices:

- No use of `os.system()` or `eval()`
- Proper subprocess handling with timeouts
- Safe JSON/AST parsing
- No hardcoded credentials
- Input validation and sanitization

## License

GNU General Public License v3.0

See [LICENSE](LICENSE) for the full license text.

## Author

Harshvardhan Sharma

## Acknowledgments

- RISU Framework Team - Original diagnostic framework
- Ansible Community - Module development patterns

## Support

- **Issues**: https://github.com/your-repo/ansible-risu/issues
- **RISU Documentation**: https://github.com/risuorg/risu
- **Ansible Documentation**: https://docs.ansible.com/

## Related Projects

- [RISU Framework](https://github.com/risuorg/risu) - The diagnostic framework this module interfaces with
- [Ansible](https://github.com/ansible/ansible) - Automation platform
