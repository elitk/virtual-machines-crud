import platform
import subprocess
import sys
import time

import requests
import os
from pathlib import Path
from humanize import naturalsize  # for human-readable file sizes
from requests.adapters import HTTPAdapter
from urllib3 import Retry

# ISO_PATH = "path/to/iso/ubuntu-24.04-desktop-amd64.iso"
from app import create_app  # Import the create_app function
from app.vms import VirtualBoxConfig

ISO_PATHS = {
    'ubuntu': {
        'path': 'drivers/ubuntu-24.04-desktop-amd64.iso',
        'download_url': 'https://releases.ubuntu.com/noble/ubuntu-24.04.1-desktop-amd64.iso',
        'fallback_url': 'https://ubuntu.com/download/desktop'  # Fallback to manual download page

    }
}


def get_os_specific_path(path):
    system = platform.system().lower()
    if system == 'windows':
        return Path(path).as_posix()  # Converts to Windows path style
    return path


def get_ubuntu_iso_url():
    base_url = "https://releases.ubuntu.com/24.04/"
    iso_name = "ubuntu-24.04-desktop-amd64.iso"

    print(f"Will download: {iso_name}")
    return f"{base_url}{iso_name}"


def create_session_with_retry():
    session = requests.Session()
    retries = Retry(
        total=5,  # number of retries
        backoff_factor=1,  # wait 1, 2, 4, 8, 16 seconds between retries
        status_forcelist=[500, 502, 503, 504, 429]  # HTTP status codes to retry on
    )
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session


def check_iso_files():
    for iso_name, iso_info in ISO_PATHS.items():
        iso_path = Path(get_os_specific_path(iso_info['path']))

        if not iso_path.exists():
            print(f"\n{iso_name.upper()} ISO not found!")

            # Check if URL is valid
            try:
                response = requests.head(iso_info['download_url'])
                if response.status_code == 404:
                    print(f"Direct download link not available.")
                    print(f"Please download manually from: {iso_info['fallback_url']}")
                    print(f"And place it in: {iso_path}")
                    continue

                size = naturalsize(int(response.headers.get('content-length', 0)))
                print(f"File size: {size}")

                user_input = input("\nWould you like to download it now? (y/n): ")
                if user_input.lower() == 'y':
                    download_iso(iso_info['download_url'], iso_path)
                else:
                    print(f"Please download manually and place in {iso_path}")
            except requests.exceptions.RequestException as e:
                print(f"Error checking download URL: {e}")
                print(f"Please download manually from: {iso_info['fallback_url']}")
                print(f"And place it in: {iso_path}")


def download_iso(url, path):
    path = Path(path)
    print(f"Starting download of {path}...")
    path.parent.mkdir(parents=True, exist_ok=True)

    session = create_session_with_retry()

    try:
        # First check if file exists and get its size
        response = session.get(url, stream=True, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        total_size = int(response.headers.get('content-length', 0))

        # If file exists and size matches, skip download
        if path.exists() and path.stat().st_size == total_size:
            print(f"File already exists and size matches ({naturalsize(total_size)})")
            return True

        # Download with progress
        with open(path, 'wb') as f:
            downloaded = 0
            start_time = time.time()
            last_print_time = start_time

            for chunk in response.iter_content(chunk_size=8192):
                if not chunk:
                    continue

                downloaded += len(chunk)
                f.write(chunk)

                # Update progress every 0.5 seconds
                current_time = time.time()
                if current_time - last_print_time > 0.5:
                    if total_size:
                        percent = int((downloaded / total_size) * 100)
                        speed = downloaded / (current_time - start_time)
                        size_downloaded = naturalsize(downloaded)
                        size_total = naturalsize(total_size)
                        eta = (total_size - downloaded) / speed if speed > 0 else 0

                        print(f"\rDownloading: {percent}% ({size_downloaded}/{size_total}) "
                              f"Speed: {naturalsize(speed)}/s ETA: {int(eta)}s", end='')

                    last_print_time = current_time

            print("\nDownload completed!")
            return True

    except requests.exceptions.ConnectionError as e:
        print(f"Connection error: {e}")
        print("Please check your internet connection and try again.")
    except requests.exceptions.Timeout as e:
        print(f"Timeout error: {e}")
        print("The download request timed out. Please try again.")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading ISO: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    # Clean up partial download on error
    if path.exists():
        try:
            path.unlink()
            print("Cleaned up partial download")
        except Exception as e:
            print(f"Error cleaning up partial download: {e}")

    return False


def check_virtualbox():
    try:
        vboxmanage = VirtualBoxConfig.get_vboxmanage_path()
        subprocess.run([vboxmanage, '--version'],
                       capture_output=True,
                       check=True)
        print(f"VirtualBox found at: {vboxmanage}")
    except Exception as e:
        print(f"ERROR: VirtualBox not properly configured: {str(e)}")
        print("Please install VirtualBox and ensure VBoxManage is accessible")
        sys.exit(1)


app = create_app()  # Create the app instance

if __name__ == '__main__':
    # Install humanize if not present
    try:
        import humanize
    except ImportError:
        print("Installing required package: humanize")
        os.system("pip install humanize")
        import humanize
    check_iso_files()
    app.run(debug=True)
