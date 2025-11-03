#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Harshvardhan Sharma

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: risu
short_description: Run RISU diagnostics or list plugins on remote hosts
description:
  - This is a reusable, standalone Ansible module for interacting with RISU (Reliability, Interoperability, Supportability, Usability) diagnostic framework.
  - Works with any RISU installation (RPM, manual, pip) on any Linux distribution.
  - Supports listing plugins, running diagnostics, and validation.
  - Includes security best practices and timeout handling.
  - Can be used independently in any Ansible playbook or role.
  - No dependencies on specific project structures or configurations.
options:
  state:
    description: Action to perform
    type: str
    choices: [list, run, validate]
    default: list
  risu_path:
    description: Path to risu command or risu.py on the remote host
    type: str
    default: /usr/bin/risu
  filter:
    description: Include filter passed to RISU (-i)
    type: str
    required: false
  output:
    description: Output file for RISU results (run mode)
    type: str
    required: false
  output_format:
    description: Output format for results
    type: str
    choices: [json, html, text]
    default: json
  quiet:
    description: Pass -q to RISU to reduce noise
    type: bool
    default: true
  timeout:
    description: Timeout in seconds for RISU execution
    type: int
    default: 300
  async_mode:
    description: Enable async execution (for MCP integration)
    type: bool
    default: false
  job_id:
    description: Job ID for async tracking (MCP integration)
    type: str
    required: false
author:
  - Harshvardhan Sharma
"""

EXAMPLES = r"""
# Basic usage examples (standalone - works in any Ansible project)

- name: Validate RISU installation
  risu:
    state: validate

- name: List all available plugins
  risu:
    state: list
  register: risu_plugins

- name: List plugins by category
  risu:
    state: list
    filter: system
  register: system_plugins

- name: Run diagnostics and save results
  risu:
    state: run
    filter: security
    output: /var/log/risu/security-scan.json
    timeout: 300
  register: scan_results

- name: Run diagnostics with custom RISU path
  risu:
    state: run
    risu_path: /opt/risu/risu.py
    output: /tmp/custom-scan.json

- name: Use async mode for long-running scans
  risu:
    state: run
    filter: all
    output: /var/log/risu/full-scan.json
    async_mode: yes
    job_id: "scan-{{ ansible_date_time.epoch }}"
    timeout: 600
"""

RETURN = r"""
plugins:
  description: List of plugins (list state)
  type: list
  returned: when state == list
  sample: [{"backend": "core", "plugin": "/opt/risu/...sh", "category": "system"}]
plugin_count:
  description: Number of plugins found
  type: int
  returned: when state == list
  sample: 941
results:
  description: Parsed risu.json results (run state)
  type: dict
  returned: when state == run and output exists
output_file:
  description: Path to output file
  type: str
  returned: when state == run and output specified
  sample: "/tmp/risu.json"
summary:
  description: Summary of diagnostic results
  type: dict
  returned: when state == run
  sample: {"total_plugins": 100, "failed": 5, "skipped": 10, "passed": 85}
rc:
  description: Return code from RISU execution
  type: int
  returned: always
stdout:
  description: Command stdout
  type: str
  returned: always
stderr:
  description: Command stderr
  type: str
  returned: always
elapsed:
  description: Execution time in seconds
  type: float
  returned: always
  sample: 45.2
risu_version:
  description: RISU version information
  type: str
  returned: when state == validate
  sample: "RISU 3.1.4"
