#!/usr/bin/env python3
"""
Flask - USB ISO Flashing Utility
A simple utility to flash ISO images to USB drives
"""

import os
import sys
import subprocess
import argparse
import time
from typing import List, Dict, Optional, Tuple


class Flask:
    def __init__(self):
        self.version = "1.0.0"
        self.supported_platforms = ["linux", "darwin"]
        self.platform = sys.platform
        self.check_platform()

    def check_platform(self):
        """Check if the current platform is supported."""
        if self.platform not in self.supported_platforms:
            print(f"Error: Flask is not compatible with {self.platform}.")
            print("Flask currently only supports Linux and macOS.")
            sys.exit(1)

    def list_available_devices(self) -> List[Dict[str, str]]:
        """List available USB devices."""
        devices = []

        if self.platform == "linux":
            # Get list of block devices
            lsblk_output = subprocess.check_output(
                ["lsblk", "-d", "-o", "NAME,SIZE,MODEL,MOUNTPOINT", "--json"],
                text=True
            )
            import json
            blockdevices = json.loads(lsblk_output)["blockdevices"]
            
            for device in blockdevices:
                # Only include removable devices (typically USB drives)
                if self.is_removable_linux(device["name"]):
                    devices.append({
                        "device": f"/dev/{device['name']}",
                        "size": device.get("size", "Unknown"),
                        "model": device.get("model", "Unknown"),
                        "mountpoint": device.get("mountpoint", "")
                    })
                    
        elif self.platform == "darwin":
            
            diskutil_output = subprocess.check_output(
                ["diskutil", "list", "-plist", "external", "physical"],
                text=True
            )
            
            import plistlib
            try:
                plist = plistlib.loads(diskutil_output.encode())
                for disk in plist.get("AllDisksAndPartitions", []):
                    disk_id = disk.get("DeviceIdentifier")
                    

                    disk_info = subprocess.check_output(
                        ["diskutil", "info", "-plist", f"/dev/{disk_id}"],
                        text=True
                    )
                    info = plistlib.loads(disk_info.encode())
                    
                    devices.append({
                        "device": f"/dev/{disk_id}",
                        "size": info.get("TotalSize", "Unknown"),
                        "model": info.get("MediaName", "Unknown"),
                        "mountpoint": info.get("MountPoint", "")
                    })
            except Exception as e:
                print(f"Error getting device information: {e}")

        return devices

    def is_removable_linux(self, device_name: str) -> bool:
        """Check if a Linux device is removable."""
        try:
            with open(f"/sys/block/{device_name}/removable", "r") as f:
                return f.read().strip() == "1"
        except FileNotFoundError:
            return False

    def print_devices(self, devices: List[Dict[str, str]]):
        """Print available devices in a formatted way."""
        if not devices:
            print("No USB devices found.")
            return

        print("\nAvailable USB devices:")
        print(f"{'Device':<15} {'Size':<10} {'Model':<20} {'Mountpoint':<15}")
        print("-" * 60)
        
        for i, device in enumerate(devices, 1):
            print(f"{device['device']:<15} {device['size']:<10} {device['model']:<20} {device['mountpoint']:<15}")

    def unmount_device(self, device: str) -> bool:
        """Unmount a device before flashing."""
        try:
            if self.platform == "linux":
                
                mounted = subprocess.run(
                    ["findmnt", device], 
                    capture_output=True
                ).returncode == 0
                
                if mounted:
                    subprocess.check_call(["umount", device])
                    print(f"Unmounted {device}")
                return True
                
            elif self.platform == "darwin":
                # On macOS, use diskutil
                subprocess.check_call(["diskutil", "unmountDisk", device])
                print(f"Unmounted {device}")
                return True
                
        except subprocess.CalledProcessError as e:
            print(f"Error unmounting device: {e}")
            return False
            
        return True

    def flash_iso(self, iso_path: str, device: str) -> bool:
        """Flash ISO image to USB device."""
        if not os.path.exists(iso_path):
            print(f"Error: ISO file '{iso_path}' does not exist.")
            return False
            
        if not self.unmount_device(device):
            return False
            
        print(f"Flashing {iso_path} to {device}...")
        print("This may take several minutes. Please do not remove the USB drive.")
        
        try:
            if self.platform == "linux" or self.platform == "darwin":
                # Use dd command for both Linux and macOS
                process = subprocess.Popen(
                    ["dd", f"if={iso_path}", f"of={device}", "bs=4M", "status=progress"],
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                
                # Show progress
                for line in process.stderr:
                    print(line, end="")
                    
                process.wait()
                if process.returncode != 0:
                    print("Error: Failed to flash ISO.")
                    return False
                    
                print("\nFlashing completed successfully!")
                print("Syncing file system...")
                subprocess.check_call(["sync"])
                print("Done. You can safely remove the USB drive.")
                return True
                
        except subprocess.CalledProcessError as e:
            print(f"Error flashing ISO: {e}")
            return False
            
        return False

    def verify_iso(self, iso_path: str, device: str) -> bool:
        """Verify the flashed ISO by comparing checksums."""
        print("Verifying flashed USB drive (this may take a while)...")
        
        try:
            # Calculate ISO checksum
            iso_md5 = subprocess.check_output(
                ["md5sum", iso_path], 
                text=True
            ).split()[0]
            
            # Calculate flashed device checksum (limited to ISO size)
            iso_size = os.path.getsize(iso_path)
            device_md5 = subprocess.check_output(
                f"dd if={device} bs=4M count={iso_size // (4 * 1024 * 1024) + 1} | md5sum",
                shell=True,
                text=True
            ).split()[0]
            
            if iso_md5 == device_md5:
                print("Verification successful! The USB drive matches the ISO image.")
                return True
            else:
                print("Verification failed. The USB drive does not match the ISO image.")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"Error during verification: {e}")
            return False

    def main(self):
        """Main entry point for the application."""
        parser = argparse.ArgumentParser(
            description="Flask - USB ISO Flashing Utility",
            epilog="Example: flask -i ubuntu.iso -d /dev/sdb"
        )
        
        parser.add_argument("-l", "--list", action="store_true", 
                            help="List available USB devices")
        parser.add_argument("-i", "--iso", type=str, 
                            help="Path to the ISO image file")
        parser.add_argument("-d", "--device", type=str, 
                            help="Device to flash (e.g., /dev/sdb)")
        parser.add_argument("-v", "--verify", action="store_true", 
                            help="Verify the flashed USB drive after writing")
        parser.add_argument("--version", action="store_true", 
                            help="Show Flask version")
        
        args = parser.parse_args()
        
        if args.version:
            print(f"Flask USB ISO Flashing Utility v{self.version}")
            return
            
        if args.list:
            devices = self.list_available_devices()
            self.print_devices(devices)
            return
            
        if args.iso and args.device:
            # Check if user is root (required for dd operations)
            if os.geteuid() != 0:
                print("Error: Flask requires root privileges to flash drives.")
                print("Please run with sudo or as root.")
                return
                
            success = self.flash_iso(args.iso, args.device)
            
            if success and args.verify:
                self.verify_iso(args.iso, args.device)
                
            return
            
        # If no valid arguments provided, show help
        parser.print_help()


if __name__ == "__main__":
    flask = Flask()
    flask.main()
