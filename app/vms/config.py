from dataclasses import dataclass
from typing import Optional
from pathlib import Path
from enum import Enum


class VMStorageController(Enum):
    IDE = "IDE Controller"
    SATA = "SATA Controller"


#
# class VirtualBoxConfig:
#     @staticmethod
#     def get_vboxmanage_path() -> str:
#         system = platform.system().lower()
#
#         if system == 'windows':
#             possible_paths = [
#                 r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe",
#                 r"C:\Program Files (x86)\Oracle\VirtualBox\VBoxManage.exe",
#             ]
#
#             for path in possible_paths:
#                 if os.path.exists(path):
#                     # Ensure Windows path format
#                     return path.replace('/', '\\')
#
#             raise FileNotFoundError(
#                 "VBoxManage.exe not found. Please install VirtualBox or add it to PATH"
#             )
#
#         elif system in ['linux', 'darwin']:  # Linux or MacOS
#             return 'vboxmanage'
#
#         raise NotImplementedError(f"System {system} not supported")
#

@dataclass
class VMConfig:
    name: str
    memory: int = 2048
    os_type: str = "Ubuntu"
    hdd_size: int = 20000  # in MB
    network_adapter: str = "en0"
    iso_path: str = "drivers/ubuntu-24.04-desktop-amd64.iso"
    vm_path: Optional[Path] = None

    # vboxmanage_path: str = VirtualBoxConfig.get_vboxmanage_path()

    def __post_init__(self):
        if self.vm_path is None:
            self.vm_path = Path(f"~/VirtualBox VMs/{self.name}/{self.name}.vdi").expanduser()

