from dataclasses import dataclass
from typing import Optional
from pathlib import Path
from enum import Enum


class VMStorageController(Enum):
    IDE = "IDE Controller"
    SATA = "SATA Controller"


@dataclass
class VMConfig:
    name: str
    memory: int = 2048
    os_type: str = "Ubuntu"
    hdd_size: int = 20000  # in MB
    network_adapter: str = "en0"
    iso_path: str = "drivers/ubuntu-24.04-desktop-amd64.iso"
    vm_path: Optional[Path] = None

    def __post_init__(self):
        if self.vm_path is None:
            self.vm_path = Path(f"~/VirtualBox VMs/{self.name}/{self.name}.vdi").expanduser()



# EDIT VM CONFIG
# sudo nano /etc/guacamole/user-mapping.xml
#
# SHOW INFO
# vboxmanage showvminfo Kali-Linux-2021.3-vbox-amd64
#
# START VM
# vboxmanage startvm --type headless Kali-Linux-2021.3-vbox-amd64
#
# LIST VM
# vboxmanage list vms
# vboxmanage list runningvms
#
# STOP VM
# vboxmanage controlvm Kali-Linux-2021.3-vbox-amd64 poweroff
#
# GET IP + MAC
# VBoxManage guestproperty get "Kali-Linux-2021.3-vbox-amd64" "/VirtualBox/GuestInfo/Net/0/V4/IP"
# VBoxManage guestproperty get "Win7" "/VirtualBox/GuestInfo/Net/0/V4/IP"
# vboxmanage dhcpserver findlease --network ens3 --mac-address=08002756BB34
# vboxmanage dhcpserver findlease --network vboxnet0 --mac-address=08002756BB34
#
# MODIFY IF
# VBoxManage modifyvm $VM_NAME --nic2 hostonly --hostonlyadapter2 vboxnet0
# vboxmanage modifyvm Win7 --nic1 bridged --bridgeadapter1 eno1 ens3
#
# DHCP
# vboxmanage dhcpserver add --netname vboxnet0 --ip 192.168.2.1 --netmask 255.255.255.0 --lowerip 192.168.2.100 --upperip 192.168.2.200 --enable
# Virtual Box folder vbox file for each guest machine
#
#
# DELETE VM
# vboxmanage unregistervm UUID/VMNAME
# vboxmanage registervm '/home/ladmin/VirtualBox VMs/Win7/Win7.vbox'
#
# 4dd3769d-bcd1-4c52-a9bc-abf310591953 KALI
# 6a7254ad-1519-421a-a9a5-9c93f2288af7 WIN7
#
# TAKE SCREENSHOT
# vboxmanage controlvm Kali-Linux-2021.3-vbox-amd64 screenshotpng kali22screen.png
#
# IMPORT OVA
# vboxmanage import kali-linux-2021.3-virtualbox-amd64.ova --vsys 0 --eula accept
#
# EXT PACKS
# vboxmanage list extpacks
#
# CREATE VM
# vboxmanage createvm --name "KALI" --register
# VBoxManage modifyvm "WIN7" --memory 1024 --acpi on --boot1 dvd --nic1 bridged --bridgeadapter1 eth0 --ostype Ubuntu
# VBoxManage storagectl "KALI" --name "IDE Controller" --add ide
#
# DEBUG VM
# vboxmanage debugvm WIN7 osinfo
# vboxmanage showinfo --details ee17fa47-8177-4e5c-a7e7-43ad66e83b02 | fgrep MAC
