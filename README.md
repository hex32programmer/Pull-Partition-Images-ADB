
# Pull Partition Images ADB Script

## Description

This Python script allows you to pull partition images or the full disk image from an Android device via ADB (Android Debug Bridge). It requires root access on the device and facilitates the extraction of various device partitions (e.g., boot, system, recovery) to a local machine.

## Features

- **ADB Check**: Verifies if ADB is installed and accessible.
- **Device Detection**: Identifies if a device is connected via ADB.
- **Root Check**: Ensures the device has root access to allow partition pulling.
- **Partition Listing**: Lists available partitions with their respective categories (e.g., bootloader, system, userdata).
- **Partition Selection**: Prompts the user to select a specific partition or the full disk image to pull.
- **Progress Tracking**: Shows a progress bar during the image pulling process using either `tqdm` or `pv` (depending on the platform).
- **Save Path Input**: Prompts the user for a save path and ensures the location is valid.
  
## Requirements

- A rooted Android device.
- ADB installed on your system.
- Python 3.x and required libraries (`tqdm`, `shutil`, `subprocess`).
- Pipe Viewer (`pv`) on Linux

## Usage

1. Ensure ADB is installed and your device is connected with USB debugging enabled.
2. Run the script using Python:
   ```bash
   python pull_partition_images_ADB.py
   ```
3. The script will check if ADB and root access are available. It will then list the partitions and prompt you to select one.
4. After selecting the partition or full disk, specify the location to save the image.
5. The script will begin pulling the image with progress feedback.

## Notes

- Root permissions are required for partition pulling.
- The script defaults to using `tqdm` for progress tracking, but on Linux, it will prefer `pv` if available.

## License
This project is licensed under the Apache-2.0 License. See the LICENSE file for more details.

## Author
@hex32programmer
