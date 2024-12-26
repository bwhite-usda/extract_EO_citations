import requests
import PyPDF2
import re
import os
import time
import logging
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm  # For progress tracking
from threading import Lock

# Constants
MAX_RETRIES = 3
DELAY = 5
CHUNK_SIZE = 1024
OUTPUT_FILE = r"C:\Users\basil.white\Python\extracted_citations.xlsx"  # Output file path updated

# Setup logging
logging.basicConfig(
    filename="script.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Lock for thread-safe logging
log_lock = Lock()

def thread_safe_log(level, message):
    """Thread-safe logging."""
    with log_lock:
        if level == "info":
            logging.info(message)
        elif level == "error":
            logging.error(message)

def download_pdf(url, filename, delay=DELAY, max_retries=MAX_RETRIES):
    """Downloads a PDF file from the given URL and saves it locally."""
    headers = {'User-Agent': 'My Custom User Agent'}
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, stream=True, headers=headers, timeout=10)
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                        if not chunk:
                            break
                        f.write(chunk)
                thread_safe_log("info", f"Successfully downloaded: {url}")
                return True
            else:
                thread_safe_log("error", f"Failed to download {url}: Status code {response.status_code}")
                break
        except requests.exceptions.RequestException as e:
            thread_safe_log("error", f"Error downloading {url} (attempt {attempt}): {e}")
            time.sleep(delay)
    return False

def extract_us_code_citations(pdf_path):
    """Extracts U.S. Code citations and surrounding context from the given PDF."""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            num_pages = len(reader.pages)
            
            citations = []
            for page_num in range(num_pages):
                page = reader.pages[page_num]
                text = page.extract_text()
                
                # Regex to match U.S. Code citations, CFR citations, and ranges
                citation_pattern = (
                    r"(\d+)\s*(U\.S\.C\.|USC|Code of Federal Regulations|CFR)\s*§?\s*(\d+(?:\.\d+)*([a-zA-Z0-9]+)*)"
                    r"(–\d+)?"
                )
                matches = re.finditer(citation_pattern, text)
                
                for match in matches:
                    citation = match.group(0)
                    start, end = match.start(), match.end()
                    context = text[max(0, start - 100):min(len(text), end + 100)]  # Extract 100 chars before and after
                    citations.append((citation, context.strip()))
                    
        thread_safe_log("info", f"Extracted {len(citations)} citations from {pdf_path}")
        return citations
        
    except (FileNotFoundError, PyPDF2.errors.PdfReadError) as e:
        thread_safe_log("error", f"Error reading PDF {pdf_path}: {e}")
        return []

def infer_title(filename):
    """Infers a human-readable title from a filename."""
    name_parts = filename.split('.')[:-1]
    title = ' '.join(name_parts).replace('_', ' ').replace('-', ' ').title()
    return title

def save_to_excel(output_path, data):
    """Saves the extracted data to an Excel file incrementally."""
    try:
        if os.path.exists(output_path):
            existing_df = pd.read_excel(output_path, engine='openpyxl')
            new_df = pd.DataFrame(data, columns=["Filename", "Citation", "Context"])
            df = pd.concat([existing_df, new_df], ignore_index=True)
        else:
            df = pd.DataFrame(data, columns=["Filename", "Citation", "Context"])
        
        df.to_excel(output_path, index=False, engine='openpyxl')
        thread_safe_log("info", f"Saved data to {output_path}")
    except Exception as e:
        thread_safe_log("error", f"Error saving data to {output_path}: {e}")

def display_filepath(output_file):
    """Displays the full filepath where the output file is saved."""
    absolute_path = os.path.abspath(output_file)
    thread_safe_log("info", f"Excel file saved at: {absolute_path}")
    print(f"Excel file saved at: {absolute_path}")

def download_and_process_pdf(url):
    """Download and process PDF in one function."""
    filename = url.split("/")[-1]
    try:
        if download_pdf(url, filename):
            citations = extract_us_code_citations(filename)
            title = infer_title(filename)
            return [(title, citation, context) for citation, context in citations]
    except Exception as e:
        thread_safe_log("error", f"Unexpected error while processing {url}: {e}")
    finally:
        if os.path.exists(filename):
            os.remove(filename)

def process_pdfs_in_parallel(pdf_urls, output_file):
    """Process multiple PDFs concurrently."""
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(download_and_process_pdf, url) for url in pdf_urls]
        all_citations = []
        for future in as_completed(futures):
            result = future.result()
            if result:
                all_citations.extend(result)
        
        # Save all results to Excel in one go.
        save_to_excel(output_file, all_citations)
        # Display the filepath where the file is saved
        display_filepath(output_file)

def main():
    pdf_urls = [
                'https://www.usda.gov/sites/default/files/documents/00-Preface-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/01-OSEC-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/02-OHS-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/03-OPPE-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/04-DA-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/05-OC-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/06-OCE-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/07-OHA-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/08-OBPA-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/09-OCIO-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/10a-OCFO-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/10b-WCF-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/10c-SCP-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/10d-eGov-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/11-OCR-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/12-AgBF-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/13-HMM-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/14-OSSP-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/15-OIG-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/16-OGC-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/17-OE-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/18-ERS-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/19-NASS-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/20-ARS-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/21-NIFA-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/22-APHIS-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/23-AMS-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/24-FSIS-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/25-FBC-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/26-FSA-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/27-RMA-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/28-NRCS-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/29-CCC-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/29a-FS-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/30-RD-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/31-RHS-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/32-RBCS-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/33-RUS-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/34-FNS-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/35-FAS-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/36-General-Provisions-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/37-Expiring-Leg-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/38-Congressional-Directives-2025-ExNotes.pdf',
        'https://www.usda.gov/sites/default/files/documents/39-GAO-IG-Act-2025-ExNotes.pdf'
    ]
    
    # Process PDFs and save the results to the specified path
    process_pdfs_in_parallel(pdf_urls, OUTPUT_FILE)

if __name__ == "__main__":
    main()

