import os
import platform
from dataclasses import dataclass
from typing import Optional
from pathlib import Path
from enum import Enum


class VMStorageController(Enum):
    IDE = "IDE Controller"
    SATA = "SATA Controller"


class VirtualBoxConfig:
    @staticmethod
    def get_vboxmanage_path() -> str:
        """Get VBoxManage path based on OS."""
        system = platform.system().lower()
        if system == 'windows':
            paths = [
                r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe",
                r"C:\Program Files (x86)\Oracle\VirtualBox\VBoxManage.exe"
            ]
            for path in paths:
                if os.path.exists(path):
                    return path
            raise FileNotFoundError("VBoxManage.exe not found")

        if system == 'darwin':  # macOS
            # Common Mac paths
            paths = [
                '/Applications/VirtualBox.app/Contents/MacOS/VBoxManage',
                '/usr/local/bin/vboxmanage',
                '/opt/homebrew/bin/vboxmanage',
                'vboxmanage'  # if in PATH
            ]
            for path in paths:
                if os.path.exists(path):
                    return path
            raise FileNotFoundError("VBoxManage not found")
        return 'vboxmanage'  # For Mac/Linux where it's in PATH


@dataclass
class VMConfig:
    name: str
    memory: int = 2048
    os_type: str = "Ubuntu"
    hdd_size: int = 20000  # in MB
    network_adapter: str = "en0"
    iso_path: str = "drivers/ubuntu-24.04-desktop-amd64.iso"
    vm_path: Optional[Path] = None
    vboxmanage_path: str = VirtualBoxConfig.get_vboxmanage_path()

    def __post_init__(self):
        if self.vm_path is None:
            self.vm_path = Path(f"~/VirtualBox VMs/{self.name}/{self.name}.vdi").expanduser()
