import platform
import requests
import os
from pathlib import Path
from humanize import naturalsize  # for human-readable file sizes

# ISO_PATH = "path/to/iso/ubuntu-24.04-desktop-amd64.iso"
from app import create_app  # Import the create_app function

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
    print(f"Starting download of {path}...")
    Path(path).parent.mkdir(parents=True, exist_ok=True)

    try:
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))

        with open(path, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                downloaded += len(chunk)
                f.write(chunk)

                if total_size:
                    percent = int((downloaded / total_size) * 100)
                    size_downloaded = naturalsize(downloaded)
                    size_total = naturalsize(total_size)
                    print(f"\rDownloading: {percent}% ({size_downloaded}/{size_total})", end='')

            print("\nDownload completed!")

    except Exception as e:
        print(f"Error downloading ISO: {e}")
        if path.exists():
            path.unlink()  # Delete partial download


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
