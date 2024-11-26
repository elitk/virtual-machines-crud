import platform
import subprocess
from datetime import datetime
from typing import Tuple, List, Dict, Union, Optional
import logging
import re
from .config import VMConfig, VirtualBoxConfig
from pathlib import Path
logger = logging.getLogger(__name__)


class VirtualMachineService:
    def __init__(self, config: Optional[VMConfig] = None):
        self.config = config
        try:
            # Get VBoxManage path first
            self.vboxmanage = VirtualBoxConfig.get_vboxmanage_path()
            if not self.vboxmanage:
                raise ValueError("VBoxManage path not found")

            # Then initialize config
            self.config = VMConfig(name="default")

            logger.info(f"VirtualBox initialized with VBoxManage at: {self.vboxmanage}")
        except Exception as e:
            logger.error(f"Failed to initialize VirtualBox service: {str(e)}")
            raise

    def _get_create_vm_command(self, vm_config: VMConfig) -> List[str]:
        """Generate create VM command based on OS."""
        system = platform.system().lower()

        base_command = [
            self.vboxmanage,
            'createvm',
            '--name', vm_config.name,
            '--register'
        ]

        # Windows uses backslashes and requires different quoting
        if system == 'windows':
            base_command = [
                self.vboxmanage,
                'createvm',
                '--name', f'"{vm_config.name}"',  # Quote the name
                '--register'
            ]
            # Ensure Windows path format
            if isinstance(self.vboxmanage, str):
                self.vboxmanage = self.vboxmanage.replace('/', '\\')

        return base_command

    def _run_command(self, command: List[str], error_message: str) -> Tuple[bool, str]:
        try:
            command[0] = self.vboxmanage
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

    def get_vm_by_uuid(self, uuid: str) -> Tuple[bool, Union[Dict[str, str], str]]:
        """Get VM information by UUID."""
        success, output = self._run_command(
            ['vboxmanage', 'showvminfo', uuid, '--machinereadable'],
            f"Failed to get VM info for {uuid}"
        )

        if not success:
            logger.error(f"Failed to get VM info for {uuid}: {output}")
            return False, output

        details = {}
        for line in output.splitlines():
            if '=' not in line:
                continue

            try:
                key, value = line.split('=', 1)
                # Remove quotes from value if present
                value = value.strip('"')
                details[key] = value
            except ValueError:
                # Handle case where split fails
                logger.warning(f"Invalid line format: {line}")
                continue

        return True, details

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

        return self._get_vms_with_details(output.splitlines())

    def get_all_vms(self) -> Tuple[bool, Union[List[Dict[str, str]], str]]:
        """Get list of VMs."""
        success, output = self._run_command(
            ['vboxmanage', 'list', 'vms'],
            "Failed to list VMs"
        )

        if not success:
            logger.error(f"Failed to get VMs: {output}")
            return False, output

        success_details, detailed_vms = self._get_vms_with_details(output.splitlines())
        return success_details, detailed_vms
        # return self._get_vms_with_details(output.splitlines())

    def _get_vms_with_details(self, vm_list: list) -> Tuple[bool, list]:
        """Get detailed information for a list of VMs."""
        detailed_vms = []

        for line in vm_list:
            vm_info = self._parse_vm_info(line)
            if vm_info:
                success, vm_details = self.get_vm_by_uuid(vm_info['uuid'])
                if success:
                    vm_info.update(vm_details)
                detailed_vms.append(vm_info)

        return True, detailed_vms

    # Your existing methods remain the same
    def create_vm(self) -> Tuple[bool, str]:
        """Create a new virtual machine with the current configuration."""
        if not self.config:
            return False, "No configuration provided"

        steps = [
            (self._create_base_vm(self.config), "Creating base VM"),
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

    def _create_base_vm(self, vm_config: VMConfig) -> Tuple[bool, str]:
        """Create the base VM."""
        try:
            # Create VM
            create_command = self._get_create_vm_command(vm_config)
            success, output = self._run_command(
                create_command,
                "Failed to create base VM"
            )
            if not success:
                return False, f"Failed to create base VM: {output}"

            command = [
                'vboxmanage', 'createvm',
                '--name', self.config.name,
                '--register'
            ]
            return self._run_command(command, "Failed to create base VM")
        except Exception as e:
            return False, str(e)

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

        # Get VM info using existing function
        success, vm_details = self.get_vm_by_uuid(uuid)
        if not success:
            return False, f"Failed to find VM with UUID {uuid}"

            # Check VM state
        vm_state = vm_details.get('VMState')
        if vm_state == "running":
            return False, "VM is already running"

        # Start the VM
        success, output = self._run_command(
            ['vboxmanage', 'startvm', uuid, '--type', 'headless'],
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

        # Get VM info using existing function
        success, vm_details = self.get_vm_by_uuid(uuid)
        if not success:
            return False, f"Failed to find VM with UUID {uuid}"

            # Check VM state
        vm_state = vm_details.get('VMState')
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

        # Get VM info using existing function
        success, vm_details = self.get_vm_by_uuid(uuid)
        if not success:
            return False, f"Failed to find VM with UUID {uuid}"

            # Check VM state
        vm_state = vm_details.get('VMState')
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

        # Get VM info using existing function
        success, vm_details = self.get_vm_by_uuid(uuid)
        if not success:
            return False, f"Failed to find VM with UUID {uuid}"

            # Check VM state
        vm_state = vm_details.get('VMState')
        if vm_state == "running":
            success, message = self.stop_vm(uuid)
            if not success:
                return False, f"Failed to stop running VM: {message}"

            # Wait for VM to stop
            for _ in range(30):  # Wait up to 30 seconds
                if success and vm_state != "running":
                    break

        # Unregister and optionally delete files
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

    def edit_vm(self, uuid: str, vm: dict) -> Tuple[bool, str]:
        """Edit VM settings."""
        logger.info(f"Editing VM with UUID: {uuid}")

        try:
            # First check if VM exists
            success, output = self._run_command(
                ['vboxmanage', 'showvminfo', uuid, '--machinereadable'],
                f"Failed to get VM info for {uuid}"
            )

            if not success:
                return False, f"Failed to find VM with UUID {uuid}"

            # Modify VM settings
            memory = vm.get('memory', 2048)
            cpus = vm.get('cpus', 1)
            name = vm.get('name', 'Kali')
            success, message = self._run_command(
                ['vboxmanage', 'modifyvm', uuid,
                 '--name', name,
                 '--memory', str(memory),
                 '--cpus', str(cpus)],
                f"Failed to modify VM {uuid}"
            )

            if success:
                logger.info(f"Successfully modified VM {uuid}")
                return True, "VM modified successfully"
            else:
                logger.error(f"Failed to modify VM {uuid}: {message}")
                return False, message
        except Exception as e:
            return False, str(e)

    def take_screenshot(self, uuid: str) -> Tuple[bool, str]:
        """Take a screenshot of the VM."""
        try:
            # Create screenshots directory using absolute path
            base_dir = Path(__file__).parent.parent  # Go up one directory from current file
            screenshot_dir = base_dir / 'static' / 'screenshots'
            screenshot_dir.mkdir(parents=True, exist_ok=True)

            # Generate unique filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{screenshot_dir}/vm_{uuid}_{timestamp}.png"

            success, output = self._run_command(
                ['vboxmanage', 'controlvm', uuid, 'screenshotpng', filename],
                f"Failed to take screenshot for VM {uuid}"
            )

            if success:
                return True, filename
            return False, f"Failed to take screenshot: {output}"

        except Exception as e:
            logger.error(f"Error taking screenshot: {str(e)}")
            return False, f"Error taking screenshot: {str(e)}"
