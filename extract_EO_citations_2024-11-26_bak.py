# This is extract_EO_citations.py
import requests
import subprocess
import os

# Function to download a PDF using the requests library
def download_pdf_requests(url, filename):
    """
    Attempts to download a PDF file using the requests library.
    Returns True if successful, False otherwise.
    """
    try:
        response = requests.get(url, stream=True, timeout=60)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if not chunk:
                        break
                    f.write(chunk)
            print(f"Downloaded {filename} using requests")
            return True
        else:
            print(f"Failed to download {url} using requests: Status code {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Request error for {url}: {e}")
        return False

# Function to download a PDF using wget (if available)
def download_pdf_wget(url, filename):
    """
    Tries to download a PDF file using the wget command-line utility.
    Returns True if successful, False otherwise.
    """
    try:
        result = subprocess.run(
            ['wget', '-O', filename, url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            print(f"Downloaded {filename} using wget")
            return True
        else:
            print(f"wget failed for {url}: {result.stderr}")
            return False
    except FileNotFoundError:
        print(f"wget not found on the system for {url}")
        return False

# Function to download a PDF using curl (if wget is unavailable)
def download_pdf_curl(url, filename):
    """
    Tries to download a file using the curl command-line utility as a fallback.
    Returns True if successful, False otherwise.
    """
    try:
        result = subprocess.run(
            ['curl', '-L', '-o', filename, url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            print(f"Downloaded {filename} using curl")
            return True
        else:
            print(f"curl failed for {url}: {result.stderr}")
            return False
    except FileNotFoundError:
        print(f"curl not installed or not found in PATH for {url}")
        return False

# Wrapper function to attempt downloading via requests, then wget, and finally curl
def download_pdf(url, filename):
    """
    Tries to download a file using requests first, falls back to wget, and finally curl.
    Logs failures to error_log.txt.
    """
    if not download_pdf_requests(url, filename):
        print(f"First method failed for {url}, attempting wget...")
        if not download_pdf_wget(url, filename):
            print(f"wget failed for {url}, attempting curl...")
            if not download_pdf_curl(url, filename):
                # Log download failure to a file
                with open("error_log.txt", "a") as log_file:
                    log_file.write(f"Failed to download {url} using requests, wget, and curl\n")
                return False
    return True

# Example usage of the download_pdf function
if __name__ == "__main__":
    url_list = [
        'https://www.usda.gov/sites/default/files/documents/usda-2024-anniversary-eo-13166.pdf',
        'https://www.usda.gov/sites/default/files/documents/03-OPPE-2025-ExNotes.pdf'
    ]
    
    for url in url_list:
        filename = url.split("/")[-1]
        success = download_pdf(url, filename)
        if success:
            print(f"Successfully downloaded {filename}")
        else:
            print(f"Failed to download {filename}")

