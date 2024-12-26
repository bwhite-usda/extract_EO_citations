

import requests
import PyPDF2
import re
import os
import pandas as pd

def download_pdf(url, filename):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if not chunk:
                    break
                f.write(chunk)
        print(f"Downloaded {filename}")
        return True
    else:
        print(f"Failed to download {url}: Status code {response.status_code}")
        return False

def extract_us_code_citations(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)

        citations = []
        for page_num in range(num_pages):
            page = reader.pages[page_num]
            text = page.extract_text()

            citation_pattern = r"(\d+)?\s*(U\.S\.C\.|USC|Code of Federal Regulations|CFR|7\s*CFR|7 CFR|\d+ CFR)\s*§?\s*(\d+(?:\.\d+)*([a-zA-Z0-9]+)*)"
            matches = re.finditer(citation_pattern, text)

            for match in matches:
                citation = match.group(0)
                start, end = match.start(), match.end()
                context = text[max(0, start - 100):min(len(text), end + 100)]  # Extract 100 chars before and after
                citations.append((citation, context.strip()))

        return citations

def main():
    url_list = [
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

    data = []
    for url in url_list:
        filename = url.split("/")[-1]
        if download_pdf(url, filename):
            citations = extract_us_code_citations(filename)
            for citation, context in citations:
                data.append([filename, citation, context])

            # Optionally, delete the downloaded PDF after processing
            os.remove(filename)

    df = pd.DataFrame(data, columns=["Filename", "Citation", "Context"])
    df.to_excel("extracted_citations.xlsx", index=False)
    print("Citations saved to extracted_citations.xlsx")

if __name__ == "__main__":
    main()

