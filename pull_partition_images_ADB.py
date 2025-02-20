import os
import platform
import shutil
import subprocess
from tqdm import tqdm

def check_adb():
    """Check if ADB is installed and accessible."""
    try:
        subprocess.run(["adb", "version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print("Error: ADB is not installed or not in PATH.")
        exit(1)

def get_device():
    """Check if a device is connected."""
    result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
    devices = result.stdout.strip().split("\n")[1:]
    
    if not devices or devices[0] == "":
        print("No device found. Make sure USB debugging is enabled.")
        exit(1)
    
    return devices[0].split("\t")[0]

def check_root():
    """Check if the device is rooted."""
    try:
        result = subprocess.run(["adb", "shell", "which su"], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            return True
        else:
            return False
    except Exception as e:
        print(f"Error while checking root status: {e}")
        return False

def get_partition_category(partition_name):
    """Map partition names to known categories."""
    categories = {
        "boot": "Bootloader",
        "recovery": "Recovery",
        "system": "Android System",
        "vendor": "Vendor Data",
        "userdata": "User Data",
        "cache": "Cache",
        "metadata": "Metadata",
        "modem": "Modem Firmware",
        "persist": "Persistent Storage",
        "dtbo": "Device Tree Blob",
        "vbmeta": "Verified Boot Metadata"
    }
    
    for key in categories:
        if key in partition_name.lower():
            return categories[key]
    
    return "Unknown"

def list_partitions():
    """Retrieve and display partitions with proper labels."""
    partitions = []
    
    result = subprocess.run(["adb", "shell", "ls -l /dev/block/by-name"], capture_output=True, text=True)
    if result.returncode == 0:
        for line in result.stdout.split("\n"):
            if "->" in line:
                parts = line.split()
                partition_label = parts[-3]  # Extract the partition name from symlink
                partition_name = parts[-1].split("/")[-1]  # Get actual block name
                category = get_partition_category(partition_label)
                partitions.append((partition_name, partition_label, category))
    
    if not partitions:
        print("Warning: Could not retrieve named partitions. Using generic mmcblk partitions.")
        result = subprocess.run(["adb", "shell", "ls /dev/block"], capture_output=True, text=True)
        partitions = [(line.strip(), line.strip(), "Unknown") for line in result.stdout.split("\n") if "mmcblk0p" in line]
    
    return partitions

def get_partition_size(partition):
    """Retrieve the actual size of the selected partition."""
    result = subprocess.run(["adb", "shell", f"su -c 'blockdev --getsize64 {partition}'"], capture_output=True, text=True)
    if result.returncode == 0 and result.stdout.strip().isdigit():
        return int(result.stdout.strip())
    return None

def choose_partition(partitions):
    """Prompt the user to select a partition or the full disk."""
    print("Available partitions:")
    for i, (part, label, category) in enumerate(partitions, start=1):
        print(f"{i}. {label} ({part}) - {category}")
    print(f"{len(partitions) + 1}. FULL DISK IMAGE")
    
    while True:
        choice = input("Enter the number of the partition (or full disk): ")
        if choice.isdigit() and 1 <= int(choice) <= len(partitions) + 1:
            break
        print("Invalid choice, try again.")
    
    if int(choice) == len(partitions) + 1:
        return "/dev/block/mmcblk0"
    
    partition_name = partitions[int(choice) - 1][0]
    return f"/dev/block/by-name/{partition_name}" if "by-name" in partition_name else f"/dev/block/{partition_name}"

def choose_save_location():
    """Prompt for a valid save location."""
    while True:
        path = input("Enter the full path where the image should be saved (including filename): ")
        if os.path.isdir(path):
            print("Error: You entered a directory. Please specify a filename.")
        elif os.path.isdir(os.path.dirname(path)):
            return path
        else:
            print("Invalid path. Make sure the parent directory exists.")

def detect_progress_tool():
    """Detects an appropriate progress tool for the OS."""
    system = platform.system()
    if system == "Windows":
        return "tqdm"  # Use tqdm for Windows progress bar
    elif system == "Linux":
        return "pv" if shutil.which("pv") else "tqdm"  # Use pv if available on Linux, fallback to tqdm
    return "tqdm"  # Fallback to tqdm for macOS or other systems

def pull_image(partition, save_path, progress_tool):
    """Pull the selected partition or full disk image with progress."""
    if not check_root():
        print("Device is not rooted. Root permissions are required for this operation.")
        exit(1)

    command = ["adb", "shell", f"su -c 'dd if={partition}'"]
    
    partition_size = get_partition_size(partition)
    
    if progress_tool == "pv" and partition_size:
        # Use pv to show progress on Linux
        with open(save_path, "wb") as f:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            total = partition_size
            progress = tqdm(total=total, unit="B", unit_scale=True, desc="Transferring")
            while True:
                data = process.stdout.read(1024 * 1024)  # Read 1 MB chunks
                if not data:
                    break
                f.write(data)
                progress.update(len(data))
            progress.close()
    elif progress_tool == "tqdm" and partition_size:
        # Use tqdm to show progress (Windows/macOS or fallback on Linux)
        with open(save_path, "wb") as f:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            total = partition_size
            progress = tqdm(total=total, unit="B", unit_scale=True, desc="Transferring")
            while True:
                data = process.stdout.read(1024 * 1024)  # Read 1 MB chunks
                if not data:
                    break
                f.write(data)
                progress.update(len(data))
            progress.close()
    else:
        # Default behavior without progress tool
        with open(save_path, "wb") as f:
            subprocess.run(command, stdout=f)
    
    print(f"")
    print(f"Image saved to {save_path}")

def main():
    check_adb()
    get_device()
    
    if not check_root():
        print("Device is not rooted. Root permissions are required to pull partition images.")
        exit(1)
    
    partitions = list_partitions()
    partition = choose_partition(partitions)
    save_path = choose_save_location()
    progress_tool = detect_progress_tool()
    pull_image(partition, save_path, progress_tool)

if __name__ == "__main__":
    main()
