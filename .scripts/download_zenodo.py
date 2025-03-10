#!/usr/bin/env python3

import json
import urllib.request
import hashlib
import sys
from pathlib import Path


def calculate_md5(filename):
    """Calculate MD5 hash of a file."""
    md5_hash = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


def download_zenodo_files(output_dir: Path):
    """
    Download all files from Zenodo record 14979785 and verify their checksums.

    Args:
        output_dir: Directory where files should be downloaded
    """
    try:
        print("Fetching files from Zenodo record 14979785...")
        with urllib.request.urlopen(
            "https://zenodo.org/api/records/14979785"
        ) as response:
            data = json.loads(response.read())

        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)

        # Now 'files' is a list, not a dictionary
        for file_info in data["files"]:
            filename = file_info["key"]  # The 'key' is the filename
            output_file = output_dir / filename
            print(f"Downloading {filename}...")
            url = file_info["links"]["self"]  # The link to download the file

            expected_md5 = file_info["checksum"].split(":")[1]  # Extract MD5 hash

            # Download the file
            urllib.request.urlretrieve(url, output_file)

            # Verify checksum
            actual_md5 = calculate_md5(output_file)
            if actual_md5 == expected_md5:
                print(f"✓ Verified {filename}")
            else:
                print(f"✗ Checksum verification failed for {filename}")
                print(f"Expected: {expected_md5}")
                print(f"Got: {actual_md5}")
                sys.exit(1)

        print("\nAll files downloaded and verified successfully!")

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: download_zenodo.py <output_directory>")
        sys.exit(1)

    output_dir = Path(sys.argv[1])
    download_zenodo_files(output_dir)