"""

import json
import os
import shutil
import subprocess
import tempfile
import time
import ast
from ansible.module_utils.basic import AnsibleModule


def normalize_filter(filter_value):
    """
    Normalize filter values for RISU.
    This function can be extended with custom normalizations as needed,
    but by default passes through the filter unchanged for maximum compatibility.
    
    Args:
        filter_value: The filter string to normalize
        
    Returns:
        Normalized filter string, or original if no normalization needed
    """
    if not filter_value:
        return filter_value
    
    # Apply any custom normalizations here if needed
    # Example for SLES-specific normalization (optional):
    # f = filter_value.strip().lower()
    # if f == "sles":
    #     return "/plugins/core/sles/"
    
    # Default: pass through unchanged for maximum compatibility
    return filter_value.strip()


def run_module():
    module_args = dict(
        state=dict(type="str", choices=["list", "run", "validate"], default="list"),
        risu_path=dict(type="str", default="/usr/bin/risu"),
        filter=dict(type="str", required=False),
        output=dict(type="str", required=False),
        output_format=dict(type="str", choices=["json", "html", "text"], default="json"),
        quiet=dict(type="bool", default=True),
        timeout=dict(type="int", default=300),
        async_mode=dict(type="bool", default=False),
        job_id=dict(type="str", required=False),
    )

    result = dict(
        changed=False,
        rc=0,
        stdout="",
        stderr="",
        elapsed=0
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)
    
    # Start timing
    start_time = time.time()

    state = module.params["state"]
    risu_path = module.params["risu_path"]
    filter_value = normalize_filter(module.params.get("filter"))
    output = module.params.get("output")
    output_format = module.params.get("output_format")
    quiet = module.params["quiet"]
    timeout = module.params["timeout"]
    async_mode = module.params["async_mode"]
    job_id = module.params.get("job_id")

    # Resolve 'risu' from PATH if user provided command name
    if os.path.basename(risu_path) == risu_path:
        resolved = shutil.which(risu_path)
        if resolved:
            risu_path = resolved

    # Validate RISU installation
    if not os.path.exists(risu_path) and not shutil.which(risu_path):
        module.fail_json(
            msg="RISU not found in PATH or at provided path",
            risu_path=risu_path,
            hint="Ensure RISU is installed. Try: risu --version or specify risu_path parameter."
        )

    # Handle validate state
    if state == "validate":
        try:
            cmd = [risu_path, "--version"]
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                env={**os.environ, 'PYTHONUNBUFFERED': '1'}
            )
            
            result['rc'] = proc.returncode
            result['stdout'] = proc.stdout
            result['stderr'] = proc.stderr
            result['elapsed'] = time.time() - start_time
            
            if proc.returncode == 0:
                # Extract version from output
                version_line = proc.stdout.strip().split('\n')[0]
                result['risu_version'] = version_line
                result['msg'] = f"RISU is installed and working: {version_line}"
            else:
                module.fail_json(msg="RISU validation failed", **result)
                
        except subprocess.TimeoutExpired:
            module.fail_json(msg="RISU validation timed out", elapsed=30)
        except Exception as e:
            module.fail_json(msg=f"Failed to validate RISU: {str(e)}")
        
        module.exit_json(**result)

    # Handle list state
    elif state == "list":
        cmd = [risu_path, "--list-plugins", "--list-categories", "--description"]
        if filter_value:
            cmd.extend(["-i", filter_value])
        if quiet:
            cmd.append("-q")
        
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
                env={**os.environ, 'PYTHONUNBUFFERED': '1'}
            )
            
            result['rc'] = proc.returncode
            result['stdout'] = proc.stdout
            result['stderr'] = proc.stderr
            result['elapsed'] = time.time() - start_time
            
            # Parse plugin output safely
            plugins = []
            for line in proc.stdout.splitlines():
                line = line.strip()
                if line.startswith("{") and "plugin" in line:
                    try:
                        # Try JSON first (safer)
                        plugin = json.loads(line.replace("'", '"'))
                        plugins.append(plugin)
                    except json.JSONDecodeError:
                        try:
                            # Fallback to ast.literal_eval (safer than eval)
                            plugin = ast.literal_eval(line)
                            plugins.append(plugin)
                        except (ValueError, SyntaxError):
                            # Skip malformed lines
                            continue
            
            result['plugins'] = plugins
            result['plugin_count'] = len(plugins)
            
            # Add summary by category
            by_category = {}
            for plugin in plugins:
                category = plugin.get('category', 'unknown')
                by_category[category] = by_category.get(category, 0) + 1
            result['plugins_by_category'] = by_category
            
            if proc.returncode != 0 and not plugins:
                module.fail_json(
                    msg="Failed to list plugins",
                    hint="Check RISU installation and permissions",
                    **result
                )
                
        except subprocess.TimeoutExpired:
            module.fail_json(
                msg=f"Plugin listing timed out after {timeout} seconds",
                elapsed=timeout
            )
        except Exception as e:
            module.fail_json(msg=f"Failed to list plugins: {str(e)}", **result)

    # Handle run state
    elif state == "run":
        cmd = [risu_path, "-l"]
        if filter_value:
            cmd.extend(["-i", filter_value])
        if quiet:
            cmd.append("-q")
        
        # Handle output file
        if output:
            cmd.extend(["--output", output])
            # Ensure output directory exists
            output_dir = os.path.dirname(output)
            if output_dir and not os.path.exists(output_dir):
                try:
                    os.makedirs(output_dir, mode=0o755)
                except OSError as e:
                    module.fail_json(msg=f"Failed to create output directory: {e}")
        else:
            # Create temporary output file for parsing
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                temp_output = f.name
            cmd.extend(["--output", temp_output])
        
        # Add format option if specified
        if output and output_format != 'json':
            if output_format == 'html':
                cmd.append("-h")
            elif output_format == 'text':
                cmd.append("-t")
        
        # Handle check mode
        if module.check_mode:
            result['msg'] = "Would run RISU diagnostics"
            result['cmd'] = ' '.join(cmd)
            module.exit_json(**result)
        
        try:
            # Record start for async tracking
            if async_mode and job_id:
                job_file = f"/tmp/risu-job-{job_id}.status"
                with open(job_file, 'w') as f:
                    json.dump({"status": "running", "started": time.time()}, f)
            
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
                env={**os.environ, 'PYTHONUNBUFFERED': '1'}
            )
            
            result['rc'] = proc.returncode
            result['stdout'] = proc.stdout
            result['stderr'] = proc.stderr
            result['elapsed'] = time.time() - start_time
            
            # Read and parse results
            output_file = output or temp_output
            if os.path.exists(output_file):
                result['output_file'] = output_file
                
                # Only parse JSON files
                if output_file.endswith('.json'):
                    try:
                        with open(output_file, 'r') as f:
                            data = json.load(f)
                        result['results'] = data
                        
                        # Generate summary
                        summary = {
                            "total_plugins": 0,
                            "failed": 0,
                            "passed": 0,
                            "skipped": 0,
                            "info": 0
                        }
                        
                        for plugin_id, plugin_result in data.get("results", {}).items():
                            summary["total_plugins"] += 1
                            if plugin_result:
                                rc = plugin_result.get("result", {}).get("rc", 0)
                                if rc == 0 or rc == 10:  # RC_OKAY
                                    summary["passed"] += 1
                                elif rc == 30:  # RC_SKIPPED
                                    summary["skipped"] += 1
                                elif rc == 40:  # RC_INFO
                                    summary["info"] += 1
                                else:
                                    summary["failed"] += 1
                        
                        result['summary'] = summary
                        
                        # Mark as changed if issues found
                        if summary["failed"] > 0:
                            result['changed'] = True
                            
                    except json.JSONDecodeError as e:
                        module.warn(f"Failed to parse JSON output: {e}")
                    except Exception as e:
                        module.warn(f"Failed to read output file: {e}")
                
                # Clean up temp file if used
                if not output and 'temp_output' in locals():
                    try:
                        os.unlink(temp_output)
                    except:
                        pass
            
            # Update job status for async mode
            if async_mode and job_id:
                with open(job_file, 'w') as f:
                    json.dump({
                        "status": "completed",
                        "started": time.time() - result['elapsed'],
                        "finished": time.time(),
                        "rc": proc.returncode,
                        "output_file": output_file if output else None
                    }, f)
                result['job_id'] = job_id
                result['job_file'] = job_file
            
        except subprocess.TimeoutExpired:
            module.fail_json(
                msg=f"RISU execution timed out after {timeout} seconds",
                hint="Increase timeout or use filter to reduce scope",
                elapsed=timeout
            )
        except Exception as e:
            module.fail_json(msg=f"Failed to run diagnostics: {str(e)}", **result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()


