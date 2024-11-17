import subprocess
from typing import Tuple, List, Dict, Union, Optional
import logging
import re
from .config import VMConfig, VMStorageController

logger = logging.getLogger(__name__)


class VirtualMachineService:
    def __init__(self, config: Optional[VMConfig] = None):
        self.config = config

    def _run_command(self, command: List[str], error_message: str) -> Tuple[bool, str]:
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            # Log the complete output for debugging
            logger.debug(f"Command stdout: {result.stdout}")
            logger.debug(f"Command stderr: {result.stderr}")
            logger.debug(f"Return code: {result.returncode}")
            if result.returncode == 0:
                return True, result.stdout
            return False, f"{error_message}: {result.stderr}"
        except subprocess.CalledProcessError as e:
            return False, f"{error_message}: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error during {error_message}: {str(e)}"

    def _parse_vm_info(self, vm_line: str) -> Optional[Dict[str, str]]:
        """Parse VM information from VBoxManage output line."""
        # VM line format: "VM Name" {uuid}
        match = re.match(r'"([^"]+)"\s+{([^}]+)}', vm_line.strip())
        if match:
            return {
                'name': match.group(1),
                'uuid': match.group(2)
            }
        return None

    def get_all_running_vms(self) -> Tuple[bool, Union[List[Dict[str, str]], str]]:
        """Get list of running VMs."""
        success, output = self._run_command(
            ['vboxmanage', 'list', 'runningvms'],
            "Failed to list running VMs"
        )

        if not success:
            logger.error(f"Failed to get running VMs: {output}")
            return False, output

        running_vms = []
        for line in output.splitlines():
            vm_info = self._parse_vm_info(line)
            if vm_info:
                # Get additional VM info if needed
                success, vm_details = self._get_vm_details(vm_info['uuid'])
                if success:
                    vm_info.update(vm_details)
                running_vms.append(vm_info)

        return True, running_vms

    def get_all_vms(self) -> Tuple[bool, Union[List[Dict[str, str]], str]]:
        """Get list of VMs."""
        success, output = self._run_command(
            ['vboxmanage', 'list', 'vms'],
            "Failed to list VMs"
        )

        if not success:
            logger.error(f"Failed to get VMs: {output}")
            return False, output

        vms = []
        for line in output.splitlines():
            vm_info = self._parse_vm_info(line)
            if vm_info:
                # Get additional VM info if needed
                success, vm_details = self._get_vm_details(vm_info['uuid'])
                if success:
                    vm_info.update(vm_details)
                vms.append(vm_info)

        return True, vms

    def _get_vm_details(self, uuid: str) -> Tuple[bool, Union[List[Dict[str, str]], str]]:
        """Get detailed information about a specific VM."""
        success, output = self._run_command(
            ['vboxmanage', 'showvminfo', uuid, '--machinereadable'],
            f"Failed to get VM details for {uuid}"
        )

        if not success:
            return False, output

        details = {}
        for line in output.splitlines():
            if '=' in line:
                key, value = line.split('=', 1)
                # Remove quotes from value if present
                value = value.strip('"')
                details[key] = value

        return True, {
            'memory': details.get('memory', 'N/A'),
            'cpus': details.get('cpus', 'N/A'),
            'os_type': details.get('ostype', 'N/A'),
            'state': details.get('VMState', 'N/A')
        }

    # Your existing methods remain the same
    def create_vm(self) -> Tuple[bool, str]:
        """Create a new virtual machine with the current configuration."""
        if not self.config:
            return False, "No configuration provided"

        steps = [
            (self._create_base_vm, "Creating base VM"),
            (self._modify_vm_settings, "Modifying VM settings"),
            (self._add_storage_controllers, "Adding storage controllers"),
            (self._create_and_attach_hard_disk, "Creating and attaching hard disk"),
            (self._attach_iso, "Attaching ISO"),
            (self._start_vm, "Starting VM")
        ]

        for step_func, step_name in steps:
            success, message = step_func()
            if not success:
                logger.error(f"Failed at step '{step_name}': {message}")
                return False, f"Failed at {step_name}: {message}"
            logger.info(f"Successfully completed: {step_name}")

        return True, "VM created and started successfully"

    def _create_base_vm(self) -> Tuple[bool, str]:
        command = [
            'vboxmanage', 'createvm',
            '--name', self.config.name,
            '--register'
        ]
        return self._run_command(command, "Failed to create base VM")

    def _create_base_vm(self) -> Tuple[bool, str]:
        """Create the base VM."""
        command = [
            'vboxmanage', 'createvm',
            '--name', self.config.name,
            '--register'
        ]
        return self._run_command(command, "Failed to create base VM")

    def _modify_vm_settings(self) -> Tuple[bool, str]:
        """Modify VM settings with memory, network, etc."""
        command = [
            'vboxmanage', 'modifyvm', self.config.name,
            '--memory', str(self.config.memory),
            '--acpi', 'on',
            '--boot1', 'dvd',
            '--nic1', 'bridged',
            '--bridgeadapter1', self.config.network_adapter,
            '--ostype', self.config.os_type
        ]
        return self._run_command(command, "Failed to modify VM settings")

    def _add_storage_controllers(self) -> Tuple[bool, str]:
        """Add IDE and SATA controllers."""
        # Add IDE Controller
        success, message = self._run_command(
            ['vboxmanage', 'storagectl', self.config.name,
             '--name', 'IDE Controller', '--add', 'ide'],
            "Failed to add IDE controller"
        )
        if not success:
            return False, message

        # Add SATA Controller
        return self._run_command(
            ['vboxmanage', 'storagectl', self.config.name,
             '--name', 'SATA Controller', '--add', 'sata'],
            "Failed to add SATA controller"
        )

    def _create_and_attach_hard_disk(self) -> Tuple[bool, str]:
        """Create and attach the virtual hard disk."""
        # Create HDD
        vdi_path = f"~/VirtualBox VMs/{self.config.name}/{self.config.name}.vdi"
        success, message = self._run_command(
            ['vboxmanage', 'createhd',
             '--filename', vdi_path,
             '--size', str(self.config.hdd_size)],
            "Failed to create virtual hard disk"
        )
        if not success:
            return False, message

        # Attach HDD
        return self._run_command(
            ['vboxmanage', 'storageattach', self.config.name,
             '--storagectl', 'SATA Controller',
             '--port', '0',
             '--device', '0',
             '--type', 'hdd',
             '--medium', vdi_path],
            "Failed to attach virtual hard disk"
        )

    def _attach_iso(self) -> Tuple[bool, str]:
        """Attach the ISO image."""
        return self._run_command(
            ['vboxmanage', 'storageattach', self.config.name,
             '--storagectl', 'IDE Controller',
             '--port', '1',
             '--device', '0',
             '--type', 'dvddrive',
             '--medium', self.config.iso_path],

            "Failed to attach ISO"
        )

    def _start_vm(self) -> Tuple[bool, str]:
        """Start the virtual machine."""
        return self._run_command(
            ['vboxmanage', 'startvm', self.config.name, '--type', 'gui'],
            "Failed to start VM"
        )

    def start_vm(self, uuid: str) -> Tuple[bool, str]:
        """Start a virtual machine by UUID."""
        logger.info(f"Starting VM with UUID: {uuid}")

        # First check if VM exists and get its current state
        success, output = self._run_command(
            ['vboxmanage', 'showvminfo', uuid, '--machinereadable'],
            f"Failed to get VM info for {uuid}"
        )

        if not success:
            return False, f"Failed to find VM with UUID {uuid}"

        # Parse the VM state
        vm_state = None
        for line in output.splitlines():
            if line.startswith('VMState='):
                vm_state = line.split('=')[1].strip('"')
                break

        # Check if VM is already running
        if vm_state == "running":
            return False, "VM is already running"

        # Start the VM
        success, output = self._run_command(
            ['vboxmanage', 'startvm', uuid, '--type', 'gui'],
            f"Failed to start VM {uuid}"
        )

        if success:
            logger.info(f"Successfully started VM {uuid}")
            return True, "VM started successfully"
        else:
            logger.error(f"Failed to start VM {uuid}: {output}")
            return False, output

    def stop_vm(self, uuid: str) -> Tuple[bool, str]:
        """Stop a virtual machine by UUID."""
        logger.info(f"Stopping VM with UUID: {uuid}")

        # First verify VM is running
        success, output = self._run_command(
            ['vboxmanage', 'showvminfo', uuid, '--machinereadable'],
            f"Failed to get VM info for {uuid}"
        )

        if not success:
            return False, f"Failed to find VM with UUID {uuid}"

        # Parse the VM state
        vm_state = None
        for line in output.splitlines():
            if line.startswith('VMState='):
                vm_state = line.split('=')[1].strip('"')
                break

        if vm_state != "running":
            return False, "VM is not running"

        # Stop the VM (using ACPI power button - safer than poweroff)
        success, output = self._run_command(
            ['vboxmanage', 'controlvm', uuid, 'poweroff'],
            f"Failed to stop VM {uuid}"
        )

        if success:
            logger.info(f"Successfully initiated shutdown of VM {uuid}")
            return True, "VM shutdown initiated"
        else:
            logger.error(f"Failed to stop VM {uuid}: {output}")
            return False, output

    def pause_vm(self, uuid: str) -> Tuple[bool, str]:
        """Pause a running virtual machine."""
        logger.info(f"Pausing VM with UUID: {uuid}")

        # First verify VM is running
        success, output = self._run_command(
            ['vboxmanage', 'showvminfo', uuid, '--machinereadable'],
            f"Failed to get VM info for {uuid}"
        )

        if not success:
            return False, f"Failed to find VM with UUID {uuid}"

        # Parse the VM state
        vm_state = None
        for line in output.splitlines():
            if line.startswith('VMState='):
                vm_state = line.split('=')[1].strip('"')
                break

        if vm_state != "running":
            return False, "VM is not running"

        # Pause the VM
        success, output = self._run_command(
            ['vboxmanage', 'controlvm', uuid, 'pause'],
            f"Failed to pause VM {uuid}"
        )

        if success:
            logger.info(f"Successfully paused VM {uuid}")
            return True, "VM paused successfully"
        else:
            logger.error(f"Failed to pause VM {uuid}: {output}")
            return False, output

    def delete_vm(self, uuid: str, delete_files: bool = True) -> Tuple[bool, str]:
        """
        Delete a virtual machine.

        Args:
            uuid: The UUID of the VM to delete
            delete_files: If True, also deletes all associated files
        """
        logger.info(f"Deleting VM with UUID: {uuid}")

        # First check if VM exists and get its state
        success, output = self._run_command(
            ['vboxmanage', 'showvminfo', uuid, '--machinereadable'],
            f"Failed to get VM info for {uuid}"
        )

        if not success:
            return False, f"Failed to find VM with UUID {uuid}"

        # Parse VM state and name
        vm_state = None
        vm_name = None
        for line in output.splitlines():
            if line.startswith('VMState='):
                vm_state = line.split('=')[1].strip('"')
            elif line.startswith('name='):
                vm_name = line.split('=')[1].strip('"')

        # If VM is running, stop it first
        if vm_state == "running":
            success, message = self.stop_vm(uuid)
            if not success:
                return False, f"Failed to stop running VM: {message}"

            # Wait for VM to stop
            import time
            for _ in range(30):  # Wait up to 30 seconds
                success, vm_details = self._get_vm_details(uuid)
                if success and vm_details['state'] != "running":
                    break
                # time.sleep(1)

        # Unregister and optionally delete files
        # time.sleep(2)
        delete_option = '--delete' if delete_files else ''
        success, message = self._run_command(
            ['vboxmanage', 'unregistervm', uuid, delete_option],
            f"Failed to delete VM {uuid}"
        )

        if success:
            logger.info(f"Successfully deleted VM {uuid}")
            return True, "VM deleted successfully"
        else:
            logger.error(f"Failed to delete VM {uuid}: {message}")
            return False, message
